# Pull Request Guide

Learn how to create great pull requests for H-hat.

## Before You Start

- [ ] Read the [Contributing Guide](guide.md)
- [ ] Development environment set up
- [ ] Issue exists for your work (or create one)
- [ ] You understand what you're implementing

## Creating a Pull Request

### 1. Prepare Your Changes

#### Ensure Quality

```bash
# Rust
cargo test
cargo clippy
cargo fmt --check

# Python  
pytest
black --check .
mypy src/
```

#### Update Documentation

* Update relevant .md files
* Add docstrings/comments
* Include examples if needed
* Update changelog for significant changes

#### Clean Up Commits

Optionally squash or organize commits:

```bash
# Interactive rebase
git rebase -i main

# Or squash all commits
git reset --soft main
git commit -m "feat: descriptive message"
```

### 2. Push to Your Fork

```bash
# Push your branch
git push origin feature/my-feature

# Force push after rebase (if needed)
git push origin feature/my-feature --force
```

### 3. Open Pull Request

#### On GitHub

1. Navigate to [github.com/hhat-lang/hhat_lang](https://github.com/hhat-lang/hhat_lang)
2. Click "New Pull Request"
3. Select your fork and branch
4. Fill out the PR template

#### PR Title

Follow conventional commit format:

```
<type>(<scope>): <description>

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Adding tests
- chore: Maintenance

Examples:
✅ feat(parser): add support for generic types
✅ fix(typecheck): resolve inference bug in nested functions
✅ docs(getting-started): add quantum examples
✅ test(compiler): add integration tests for HIR generation
```

#### PR Description

Use the template:

```markdown
## Description
<!-- What does this PR do? -->

## Motivation
<!-- Why is this change needed? -->

## Changes
<!-- List the key changes -->
- Change 1
- Change 2

## Testing
<!-- How was this tested? -->

## Screenshots (if applicable)
<!-- Add screenshots for UI changes -->

## Checklist
- [ ] Tests pass
- [ ] Code formatted
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Issue linked (Closes #XXX)
```

**Example**:

```markdown
## Description
Adds support for generic type parameters in function definitions.

## Motivation
Closes #123. Users need generic functions to write reusable code.

## Changes
- Implemented generic type parsing
- Added type parameter resolution
- Updated type checker for generics
- Added monomorphization pass

## Testing
- Added unit tests for parser
- Added integration tests with various generic patterns
- Tested with real-world examples

## Checklist
- [x] Tests pass
- [x] Code formatted
- [x] Documentation updated
- [x] Breaking changes documented
- [x] Issue linked (Closes #123)
```

### 4. Link the Issue

In your PR description:

```markdown
Closes #123
Fixes #456
Resolves #789
```

Or use GitHub's UI to link issues.

## Review Process

### What Happens Next

1. **Automated Checks**: CI runs tests and linters
2. **Initial Review**: Maintainer reviews within a few days
3. **Feedback**: You'll receive comments and suggestions
4. **Iteration**: Make requested changes
5. **Approval**: PR approved when ready
6. **Merge**: Maintainer merges your PR

### Responding to Feedback

#### Be Responsive

* Check GitHub notifications regularly
* Respond within a few days
* Ask questions if unclear
* Make requested changes promptly

#### Making Changes

```bash
# Make changes locally
# ... edit files ...

# Commit changes
git add .
git commit -m "fix: address review feedback"

# Push to update PR
git push origin feature/my-feature
```

The PR updates automatically!

#### Resolving Conflicts

If your PR has conflicts:

```bash
# Update main branch
git checkout main
git pull upstream main

# Rebase your branch
git checkout feature/my-feature
git rebase main

# Resolve conflicts
# ... edit files ...
git add .
git rebase --continue

# Force push
git push origin feature/my-feature --force
```

### Common Review Comments

#### "Can you add tests for this?"

* Write tests covering your changes
* Include edge cases
* Test error conditions

#### "This breaks existing functionality"

* Run full test suite
* Check for regressions
* May need to adjust approach

#### "Can you split this into smaller PRs?"

* Large PRs are hard to review
* Create separate branches
* Submit multiple focused PRs

#### "Please update the documentation"

* Add docstrings/comments
* Update user docs
* Add examples

## PR Best Practices

### Keep PRs Focused

✅ **Good PRs**:
* One feature/fix per PR
* Clear scope
* Easy to review
* Focused tests

❌ **Bad PRs**:
* Multiple unrelated changes
* Too large (>500 lines)
* Mix features with refactoring
* Hard to understand

### Write Good Descriptions

✅ **Good**:
```markdown
## Description
Fixes type inference bug where generic functions with nested calls
would incorrectly infer types, causing compilation errors.

## Changes
- Modified type unification algorithm
- Added constraint propagation for nested generics
- Updated error messages

## Testing
Added test cases from issues #123, #456, and #789
```

❌ **Bad**:
```markdown
fixed stuff
```

### Communicate Effectively

**In comments**:

* Be respectful and professional
* Explain your reasoning
* Ask questions when unsure
* Thank reviewers for feedback

**Example**:

```markdown
Thanks for the feedback! I've made the requested changes:

1. Added tests for edge cases
2. Refactored the error handling
3. Updated documentation

Regarding your question about performance: I ran benchmarks and
this approach is 2x faster than the alternative. Happy to discuss
further if you have concerns!
```

### Keep PR Updated

* Rebase on main regularly
* Resolve conflicts promptly
* Keep CI passing
* Respond to comments

## After Your PR is Merged

### Celebrate! 🎉

Your contribution is now part of H-hat!

### What Happens

* Your commits appear in main
* You're added to contributors
* Issue is closed
* Feature/fix is in next release

### Clean Up

```bash
# Delete local branch
git branch -d feature/my-feature

# Delete remote branch
git push origin --delete feature/my-feature

# Update your fork
git checkout main
git pull upstream main
git push origin main
```

## PR Checklists

### Before Opening

- [ ] Code compiles and runs
- [ ] All tests pass
- [ ] Code is formatted
- [ ] No linter warnings
- [ ] Documentation updated
- [ ] Examples added (if applicable)
- [ ] Commits are clean
- [ ] Branch is up-to-date with main

### PR Description

- [ ] Clear title following conventions
- [ ] Complete description
- [ ] Motivation explained
- [ ] Changes listed
- [ ] Testing described
- [ ] Issue linked
- [ ] Breaking changes noted (if any)

### During Review

- [ ] Responded to all comments
- [ ] Requested changes made
- [ ] Tests added as requested
- [ ] Documentation improved
- [ ] Conflicts resolved
- [ ] CI is green

## Troubleshooting

### "CI is failing"

Check the logs:

* Test failures: Fix the tests or code
* Linter errors: Run `cargo clippy` or linters locally
* Formatting: Run `cargo fmt` or `black .`

### "Conflicts with main"

Rebase your branch:

```bash
git fetch upstream
git rebase upstream/main
# Resolve conflicts
git push --force
```

### "Reviewer hasn't responded"

Be patient! But if it's been over a week:

* Politely ping on the PR
* Ask on Discord
* Check if more info is needed

### "My PR was closed"

Reasons PRs get closed:

* Duplicate
* Out of scope
* No response to feedback
* Superseded by another PR
* AI-generated without understanding

If closed, you can:

* Ask for clarification
* Revise and reopen
* Start fresh with feedback incorporated

## Advanced Tips

### Draft PRs

Open as draft for early feedback:

1. Click "Create draft pull request"
2. Get early feedback
3. Click "Ready for review" when done

### WIP Commits

Use `[WIP]` prefix for work-in-progress:

```
[WIP] feat: implementing feature X
```

Remove before final review.

### Breaking Changes

If your PR breaks compatibility:

```markdown
## BREAKING CHANGES

### What Changed
The `cast` function now requires an explicit type parameter.

### Before
```heather
let x = cast(q)
```

### After
```heather
let x:bool = cast(q, bool)
```

### Migration Guide
Update all cast calls to include the target type.
```

## Getting Help

Need help with your PR?

* **Discord**: Ask in [#h-hat](http://discord.unitary.foundation)
* **PR Comments**: Ask reviewers directly
* **Discussions**: Post in [Discussions](https://github.com/hhat-lang/hhat_lang/discussions)

## Resources

### GitHub Guides

* [Creating a Pull Request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request)
* [Addressing Merge Conflicts](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/addressing-merge-conflicts)
* [Reviewing Changes](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests)

### Project Resources

* [Contributing Guide](guide.md)
* [Development Setup](development.md)
* [Code of Conduct](../community/code_of_conduct.md)

---

## Quick Reference

### Good PR Checklist

✅ Focused scope
✅ Tests included
✅ Documentation updated
✅ Clear description
✅ Linked issue
✅ Clean commits
✅ CI passing
✅ Responsive to feedback

### PR Title Format

```
<type>(<scope>): <description>

feat(parser): add generic types
fix(typecheck): resolve inference bug
docs(examples): add quantum samples
```

### Common Commands

```bash
# Update branch
git fetch upstream
git rebase upstream/main

# Force push after rebase
git push --force

# Squash commits
git rebase -i main

# Clean up after merge
git branch -d feature/my-feature
```

---

**Ready to create your first PR?** Go for it! Don't be afraid to ask for help along the way. 🚀
