# Czech Technical University in Prague


Czech Technical University (CTU) in Prague.
Course material is currently submitted as git submodules that do NOT follow the standards of this repo.
We hope to restructure to adhere and pool resources in the future.

The Computer Architectures course material (B35APO / BE5B35APO) at the
Faculty of Electrical Engineering, brought in as a git submodule pointing
at the real upstream repository,
[`cvut/comparch-slides`](https://github.com/cvut/comparch-slides) — the
worked example for the by-reference contribution path described in
`CONTRIBUTING.md`.

## Status

`comparch-slides` predates this repository's conventions: it has no
`course.yml` and its shared figures live in its own `common/` directory
rather than an `assets/<topic>/` folder, so nothing from it is auto-pooled
yet. That's expected, not an error — the validator models unstructured
submodule content without failing CI, and it shows up here as **Listed**
rather than **Structured** on the scorecard
until course.yml and an `assets/<topic>/` layout are added upstream. See
[`resources/aurora-ridge`](/resources/aurora-ridge) for the direct-files
path with full structure and a pooled example instead.
