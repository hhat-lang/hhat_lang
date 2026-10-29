from __future__ import annotations

from pathlib import Path

from hhat_lang.toolchain.project.update import update_project


def _make_project(tmp_path: Path) -> Path:
    project_root = tmp_path / "example_project"
    (project_root / "src" / "hat_types").mkdir(parents=True)
    (project_root / "docs").mkdir()
    return project_root


def test_update_creates_function_signature_doc_like_issue_example(tmp_path: Path) -> None:
    project_root = _make_project(tmp_path)
    (project_root / "src" / "some-file.hat").write_text(
        "fn some-fn (arg1:ty1 arg2:ty2 arg3:ty3) fn-ty { fn-body }\n",
        encoding="utf-8",
    )

    result = update_project(project_root)

    doc_file = project_root / "docs" / "some-file.md"
    assert doc_file.is_file()
    assert result.created_docs == (doc_file,)
    assert result.checked_signature_count == 1
    assert result.updated_signature_count == 1
    assert result.signature_mismatch_count == 0

    assert doc_file.read_text(encoding="utf-8") == (
        "# some-file\n"
        "\n"
        "## some-fn\n"
        "\n"
        "### Signature\n"
        "- Name: some-fn\n"
        "- Type: fn-ty\n"
        "- Kind: function\n"
        "- Paradigm: classical\n"
        "- Arguments:\n"
        "\n"
        "  | Argument | Type | Paradigm |\n"
        "  | :--- | :--- | :--- |\n"
        "  | arg1 | ty1 | classical |\n"
        "  | arg2 | ty2 | classical |\n"
        "  | arg3 | ty3 | classical |\n"
        "\n"
        "### Documentation\n"
        "\n"
    )


def test_update_creates_type_signature_doc_like_issue_example(tmp_path: Path) -> None:
    project_root = _make_project(tmp_path)
    (project_root / "src" / "hat_types" / "some-file.hat").write_text(
        "type @some-struct-ty {\n"
        "    m1:ty1\n"
        "    @m2:@ty2\n"
        "}\n"
        "\n"
        "type some-enum-ty {\n"
        "  named1\n"
        "  tagged1 { m1:ty1 m2:ty2 }\n"
        "}\n",
        encoding="utf-8",
    )

    result = update_project(project_root)

    doc_file = project_root / "docs" / "hat_types" / "some-file.md"
    assert doc_file.is_file()
    assert result.created_docs == (doc_file,)
    assert result.checked_signature_count == 2
    assert result.updated_signature_count == 2
    assert result.signature_mismatch_count == 0

    assert doc_file.read_text(encoding="utf-8") == (
        "# some-file\n"
        "\n"
        "## @some-struct-ty\n"
        "\n"
        "### Signature\n"
        "- Name: @some-struct-ty\n"
        "- Kind: struct\n"
        "- Paradigm: quantum\n"
        "- Members/Fields:\n"
        "\n"
        "  | Member/Field | Type | Paradigm |\n"
        "  | :--- | :--- | :--- |\n"
        "  | m1 | ty1 | classical |\n"
        "  | @m2 | @ty2 | quantum |\n"
        "\n"
        "### Documentation\n"
        "\n"
        "## some-enum-ty\n"
        "\n"
        "### Signature\n"
        "- Name: some-enum-ty\n"
        "- Kind: enum\n"
        "- Paradigm: classical\n"
        "- Variants:\n"
        "\n"
        "  | Variant | Type | Paradigm |\n"
        "  | :--- | :--- | :--- |\n"
        "  | named1 | Named | classical |\n"
        "  | tagged1 | Tagged | classical |\n"
        "\n"
        "### Documentation\n"
        "\n"
    )


def test_update_renames_doc_without_code_counterpart_to_orphan(tmp_path: Path) -> None:
    project_root = _make_project(tmp_path)
    orphan_source = project_root / "docs" / "deleted-file.md"
    orphan_source.write_text(
        "# deleted-file\n\nKeep this orphan documentation.\n",
        encoding="utf-8",
    )

    result = update_project(project_root)

    orphan_target = project_root / "docs" / "orphan.deleted-file.md"
    assert result.orphaned_doc_count == 1
    assert result.orphaned_docs[0].original_path == orphan_source
    assert result.orphaned_docs[0].orphan_path == orphan_target
    assert not orphan_source.exists()
    assert orphan_target.read_text(encoding="utf-8") == (
        "# deleted-file\n\nKeep this orphan documentation.\n"
    )

    second_result = update_project(project_root)
    assert second_result.orphaned_doc_count == 0
    assert orphan_target.is_file()


def test_update_mirrors_src_tree_into_docs_for_missing_doc_files(tmp_path: Path) -> None:
    project_root = _make_project(tmp_path)
    (project_root / "src" / "main.hat").write_text("main {\n}\n", encoding="utf-8")
    (project_root / "src" / "nested").mkdir()
    (project_root / "src" / "nested" / "ops.hat").write_text(
        "fn op () op-ty { }\n",
        encoding="utf-8",
    )
    (project_root / "src" / "hat_types" / "state.hat").write_text(
        "type state: int\n",
        encoding="utf-8",
    )

    result = update_project(project_root)

    created_docs = {doc.relative_to(project_root).as_posix() for doc in result.created_docs}
    assert created_docs == {
        "docs/main.md",
        "docs/nested/ops.md",
        "docs/hat_types/state.md",
    }
    assert (project_root / "docs" / "main.md").is_file()
    assert (project_root / "docs" / "nested" / "ops.md").is_file()
    assert (project_root / "docs" / "hat_types" / "state.md").is_file()
    assert result.orphaned_doc_count == 0
    assert result.signature_mismatch_count == 0


def test_update_leaves_matching_signature_unchanged(tmp_path: Path) -> None:
    project_root = _make_project(tmp_path)
    code_file = project_root / "src" / "some-file.hat"
    doc_file = project_root / "docs" / "some-file.md"
    code_file.write_text(
        "fn some-fn (arg1:ty1 arg2:ty2) fn-ty { fn-body }\n",
        encoding="utf-8",
    )
    doc_content = (
        "# some-file\n"
        "\n"
        "## some-fn\n"
        "\n"
        "### Signature\n"
        "- Name: some-fn\n"
        "- Type: fn-ty\n"
        "- Kind: function\n"
        "- Paradigm: classical\n"
        "- Arguments:\n"
        "\n"
        "  | Argument | Type | Paradigm |\n"
        "  | :--- | :--- | :--- |\n"
        "  | arg1 | ty1 | classical |\n"
        "  | arg2 | ty2 | classical |\n"
        "\n"
        "### Documentation\n"
        "\n"
        "Keep docs.\n"
    )
    doc_file.write_text(doc_content, encoding="utf-8")

    result = update_project(project_root)

    assert result.checked_signature_count == 1
    assert result.updated_signature_count == 0
    assert result.signature_mismatch_count == 0
    assert doc_file.read_text(encoding="utf-8") == doc_content


def test_update_replaces_non_matching_doc_signature(tmp_path: Path) -> None:
    project_root = _make_project(tmp_path)
    code_file = project_root / "src" / "some-file.hat"
    doc_file = project_root / "docs" / "some-file.md"
    code_file.write_text(
        "fn some-fn (arg1:ty1 arg2:ty2) fn-ty { fn-body }\n",
        encoding="utf-8",
    )
    doc_file.write_text(
        "# some-file\n"
        "\n"
        "## some-fn\n"
        "\n"
        "### Signature\n"
        "- Name: some-fn\n"
        "- Type: wrong-ty\n"
        "- Kind: function\n"
        "- Paradigm: classical\n"
        "- Arguments:\n"
        "\n"
        "  | Argument | Type | Paradigm |\n"
        "  | :--- | :--- | :--- |\n"
        "  | arg1 | wrong-ty | classical |\n"
        "\n"
        "### Documentation\n"
        "\n"
        "Keep docs.\n",
        encoding="utf-8",
    )

    result = update_project(project_root)

    assert result.checked_signature_count == 1
    assert result.updated_signature_count == 1
    assert result.signature_mismatch_count == 0
    assert doc_file.read_text(encoding="utf-8") == (
        "# some-file\n"
        "\n"
        "## some-fn\n"
        "\n"
        "### Signature\n"
        "- Name: some-fn\n"
        "- Type: fn-ty\n"
        "- Kind: function\n"
        "- Paradigm: classical\n"
        "- Arguments:\n"
        "\n"
        "  | Argument | Type | Paradigm |\n"
        "  | :--- | :--- | :--- |\n"
        "  | arg1 | ty1 | classical |\n"
        "  | arg2 | ty2 | classical |\n"
        "\n"
        "### Documentation\n"
        "\n"
        "Keep docs.\n"
    )


def test_update_creates_docs_folder_when_missing_from_target_directory(tmp_path: Path) -> None:
    project_root = tmp_path / "project_without_docs"
    (project_root / "src").mkdir(parents=True)
    (project_root / "src" / "module.hat").write_text(
        "fn module-fn () module-ty { }\n",
        encoding="utf-8",
    )

    result = update_project(project_root)

    doc_file = project_root / "docs" / "module.md"
    assert result.created_docs == (doc_file,)
    assert doc_file.is_file()
    assert result.signature_mismatch_count == 0


def test_cli_update_uses_current_directory_when_not_in_project(tmp_path: Path, monkeypatch) -> None:
    from typer.testing import CliRunner

    from hhat_lang.toolchain.cli.cli import app

    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "module.hat").write_text(
        "fn module-fn () module-ty { }\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(app, ["update"])

    assert result.exit_code == 0, result.output
    assert (tmp_path / "docs" / "module.md").is_file()


def test_cli_update_uses_parent_with_src_from_nested_directory(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from typer.testing import CliRunner

    from hhat_lang.toolchain.cli.cli import app

    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "module.hat").write_text(
        "fn module-fn () module-ty { }\n",
        encoding="utf-8",
    )
    nested_dir = tmp_path / "a" / "nested" / "directory"
    nested_dir.mkdir(parents=True)
    monkeypatch.chdir(nested_dir)

    result = CliRunner().invoke(app, ["update"])

    assert result.exit_code == 0, result.output
    assert (tmp_path / "docs" / "module.md").is_file()
    assert not (nested_dir / "docs").exists()


def test_heather_comment_syntax_is_stripped_before_signature_parsing(tmp_path: Path) -> None:
    project_root = tmp_path / "project_with_commented_signatures"
    (project_root / "src").mkdir(parents=True)
    (project_root / "src" / "module.hat").write_text(
        "// fn ignored-line () wrong { }\n"
        "/- fn ignored-block () wrong { } -/\n"
        "fn visible () result { }\n",
        encoding="utf-8",
    )

    result = update_project(project_root)

    doc_text = (project_root / "docs" / "module.md").read_text(encoding="utf-8")
    assert result.checked_signature_count == 1
    assert "## visible" in doc_text
    assert "ignored-line" not in doc_text
    assert "ignored-block" not in doc_text


def test_update_loads_selected_dialect_without_importing_heather(
    tmp_path: Path,
    monkeypatch,
) -> None:
    project_root = tmp_path / "project_with_custom_dialect"
    (project_root / "src").mkdir(parents=True)
    (project_root / "src" / "module.hat").write_text("custom signature source\n", encoding="utf-8")

    import hhat_lang.dialects

    fake_dialects_root = tmp_path / "fake_dialects"
    dialect_root = fake_dialects_root / "custom"
    grammar_root = dialect_root / "grammar"
    grammar_root.mkdir(parents=True)
    (dialect_root / "__init__.py").write_text("", encoding="utf-8")
    (grammar_root / "__init__.py").write_text("", encoding="utf-8")
    (grammar_root / "doc_signatures.py").write_text(
        "from pathlib import Path\n"
        "from hhat_lang.toolchain.project.doc_signatures import CodeSignature\n\n"
        "def parse_code_signatures(code_file: Path) -> tuple[CodeSignature, ...]:\n"
        "    return (CodeSignature(name='custom-fn', kind='function', paradigm='classical'),)\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        hhat_lang.dialects,
        "__path__",
        [*hhat_lang.dialects.__path__, str(fake_dialects_root)],
    )

    result = update_project(project_root, dialect="custom")

    doc_file = project_root / "docs" / "module.md"
    assert result.checked_signature_count == 1
    assert result.signature_mismatch_count == 0
    assert "## custom-fn" in doc_file.read_text(encoding="utf-8")
