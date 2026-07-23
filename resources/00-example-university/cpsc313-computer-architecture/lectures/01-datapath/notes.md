# Lecture 1: The CPU Datapath and Memory Hierarchy

A single instruction moves through five stages: fetch, decode, execute,
memory access, and writeback. Each stage does a small, fixed amount of
work, which is what makes pipelining them profitable — see
`assets/cpu/datapath-overview.svg`.

Below the CPU, memory is organized as a hierarchy: a small, fast L1 cache
backed by a larger, slower L2, an even larger L3, and finally main memory
(DRAM). Each level trades capacity for latency; see
`assets/memory/cache-hierarchy.svg`.
