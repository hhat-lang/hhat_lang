# Import System

The `imports/` module implements H-hat's module import and dependency management system.

## Overview

Handles:
- Local file imports
- Remote resource loading
- Module caching
- Dependency resolution
- Circular import detection

## Structure

```
imports/
├── __init__.py     # Module exports
├── importer.py     # Import logic
└── utils.py        # Import utilities
```

## Import Syntax

```heather
// Single import
use(const:<path.constant-name>)

// Multiple imports
use(
    type:<path.type1>
    fn:<path.function1>
)

// Namespace import
use(module:<path.module>)
```

## Import Resolution

```
Import Statement
    ↓
Parse Path
    ↓
Check Cache
    ├─ Found → Return cached
    └─ Not Found ↓
         Search Paths
              ↓
         Load File
              ↓
         Parse & Compile
              ↓
         Cache Result
              ↓
         Return Module
```

## Module Search Paths

1. Current directory
2. Standard library (`src/hat_types/.hat_std/`)
3. User-defined paths
4. Remote repositories (future)

## Integration Points

- **core.compiler**: Compile imported modules
- **core.data**: Import symbols
- **toolchain.project**: Project dependencies

## Related Documentation
- [Core README](../README.md)
- [Compiler](../compiler/README.md)
