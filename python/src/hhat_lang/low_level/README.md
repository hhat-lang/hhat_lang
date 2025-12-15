# Low-level

Low-level holds all the code implementation for the low-level quantum language (LLQ) and the target backend.

## Low-level quantum language (LLQ)

LLQ's can be defined as gate-based (digital) or Hamiltonian-based (analog) instructions to be later translated as pulse sequences (or equivalent) on a given target backend. H-hat instructions must be independent of LLQs and target backends definitions, so a same program can potentially be executed on different platforms and devices.


## Target backend

A target backend is the interface for a vendor's hardware, simulator or emulator device. It must have at least one LLQ to read instructions from.
