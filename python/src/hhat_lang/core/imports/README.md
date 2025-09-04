# Imports Layer Overview

Facilities for discovery, parsing, and linkage of external type and function artifacts across intermediate representation units. The layer provides name to path mapping, on demand materialization of modules into the program graph, and population of reference structures used during validation and linking. It is dialect agnostic and delegates syntax to an injected grammar and start rule.

## 1. Purpose
Provide deterministic and validated resolution of cross unit references. The layer maps qualified names to module files under the project source tree, parses modules when needed, and returns pairs that associate logical keys with defining module paths. These pairs are consumed by the program graph to build reference tables for types and for functions.

## 2. Project Layout Assumptions
* Project root contains a source tree named `src`.
* Type definitions live under `src/hat_types`.
* Function and program files are addressed under `src`.
* Modules are plain text files with extension `.hat`.
* Importers compute module paths relative to these directories.
* Importers compute module paths under these source subtrees. Inputs must avoid traversal segments and remain confined to the project root.

## 3. Name to Path Mapping
**Terminology**: Artifact denotes a declared type or function inside a module. Function descriptor denotes a pair of a function name and an ordered tuple of argument types. Staging set denotes the collection of nodes accumulated before graph finalization.
Qualified names are treated as ordered sequences of segments.
* **Single segment**: the file name equals the segment and the artifact name also equals the same segment.
* **Two or more segments**: directory path is the prefix that excludes the last two segments, the file name equals the penultimate segment, and the artifact name equals the final segment.
* The physical path is computed by joining the base directory, the derived directory path, and the file name plus the `.hat` extension.

This mapping is uniform for both type references and function references. The final segment denotes the artifact name within the addressed module file.

## 4. Loading and Graph Interaction
* For each computed module path, if the module is not already present in the program graph, the importer reads the file and invokes the provided parser pipeline that consists of a grammar provider and a start rule. The parser pipeline materializes the resulting intermediate representation unit into the graph as a new node.
* Addition is idempotent with respect to a file path during discovery before graph finalization. Repeated requests for the same path do not duplicate nodes within this phase.
* Import operations must run before graph finalization. Finalization moves accumulated nodes into an immutable set and computes a perfect hash for constant time addressing.
* Finalization is a required step before the graph is used for constant time addressing or validation.
* Function discovery operates over the prebuild staging set of nodes. Post finalization discovery is out of scope for this layer.
* Parse failures in the injected pipeline propagate to the caller. Higher layers may surface them as typed errors.
* Existence checks during discovery consult only the prebuild staging set and do not consult the finalized node set.
* Typical workflow: request names for types or functions, load any missing modules, aggregate pairs, populate reference tables with the program graph routine, then finalize the graph.

## 5. Type Resolution
* For each requested type name, the importer returns a pair that associates the logical type key with the module file path that is addressed by the name to path mapping.
* Discovery triggers loading of any not yet materialized module files that are required to resolve the request.
* At this stage the importer does not verify that the addressed module declares the requested type. Name level validation remains the responsibility of consumers until a dedicated check is introduced in the graph.
* Returned keys for types are artifact names rather than fully qualified names. Consumers that require uniqueness across modules must avoid collisions or enforce qualification at a higher layer.
* When multiple requested type names are identical across modules, later pairs overwrite earlier ones due to mapping semantics.
* Cycles during discovery are tolerated. Completeness is enforced when the program graph is finalized. Missing modules yield file not found or validation errors.
* Overwrite behavior for duplicate type names follows the request sequence and is a contract.

## 6. Function Resolution
* For each requested function name, the importer queries the accumulated nodes for definitions with the requested name in the addressed module. The search scope is the addressed module only. If multiple overloads exist in that module, one pair is returned per overload.
* Each pair associates a function descriptor formed from the name and ordered argument types with the module file path that defines it.
* If no definition with the requested name is present in the addressed module, an error is raised by the program graph utility used to query functions.
* When multiple modules define the same function descriptor, later entries overwrite earlier ones in the aggregated mapping.

## 7. Reference Table Construction
* A routine in the program graph consumes the returned pairs to populate the reference structures for types and for functions.
* References are stored as logical keys that map to node keys derived from module paths and stable within a process.
* During graph finalization, validation verifies that referenced modules are present in the graph. It does not recheck that the target name exists inside the module. If any referenced module is missing, finalization fails.

## 8. File Inventory
* `__init__.py`: Package marker that exposes the type import facility for convenience.
* `importer.py`: Common importer infrastructure that derives module paths from qualified names, performs file loading and parser invocation, inserts resulting units into the program graph, and provides two concrete mechanisms for resolving types and functions. The function mechanism returns one entry per overload present in the addressed module.
* `utils.py`: Base protocol for aggregated import results expressed as two mappings, one for types and one for functions.
