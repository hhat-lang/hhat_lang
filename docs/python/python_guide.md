To properly and safely install H-hat on your computer, you need to configure a [Python virtual environment](https://docs.python.org/3/tutorial/venv.html "Python official virtual environment tutorial"). You can choose between various packages, including [venv](https://docs.python.org/3/library/venv.html#creating-virtual-environments "Create with Python's venv"), [hatch](https://hatch.pypa.io/1.12/ "Hatch: package and project manager"), [uv](https://docs.astral.sh/uv/ "uv: fast package and project manager in Rust"), [pdm](https://pdm-project.org/latest/ "PDM: modern package and project manager"), and [poetry](https://python-poetry.org/ "poetry: package manager"). (1)
{ .annotate }

1.  Here we mentioned the most common ones, but there are plenty of other package and project managers. Choose the one that suits your needs.

After configuring it, activate it (_each package has their own way to do it, please check it out before proceeding_), and choose **one** of the methods below to install `H-hat`, [Pypi](#via-pypi) or [Source code (currently recommended)](#via-source-code):

## Via Pypi

!!! note

    `hhat-lang` library might be out-of-date compared to the [source code](https://github.com/hhat-lang/hhat_lang) method below.

This is the easiest, most straightforward and simplest way to install `H-hat`. On the terminal, with the virtual environment enabled, type:[^1]

[^1]: How to check [which shell I am using](https://askubuntu.com/questions/590899/how-do-i-check-which-shell-i-am-using#590902)?

### If you are using `bash` shell:

```sh
pip install hhat-lang .[all]
```

### If you are using `zsh` shell:

```sh
pip install hhat-lang ".[all]"
```

Either the options above will install all the [tools](../toolchain.md), features and a [H-hat dialect](../dialects/index.md) called [Heather](../dialects/heather/index.md) so you can start learning and writing your own code.


## Via source code <small>recommended</small> {#via-source-code}

Use the clone HTTPS link in [the H-hat repository page](https://github.com/hhat-lang/hhat_lang) and git clone it, using the terminal:

```sh
git clone https://github.com/hhat-lang/hhat_lang.git
```

This will create the `hhat_lang/` folder with all the code content, where you can pip install through the editable mode:


### If you are using `bash` shell:

```sh
pip install -e .[all]
```

### If you are using `zsh` shell:

```sh
pip install -e ".[all]"
```

!!! note
    This approach is meant to be used for those who want to modify the code.
