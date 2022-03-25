# Examples


## Import example (how it should/will be)

```
import ("home/folder/file.hht", "home/folder/file2.hht")
```


## Attribute declaration possibilities

```
int a
int a(3)
int a(3) = (0:50, ..)
```

## Attribute and function call possibilities

```
print(a)
print(a(2))
print(add(a 12))
```


## Complete code example


### Example 1

```
main null H: (
	int a = (:2, :print('var a='), :add(5), :print('something'))
	int b(3) = ((0 1):a, 1..2:10, :print('now b='), 0..3:40..43)
	print(b)
)
```

### Example 2

```
func int sum (int a, int b) ( return (add(a b)) )

main null C: (
	int x = (:4)
	int y = (:5)
	int z = (:sum(x y), :print)
)
```



