# Czech Technical University in Prague

Material from the Computer Architectures course (B35APO / BE5B35APO) at the
Faculty of Electrical Engineering, migrated here from
[`comparch-slides`](https://github.com/cvut/comparch-slides) as the first
institution to prove the repository's conventions against real content.

## Status of this migration

This is a structural proof of concept, not a full port: one lecture
(`b35apo-en/lectures/01-intro`) is migrated with its actually-referenced
figures, to exercise every part of the shared-asset pipeline (folder
convention, sidecar overrides, license opt-out, the generated `common/`
pool) against genuine material rather than synthetic examples. The upstream
repository's LaTeX build toolchain (`_latex/`) is intentionally not
migrated; this repository validates structure and metadata, not builds, so a
course directory here is free to bring its own toolchain or none at all.
Remaining lectures and the Czech-language variant (`b35apo-cz`) can follow
the same pattern in a later pull request.
