# RVI Education Central — Technical Plan

A central GitHub repository where academics and professors publish, discover, and reuse
RISC-V lecture and lab material. Structure is defined by lightweight conventions and
enforced by automation rather than manual gatekeeping, so contributing stays cheap while
the repository stays navigable.

This plan is grounded in the reference material under `references/comparch-slides`, whose
`common/` directory already demonstrates the pattern we are generalizing: shared figures
organized by topic (`cpu`, `memory`, `io`, `logic`, …), with language suffixes such as
`-en.svg` and `-cz.svg`, pulled into individual lectures through a path convention.


## 1. Design goals and constraints

The repository has to earn contributions from busy academics, so the guiding constraint is
that the default path to contributing is nearly effortless and every stricter requirement is
opt-in and rewarded rather than forced. A professor who drops a folder of PDFs with a name
that matches the convention should already be listed. Everything beyond that (metadata,
shared assets, licensing) buys more visibility and a higher standing on a public scorecard,
which is how we pull people toward the standards without blocking them.

Four decisions frame the rest of the plan, confirmed up front:

- Resource directories are format-agnostic. CI validates structure and metadata, never build
  toolchains. LaTeX, Markdown, PPTX, PDF, SVG, and notebooks are all first-class.
- Shareable assets are categorized two ways that layer: a folder convention for zero effort,
  and an optional sidecar metadata file for override and enrichment.
- A repository-wide default license (CC-BY-SA-4.0) applies to directly contributed material,
  overridable at the resource, course, or individual asset level. Contributors can opt a piece
  of material out of reuse explicitly, which hosts it but keeps it out of the shared pool.
- Institutions may contribute material two ways: directly, with files committed into a resource
  directory, or by reference, with their own repository added as a git submodule. Both are
  first-class and validated identically once checked out.
- All automation is written in Python, exposed through GitHub Actions.


## 2. Repository layout

```
/
├── README.md                     generated: landing page + institution index
├── STANDARDS.md                  generated: compliance scorecard / leaderboard
├── CONTRIBUTING.md               hand-written: how to add material
├── institutions.yml             registry of institution slugs (human-edited, CI-validated)
├── topics.yml                    controlled topic vocabulary (human-edited via PR/issue)
├── LICENSES/                    reference copies of accepted license texts
├── schema/
│   ├── institution.schema.json
│   ├── resource.schema.json
│   ├── course.schema.json
│   └── asset-meta.schema.json
├── tools/                        Python automation (the single source of logic)
│   ├── model.py                  load + resolve the repo into an in-memory model
│   ├── validate.py               structural + schema + naming checks
│   ├── build_common.py           regenerate the common/ symlink tree + galleries
│   ├── gen_readme.py             regenerate README.md and per-institution indexes
│   ├── scorecard.py              compute compliance tiers, write STANDARDS.md + badges
│   └── pyproject.toml            pinned deps: pyyaml, jsonschema, click
├── .github/
│   ├── workflows/
│   │   ├── validate.yml          runs on pull_request
│   │   └── build.yml             runs on push to main (regenerate + bot-commit)
│   └── actions/setup/            composite action: install uv + sync tools/ deps
├── common/                       generated, bot-owned symlink tree (do not hand-edit)
│   ├── cpu/
│   ├── memory/
│   └── …
└── resources/
    └── <institution-slug>/
        ├── resource.yml
        ├── README.md
        └── <course-slug>/
            ├── course.yml
            ├── README.md
            ├── lectures/
            │   └── 01-intro/
            │       ├── slides.pdf
            │       └── assets/
            │           └── cpu/
            │               ├── pipeline.svg
            │               └── pipeline.svg.meta.yml   (optional)
            └── labs/
                └── 01-toolchain/
                    └── …
```

Three layout notes. First, institution directories live under a `resources/` container rather
than sprawling across the repository root next to `tools/` and `schema/`. This keeps the root
readable and gives validation a single unambiguous place to scan; the container is a small
deviation from a literal reading of the goal that pays off in tooling simplicity. Second,
`common/` is entirely machine-generated. It is owned by the build bot, and manual edits there
are rejected by CI so the tree can always be rebuilt from scratch. Third, a `<course-slug>`
directory can be either real files as shown above or a git submodule pointing at the
institution's own repository; the two forms are interchangeable to the tooling, and section 5.3
covers the submodule case.


## 3. Naming conventions

Names are the one thing CI cannot infer, so they are the strictest rule and the first gate a
contributor meets.

Institution slugs are lowercase, hyphen-separated, matching `^[a-z0-9]+(-[a-z0-9]+)*$`, for
example `ctu-prague`, `iit-madras`, `uc-berkeley`. A slug is only valid if it has an entry in
the top-level `institutions.yml` registry, which maps the slug to the institution's full
name, country, homepage, and an optional logo. Requiring the registry entry gives us enforced
naming and clean human-readable metadata for the generated README in one step, and it makes
slug collisions and typos impossible to merge.

Course slugs follow `<course-code>-<short-name>`, again lowercased and hyphenated, for example
`b35apo-computer-architecture`. Lecture and lab subdirectories use a two-digit ordering prefix
followed by a topic slug, mirroring the reference repository's `01-intro`, `03-cpu`,
`04-pipeline`. The numeric prefix gives deterministic ordering in generated listings without a
separate sort key.

The validator reports naming failures with the exact offending path and the regex it violated,
so the fix is obvious from the CI log alone.


## 4. Metadata model

Metadata is YAML, validated against JSON Schema with Python's `jsonschema`. There are three
descriptor files plus one optional per-asset sidecar. Each is small, and each field that can
be inferred has a sensible default so the minimum viable contribution needs almost nothing.

`resource.yml` sits at the root of an institution's directory and is mostly a pointer back to
the registry plus contact and maintenance info:

```yaml
institution: ctu-prague          # must match the directory name and a registry entry
maintainers:
  - name: Jane Doe
    github: janedoe
default_license: CC-BY-4.0        # inherited by courses/assets that omit their own
```

`course.yml` describes one course:

```yaml
title: Computer Architectures
code: B35APO
language: [en, cz]               # ISO 639-1 codes present in this course
level: undergraduate
topics: [cpu, memory, pipeline, io]
license: CC-BY-4.0               # optional; falls back to resource default_license
homepage: https://cw.fel.cvut.cz/wiki/courses/b35apo/en/start
```

`asset-meta.schema.json` governs the optional sidecar described in the next section.

Descriptions for the generated README come from the `title`/`topics` fields and from the first
paragraph of each `README.md`, so a professor writing a normal readme is simultaneously feeding
the index with no extra work.


## 5. Shared assets and the `common/` pool

This is the heart of the system and the part that most needs to stay low-friction, so it is
built as two layers with a single, documented resolution order.

The default layer is a folder convention. Any file placed under an `assets/<topic>/` directory
anywhere inside a course is categorized by that `<topic>` with zero metadata. Dropping
`pipeline.svg` into `lectures/03-cpu/assets/cpu/` is enough for it to be recognized as a `cpu`
asset. This mirrors exactly what `references/comparch-slides/common/cpu/` already does, so it is
a proven, familiar pattern.

The enrichment layer is an optional sidecar file named `<asset>.meta.yml` placed next to the
asset. It exists for two reasons: to override or refine what the path implies, and to carry the
license that admits the asset into the shared pool.

```yaml
# lectures/03-cpu/assets/cpu/pipeline.svg.meta.yml
topic: cpu                        # overrides path inference if they disagree
lang: en                          # overrides the filename suffix
title: Five-stage RISC-V pipeline
tags: [pipeline, hazards, forwarding]
license: CC-BY-4.0                # required to enter common/; else inherits course license
attribution: "CTU Prague, APO course"
```

Resolution order, applied by `tools/model.py`, is fixed and documented so nothing is
ambiguous:

1. Topic comes from the sidecar `topic` if present, otherwise from the nearest ancestor
   `assets/<topic>/` directory, otherwise the asset is uncategorized and not pooled. In both
   cases the resolved topic must exist in the central `topics.yml` vocabulary, described below,
   or validation fails with the list of valid topics.
2. Language comes from the sidecar `lang`, otherwise from a `-en` / `-cz` (or `_en` / `_cz`)
   filename suffix, otherwise unset.
3. License comes from the sidecar `license`, otherwise the course license, otherwise the
   resource `default_license`, otherwise the repository-wide default (CC-BY-SA-4.0). Because
   the cascade always terminates in the repo default, a license normally always resolves. A
   contributor who wants to host material without offering it for reuse sets `license: none`
   (or an all-rights-reserved marker) at any level, which excludes it from the pool.

An asset is admitted to the pool when it has a resolved topic and a resolved open license,
which is the common case by default. Licensing is therefore a light opt-out rather than an
opt-in form: set nothing and your figures under `assets/<topic>/` flow into the pool under the
share-alike default; override the license anywhere in the cascade to relicense; set `none` to
hold a piece back. The one exception is submodule content, covered in section 5.3, where the
repo default deliberately does not apply.

`tools/build_common.py` regenerates the tree deterministically. For each admitted asset it
creates a relative symlink at `common/<topic>/<institution>__<original-name>`. Namespacing stops
at the institution rather than including the course, which keeps names short and puts the least
burden on contributors while still preventing collisions between different institutions that use
the same file names (something the reference repo's flat topic folders cannot do). The remaining
narrow case, one institution reusing the same filename under the same topic across two courses,
is handled by the builder appending a short deterministic suffix only when it actually detects a
clash, and the validator emits a warning so the contributor can rename if they prefer a cleaner
result. Symlinks are relative so the tree is portable and survives clones.

Symlinks alone have a known weakness: GitHub's web view renders a symlink as a tiny text file
showing its target, not as the image itself, and Windows checkouts without developer mode may
materialize them as plain text. Because `common/` is meant for human discovery, the builder also
emits a `common/<topic>/README.md` gallery per category that embeds the real images by relative
path and lists title, source institution, language, and license in a table. Human browsers get
real previews from the galleries; build tools and scripts get stable filesystem paths from the
symlinks. The authoritative record is always the metadata model, so both artifacts are pure
derivatives that can be thrown away and rebuilt.

### 5.1 The topic vocabulary

Topics are a controlled vocabulary held in a single central `topics.yml` at the repository root,
which is the one place anyone looks to see what categories exist. Each entry pairs a slug with a
human label and a short description, seeded from the reference repository's proven set (`cpu`,
`memory`, `io`, `logic`, `arch`, `abi`, `numbers`, and so on) and extended with RISC-V specific
categories such as privileged architecture, vector, compressed, toolchain, and boot. The
validator loads this file and rejects any asset whose resolved topic is not in it, so the pool
never fragments into near-duplicate categories invented ad hoc.

Because the vocabulary is deliberately governed rather than open, `CONTRIBUTING.md` documents how
to request a new topic: open a GitHub issue proposing the slug and its scope, or open a pull
request adding the entry to `topics.yml` directly. Either way the addition is a small reviewed
change, which is the right amount of friction to keep the taxonomy coherent without blocking a
contributor for long. Keeping the vocabulary in its own YAML file rather than buried in a JSON
schema enum is a low-friction choice, it is the natural thing to point a professor at and the
natural thing to edit in a PR.

### 5.2 Large binaries and external references

Not everything belongs in git. Lecture videos, multi-hundred-megabyte slide decks, and datasets
are referenced by external link rather than committed, keeping clones fast and avoiding Git LFS
quotas. An external resource is a metadata-only entry, declared in the course descriptor, that
carries the same fields a pooled asset would:

```yaml
# course.yml
external_assets:
  - title: Full lecture recording, pipelining
    url: https://videos.example.edu/apo/lecture-03.mp4
    topic: pipeline
    license: CC-BY-4.0
    lang: en
```

External resources are never symlinked, since there is no local file, but a categorized and
licensed one appears in its topic gallery as a link entry alongside the inline images, so it is
just as discoverable. The generated indexes surface external material next to committed material,
and the contributor's only obligation is to keep the link alive. This gives contributors a clean
answer for their heaviest material without pushing large binaries through the repository.

### 5.3 Contributing by submodule

An institution that already maintains its material in its own git repository can attach that
repository as a submodule at `resources/<institution>/<course>` instead of copying files in.
This is a natural fit for the RISC-V audience: the reference `comparch-slides` material is
itself a standalone repository, and many professors keep their slides under their own version
control already. The submodule must be self-describing, carrying its own `course.yml`,
`README.md`, and `assets/<topic>/` folders, so that once checked out it passes exactly the same
validation as directly committed content with no special-casing in the model.

Three mechanical consequences follow from git's submodule semantics. First, every workflow that
inspects content must check out submodules (`actions/checkout` with `submodules: recursive`),
otherwise the model sees empty directories. Second, the parent repository pins a specific commit
of each submodule, so new upstream material becomes visible only when that pointer is bumped;
this can stay a manual maintainer action or be automated with a scheduled workflow that opens a
pointer-bump pull request, and either way the pinning is a feature because it makes the central
repository's state reproducible. Third, GitHub's web view does not inline a submodule's files
into the parent, so a gallery that referenced submodule assets by relative path would render
broken images. The builder handles this by detecting when an asset lives inside a submodule and
emitting a `raw.githubusercontent.com` URL pinned to the submodule's remote and current SHA,
both of which CI can read from `.gitmodules` and the pinned commit. Those raw URLs inline
correctly in the generated galleries, and the `common/` symlinks continue to resolve on any
fully checked-out working tree.

Licensing is the one place submodules are treated differently on purpose. A submodule is
external content under its own authorship and its own LICENSE, so the repository-wide default
must never silently relicense it. A submodule asset is admitted to the pool only if the license
resolves from metadata or a LICENSE file inside the submodule itself; if none is present, the
content is still listed and browsable but is not pooled, and the scorecard flags the missing
license so the maintainer knows what is holding it back.


## 6. Licensing

The repository accepts a fixed allowlist of open licenses suitable for educational reuse,
Creative Commons variants such as CC-BY-4.0 and CC-BY-SA-4.0 plus common permissive code
licenses for lab code (MIT, Apache-2.0, BSD). The allowlist lives in the schema as an enum, so
an unknown or proprietary license string fails validation with a clear message, and `none` is
an accepted value meaning host-but-do-not-pool. Reference copies live under `LICENSES/`.

The repository-wide default is CC-BY-SA-4.0. Every piece of directly contributed material is
offered under it unless a resource, course, or asset overrides the value in the cascade
described in section 5. Defaulting a license onto contributed work is sound on an
inbound-equals-outbound basis, the contributor accepts the default by opening the pull request,
but only if that is stated plainly, so `CONTRIBUTING.md` and the pull request template both spell
out the default and the override mechanism. Share-alike is chosen as the default because it keeps
reused educational material open downstream, while contributors who prefer the more permissive
CC-BY, or a code license for lab sources, simply set it. Submodule content is exempt from the
default for the authorship reasons given in section 5.3.


## 7. Automation

All repository logic lives in `tools/` as importable Python, and the workflows are thin
wrappers that call it. This keeps the behavior testable locally (`python -m tools.validate .`)
and identical in CI, which matters for contributors who want to check their work before opening
a pull request.

The validation workflow runs on every pull request and is the only required status check. It
checks out submodules recursively so that referenced material is validated identically to
directly committed material, loads the whole repository into the model, runs schema validation
on every descriptor, enforces naming, verifies that every resolved topic exists in `topics.yml`,
confirms that registry entries exist for every institution directory,
checks that `.gitmodules` entries resolve, and rejects manual edits under `common/`. Failures
are annotated inline on the diff so a contributor sees the problem on the exact line.

The build workflow runs on push to `main` after a merge. It regenerates the `common/` symlink
tree and galleries, the root `README.md` and per-institution indexes, and the `STANDARDS.md`
scorecard with its badges, then commits the results back with the actions bot identity. To avoid
an infinite build loop, the workflow is guarded with `if: github.actor != 'github-actions[bot]'`
and its bot commit carries `[skip ci]`, and the regeneration is deterministic so a no-op merge
produces an empty diff and no commit at all.

Determinism is a hard requirement across all generators: sorted iteration, stable namespacing,
and no timestamps in output, so the only time a generated file changes is when the underlying
material actually changed. This keeps bot commits meaningful and reviewable.


## 8. Compliance tracking and the scorecard

The mechanism that pulls people toward the standards without punishing anyone is a public,
automatically computed scorecard rendered into `STANDARDS.md` and surfaced as badges. Every
resource directory earns a tier based on how much of the optional structure it has adopted:

- Listed: the directory name is valid and has a registry entry. This is the floor; a folder of
  correctly named PDFs qualifies.
- Structured: `resource.yml` and every `course.yml` are present and valid.
- Documented: every course and the institution have a non-trivial `README.md`.
- Pooled: at least one asset is admitted to `common/`, meaning topics and licensing are set.

`tools/scorecard.py` scores each resource, assigns a tier (for example ⬜ Listed, 🥉 Structured,
🥈 Documented, 🥇 Pooled), and writes a leaderboard table sorted by tier and contribution count.
The same script emits a shields.io endpoint JSON per institution committed into the repo, so an
institution can drop a live badge into its own README and see its standing update automatically.
Because the whole thing is generated from the model, a contributor who adds one `course.yml`
watches their tier rise on the next merge, which is the low-friction feedback loop that makes the
standards feel like a game to climb rather than a wall to clear.


## 9. Contributor workflow

The onboarding story has to fit in a professor's coffee break. The minimal path: create
`resources/<slug>/`, add an entry to `institutions.yml`, drop material into a course folder with
a conventional name, open a pull request. Validation runs, the contributor is Listed, done. From
there `CONTRIBUTING.md` shows the incremental upgrades, add a `course.yml`, set a license once,
move figures under `assets/<topic>/`, each of which is independently valuable and independently
rewarded on the scorecard.

To make local checking trivial, `tools/` ships a single entry point so a contributor can run the
exact CI checks before pushing, and the same command can scaffold a new resource directory from a
template to remove the blank-page friction entirely.


## 10. Rollout phases

Phase one establishes the skeleton: the layout, the schemas, `institutions.yml`, the validation
workflow, and `CONTRIBUTING.md`, seeded by migrating the `references/comparch-slides` material in
as the first real institution to prove the conventions against genuine content.

Phase two adds generation: `gen_readme.py` and the build workflow with the bot-commit loop guard,
so the index maintains itself.

Phase three adds the shared pool: `build_common.py`, the sidecar schema, the symlink tree, and
the category galleries, validated against the migrated figures which already fit the topic model.

Phase four adds the scorecard and badges, turning adherence into a visible, self-updating signal.

Sequencing generation before the shared pool is deliberate: the README and validation deliver
value with the least contributor effort, which is what will attract the first cohort, while the
symlink pool and scorecard reward the contributors who arrive once the repository already looks
alive.


## 11. Risks and open questions

The symlink rendering gap on GitHub web is the main technical wrinkle; the galleries mitigate it
but are worth validating with a real browse-through before committing to symlinks over a
pure-manifest alternative. Windows contributors cloning the repo may see broken symlinks locally,
which is acceptable if we document that `common/` is a generated convenience and never something
they edit or depend on for building.

The remaining open item is submodule freshness: whether pointer bumps that pull in new upstream
material should be a manual maintainer action or an automated scheduled pull request. Manual
keeps the central repository's state deliberate and reproducible; automated keeps material fresh
with less babysitting. The recommendation is a weekly bump pull request opened by a bot, which
keeps material current while leaving a human to review each pointer move, but this can be decided
at phase three without affecting anything earlier.

Three earlier questions are now settled and reflected above. Asset namespacing stops at the
institution, with per-clash disambiguation, to keep names short and the burden low (section 5).
Very large binaries are referenced by external link from metadata rather than committed or pushed
through Git LFS (section 5.2). The topic vocabulary lives in a central, governed `topics.yml`,
extended through a documented issue-or-PR request process (section 5.1).
