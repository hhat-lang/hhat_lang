# Contributing to H-hat

Thank you for your interest in contributing to H-hat! We welcome contributions from everyone, whether you're fixing a typo, adding documentation, or implementing new features.

## Quick Links

<div class="grid cards" markdown>

-   :material-bug:{ .lg .middle } __Report Bugs__

    ---

    Found a bug? Let us know!

    [:octicons-arrow-right-24: Open Issue](https://github.com/hhat-lang/hhat_lang/issues/new)

-   :material-lightbulb:{ .lg .middle } __Suggest Features__

    ---

    Have an idea? Share it!

    [:octicons-arrow-right-24: Start Discussion](https://github.com/hhat-lang/hhat_lang/discussions)

-   :material-code-tags:{ .lg .middle } __Submit Code__

    ---

    Ready to code? Make a PR!

    [:octicons-arrow-right-24: Pull Request Guide](pull_requests.md)

-   :material-book-edit:{ .lg .middle } __Improve Docs__

    ---

    Help others learn

    [:octicons-arrow-right-24: Documentation Guide](#documentation)

</div>

## Ways to Contribute

### 🐛 Report Bugs

Help us improve by reporting bugs:

* Use the [issue tracker](https://github.com/hhat-lang/hhat_lang/issues)
* Search for existing issues first
* Include clear reproduction steps
* Provide environment details

[Learn more about reporting bugs →](https://github.com/hhat-lang/hhat_lang/blob/main/.github/ISSUE_TEMPLATE/bug_report.md)

### 💡 Suggest Features

Share your ideas for improvements:

* Start a [discussion](https://github.com/hhat-lang/hhat_lang/discussions)
* Explain the use case
* Describe the proposed solution
* Discuss alternatives

### 📝 Improve Documentation

Documentation is crucial and always needs improvement:

* Fix typos and errors
* Add examples
* Write tutorials
* Improve explanations
* Translate to other languages

### 💻 Write Code

Contribute to the codebase:

* Fix bugs
* Implement features
* Optimize performance
* Add tests
* Refactor code

### 🎓 Help Others

Support the community:

* Answer questions on [Discord](http://discord.unitary.foundation)
* Help in [GitHub Discussions](https://github.com/hhat-lang/hhat_lang/discussions)
* Review pull requests
* Write blog posts or tutorials

### 🧪 Test Features

Help ensure quality:

* Test new releases
* Try alpha/beta features
* Report edge cases
* Verify fixes

## Getting Started

### 1. Find Something to Work On

#### Good First Issues

Start with beginner-friendly tasks:

* Browse [good first issues](https://github.com/hhat-lang/hhat_lang/issues?q=is%3Aissue+state%3Aopen+label%3A%22good+first+issue%22)
* Look for `help wanted` label
* Check documentation TODOs
* Fix typos and small bugs

#### Current Priorities

Check the [roadmap](../introduction/status.md) for priorities:

* Version 0.3.0 goals
* Critical bugs
* Missing features
* Documentation gaps

#### Propose Your Own

Have your own idea?

1. Search existing issues/discussions
2. Create a discussion to propose it
3. Get feedback from maintainers
4. Open an issue if approved
5. Start working on it!

### 2. Set Up Development Environment

Choose your implementation language:

=== "Rust (Primary)"

    ```bash
    # Clone the repository
    git clone https://github.com/hhat-lang/hhat_lang.git
    cd hhat_lang/rust/hhat_lang
    
    # Install Rust (if needed)
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    
    # Build the project
    cargo build
    
    # Run tests
    cargo test
    
    # Check code
    cargo check
    cargo clippy
    cargo fmt --check
    ```

    [Detailed Rust setup →](../rust/rust_guide.md)

=== "Python (Reference)"

    ```bash
    # Clone the repository
    git clone https://github.com/hhat-lang/hhat_lang.git
    cd hhat_lang/python
    
    # Create virtual environment
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    
    # Install in development mode
    pip install -e .
    pip install -r requirements-dev.txt
    
    # Run tests
    pytest
    
    # Check formatting
    pre-commit run --all-files
    ```

    [Detailed Python setup →](../python/python_guide.md)

### 3. Make Your Changes

Follow these guidelines:

* **One change per PR**: Keep PRs focused
* **Write tests**: Cover your changes
* **Follow style**: Use project conventions
* **Document**: Update docs as needed
* **Commit messages**: Write clear descriptions

### 4. Submit Your Contribution

See the [Pull Request Guide](pull_requests.md) for details.

## Development Guidelines

### Code Style

#### Rust

* Follow `rustfmt` formatting: `cargo fmt`
* Pass `clippy` lints: `cargo clippy`
* Write idiomatic Rust
* Document public APIs
* Use meaningful names

#### Python

* Follow PEP 8 style guide
* Use Black formatter: `black .`
* Check with pre-commit hooks
* Type hints encouraged
* Docstrings for functions

### Testing

**Write tests for**:

* New features
* Bug fixes
* Edge cases
* Error conditions

**Test requirements**:

* All tests must pass
* Coverage should not decrease
* Tests should be deterministic
* Use descriptive test names

**Running tests**:

=== "Rust"

    ```bash
    # All tests
    cargo test
    
    # Specific test
    cargo test test_name
    
    # With output
    cargo test -- --nocapture
    ```

=== "Python"

    ```bash
    # All tests
    pytest
    
    # Specific test
    pytest tests/test_file.py::test_name
    
    # With coverage
    pytest --cov=hhat_lang
    ```

### Documentation

**Update documentation when you**:

* Add features
* Change behavior
* Fix bugs (if it affects usage)
* Add examples

**Documentation checklist**:

* [ ] Update relevant .md files
* [ ] Add/update code examples
* [ ] Check for broken links
* [ ] Test code samples work
* [ ] Update changelog (if applicable)

### Commit Messages

Write clear, descriptive commit messages:

**Format**:
```
<type>: <short summary>

<detailed description>

<footer>
```

**Types**:
* `feat`: New feature
* `fix`: Bug fix
* `docs`: Documentation
* `style`: Formatting
* `refactor`: Code restructuring
* `test`: Adding tests
* `chore`: Maintenance

**Examples**:

```
feat: add quantum error correction types

Implements basic QEC types including:
- Stabilizer codes
- Surface codes
- Error syndrome detection

Closes #123
```

```
fix: resolve type inference bug in generic functions

The type checker was incorrectly handling nested generic
function calls, causing false positive errors.

Fixes #456
```

## AI Contributions

The rise of Generative AI has brought opportunities and challenges. Our policy:

### ✅ Acceptable Use

* Using AI for research and learning
* AI-assisted code generation as a starting point
* Using AI to understand concepts
* AI help with formatting and style

### ❌ Not Acceptable

* Submitting AI-generated code without understanding
* AI-written PRs without critical review
* Low-quality bulk contributions
* Copy-pasting AI output without verification

### Requirements

**You are responsible for**:

* Understanding the code you submit
* Verifying it works correctly
* Ensuring it fits the codebase
* Testing thoroughly
* Explaining your approach

**PRs with automated AI content** (description, code) **without demonstrated understanding will be closed**.

## Review Process

### What to Expect

1. **Initial review**: Within a few days
2. **Feedback**: Constructive suggestions
3. **Iteration**: Make requested changes
4. **Approval**: When ready, PR is approved
5. **Merge**: Maintainer merges your PR

### Tips for Success

* **Respond promptly** to feedback
* **Ask questions** if unclear
* **Be patient** - reviews take time
* **Be receptive** to suggestions
* **Keep PRs updated** with main branch

## Code of Conduct

All contributors must follow our [Code of Conduct](../community/code_of_conduct.md):

* Be respectful and welcoming
* Accept constructive criticism
* Focus on what's best for the community
* Show empathy towards others

Violations will be handled according to our enforcement guidelines.

## Recognition

We value all contributions! Contributors are:

* Listed in GitHub contributors
* Mentioned in release notes
* Acknowledged in documentation
* Invited to community events
* Eligible for recognition badges

## Getting Help

Need help contributing?

* **Discord**: Ask in [#h-hat channel](http://discord.unitary.foundation)
* **Discussions**: Post in [GitHub Discussions](https://github.com/hhat-lang/hhat_lang/discussions)
* **Issues**: Comment on the issue you're working on
* **Mentorship**: Ask for guidance from maintainers

## Resources

### Project Resources

* [GitHub Repository](https://github.com/hhat-lang/hhat_lang)
* [Issue Tracker](https://github.com/hhat-lang/hhat_lang/issues)
* [Discussions](https://github.com/hhat-lang/hhat_lang/discussions)
* [Project Board](https://github.com/hhat-lang/hhat_lang/projects)

### Documentation

* [Development Setup](development.md)
* [Pull Request Guide](pull_requests.md)
* [Rust Guide](../rust/rust_guide.md)
* [Python Guide](../python/python_guide.md)
* [Architecture](../core/compiler_framework.md)

### Community

* [Discord Server](http://discord.unitary.foundation)
* [Community Page](../community/index.md)
* [Blog](../blog/index.md)

## License

By contributing to H-hat, you agree that your contributions will be licensed under the MIT License.

---

## Thank You! 🎉

Every contribution, no matter how small, helps make H-hat better. Thank you for taking the time to contribute to the future of quantum programming!

<div class="grid cards" markdown>

-   __Browse Issues__

    Find something to work on

    [:octicons-arrow-right-24: Good First Issues](https://github.com/hhat-lang/hhat_lang/issues?q=is%3Aissue+state%3Aopen+label%3A%22good+first+issue%22)

-   __Join Discord__

    Connect with other contributors

    [:octicons-arrow-right-24: Join Now](http://discord.unitary.foundation)

-   __Read the Guide__

    Learn about making great PRs

    [:octicons-arrow-right-24: PR Guide](pull_requests.md)

-   __Start Coding__

    Set up your environment

    [:octicons-arrow-right-24: Development Setup](development.md)

</div>
