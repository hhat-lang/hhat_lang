# Language Syntax


Here we present the language syntax, from data types to the way expressions look like. In the end of every subsection, there is a _TLDR; Summary_ subsubsection for rushy people. 


## Current Data Types

There are some data types defined below:
 
- `null`
- `bool`
- `int`
- `float`
- `str`
- `hashmap`
- `circuit`


## Structure

The general structure of the language relies on function scopes. There are the functions and the main scope. Functions can be called from within or outside (as an import), while main function is only made once and it is only called when the file is executed directly through an interpreter or compiler. There is no keyword to separate each expression; their scope is well defined by their own syntax. In short, you can write a one-line code, a nice python-like indented code or whatever you want. Good code practices are very encouraged by project needs and not by the language itself.


### Functions

For a main function, the syntax is defined as the below.

#### Main

Main is a special case for functions. It receives all the code that will be execute when the file is directly called from an interpreter/compiler. Its form is like:

```
main ( /* code goes here */ )
```

If no main is provided, no action will occur when the file is directly called.


#### Function


##### No Arguments

When no function arguments are needed it is possible to choose either simple colon:

```
func null{} X: ( /* code goes here */ )
```

or empty parenthesis:

```
func null{} X() ( /* code goes here */ )
```


#### With Arguments

When functions do have arguments, they are placed as:

```
func null{} Y (int{} a int{} b) ( /* code goes here */ )
```

where the arguments are always written as `<type>{<array length>} <name>`, using commas between arguments declaration. Array length is optional (mutable array if let blank) or enforced (immutable if a value is provided). 


#### Return

If the function is not of the null type, it must have a return:

```
func int{1} sum (int{1} a, int{1} b) ( 
	/* code goes here */ 
	return /* expression that generates an int return */
)
```

When having more than one expression on `return`, they must be contained inside a paranthesis scope `(/* code goes here */ )`.


#### TLDR; Summary

The correct syntax is `func` keyword followed by the `<type>` (one of the above in [Data Types](#data-types) section) followed by `{<array length>}` (blank is mutable length; value is immutable),  followed by its `<name>`. Arguments syntax is `(<type>{<array length>} <name>, <type>{<array length>} <name>, ...)`, while return syntax is `return /* expression */`.


### Functions Body (or Functions Code)

Inside a function there can be none, one or more expressions, ranging from variable (or attribute) declaration to conditionals, loops and more.


#### Variable Declaration

To declare a variable you can choose from two options:
1. Create the variable with no assignment
2. Create the variable and place the assignment

The **first** option is defined as:

```
int{1} a
```

if you have a single element, or:

```
int{N} b
```

if you have `N` elements (an array of type `int`); or if there is no definite length:

```
int{} c
```

The **second** option is simply:

```
int{1} a = (:2)
```

for single values, or:

```
int{3} b = (:5)
int{4} c = (0:20, (2 3):34, 1:add(4 6))
```

for list of values; or also:

```
int{} d = (:10, 2:20, (6 9):100, :add(500))
```

for a mutable size array (in the end of the operations above, it will end up with 10 elements.) Above we introduced many syntax sugars and important core concepts of the language that we are going to discuss right after [Variable Assignment](#variable-assignment).


#### Variable Assignment 

To assign a value to a variable that has already been created, simply put:

```
a(:5)
```

#### Value Assignment

A value is assigned to an element, or index through the following syntax:

```
<var> (<index pos>:<value pos>)
```

`<index pos>` can be a single index value as an integer or an integer variable, for instance (some data types have other ways to represent it), a sequence of indexes scoped by parenthesis (as in `(1 5 12)` and `(7 x)` ), a range of values defined by `<first value>..<last value>`, or a blank value, meaning that the value will be placed on **all** the indexes; and `<value pos>` is a value that will be placed inside the index which can be a literal value, a variable value, an operation/function output or a sequence of any of them scoped by parenthesis. A short cut syntax can be used if you have just one operation/value assigned: `<type>{<array length} <var> = <value>` ex:


```
int{3} b = 10
```

this assigns the value `10` to all the indexes (to name: `0`, `1` and `2`) of the variable `b`.

```
int{3} b = (0:100, 1:200, 2:300)
```

this assigns `100` to index `0`, `200` to `1` and `300` to `2` of the variable `b`.

```
int{3} b = ((0 2):500, 1:11)
```

this assigns `500` to indices `0` and `2`, and `11` to `1` of the variable `b`.


#### Variable Call

To call a single value variable, just use:

```
a
```

In case of multiple values variable, you can either use:

```
b
```

and it will show all the variable values, or:

```
b(M)
```

where `M` is the index (first starting from `0`) you want to access. You can return multiple values:

```
c(0 2 3)
```

even in different order:

```
c(3 1 2 0)
```

#### Function Call

A function can be called simply by calling it and its arguments:

```
sum(1 6)
```

or with empty parenthesis in case of no arguments needed:

```
close_connection()
```

Functions can also be called inside variable assignment:

```
a (:add(5))
```

where the code above means `5` is being added to the current value of `a` (default value for int variables is `0`.) You can place as many arguments as the function can have:

```
a (:add(5 10 15 20))
```

A special case for function call inside variable assignment is `print`:

```
b (:print)
```

where it will print **all** the values from `b` in order. If you want also to write something before it, you can just:

```
b (:print('this text comes before'))
```

and then you have first the argument inside `print` call and then the values from the variable. The code should result in:

```
> this text comes before 500 11 500
```

#### Conditional

Conditional is designed to match the first succesful test and skip the rest. Its structure is as follows:

```
if (test: /* code goes here */ )
```

for single if statement; or:

```
if (test: /* code goes here */,
    T: /* code goes here */ ) 
```

for `if-else`-like statement, where `T` is the boolean value for **true**; or:

```
if (test: /* code goes here */,
    test2: /* code goes here */,
    ...
    T: /* code goes here */ 
)
```

for `if-elif-else`-like statements. The `test` will be any operation, boolean or function output that returns a boolean value, such as:

```
and( or( and(<var1> <var2>) <var3>) not(<var4>) ) ...
```


#### Loop

Loops are defined as:

```
for M..N: (k: ( /* code goes here */ ) )
```

for traditional way of having a range from `M` to `N-1` and a loop variable `k`, and:

```
for M..N: (: ( /* code goes here */ ) )
```

when there is no need for a loop variable. Lists can also be placed in the range, as:

```
for b: (k: ( /* code goes here */ ) )
```

when each loop variable `k` will be the respective element of `b`, as well as hashmaps, measurements and circuits.


##### Range

You can use range for indices or assignment:

```
int f (100) = (3..21:400, (0 1 2):400..403)
```



### the treta

circuit @c1 = (:@algumacoisa)




