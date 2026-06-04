from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from hhat_lang.toolchain.cli.cli import app
from hhat_lang.toolchain.project.update import AUTO_END, AUTO_START, update_project

runner = CliRunner()


def _project(tmp_path: Path) -> Path:
    project_root = tmp_path / "demo"
    (project_root / "src" / "hat_types").mkdir(parents=True)
    (project_root / "docs").mkdir()
    (project_root / "src" / "main.hat").write_text("main {\n\n}\n")
    return project_root


def test_update_project_creates_mirrored_docs_with_heather_signatures(
    tmp_path: Path,
) -> None:
    project_root = _project(tmp_path)
    (project_root / "src" / "math.hat").write_text("fn sum(a:i64 @q:@u3) @sample { :: add(a b) }\n")
    (project_root / "src" / "hat_types" / "geometry.hat").write_text(
        "type @point { x:i32 @q:@u3 }\n"
    )

    result = update_project(project_root)

    assert result.signature_count == 2
    assert (project_root / "docs" / "math.md").read_text() == (
        "# math\n"
        "\n"
        f"{AUTO_START}\n"
        "## sum\n"
        "\n"
        "### Signature\n"
        "\n"
        "- Name: `sum`\n"
        "- Name paradigm: classical\n"
        "- Kind: function\n"
        "- Type: `@sample`\n"
        "- Type paradigm: quantum\n"
        "- Arguments:\n"
        "\n"
        "  | Argument | Argument paradigm | Type | Type paradigm |\n"
        "  | :--- | :--- | :--- | :--- |\n"
        "  | `a` | classical | `i64` | classical |\n"
        "  | `@q` | quantum | `@u3` | quantum |\n"
        f"{AUTO_END}\n"
    )
    assert (project_root / "docs" / "hat_types" / "geometry.md").read_text() == (
        "# geometry\n"
        "\n"
        f"{AUTO_START}\n"
        "## @point\n"
        "\n"
        "### Signature\n"
        "\n"
        "- Name: `@point`\n"
        "- Name paradigm: quantum\n"
        "- Kind: struct type\n"
        "- Members:\n"
        "\n"
        "  | Member | Member paradigm | Type | Type paradigm |\n"
        "  | :--- | :--- | :--- | :--- |\n"
        "  | `x` | classical | `i32` | classical |\n"
        "  | `@q` | quantum | `@u3` | quantum |\n"
        f"{AUTO_END}\n"
    )


def test_update_project_refreshes_generated_block_and_preserves_notes(
    tmp_path: Path,
) -> None:
    project_root = _project(tmp_path)
    source = project_root / "src" / "math.hat"
    doc = project_root / "docs" / "math.md"
    source.write_text("fn sum(a:i64 b:i64) i64 { :: add(a b) }\n")
    doc.write_text(
        "# Math\n\n"
        "Manual introduction.\n\n"
        f"{AUTO_START}\nold signature\n{AUTO_END}\n\n"
        "Manual notes.\n"
    )

    update_project(project_root)

    assert doc.read_text() == (
        "# Math\n"
        "\n"
        "Manual introduction.\n"
        "\n"
        f"{AUTO_START}\n"
        "## sum\n"
        "\n"
        "### Signature\n"
        "\n"
        "- Name: `sum`\n"
        "- Name paradigm: classical\n"
        "- Kind: function\n"
        "- Type: `i64`\n"
        "- Type paradigm: classical\n"
        "- Arguments:\n"
        "\n"
        "  | Argument | Argument paradigm | Type | Type paradigm |\n"
        "  | :--- | :--- | :--- | :--- |\n"
        "  | `a` | classical | `i64` | classical |\n"
        "  | `b` | classical | `i64` | classical |\n"
        f"{AUTO_END}\n"
        "\n"
        "Manual notes.\n"
    )


def test_update_project_does_not_rewrite_unchanged_docs(tmp_path: Path) -> None:
    project_root = _project(tmp_path)
    (project_root / "src" / "math.hat").write_text("fn double(x:i64) i64 { :: add(x x) }\n")

    first = update_project(project_root)
    second = update_project(project_root)

    doc = project_root / "docs" / "math.md"
    assert doc in first.created_docs
    assert doc in second.unchanged_docs
    assert not second.created_docs
    assert not second.updated_docs


def test_update_project_reports_orphan_docs_without_deleting_user_content(
    tmp_path: Path,
) -> None:
    project_root = _project(tmp_path)
    orphan_doc = project_root / "docs" / "stale.md"
    orphan_doc.write_text("# Stale\n\nKeep me for now.\n")

    result = update_project(project_root)

    assert orphan_doc in result.orphan_docs
    assert orphan_doc.read_text() == "# Stale\n\nKeep me for now.\n"


def test_update_command_refreshes_current_project_docs(
    tmp_path: Path,
    monkeypatch,
) -> None:
    project_root = _project(tmp_path)
    (project_root / "src" / "math.hat").write_text("fn double(x:i64) i64 { :: add(x x) }\n")
    monkeypatch.chdir(project_root)

    result = runner.invoke(app, ["update"])

    assert result.exit_code == 0
    assert "Project update completed successfully" in result.stdout
    assert "Signatures found: 1" in result.stdout
    assert "## double" in (project_root / "docs" / "math.md").read_text()
