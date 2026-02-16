!!! warning

    The Python project is currently on halt. You can use as reference or to continue developing it.


To work on H-hat on your computer, you need to:

1. Download the repository via the terminal with:

    ```bash
    git clone https://github.com/hhat-lang/hhat_lang.git
    ```
2. Go to the project folder (`cd hhat_lang/` by default)
3. Configure a [Python virtual environment](https://docs.python.org/3/tutorial/venv.html "Python official virtual environment tutorial"). You can choose between various packages, including [venv](https://docs.python.org/3/library/venv.html#creating-virtual-environments "Create with Python's venv"), [hatch](https://hatch.pypa.io/1.12/ "Hatch: package and project manager"), [uv](https://docs.astral.sh/uv/ "uv: fast package and project manager in Rust"), [pdm](https://pdm-project.org/latest/ "PDM: modern package and project manager"), and [poetry](https://python-poetry.org/ "poetry: package manager"). (1)
{ .annotate }

   1.  Here we mentioned the most common ones, but there are plenty of other package and project managers. Choose the one that suits your needs.

4. Activate it (_each package has their own way to do it, please check it out before proceeding_)
5. Install the package via `pip` as follows:

   - if you are using `bash` shell[^1]:
      ```bash
      pip install -e .[all]
      ```

   - if you are using `zsh` shell:
      ```sh
      pip install -e ".[all]"
      ```


[^1]: How to check [which shell I am using](https://askubuntu.com/questions/590899/how-do-i-check-which-shell-i-am-using#590902)?
