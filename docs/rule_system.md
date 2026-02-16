
H-hat's rule system is the set of rules to define expected behavior for core features of the language, while keeping open possibilities for dialects to exist and integrate between each other. Those rules are:

- Code syntax is consistent across multiple backend kinds, with identifiable syntax sugar annotations between them for types, variables, constants, functions. It should be enough to identify each individual piece as unique.
- The language defines types, constants, variables, functions, meta-functions, super-types and modifiers as core features. They all can be user defined.
- Aggregatable definitions are:
    - (1) types;
    - (2) constants;
    - (3) functions, meta-functions, super-types and modifiers, with a `main` closure in the `main.hat` file only.
    - Those numbered definitions above must have their own files in a way that they do not mix with other. Importing from one to another is possible and expected. Further explanation:
        - The `main.hat` file lives on `<project-name>/src/` folder.
        - Types must be placed inside the type folder, `<project-name>/src/hat_types/`; they can exist inside nested folders (as long as they exist inside the `<project-name>/src/hat_types/` folder)
        - Constants must exist inside a `consts.hat` file and can be defined anywhere inside the `<project-name>/src/` folder (except the reserved folders). Nested folders are allowed.
        - Group functions can exist anywhere inside the `<project-name>/src/` folder (except the reserved folders). Nested folders are allowed.
        - Built-in types, constants and group functions must exist inside a separated  `<project-name>/src/.core/` folder, not accessible for user defined files and instances.
- Imports must be done by aggregatable definitions, so there is no confusing if an import is a type or a function, for instance.
- Types, constants, variables and functions are backend kind-specific, meaning that once they are defined by the syntax sugar of a particular backend-kind, they are tied to it and cannot be changed.
- Strict evaluation and lazy evaluation modes for constants and variables are predefined on a given backend kind. Some backend kinds permit the evaluation mode to change, and this is done through modifiers.
