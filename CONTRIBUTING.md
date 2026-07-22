# Contributing

Contributing does not take long, you might even be able to fit it within in a coffee break.
Everything past the minimal path below is optional and rewarded on the scorecard in
[`STANDARDS.md`](STANDARDS.md), but are not required to be listed.

## Minimal path

1. Pick a slug for your institution: lowercase, hyphen-separated, e.g.
   `uc-berkeley`. Add an entry to [`institutions.yml`](institutions.yml)
   with full institution name, country, and homepage.
2. Create `resources/<your-slug>/resource.yml`:
   ```yaml
   institution: <your-slug>
   maintainers:
     - name: Your Name
       github: your-github-handle
   ```
3. Add a normal `README.md` next to it. Its first paragraph becomes
   the blurb on the root README, so nothing extra is needed.
4. Drop your material into `resources/<your-slug>/<course-slug>/`, with a
   `course.yml`:
   ```yaml
   title: Your Course Title
   code: YOUR101
   language: [en]
   level: undergraduate
   topics: [cpu, memory]   # informational; doesn't have to be exhaustive
   ```
5. Open a pull request. The `validate` check runs automatically; once it's
   green, you're listed.

Any format is welcome: LaTeX, Markdown, PDF, PPTX, SVG, Jupyter notebooks.
Nothing here builds your material, only checks its structure and metadata.

## Check your work before opening a pull request

```
uv run --project _tools python -m _tools.cli check .
```

This runs exactly what the `validate` workflow runs on your pull request,
with the same error messages.

## Incremental upgrades

Each of these is independent, and each moves your institution up a tier on
the scorecard:

- Fill in `default_license` on `resource.yml`, or `license` on a
  `course.yml`, if you want something other than the repository default
  (see Licensing below).
- Organize shareable figures under an `assets/<topic>/` directory anywhere
  inside your course (see Shared assets below) to enter the pool at
  [`common/`](common/).
- Write a substantive `README.md` for the institution and each course.

## Shared assets

Any file under an `assets/<topic>/` directory anywhere inside a course is
picked up automatically, no metadata required. `<topic>` must be a slug
listed in [`topics.yml`](topics.yml); see below to add one.

To override the topic, add a language, set a friendlier title, or license a
specific asset differently, add a sidecar file named `<asset>.meta.yml`
next to it:

```yaml
# pipeline.svg.meta.yml
topic: cpu
lang: en
title: Five-stage RISC-V pipeline
license: CC-BY-4.0
attribution: "Your Institution, Your Course"
```

Every field is optional. A resolved topic and an open license are what admit
an asset into `common/`; both usually resolve without you setting anything.

### Requesting a new topic

If your material doesn't fit an existing entry in
[`topics.yml`](topics.yml), open a GitHub issue proposing the slug and its
scope, or open a pull request adding the entry directly. It's a small,
quickly reviewed change — the vocabulary stays useful by staying curated,
not by staying closed.

### Large files

Recordings, oversized decks, and datasets don't belong in git. Reference
them instead, in `course.yml`:

```yaml
external_assets:
  - title: Full lecture recording
    url: https://your-host.edu/lecture-03.mp4
    topic: pipeline
    license: CC-BY-4.0
    lang: en
```

### Contributing by submodule

Already maintain your material in your own repository? Add it as a git
submodule at `resources/<your-slug>/<course-slug>` instead of copying files
in. It must be self-describing (its own `course.yml`, `README.md`, and
`assets/<topic>/` layout) to reach the same tiers as directly committed
material. A pooled image from a submodule is embedded in its topic gallery
as a `raw.githubusercontent.com` link pinned to the exact commit the
submodule is checked out at, not copied into this repository. The
repository's default license does not apply to submodule content either
(see Licensing below); it needs its own explicit license to be pooled.

[`resources/ctu-prague`](resources/ctu-prague) is a live example: a
submodule pointing at a real institution's own repository, which predates
this repository's conventions and so is validated and listed without being
pooled. [`resources/aurora-ridge`](resources/aurora-ridge) is the companion
example of the direct-files path, fully structured and pooled, for
comparison.

## Licensing

Accepted licenses: `CC-BY-4.0`, `CC-BY-SA-4.0`, `MIT`, `Apache-2.0`,
`BSD-3-Clause` (see [`LICENSES/`](LICENSES/) for canonical texts), or `none`
to host material without offering it for reuse.

By opening a pull request with material that doesn't set an explicit
license anywhere in `resource.yml`, `course.yml`, or an asset sidecar, you
agree to license that material under the repository default,
**CC-BY-SA-4.0**. Set `license: none` at any of those levels to opt out and
host without pooling instead. Submodule content is exempt from the default;
it needs its own license, from metadata or a `LICENSE` file inside the
submodule, to be pooled.

## Naming

- Institution slugs: `^[a-z0-9]+(-[a-z0-9]+)*$`, must have an
  `institutions.yml` entry.
- Course slugs: `<course-code>-<short-name>`, same character rules.
- Lecture/lab subdirectories: `NN-topic`, e.g. `03-pipeline`.

The validator reports the exact path and the regex it violated, so a naming
failure is fixable from the CI log alone.
