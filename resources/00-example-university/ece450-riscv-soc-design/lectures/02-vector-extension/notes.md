# Lecture 2: The RISC-V Vector Extension

RVV processes a vector register as a set of parallel lanes, each an independent
element-wide slice of the datapath. A single vector instruction keeps every lane
busy, which is where the throughput comes from; see `assets/vector/rvv-lanes.svg`.

Gather and scatter operations break the regular lane pattern: each element uses an
index vector to address memory independently. The German-labelled diagram
`assets/vector/gather-scatter.svg` illustrates this; it carries no filename suffix,
so its `lang` comes from a sidecar override instead.
