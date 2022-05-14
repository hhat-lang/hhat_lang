# Language Syntax


Here we present the language syntax, from data types to the way expressions look like. In the end of every subsection, there is a _TLDR; Summary_ subsubsection for rushy people. 


## Data Types

There are some data types defined below:
 
- `null`
- `bool`
- `int`
- `float`
- `str`
- `list` *
- `hashmap`
- `circuit`
- `measurement`

* `list` is viewed as an ordered sequence of the same data type, but cannot be defined alone.


## Structure

The general structure of the language relies on function scopes. There are the functions and the main scope. Functions can be called from within or outside (as an import), while main function is only made once and it is only called when the file is executed directly. There is no endline keyword to separate each expression inside the functions; their scope is well defined by their own syntax. In short, you can write a one-line code, a nice python-like indented code or whatever you want. Good code practices are very encouraged by project and not by the language.

### Functions

For a main function, the syntax is defined as the below.

#### No Arguments

When no function arguments are needed it is possible to choose either simple colon:

```
main null C: ( /* code goes here */ )
```

or empty parenthesis:

```
main null C () ( /* code goes here */ )
```

As for a function syntax, it follows the same main function principle, except it uses `func` instead:

```
func null X: ( /* code goes here */ )

func null Y () ( /* code goes here */ )
```

#### With Arguments

When functions do have arguments, they are placed as:

```
main null X (int a, int b) ( /* code goes here */ )
```

where the arguments are always written as `<type> <name>`, using commas between arguments declaration.


#### Return

If the function is not of the null type, it must have a return:

```
func int sum (int a, int b) ( 
	/* code goes here */ 
	return ( /* expression that generates an int return */ )
)
```

#### TLDR; Summary

The correct syntax is `func/main` keyword followed by the `<type>` (one of the above in [Data Types](#data-types) section) followed by its `<name>` (`C` in the case of the `main` example and `X`, `Y` for function's). Arguments syntax is `(<type> <name>, <type> <name>, ...)`, while return syntax is `return (/* expression */)`.


### Functions Body (or Functions Code)

Inside a function there can be none, one or more expressions, ranging from variable (or attribute) declaration to conditionals, loops and more.

#### Variable Declaration

To declare a variable you can choose from two options:
1. Just create the variable with no assignment
2. Create the variable and place the assignment

The first option is defined as:

```
int a
```

if you have a single value, or:

```
int b (N)
```

if you have `N` values (a list of type `int`).

The second option is simply:

```
int a = (:2)
```

for single values, or:

```
int b (3) = (:5)
int c (4) = (0:20, (2 3):34, 1:add(4 6))
```

for list of values. Above we introduced many syntax sugars and important core concepts of the language that we are going to discuss right after [Variable Assignment](#variable-assignment).

#### Variable Assignment 

To assign a value to a variable that has already been created, simply put:

```
a (:5)
```

#### Value Assignment

A value is assigned to a variable when you place `:` keyword between the parenthesis and place the expression at the _right_ side of the keyword. If the variable is single value, this keyword just represents that you are actually _writing_ a value in the variable rather than _reading_ an index on that variable. If it is a multiple value variable, you can still use the sambe keyword and the expression on its right side will be assigned to **all** the indices. In case you want to assign different values for different indices, you must place the indices on the _left_ side of the `:` keyword. Examples:

```
int a = (:2)
```

this assigns the value `2` to the variable `a`.

```
int b (3) = (:10)
```

this assigns the value `10` to all the indices (to name: `0`, `1` and `2`) of the variable `b`.

```
int b (3) = (0:100, 1:200, 2:300)
```

this assigns `100` to index `0`, `200` to `1` and `300` to `2` of the variable `b`.

```
int b (3) = ((0 2):500, 1:11)
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

Conditional follows the structure:

```
if (test): ( /* code goes here */ )

if (test): ( /* code goes here */) else: ( /* code goes here */ )

if (test): (
	/* code goes here */
) elif (test): (
	/* code goes here */
) else: (
	/* code goes here */ 
)
```

where `test` is something like:

```
( and( or( and(test1 test2) test3 ) not(test4) ) ... )
```


##### Inline Conditional

```
int d (10) = ( ( if (test):( /* code */ ) else:( /* code */ ) ):10 )
```

P.S.: Is it good?

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




