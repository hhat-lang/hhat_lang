# Compiler Layer Overview

Interfaces and orchestration logic for transforming dialect-specific parsed representations (AST or direct builders) into Core IR modules ready for import/link, execution, and backend emission. This layer defines the stable contract a dialect compiler must satisfy without prescribing parsing strategy or syntax shape.

## 1. Purpose
Provide a small, explicit abstraction boundary between (a) dialect frontends that understand source syntax and (b) the Core IR + runtime subsystems. The compiler layer centralizes:
* Lowering pipeline stages (parse → validate → build IR structures).
* Integration points for multi-dialect / mixed classical–quantum compilation.
* Capability discovery (available evaluators, quantum language backends, device specs) influencing lowering choices.
* Deterministic production of IR Modules, Blocks, Instructions, and populated symbol / reference tables consistent with Core invariants.

## 2. Scope & Responsibilities
Included:
* Abstract base compiler API (`BaseCompiler`) establishing required entry points (`parse`, `evaluate` / future `lower`).
* Coordination placeholders for: other dialect compilers, classical vs quantum lowering paths, evaluator selection.
* Strategy hooks for injecting backend capability checks early (fail fast if an instruction family cannot be emitted downstream).
* Normalization rules from dialect-specific constructs into canonical IR instruction & type forms.

Excluded (handled elsewhere):
* Concrete parsing logic (dialect directories own tokenization / AST building).
* Execution semantics (execution layer / evaluators).
* Memory allocation details (memory layer) or runtime value materialization.
* Cross-module symbol resolution (imports layer) beyond emitting required reference metadata.
* Low-level backend instruction emission (lowlevel layer).

## 3. High-Level Flow
Dialect Source → (Dialect Parser) → Parsed Representation (AST or builder calls) → Compiler Lowering → Core IR Module(s) → (Imports / Linking) → Execution / Backend.

Stage emphasis within this layer:
1. Parse: Produce a structurally validated intermediate (may be skipped if dialect builds IR directly).
2. Analyze & Normalize: Apply dialect rules, resolve local symbols, enforce early type constraints.
3. Lower: Create IR blocks + instructions with stable ordering / hashing assumptions respected.
4. Prepare for Linking: Emit placeholders or reference table entries for external symbols/types (no lazy late binding).
5. Handoff: Return fully constructed IR module graph to import layer / execution orchestrator.

## 4. Status
Current implementation provides only the abstract base (`BaseCompiler`). Concrete dialect compilers, extended lowering APIs, and optimization hooks will live in dialect directories and toolchain integration layers. This README intentionally omits per-file detail pending expansion.