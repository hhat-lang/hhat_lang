# Running H-hat


## With CLI :safety_vest:

!!! warning "In development"
    This step is not implemented yet and sits in a TODO list to be done.

With the [CLI](cli.md "commandline interface") configured and installed, it can be used on the terminal through the `hat` command.

```sh
hat --help
```

For more information on commands available.


## With Python <small>currently available</small> :gear:

!!! info "In progress"
    This step is in progress, so you may experience some breaking or incomplete parts.

The project file organization is created as follows:

```
project_name/
├─ src/
│  ├─ hat_types/
│  ├─ hat_docs/
│  │  ├─ hat_types/
│  │  └─ main.hat.md
│  └─ main.hat
└─ tests/
```

Using H-hat library, one can access it through the `hhat_lang.toolchain.cli` module.

### Creating a new project


```python
from hhat_lang.toolchain.cli import new

new.create_new_project("new_project")

```

This will create a new project called `new_project`, with all the folders and auxiliary tools to enable start developing in H-hat with the select dialect :material-information-outline:{ title="A H-hat dialect is needed. By default, Heather dialect is provided"}.


### Creating a new file

A new file can be created through:

```python

new.create_new_file("new_project", "file_name")
```

This will create a `file_name.hat` file into the `new_project` project, as well as a `file_name.hat.md` file at `hat_docs/`. For every file, there will be a documentation file.

New type files are created slightly different:

```python

new.create_new_type_file("new_project", "file_type")
```

It will create a `file_type.hat` at `hat_types/`, as well as its documentation counterpart at the `hat_docs/hat_types/file_type.hat.md`.


## With Rust :x:

!!! failure "Unavailable"
    This step is currently unavailable. May be implemented in the future.
