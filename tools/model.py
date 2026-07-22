"""Load the repository into an in-memory model shared by every other tool.

Nothing here writes to disk. `validate.py`, `build_common.py`, `gen_readme.py`,
and `scorecard.py` all start by calling `load()` and then work from the same
`RepoModel`, so structural knowledge (naming rules, resolution order, license
cascade) is defined exactly once.
"""
from __future__ import annotations

import configparser
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

REPO_ROOT_MARKER = "institutions.yml"

INSTITUTION_SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
COURSE_SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
NUMBERED_DIR_RE = re.compile(r"^\d{2}-[a-z0-9]+(-[a-z0-9]+)*$")
LANG_SUFFIX_RE = re.compile(r"[-_]([a-z]{2})(?=\.[^.]+$)")

LICENSES = ("CC-BY-4.0", "CC-BY-SA-4.0", "MIT", "Apache-2.0", "BSD-3-Clause", "none")
DEFAULT_LICENSE = "CC-BY-SA-4.0"

ASSET_META_SUFFIX = ".meta.yml"
ASSETS_DIR_NAME = "assets"
LECTURE_KIND_DIRS = ("lectures", "labs")


def find_repo_root(start: Path) -> Path:
    """Walk upward from `start` looking for the file that marks the repo root."""
    start = start.resolve()
    for candidate in (start, *start.parents):
        if (candidate / REPO_ROOT_MARKER).exists():
            return candidate
    return start


@dataclass
class ModelError:
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


@dataclass
class Institution:
    slug: str
    name: str
    country: str
    homepage: str
    logo: str | None = None


@dataclass
class ExternalAsset:
    title: str
    url: str
    topic: str
    license: str
    lang: str | None = None


@dataclass
class Asset:
    path: Path  # repo-root-relative path to the asset file
    resource_slug: str
    course_slug: str
    topic: str
    topic_valid: bool
    lang: str | None
    license: str
    title: str | None = None
    tags: list[str] = field(default_factory=list)
    attribution: str | None = None
    from_submodule: bool = False

    @property
    def pooled(self) -> bool:
        return self.topic_valid and self.license != "none"


@dataclass
class Course:
    slug: str
    path: Path  # repo-root-relative
    resource_slug: str
    title: str
    code: str
    languages: list[str]
    level: str
    topics: list[str]
    license: str | None
    homepage: str | None
    external_assets: list[ExternalAsset]
    assets: list[Asset]
    is_submodule: bool
    readme_summary: str | None = None


@dataclass
class Resource:
    slug: str
    path: Path  # repo-root-relative
    maintainers: list[dict]
    default_license: str | None
    courses: list[Course]
    readme_summary: str | None = None


@dataclass
class RepoModel:
    root: Path
    institutions: dict[str, Institution]
    topics: dict[str, dict]
    resources: list[Resource]
    gitmodules: dict[str, str]  # course path (posix, repo-relative) -> remote url
    errors: list[ModelError]

    def resource(self, slug: str) -> Resource | None:
        return next((r for r in self.resources if r.slug == slug), None)

    def all_assets(self) -> list[Asset]:
        return [a for r in self.resources for c in r.courses for a in c.assets]


def _load_yaml(path: Path) -> object:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _first_paragraph(readme_path: Path) -> str | None:
    """The first non-heading paragraph of a README, used as a generated-index blurb."""
    if not readme_path.exists():
        return None
    lines = readme_path.read_text(encoding="utf-8").splitlines()
    para: list[str] = []
    started = False
    for line in lines:
        stripped = line.strip()
        if not started:
            if not stripped or stripped.startswith("#"):
                continue
            started = True
        if started:
            if not stripped:
                break
            para.append(stripped)
    return " ".join(para) if para else None


def load_topics(root: Path, errors: list[ModelError]) -> dict[str, dict]:
    path = root / "topics.yml"
    if not path.exists():
        errors.append(ModelError("topics.yml", "file is missing"))
        return {}
    data = _load_yaml(path)
    topics: dict[str, dict] = {}
    if not isinstance(data, list):
        errors.append(ModelError("topics.yml", "must be a YAML list of {slug, label, description}"))
        return topics
    for entry in data:
        slug = isinstance(entry, dict) and entry.get("slug")
        if not slug:
            errors.append(ModelError("topics.yml", f"entry missing 'slug': {entry!r}"))
            continue
        topics[slug] = entry
    return topics


def load_institutions(root: Path, errors: list[ModelError]) -> dict[str, Institution]:
    path = root / "institutions.yml"
    if not path.exists():
        errors.append(ModelError("institutions.yml", "file is missing"))
        return {}
    data = _load_yaml(path) or {}
    out: dict[str, Institution] = {}
    if not isinstance(data, dict):
        errors.append(ModelError("institutions.yml", "must be a YAML mapping of slug -> entry"))
        return out
    for slug, entry in data.items():
        if not isinstance(entry, dict):
            errors.append(ModelError("institutions.yml", f"entry for '{slug}' must be a mapping"))
            continue
        out[slug] = Institution(
            slug=slug,
            name=entry.get("name", ""),
            country=entry.get("country", ""),
            homepage=entry.get("homepage", ""),
            logo=entry.get("logo"),
        )
    return out


def load_gitmodules(root: Path) -> dict[str, str]:
    """Return {submodule path (posix, repo-relative): remote url} from .gitmodules."""
    path = root / ".gitmodules"
    if not path.exists():
        return {}
    parser = configparser.ConfigParser()
    parser.read(path, encoding="utf-8")
    out: dict[str, str] = {}
    for section in parser.sections():
        if not parser.has_option(section, "path"):
            continue
        sub_path = parser.get(section, "path")
        out[Path(sub_path).as_posix()] = parser.get(section, "url", fallback="")
    return out


def _resolve_lang_from_filename(name: str) -> str | None:
    match = LANG_SUFFIX_RE.search(name)
    return match.group(1) if match else None


def _iter_asset_topic_dirs(course_path: Path):
    for assets_dir in sorted(course_path.rglob(ASSETS_DIR_NAME)):
        if not assets_dir.is_dir():
            continue
        for topic_dir in sorted(p for p in assets_dir.iterdir() if p.is_dir()):
            yield topic_dir


def _load_asset_meta(asset_path: Path, errors: list[ModelError], root: Path) -> dict:
    meta_path = asset_path.with_name(asset_path.name + ASSET_META_SUFFIX)
    if not meta_path.exists():
        return {}
    data = _load_yaml(meta_path)
    if not isinstance(data, dict):
        errors.append(ModelError(str(meta_path.relative_to(root)), "sidecar must be a YAML mapping"))
        return {}
    return data


def _load_course_assets(
    course_path: Path,
    resource_slug: str,
    course_slug: str,
    course_license: str | None,
    resource_default_license: str | None,
    topics: dict[str, dict],
    is_submodule: bool,
    errors: list[ModelError],
    root: Path,
) -> list[Asset]:
    assets: list[Asset] = []
    for topic_dir in _iter_asset_topic_dirs(course_path):
        path_topic = topic_dir.name
        for f in sorted(topic_dir.iterdir()):
            if f.is_dir() or f.name.endswith(ASSET_META_SUFFIX):
                continue
            meta = _load_asset_meta(f, errors, root)
            topic = meta.get("topic") or path_topic
            topic_valid = topic in topics
            if not topic_valid:
                errors.append(ModelError(
                    str(f.relative_to(root)),
                    f"unresolved topic '{topic}'; must be one of: {', '.join(sorted(topics))}",
                ))
            lang = meta.get("lang") or _resolve_lang_from_filename(f.name)
            if is_submodule:
                # Submodule content is under its own authorship; the repository-wide default
                # must never silently relicense it. Only an explicit license, from the sidecar
                # or the submodule's own course.yml, admits it to the pool. No resource/repo-default
                # fallback here.
                license_ = meta.get("license") or course_license or "none"
            else:
                license_ = meta.get("license") or course_license or resource_default_license or DEFAULT_LICENSE
            if license_ not in LICENSES:
                errors.append(ModelError(str(f.relative_to(root)), f"invalid license '{license_}'"))
            assets.append(Asset(
                path=f.relative_to(root),
                resource_slug=resource_slug,
                course_slug=course_slug,
                topic=topic,
                topic_valid=topic_valid,
                lang=lang,
                license=license_,
                title=meta.get("title"),
                tags=list(meta.get("tags", []) or []),
                attribution=meta.get("attribution"),
                from_submodule=is_submodule,
            ))
    return assets


def _load_course(
    course_dir: Path,
    resource_slug: str,
    resource_default_license: str | None,
    topics: dict[str, dict],
    gitmodules: dict[str, str],
    errors: list[ModelError],
    root: Path,
) -> Course | None:
    course_slug = course_dir.name
    rel = course_dir.relative_to(root)
    if not COURSE_SLUG_RE.match(course_slug):
        errors.append(ModelError(str(rel), f"course slug '{course_slug}' does not match ^[a-z0-9]+(-[a-z0-9]+)*$"))

    is_submodule = rel.as_posix() in gitmodules
    course_yml = course_dir / "course.yml"
    data: dict = {}
    if not course_yml.exists():
        if is_submodule and not any(course_dir.iterdir()):
            errors.append(ModelError(str(rel), "submodule looks uninitialized; check it out with --recursive"))
            return None
        # No descriptor: still modeled, with blank metadata, so assets under the folder
        # convention stay discoverable and the directory can still reach "Listed" on the
        # scorecard. This is deliberate: a missing course.yml is a lower tier, not a
        # validation failure. Real third-party content (e.g. a submodule that predates
        # this repo's conventions) hits exactly this path.
    else:
        data = _load_yaml(course_yml)
        if not isinstance(data, dict):
            errors.append(ModelError(str(course_yml.relative_to(root)), "course.yml must be a YAML mapping"))
            data = {}

    course_license = data.get("license")

    external_assets: list[ExternalAsset] = []
    for entry in data.get("external_assets", []) or []:
        ea = ExternalAsset(
            title=entry.get("title", ""),
            url=entry.get("url", ""),
            topic=entry.get("topic", ""),
            license=entry.get("license", DEFAULT_LICENSE),
            lang=entry.get("lang"),
        )
        if ea.topic not in topics:
            errors.append(ModelError(
                str(course_yml.relative_to(root)),
                f"external_assets entry '{ea.title}' has unresolved topic '{ea.topic}'",
            ))
        external_assets.append(ea)

    for kind in LECTURE_KIND_DIRS:
        kind_dir = course_dir / kind
        if not kind_dir.is_dir():
            continue
        for entry in sorted(kind_dir.iterdir()):
            if entry.is_dir() and not NUMBERED_DIR_RE.match(entry.name):
                errors.append(ModelError(
                    str(entry.relative_to(root)),
                    "directory name does not match ^\\d{2}-[a-z0-9-]+$",
                ))

    course = Course(
        slug=course_slug,
        path=rel,
        resource_slug=resource_slug,
        title=data.get("title", ""),
        code=data.get("code", ""),
        languages=list(data.get("language", []) or []),
        level=data.get("level", ""),
        topics=list(data.get("topics", []) or []),
        license=course_license,
        homepage=data.get("homepage"),
        external_assets=external_assets,
        assets=[],
        is_submodule=is_submodule,
        readme_summary=_first_paragraph(course_dir / "README.md"),
    )
    course.assets = _load_course_assets(
        course_dir, resource_slug, course_slug, course_license,
        resource_default_license, topics, is_submodule, errors, root,
    )
    return course


def _load_resource(
    resource_dir: Path,
    institutions: dict[str, Institution],
    topics: dict[str, dict],
    gitmodules: dict[str, str],
    errors: list[ModelError],
    root: Path,
) -> Resource:
    slug = resource_dir.name
    rel = resource_dir.relative_to(root)
    if not INSTITUTION_SLUG_RE.match(slug):
        errors.append(ModelError(str(rel), f"institution slug '{slug}' does not match ^[a-z0-9]+(-[a-z0-9]+)*$"))
    if slug not in institutions:
        errors.append(ModelError(str(rel), f"no entry for '{slug}' in institutions.yml"))

    resource_yml = resource_dir / "resource.yml"
    maintainers: list[dict] = []
    default_license: str | None = None
    # A missing resource.yml is not a validation error, only a lower scorecard tier:
    # "a folder of correctly named PDFs" is meant to qualify.
    if resource_yml.exists():
        data = _load_yaml(resource_yml)
        if not isinstance(data, dict):
            errors.append(ModelError(str(resource_yml.relative_to(root)), "resource.yml must be a YAML mapping"))
            data = {}
        if data.get("institution") != slug:
            errors.append(ModelError(
                str(resource_yml.relative_to(root)),
                f"institution field '{data.get('institution')}' does not match directory name '{slug}'",
            ))
        maintainers = list(data.get("maintainers", []) or [])
        default_license = data.get("default_license")
        if default_license and default_license not in LICENSES:
            errors.append(ModelError(str(resource_yml.relative_to(root)), f"invalid default_license '{default_license}'"))

    courses = [
        course
        for course_dir in sorted(p for p in resource_dir.iterdir() if p.is_dir())
        if (course := _load_course(course_dir, slug, default_license, topics, gitmodules, errors, root)) is not None
    ]

    return Resource(
        slug=slug,
        path=rel,
        maintainers=maintainers,
        default_license=default_license,
        courses=courses,
        readme_summary=_first_paragraph(resource_dir / "README.md"),
    )


def load(root: Path) -> RepoModel:
    root = root.resolve()
    errors: list[ModelError] = []
    topics = load_topics(root, errors)
    institutions = load_institutions(root, errors)
    gitmodules = load_gitmodules(root)

    resources: list[Resource] = []
    resources_dir = root / "resources"
    if resources_dir.is_dir():
        for entry in sorted(p for p in resources_dir.iterdir() if p.is_dir()):
            resources.append(_load_resource(entry, institutions, topics, gitmodules, errors, root))

    return RepoModel(
        root=root,
        institutions=institutions,
        topics=topics,
        resources=resources,
        gitmodules=gitmodules,
        errors=errors,
    )
