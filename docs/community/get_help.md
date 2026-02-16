# Get Help

Need assistance with H-hat? Here's how to get the help you need.

## Quick Help

### Common Issues

Before asking for help, check these common issues:

#### Installation Problems

**Issue**: `hhat` command not found

**Solution**: 
- Verify installation completed successfully
- Check that H-hat is in your PATH
- Try running with full path or `python -m hhat_lang`

**Issue**: Dependencies not installed

**Solution**:
- For Rust: Run `cargo build`
- For Python: Run `pip install -e .` in the `python/` directory

#### Compilation Errors

**Issue**: Syntax errors

**Solution**:
- Check the [Heather syntax guide](../dialects/heather/syntax.md)
- Verify file has `.hat` extension
- Look for missing or mismatched braces

**Issue**: Type errors

**Solution**:
- Ensure variables have correct type annotations
- Check function argument types match
- Verify cast operations are valid

#### Runtime Errors

**Issue**: Cast operations fail

**Solution**:
- Ensure quantum backend is configured
- Check that types are compatible for casting
- Verify quantum operations are supported

## Where to Ask

### 1. Discord (Fastest Response)

**Best for**: Quick questions, real-time help, general discussion

**Join**: [Unitary Foundation Discord](http://discord.unitary.foundation) → `#h-hat` channel

**When to use**:
- You're stuck and need help now
- You have a quick question
- You want to discuss something casually
- You want to connect with other users

**Tips**:
- Search the channel history first
- Provide code snippets and error messages
- Mention your OS and H-hat version
- Be patient and respectful

### 2. GitHub Issues (Bug Reports)

**Best for**: Bug reports, feature requests, tracked problems

**Create issue**: [New Issue](https://github.com/hhat-lang/hhat_lang/issues/new)

**When to use**:
- You found a bug
- Something that used to work doesn't anymore
- You have a reproducible error
- You want to request a feature

**What to include**:

```markdown
## Description
Clear description of the problem

## Steps to Reproduce
1. Step one
2. Step two
3. Error occurs

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: Ubuntu 22.04
- H-hat version: 0.3.0-alpha
- Rust/Python version: ...

## Code Sample
```heather
// Minimal code that reproduces the issue
```
```

### 3. GitHub Discussions (Long-form)

**Best for**: Feature proposals, design discussions, questions

**Visit**: [Discussions](https://github.com/hhat-lang/hhat_lang/discussions)

**When to use**:
- You have an idea for a feature
- You want to discuss design decisions
- You need to ask a complex question
- You want to share knowledge

### 4. Documentation Issues

**Best for**: Errors or improvements in documentation

**Report**: [Documentation Issue](https://github.com/hhat-lang/hhat_lang/issues/new)

**When to use**:
- Documentation is wrong or unclear
- Examples don't work
- Missing information
- Typos or formatting issues

## How to Ask Good Questions

### Prepare Your Question

1. **Search first**: Has someone already asked this?
2. **Isolate the problem**: Create a minimal example
3. **Gather information**: Version numbers, OS, error messages
4. **Be specific**: "X doesn't work" → "X gives error Y when I do Z"

### Provide Context

**Good question** ✅:
```
I'm trying to create entanglement in H-hat 0.3.0-alpha on Ubuntu.
This code:

```heather
let q1:qubit = |0>
let q2:qubit = |0>
let q1_h:qubit = h(q1)
let pair:tuple = cnot(q1_h, q2)
```

Gives this error:
"Type mismatch: expected qubit, found tuple<qubit, qubit>"

How do I unpack the tuple?
```

**Bad question** ❌:
```
entanglement doesn't work help
```

### Share Code

When sharing code:

**In Discord**: Use code blocks
```
```heather
// Your code here
```
```

**In GitHub**: Use the code block syntax or attach files

**Always include**:
- Minimal reproducible example
- Expected vs actual behavior
- Error messages (full text)

## Self-Help Resources

### Documentation

Start here for most questions:

- [Getting Started](../getting_started.md) - Installation and basics
- [Language Concepts](../core/index.md) - Core features explained
- [Examples](../examples/index.md) - Code samples
- [Heather Syntax](../dialects/heather/syntax.md) - Syntax reference
- [CLI Reference](../cli.md) - Command-line usage

### Tutorials

Step-by-step guides:

- [Your First Program](../getting_started/first_program.md)
- [Quantum Examples](../examples/quantum/quantum_types.md)
- [Custom Types](../examples/advanced/custom_types.md)

### Blog

Deep dives and explanations:

- [Roadmap posts](../blog/posts/2025/2025-09-09_roadmap_v0.3.md)
- Technical articles
- Use case demonstrations

## Debugging Tips

### Read Error Messages Carefully

H-hat error messages are designed to be helpful:

```
Error: Type mismatch at line 5
  Expected: qubit
  Found: bool
  
  let q:qubit = true
                ^^^^ this has type bool
```

Pay attention to:
- **Line numbers**: Where the error occurred
- **Type information**: What was expected vs found
- **Hints**: Suggestions for fixing

### Use Print Debugging

Insert print statements to understand program flow:

```heather
print("Before cast")
let result:bool = cast(q, bool)
print("After cast: ")
print(result)
```

### Simplify Your Code

If something doesn't work:

1. Remove parts until it works
2. Identify what causes the problem
3. Check that specific feature

### Check the Status Page

Some features might not be implemented yet:

[Project Status](../introduction/status.md) - What works and what doesn't

## Response Times

### Discord
- Usually **minutes to hours**
- Active during US/EU daytime
- Community-driven, not guaranteed

### GitHub Issues
- **Days to weeks** depending on priority
- Maintainers review regularly
- Critical bugs get faster attention

### GitHub Discussions
- **Days** typically
- Good for non-urgent questions
- Community often responds

## Emergency Help

### Critical Bugs

If you discover a security issue or critical bug:

1. **Do NOT** open a public issue
2. Contact maintainers directly on Discord (@moderator)
3. Or email the Unitary Foundation
4. We'll coordinate a fix and disclosure

### Urgent Questions

For urgent needs (e.g., conference deadline):

1. Try Discord first
2. Mention it's urgent and why
3. Be as specific as possible
4. Consider offering to help fix it

## Office Hours

The H-hat team holds occasional office hours:

- **When**: Announced on Discord
- **Where**: Discord voice/video
- **What**: Open Q&A, help sessions, demos

Check `#h-hat` channel for schedule!

## Community Support

Remember: H-hat is community-driven!

- **Help others**: Answer questions you know
- **Share knowledge**: Document solutions you find
- **Be patient**: Everyone was a beginner once
- **Be kind**: We're all learning together

## Still Need Help?

If you've tried everything and still need help:

1. **Summarize what you've tried**: "I checked X, Y, Z"
2. **Provide all context**: Code, errors, environment
3. **Ask specific questions**: What exactly you need to know
4. **Be patient**: We're volunteers helping when we can

**Most important**: Don't give up! The community is here to help you succeed with H-hat.

---

<div class="grid cards" markdown>

-   __Join Discord__

    Get real-time help from the community

    [:octicons-arrow-right-24: Join Now](http://discord.unitary.foundation)

-   __Browse Examples__

    Learn from working code

    [:octicons-arrow-right-24: View Examples](../examples/index.md)

-   __Read Docs__

    Comprehensive guides and references

    [:octicons-arrow-right-24: Documentation](../index.md)

-   __Report Bug__

    Found an issue? Let us know

    [:octicons-arrow-right-24: Open Issue](https://github.com/hhat-lang/hhat_lang/issues/new)

</div>
