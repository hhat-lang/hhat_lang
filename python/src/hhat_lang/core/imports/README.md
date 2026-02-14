# Imports

Handles loading and resolving type definitions from `.hat` source files within a project's `src/hat_types/` directory.

## Overview

When H-hat code uses `use(type: ...)` statements, the imported type names need to be resolved to their definitions. `TypeImporter` locates the corresponding `.hat` files, parses them for `type` declarations and nested `use(type: ...)` imports, and recursively resolves all transitive dependencies.

## Directory Structure

```
imports/
  __init__.py           # Exports TypeImporter
  types_importer.py     # TypeImporter class with recursive resolution and caching
```

## Module Details

### types_importer.py

**`TypeImporter`** -- Main class for import resolution. Initialized with the project's `hat_types/` directory path.

Key methods:

- **`import_types(names)`** -- Entry point. Takes a list of `CompositeSymbol` names (e.g., `CompositeSymbol(("math", "vector"))`) and resolves them to their type definitions. Returns the parsed results.

Internal helpers:

- **`_parse_file(filepath)`** -- Parses a single `.hat` file to extract type names and import statements. Results are cached using `_PARSE_CACHE` with file modification time (mtime) invalidation, so unchanged files are not re-parsed.
- **`_expand_group_closures(imports)`** -- Expands grouped import syntax (e.g., `A.{B, C}`) into individual import paths (`A.B`, `A.C`).
- **`_parse_type_names(content)`** -- Extracts type declaration names from parsed content.
- **`_parse_type_imports(content)`** -- Extracts `use(type: ...)` import references from parsed content.

The resolution process walks the dependency graph, tolerating circular imports by tracking already-visited files in a `_processing` set. This is important because type definition files can reference each other (e.g., `types_a.hat` imports from `types_b.hat` which imports from `types_a.hat`) -- the importer simply skips files it's already processing rather than entering an infinite loop.

## Connections

- **[`../../dialects/heather/parsing/imports.py`](../../dialects/heather/parsing/imports.py)**: Calls `TypeImporter.import_types()` during the import resolution phase
- **[`../../dialects/heather/parsing/run.py`](../../dialects/heather/parsing/run.py)**: `TypeImporter` uses the dialect's parser to parse `.hat` files
- **[`../data/core.py`](../data/core.py)**: Works with `CompositeSymbol` for multi-part type names

## Current Status

Fully implemented, including mtime-based caching and recursive dependency resolution with circular import tolerance.
