"""Single entry point for local contributor checks and scaffolding.

`check` reproduces exactly what the validate.yml workflow runs, so a
contributor can find a problem before opening a pull request. `new-resource`
removes the blank-page problem for a first-time contributor.
"""
from __future__ import annotations

from pathlib import Path

import click

from . import build_common, gen_readme, model as m, scorecard, validate

RESOURCE_YML_TEMPLATE = """institution: {slug}
maintainers:
  - name: {maintainer_name}
    github: {maintainer_github}
# default_license: CC-BY-SA-4.0   # optional override; the repository default applies if omitted
"""

RESOURCE_README_TEMPLATE = """# {name}

<!-- One paragraph about your institution and what's here. It becomes the
     blurb on the generated root README, so a normal paragraph is enough. -->
"""


@click.group()
def main() -> None:
    """RVI Education Central repository tooling."""


@main.command()
@click.argument("root", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path))
def check(root: Path) -> None:
    """Run the exact validation the pull-request workflow runs."""
    errors = validate.validate_repo(m.find_repo_root(root))
    if errors:
        for e in errors:
            click.echo(e, err=True)
        click.echo(f"\n{len(errors)} error(s).", err=True)
        raise SystemExit(1)
    click.echo("ok")


@main.command()
@click.argument("root", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path))
def build(root: Path) -> None:
    """Regenerate common/, README.md, and STANDARDS.md, in that order."""
    resolved = m.find_repo_root(root)
    build_common.build(resolved)
    gen_readme.build(resolved)
    scorecard.build(resolved)
    click.echo("build complete")


@main.command("new-resource")
@click.argument("slug")
@click.option("--name", required=True, help="Full institution name, for institutions.yml and the README stub.")
@click.option("--maintainer-name", required=True)
@click.option("--maintainer-github", required=True)
@click.option("--root", "root", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path))
def new_resource(slug: str, name: str, maintainer_name: str, maintainer_github: str, root: Path) -> None:
    """Scaffold resources/<slug>/ with a resource.yml and README.md stub."""
    if not m.INSTITUTION_SLUG_RE.match(slug):
        raise click.ClickException(f"'{slug}' does not match ^[a-z0-9]+(-[a-z0-9]+)*$")
    resolved = m.find_repo_root(root)
    resource_dir = resolved / "resources" / slug
    if resource_dir.exists():
        raise click.ClickException(f"resources/{slug} already exists")

    resource_dir.mkdir(parents=True)
    (resource_dir / "resource.yml").write_text(
        RESOURCE_YML_TEMPLATE.format(slug=slug, maintainer_name=maintainer_name, maintainer_github=maintainer_github),
        encoding="utf-8",
    )
    (resource_dir / "README.md").write_text(RESOURCE_README_TEMPLATE.format(name=name), encoding="utf-8")

    click.echo(f"created resources/{slug}/")
    click.echo(f"next: add an entry for '{slug}' to institutions.yml, then add a course directory under resources/{slug}/")


if __name__ == "__main__":
    main()
