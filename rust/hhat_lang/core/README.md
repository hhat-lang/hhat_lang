# H-hat Core


## Overview

This is the H-hat's core crate, containing all the core components that define H-hat a rule system, compiler and toolchain framework, and language family. It defines the essential aspects that a language must have in order to be considered a H-hat dialect, and to enable future interoperability between those dialects.

A dialect must import from here all the tooling utilized on its construction, from the rule system's macros and proc-macros, base serialization and basic compiler components, to the toolchain for CLI interactions, diagnoses, debugging, proof assistant, and future external library management tools.


## Core concepts

H-hat relies on its rule system to define expected behavior when compiling and executing quantum programs as well as hybrid quantum--classical programs.


## Building a dialect

> [!warning]
> As a dialect builder you should only import tooling from this crate, not from [`rulesystem` crate](../rulesystem) or [`rules` crate](../rules).
> 

More information to be placed here.
