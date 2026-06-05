# Contributing to H-hat

You can check the issues in the [H-hat issue's page](https://github.com/hhat-lang/hhat_lang/issues) and try contributing on the issues with [good first issue](https://github.com/hhat-lang/hhat_lang/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22) label. Depending on the programming language you are using, some formatting styles and checks are required. For instance:
- Python:
    - Pull Request (PR) code should follow formatting from [pre-commit configuration](https://github.com/hhat-lang/hhat_lang/blob/main/python/.pre-commit-config.yaml) and [pyproject](https://github.com/hhat-lang/hhat_lang/blob/main/python/pyproject.toml).
- Rust:
    - Besides from rust formatter and analyzer, `cargo check` and `cargo audit` is recommended to run.
    - More information to come.


Additionally to code contribution, you are encourage to make part of discussions involving how H-hat can handle some language features or concepts. Reach us out at the [Discord](http://discord.unitary.foundation)'s `#h-hat` channel to learn more on how to contribute on that and also to chill and chat, if you feel like doing so.


## AI Contributions

The rise of Generative AI brought many advancements for newcomers to start writing code, but also created concerning situations when incorporating AI-generated code to repositories. Regardless whether you choose to use the tool or not, the code you put in a PR is your responsibility. Make sure you checked it is doing what is intended to do, and does not introduce unnecessary complexity or bugs to the existing codebase. Simply AI prompted code will not be accepted. You are required to evaluate the intent of existing issue or PR, the existing codebase, and the code you are bringing up. Should your PR produce automated AI content (description and content) without support of your critical thinking, it will be closed.    
