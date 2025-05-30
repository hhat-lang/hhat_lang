# $\hat{H}$'s Heather dialect syntax

### Importing types

To enable a type contained in the `hhat_types/` folder:

```
use(type:point)
```

for more than one type:

```
use(type:[point point3d])
```

for types in nested folders (`scalar/` in the example below) inside `hhat_types/` folder:

```
use(type:[scalar.pos scalar.velocity scalar.acceleration])
```

or

```
use(type:[scalar.{pos velocity acceleration}])
```

---

**Note**: Incorporating external types downloaded from a valid collection repository or from another local project is still in design phase.



### Importing functions

To enable a function in the project:

```
use(fn:sum)
```

for more than one function:

```
use(fn:[sum times safe-div])
```

for functions inside nested folders (`linalg/` in the example below) on `src/` folder:

```
use(fn:[linalg.dot linalg.inner linalg.outer])
```

or

```
use(fn:[linalg.{dot inner outer}])
```

and

```
use(
    fn:[
        linalg.{
            dot
            inner
            outer
        }
        stats.{
            rv-continuous:rvc
            rv-discrete:rvd
        }
    ]
)
```

where `rvc` is the label for `stats.rv-continuous` and `rvd` is the label for `stats.rv-discrete` function, respectively.


---

**Note**: Incorporating external functions from downloaded sources or local project is still on design phase.
