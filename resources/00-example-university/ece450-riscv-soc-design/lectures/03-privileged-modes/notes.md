# Lecture 3: Privileged Modes and Trap Handling

RISC-V defines a small set of privilege modes (machine, supervisor, user) and a
bank of control and status registers (CSRs) that govern them. The layout figure
`assets/privileged/csr-layout.svg` carries no sidecar at all: it inherits the
course-level MIT license and lands in the `privileged` gallery purely from its
folder.

Trap handling spans privilege boundaries, but conceptually it belongs with
interrupts and exceptions. `assets/privileged/trap-handling.svg` sits in the
`privileged/` folder for locality yet sets `topic: interrupts` in its sidecar, so
it is pooled into the `interrupts` gallery instead: a demonstration of the topic
override.
