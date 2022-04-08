
## Conditional Syntax

### 1st attempt

Current approach:

```
if (cond1): (body)
elif (cond2): (body)
else: (body)
```

### 2nd attempt

New proposal:

```
if (
	(cond1): (body)
	(cond2): (body)
	...
	T: (body)
)
```

`T` is 'true' and, in this context, it should be the "else" statement. The `if` should be thought as a conditional statements holder. It will try to find the first **true** value in the *left* side of the **:** and then execute the *right* side. By the end, a true value (`T`) should be provided as a `else` statement. If no true value is reached, no code is executed, just as in an if-statement without else. If the `body` contains only *one* expression, a comma `,` may come after it instead of the full parenthesis between the body.

### Conditions/Test

`(1 == 1)` should be:

```
eq(1 1)
```

`(1 > 0)` should be:

```
gt(1 0)
```

`(1==1) && (2<4)` should be:

```
and(eq(1 1) lt(2 4))
```

and so on.

### Full Example

Full example on attempt #1:

```
if (and(eq(a b) gt(5 a))): ( print('hello!') )
elif (and(not(eq(a b)) gt(5 2))): ( print('oh') print(add(5 10)) )
else: ( print('something else.') )
```

Full example on attempt #2:

```
if (
	(and(eq(a b) gt(5 2))): print('hello!'),
	(and(not(eq(a b)) gt(5 2))): ( print('oh') print(add(5 10)) )
	T: print('something else.')
)
```


## Loop Syntax


### 1st attempt

The current approach:

```
for k in 0..4: (body)
for 0..4 as k: (body)
for 0..4: (body)
```

In the example, the loop variable is `k` if a variable is needed inside the loop body, otherwise you can just not use any (third line). The range is `0..4` where `0` is the start and `4` is the end, and will produce the values `0, 1, 2, 3`. The start and end can be variables, function and variable calls. A range can also be a variable: list of values, hashmap, measurement or circuit type.


### 2nd attempt

A new approach based on the syntax cohesion:

```
for (0..4) (k: expr, k: expr, ...)
for (0..4) (k: (body))
for (0..4) (k: expr, k: (body), ...)
for (0..4) (: (body))
for (0..4) (: expr, : expr, ...)
for (0..4) (: expr, : (body), ...)
```

The principle is the same as above, but the loop variable is located inside the parenthesis. All the expressions inside the loop body must have the loop variable as their loop "index", but the last call; in case of no variable needed, any body expression will have empty loop "index". The loop syntax follows the same rules of the attribute/variable declaration/assignment syntax.



