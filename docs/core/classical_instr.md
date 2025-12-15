# Classical Instructions

Below you can find a list of existing (:white_check_mark:), under implementation (:construction:), or on TODO (:memo:) list functions/instructions.


## 1. `null` type

### `print`

- Status: :memo:
- Syntax: `print(msg:?T)`
- Description: print `msg` (generic) argument as text on the terminal
- Returns: nothing


## 2. `bool` type

### `not`

- Status: :memo:
- Syntax: `not(data:bool)`
- Description: negates `data` (`bool`) argument binary data
- Returns: the same type as `data` argument


### `eq`

- Status: :memo:
- Syntax: `eq(a:?T b:?T)`
- Description: compares `a` (generic) argument with `b` (generic) argument; both must be of the same type
- Returns: a boolean literal (`true`, `false`) from the comparison


### `le`

- Status: :memo:
- Syntax: `le(a:?T b:?T)`
- Description: checks if `a` (generic) argument is less or equal than `b` (generic) argument; both must be of the same type
- Returns: a boolean literal from the comparison


### `lt`

- Status: :memo:
- Syntax: `lt(a:?T b:?T)`
- Description: checks if `a` (generic) argument is less than `b` (generic) argument; both must be of the same type
- Returns: a boolean literal from the comparison


### `ge`

- Status: :memo:
- Syntax: `ge(a:?T b:?T)`
- Description: checks if `a` (generic) argument is greater or equal than `b` (generic) argument; both must be of the same type
- Returns: a boolean literal from the comparison


### `gt`

- Status: :memo:
- Syntax: `gt(a:?T b:?T)`
- Description: checks if `a` (generic) argument is greater than `b` (generic) argument; both must be of the same type
- Returns: a boolean literal from the comparison


## 3. `u16` type


## 4. `u32` type

### `add`

- Status: :memo:
- Syntax: `add(a:u32 b:u32)`
- Description: performs an addition operation on `a` (`u32`) and `b` (`u32`) arguments
- Returns: a `u32` type from the operation


## 5. `u64` type

### `add`

- Status: :memo:
- Syntax: `add(a:u64 b:u64)`
- Description: performs an addition operation on `a` (`u64`) and `b` (`u64`) arguments
- Returns: a `u64` type from the operation
