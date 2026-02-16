# Contributing Guide

Detailed guide for making contributions to H-hat.

!!! tip "New to contributing?"
    Check out the [main contributing page](index.md) first for an overview, then come back here for detailed instructions.

## Contribution Workflow

### 1. Choose What to Work On

#### Find an Issue

Browse the [issue tracker](https://github.com/hhat-lang/hhat_lang/issues):

* Filter by labels:
    * `good first issue` - Great for newcomers
    * `help wanted` - Community help needed
    * `bug` - Fix a bug
    * `enhancement` - Add a feature
    * `documentation` - Improve docs

* Check the issue status:
    * No assignee? Available to work on
    * Someone assigned? They're working on it
    * `in progress` label? Work has started

#### Claim an Issue

1. Comment on the issue: "I'd like to work on this"
2. Wait for maintainer approval (usually quick)
3. Get assigned to the issue
4. Start working!

#### Create Your Own Issue

Have something new?

1. **Search first**: Make sure it doesn't exist
2. **Open an issue**:
    * Clear title
    * Detailed description
    * Why it's needed
    * Proposed approach (if you have one)
3. **Get feedback**: Wait for maintainer input
4. **Start work**: Once approved

### 2. Set Up Your Fork

#### Fork the Repository

1. Visit [github.com/hhat-lang/hhat_lang](https://github.com/hhat-lang/hhat_lang)
2. Click "Fork" in the top-right
3. Choose your account

#### Clone Your Fork

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/hhat_lang.git
cd hhat_lang

# Add upstream remote
git remote add upstream https://github.com/hhat-lang/hhat_lang.git

# Verify remotes
git remote -v
```

#### Keep Your Fork Updated

```bash
# Fetch upstream changes
git fetch upstream

# Update your main branch
git checkout main
git merge upstream/main

# Push to your fork
git push origin main
```

### 3. Create a Branch

Always create a new branch for your work:

```bash
# Create and switch to new branch
git checkout -b feature/my-feature

# Or for bug fixes
git checkout -b fix/issue-123
```

**Branch naming conventions**:

* `feature/description` - New features
* `fix/description` - Bug fixes
* `docs/description` - Documentation
* `refactor/description` - Code refactoring
* `test/description` - Adding tests

### 4. Make Your Changes

#### Before You Code

* **Read related code**: Understand the context
* **Check conventions**: Follow existing patterns
* **Plan your approach**: Think before coding
* **Ask questions**: Clarify if unsure

#### While Coding

**Write clean code**:

* Follow project style guidelines
* Use meaningful names
* Add comments for complex logic
* Keep functions focused
* Avoid duplication

**Test as you go**:

```bash
# Rust
cargo test
cargo clippy
cargo fmt

# Python
pytest
black .
mypy .
```

**Commit regularly**:

```bash
# Stage changes
git add file1.rs file2.rs

# Commit with message
git commit -m "feat: add function to handle X"

# Multiple commits are fine!
# You can squash them later if needed
```

#### After Coding

* [ ] All tests pass
* [ ] Code is formatted
* [ ] No linter warnings
* [ ] Documentation updated
* [ ] Examples added (if applicable)
* [ ] Changelog updated (if significant)

### 5. Write Tests

**Test requirements**:

* Every bug fix needs a test
* New features need comprehensive tests
* Tests must be deterministic
* Tests must be maintainable

**Test structure**:

=== "Rust"

    ```rust
    #[cfg(test)]
    mod tests {
        use super::*;
    
        #[test]
        fn test_feature_works() {
            // Arrange
            let input = setup_test_data();
            
            // Act
            let result = my_function(input);
            
            // Assert
            assert_eq!(result, expected_value);
        }
    
        #[test]
        fn test_error_handling() {
            let invalid_input = invalid_data();
            assert!(my_function(invalid_input).is_err());
        }
    }
    ```

=== "Python"

    ```python
    import pytest
    from hhat_lang import my_module
    
    def test_feature_works():
        # Arrange
        input_data = setup_test_data()
        
        # Act
        result = my_module.my_function(input_data)
        
        # Assert
        assert result == expected_value
    
    def test_error_handling():
        with pytest.raises(ValueError):
            my_module.my_function(invalid_data)
    ```

**Test coverage**:

* Happy path (normal usage)
* Edge cases (boundaries)
* Error conditions
* Different input types

### 6. Update Documentation

**What to document**:

* **API changes**: Update reference docs
* **New features**: Add guides and examples
* **Breaking changes**: Highlight clearly
* **Configuration**: Document new options

**Where to document**:

* Code comments and docstrings
* Markdown files in `docs/`
* README if relevant
* CHANGELOG for significant changes

**Documentation checklist**:

* [ ] Public APIs documented
* [ ] Examples provided
* [ ] Edge cases explained
* [ ] Links working
* [ ] Spelling checked

### 7. Submit Pull Request

See the [Pull Request Guide](pull_requests.md) for detailed instructions.

## Contribution Best Practices

### Communication

**Before starting work**:

* Comment on the issue
* Discuss your approach
* Ask questions early
* Confirm no one else is working on it

**During development**:

* Update the issue with progress
* Ask for help if stuck
* Share draft PRs for early feedback
* Communicate delays

**After submission**:

* Respond to reviews promptly
* Ask questions about feedback
* Make requested changes
* Keep PR updated

### Code Quality

**Readability**:

* Clear, descriptive names
* Consistent formatting
* Appropriate comments
* Logical organization

**Maintainability**:

* DRY (Don't Repeat Yourself)
* Single responsibility
* Loose coupling
* Easy to test

**Performance**:

* Optimize when needed
* Profile before optimizing
* Document performance characteristics
* Consider memory usage

### Testing

**Test thoroughly**:

* Unit tests for functions
* Integration tests for features
* End-to-end tests for workflows
* Edge cases and errors

**Test quality**:

* Tests should be fast
* Tests should be isolated
* Tests should be readable
* Tests should be reliable

### Documentation

**Be comprehensive**:

* Explain what and why
* Provide examples
* Document edge cases
* Link to related info

**Be clear**:

* Use simple language
* Break down complex topics
* Use headings and lists
* Add diagrams if helpful

## Specific Contribution Types

### Bug Fixes

1. **Reproduce the bug**:
    * Verify it exists
    * Understand the cause
    * Write a failing test

2. **Fix the issue**:
    * Make minimal changes
    * Focus on the root cause
    * Don't introduce new features

3. **Verify the fix**:
    * Test passes
    * No regression
    * Bug doesn't reappear

4. **Document**:
    * Update changelog
    * Add test describing the bug
    * Comment if fix is non-obvious

### New Features

1. **Design first**:
    * Write a design doc
    * Get feedback on approach
    * Consider alternatives
    * Think about edge cases

2. **Implement incrementally**:
    * Start with core functionality
    * Add tests as you go
    * Commit logical chunks
    * Keep PRs manageable

3. **Document thoroughly**:
    * API documentation
    * Usage examples
    * Integration guide
    * Migration notes (if breaking)

4. **Polish**:
    * Error messages
    * Performance
    * Edge cases
    * User experience

### Documentation

1. **Identify gaps**:
    * Missing information
    * Outdated content
    * Unclear explanations
    * Broken links

2. **Improve clarity**:
    * Simplify language
    * Add examples
    * Structure with headings
    * Use visual aids

3. **Verify accuracy**:
    * Test code samples
    * Check links
    * Verify version info
    * Cross-reference

4. **Get feedback**:
    * Ask for review
    * Test with beginners
    * Iterate on feedback

### Refactoring

1. **Preserve behavior**:
    * Ensure tests still pass
    * No functional changes
    * Separate refactor from features

2. **Improve structure**:
    * Better organization
    * Clearer names
    * Reduced complexity
    * Better patterns

3. **Document changes**:
    * Why refactoring was needed
    * What changed
    * Impact on other code

## Common Challenges

### "I don't know where to start"

* Start with documentation
* Fix typos and small bugs
* Add tests
* Improve error messages
* Ask for a mentor

### "I'm stuck on a problem"

* Ask on Discord
* Comment on the issue
* Review similar code
* Take a break and come back
* Simplify the problem

### "My PR is too big"

* Split into smaller PRs
* Focus on one thing
* Use feature flags
* Incremental improvements

### "I don't understand the feedback"

* Ask for clarification
* Discuss on Discord
* Request examples
* Pair with a maintainer

### "I made a mistake"

* Everyone makes mistakes!
* Ask for help
* Force push is OK (on your branch)
* Learn and improve
* Don't be discouraged

## Resources

### Getting Help

* [Discord #h-hat](http://discord.unitary.foundation)
* [GitHub Discussions](https://github.com/hhat-lang/hhat_lang/discussions)
* [Issue Comments](https://github.com/hhat-lang/hhat_lang/issues)

### Learning Resources

* [Rust Book](https://doc.rust-lang.org/book/) - Learn Rust
* [Python Guide](https://docs.python-guide.org/) - Python best practices
* [Git Tutorial](https://git-scm.com/docs/gittutorial) - Git basics
* [GitHub Docs](https://docs.github.com/) - GitHub features

### Project Resources

* [Architecture](../core/compiler_framework.md)
* [Language Design](../core/language_design.md)
* [Rust Guide](../rust/rust_guide.md)
* [Python Guide](../python/python_guide.md)

## Next Steps

Ready to contribute?

<div class="grid cards" markdown>

-   __Find an Issue__

    Browse good first issues

    [:octicons-arrow-right-24: Issue Tracker](https://github.com/hhat-lang/hhat_lang/issues?q=is%3Aissue+state%3Aopen+label%3A%22good+first+issue%22)

-   __Set Up Environment__

    Configure your development setup

    [:octicons-arrow-right-24: Development Guide](development.md)

-   __Submit a PR__

    Learn the PR process

    [:octicons-arrow-right-24: PR Guide](pull_requests.md)

-   __Get Help__

    Join the community

    [:octicons-arrow-right-24: Discord](http://discord.unitary.foundation)

</div>

---

Thank you for contributing to H-hat! Your efforts help make quantum programming accessible to everyone. 🚀
