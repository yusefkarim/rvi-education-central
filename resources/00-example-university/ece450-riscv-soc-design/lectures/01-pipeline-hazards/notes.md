# Lecture 1: Pipeline Hazards and Forwarding

A five-stage pipeline overlaps consecutive instructions, but a later instruction
that reads a register an earlier one has not yet written back sees a stale value:
a data hazard. Forwarding paths route a result from the EX or MEM stage straight
back to a waiting instruction's inputs, avoiding a stall in the common case; see
`assets/pipeline/hazard-forwarding_en.svg`.

The same diagram is provided in German as
`assets/pipeline/hazard-forwarding_de.svg`. The `_en` and `_de` filename suffixes
are what the tooling reads to tag each figure's language in the pooled gallery, no
sidecar required.
