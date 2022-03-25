# Walkthrough the Language (:


The grammar for the syntax is defined below.

```
[import ([<path/file> [, <path/file>]*])]


[func <func_template>]*

main <func_template>


<func_template>
	- <type> <symbol> <params> (<body> <result>)

<params>
	- (<type> <symbol> [, <type> <symbol> ]*)
	- ()
	- :

<type>
	- null
	- bool
	- int
	- float
	- str
	- circuit
	- hashmap
	- measurement

<symbol>
	- anything else [a-zA-Z_[a-zA-Z_0-9]*]
	- anything else \@[a-zA-Z_[a-zA-Z_0-9]*]

<body>
	- <attr_decl>
	- <attr_assign>
	- <generic_call>

<attr_decl>
	- <type> <symbol>
	- <type> <symbol> (<expr>)
	- <type> <symbol> (<expr>) = <attr_decl_assign>
	- <type> <symbol> = (<attr_decl_assign)

<expr>
	- <number>
	- <symbol>
	- <str>
	- <attr_call>
	- <generic_call>
	- <expr> .. <expr>
	- <inline_func>

<attr_decl_assign>
	- (<entity> [, <entity>]*)

<entity>
	- <expr>:<expr>
	- :<expr>
	- <expr>:print
	- :print

<attr_assign>
	- <symbol> <attr_decl_assign>

<generic_call>
	- <func> ([<expr>]*)

<attr_call>
	- <symbol> ([<expr>]*)
	- <symbol>

<func>
	- <symbol>
	- <reserved_keyword> # print, add, ...

```

