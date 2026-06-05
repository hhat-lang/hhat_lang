# H-hat's Heather dialect


The name is twofold: a [plant](https://en.wikipedia.org/wiki/Calluna)[^1] and a [song](https://en.wikipedia.org/wiki/Crosswinds_(Billy_Cobham_album)#Side_two)[^2]. There is no especial reason behind the name besides the author enjoyment for the song.


[^1]: Scientific name: _Calluna vulgaris_, a small flowering shrub.
[^2]: Billy Cobham's Crosswinds album, second track of side two.


## Introduction

This dialect was developed to enable programmers to experience H-hat rule system and explore ideas for a new quantum computer science theory that intends to focus more on the computer science of the thing, namely manipulate quantum data rather than quantum states.

### Features

The language supports:
- declaring a variable with an explicit type
- assigning a value to a variable of the same type
- calling functions with zero or more arguments
- calling meta-function types that may contain arguments and body declaration (namely: option or cases, body or blocks, option-body or case-blocks)
- converting a data into another type through cast operator
- using modifiers on data to change its properties (reference/borrowing, pointers/dereference, setting data evaluation to be strict or lazy, setting target architecture, etc.)
- special case when casting data from quantum to classical (reflective cast)
- defining constant values with an explicit type
- defining types (structs and enums) by backend type
- defining functions, meta-functions, modifiers and cast operations
- explicit imports of constants, types, functions, meta-functions, modifiers and cast operations

--- 

Next, there are syntax and semantic definitions for each part of the dialect at [Heather syntax]().