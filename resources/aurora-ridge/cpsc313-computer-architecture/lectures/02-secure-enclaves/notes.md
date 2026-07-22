# Lecture 2: Trusted Execution and Secure Enclaves

A secure enclave carves out a region of memory that even a compromised
operating system cannot read or modify. Code and data inside the enclave
boundary are only accessible through a narrow, hardware-checked entry
point; everything outside, including the OS kernel, is treated as
untrusted — see `assets/security/enclave-boundary.svg`.

The recorded lecture (linked from `course.yml`) covers the RISC-V
enclave-relevant proposals and how they compare to existing trusted
execution environments on other architectures.
