# H-hat Documentation

This directory contains the source files for the H-hat documentation website at [docs.hhat-lang.org](https://docs.hhat-lang.org).

## Structure

```
docs/
├── index.md                    # Homepage
├── getting_started.md          # Quick start guide
├── introduction/               # Introduction section
│   ├── why_hhat.md
│   ├── features.md
│   └── status.md
├── getting_started/            # Getting started guides
│   └── first_program.md
├── core/                       # Language concepts
│   ├── index.md
│   ├── language_design.md
│   ├── compiler_framework.md
│   └── ...
├── concepts/                   # Detailed concept pages
│   ├── types.md
│   ├── quantum_types.md
│   └── ...
├── dialects/                   # Dialect documentation
│   ├── index.md
│   └── heather/
│       ├── index.md
│       ├── syntax.md
│       └── grammar.md
├── examples/                   # Code examples
│   ├── index.md
│   ├── basic/
│   ├── quantum/
│   └── advanced/
├── community/                  # Community resources
│   ├── index.md
│   ├── get_help.md
│   ├── discussions.md
│   └── code_of_conduct.md
├── contributing/               # Contributing guides
│   ├── index.md
│   ├── guide.md
│   ├── development.md
│   └── pull_requests.md
├── python/                     # Python implementation guide
│   └── python_guide.md
├── rust/                       # Rust implementation guide
│   └── rust_guide.md
├── blog/                       # Blog posts
│   └── ...
└── stylesheets/                # Custom CSS
    └── extra.css
```

## Building Documentation

### Prerequisites

```bash
pip install mkdocs-material
```

### Local Development

Serve documentation locally with live reload:

```bash
mkdocs serve
```

Visit [http://localhost:8000](http://localhost:8000)

### Building

Build static site:

```bash
mkdocs build
```

Output will be in `site/` directory.

### Deployment

Documentation is automatically deployed when changes are pushed to the main branch (configure GitHub Actions or your deployment pipeline).

## Writing Documentation

### Creating New Pages

1. Create a `.md` file in the appropriate directory
2. Add the page to navigation in `mkdocs.yml`
3. Use proper Markdown formatting
4. Include examples where applicable

### Style Guide

#### Headings

```markdown
# Page Title (H1 - only one per page)

## Main Section (H2)

### Subsection (H3)

#### Detail (H4)
```

#### Code Blocks

````markdown
```heather
// H-hat code example
main {
    print("Hello!")
}
```
````

#### Admonitions

```markdown
!!! note
    This is a note

!!! warning
    This is a warning

!!! tip
    This is a tip

!!! info
    This is info
```

#### Cards (MkDocs Material)

```markdown
<div class="grid cards" markdown>

-   :material-icon:{ .lg .middle } __Title__

    ---

    Description

    [:octicons-arrow-right-24: Link](url)

</div>
```

#### Links

```markdown
[Link text](relative/path.md)
[External link](https://example.com)
```

### File Naming

- Use lowercase
- Use hyphens, not underscores
- Be descriptive: `getting-started.md` not `gs.md`

### Front Matter

Not required for basic pages, but can be added:

```yaml
---
title: Page Title
description: Page description
---
```

## Documentation Structure Guidelines

### Page Structure

Every documentation page should have:

1. **Clear title** (H1)
2. **Brief introduction** (what this page covers)
3. **Sections** with H2 headings
4. **Code examples** where applicable
5. **Links to related pages**
6. **Next steps** or call-to-action

### Example Template

```markdown
# Page Title

Brief introduction explaining what this page covers.

## Section 1

Content here...

### Subsection

More specific content...

## Section 2

More content...

## Examples

```heather
// Code example
```

## Next Steps

<div class="grid cards" markdown>

-   __Related Topic 1__

    Description

    [:octicons-arrow-right-24: Link](page1.md)

-   __Related Topic 2__

    Description

    [:octicons-arrow-right-24: Link](page2.md)

</div>
```

## Contributing to Documentation

### Types of Contributions

- **Fix typos/errors**: Small fixes are always welcome
- **Improve clarity**: Make explanations clearer
- **Add examples**: More code samples help everyone
- **Expand coverage**: Fill in placeholder pages
- **Update content**: Keep information current

### Process

1. Fork the repository
2. Create a branch: `git checkout -b docs/your-topic`
3. Make your changes
4. Test locally: `mkdocs serve`
5. Commit: `git commit -m "docs: describe your changes"`
6. Push and create a pull request

See [Contributing Guide](contributing/guide.md) for detailed instructions.

## Configuration

Documentation is configured in `mkdocs.yml` at the repository root.

Key settings:

- **site_name**: Site title
- **site_url**: Production URL
- **repo_url**: GitHub repository
- **nav**: Navigation structure
- **theme**: Material theme configuration
- **plugins**: Enabled plugins (search, blog, etc.)
- **markdown_extensions**: Markdown features

## Plugins

Enabled plugins:

- **search**: Full-text search
- **blog**: Blog functionality
- **privacy**: External link privacy
- **meta**: Page metadata support
- **tags**: Tagging system

## Markdown Extensions

Enabled extensions:

- Code highlighting with line numbers
- Admonitions (notes, warnings, tips)
- Tables and lists
- Math equations (MathJax)
- Emoji support
- Tabbed content
- And more...

See [MkDocs Material documentation](https://squidfunk.github.io/mkdocs-material/) for full list.

## Theme Customization

### Colors

Defined in `mkdocs.yml`:

- **Light mode**: Primary: Teal, Accent: Deep Purple
- **Dark mode**: Primary: Amber, Accent: Teal

### Logo & Favicon

- Logo: `docs/hhat_logo.svg`
- Favicon: `docs/hhat_logo.ico`

### Custom CSS

Add custom styles in `docs/stylesheets/extra.css`

### Custom Icons

Place custom icons in `overrides/.icons/` (create directory if needed)

## Troubleshooting

### "Page not found"

- Check the file exists in the `docs/` directory
- Verify the path in `mkdocs.yml` navigation
- Ensure the file has `.md` extension

### "Invalid configuration"

- Check YAML syntax in `mkdocs.yml`
- Ensure proper indentation (2 spaces)
- Validate paths and file names

### "Build fails"

- Check for broken links
- Verify markdown syntax
- Look for missing files referenced in navigation

### "Styles don't apply"

- Clear browser cache
- Check custom CSS syntax
- Rebuild the documentation

## Resources

- **MkDocs**: [https://www.mkdocs.org/](https://www.mkdocs.org/)
- **Material Theme**: [https://squidfunk.github.io/mkdocs-material/](https://squidfunk.github.io/mkdocs-material/)
- **Markdown Guide**: [https://www.markdownguide.org/](https://www.markdownguide.org/)

## Getting Help

Need help with documentation?

- **Discord**: Ask in `#h-hat` channel on [Unitary Foundation Discord](http://discord.unitary.foundation)
- **GitHub**: Open an issue with the `documentation` label
- **Discussions**: Post in [GitHub Discussions](https://github.com/hhat-lang/hhat_lang/discussions)

## Placeholder Pages

Some pages are marked as "Under Construction" with placeholder content. These are intentionally included to establish the documentation structure and will be filled in as features are implemented.

If you'd like to contribute content to these pages, please coordinate via Discord or GitHub to avoid duplicate work.

---

**Thank you for contributing to H-hat documentation!** Clear, comprehensive documentation helps everyone learn and use the language effectively. 📚✨
