from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from hhat_lang.toolchain.cli.cli import app
from hhat_lang.toolchain.project.new import create_new_project
from hhat_lang.toolchain.project.update import parse_code_signatures, update_project

runner = CliRunner()


def test_parse_code_signatures_from_functions_structs_and_enums() -> None:
    code = """
    fn some-fn (arg1:ty1 arg2:@ty2) fn-ty { fn-body }

    type @some-struct-ty {
        m1:ty1
        @m2:@ty2
    }

    type some-enum-ty {
      named1
      tagged1 { m1:ty1 m2:ty2 }
    }
    """

    signatures = {signature.name: signature for signature in parse_code_signatures(code)}

    assert signatures["some-fn"].kind == "function"
    assert signatures["some-fn"].type == "fn-ty"
    assert [arg.name for arg in signatures["some-fn"].arguments] == ["arg1", "arg2"]

    assert signatures["@some-struct-ty"].kind == "struct"
    assert signatures["@some-struct-ty"].paradigm == "quantum"
    assert [member.name for member in signatures["@some-struct-ty"].members] == ["m1", "@m2"]

    assert signatures["some-enum-ty"].kind == "enum"
    assert [variant.type for variant in signatures["some-enum-ty"].variants] == ["Named", "Tagged"]


def test_update_project_mirrors_docs_and_preserves_manual_documentation(tmp_path: Path) -> None:
    project = tmp_path / "sample"
    create_new_project(project)

    ops_file = project / "src" / "ops.hat"
    ops_file.write_text("fn sum(a:i64 b:i64) i64 { ::add(a b) }\n")

    type_file = project / "src" / "hat_types" / "shape.hat"
    type_file.write_text(
        """
        type point { x:i32 y:i32 }
        type status_t {
            ON
            DATA { value:u64 }
        }
        """
    )

    ops_doc = project / "docs" / "ops.md"
    ops_doc.write_text(
        """
        # Previous title

        ## sum

        ### Signature

        - old signature

        ### Documentation

        Keep this explanation.
        """.strip()
        + "\n"
    )
    stale_doc = project / "docs" / "stale.md"
    stale_doc.write_text("# stale\n")

    summary = update_project(project)

    assert summary.created_docs == 1
    assert summary.updated_docs == 1
    assert summary.orphaned_docs == 1

    updated_ops_doc = ops_doc.read_text()
    assert "# Previous title" in updated_ops_doc
    assert "- Type: i64" in updated_ops_doc
    assert "| a | i64 | classical |" in updated_ops_doc
    assert "Keep this explanation." in updated_ops_doc

    updated_type_doc = (project / "docs" / "hat_types" / "shape.md").read_text()
    assert "## point" in updated_type_doc
    assert "| x | i32 | classical |" in updated_type_doc
    assert "## status_t" in updated_type_doc
    assert "| DATA | Tagged | classical |" in updated_type_doc

    assert not stale_doc.exists()
    assert (project / "docs" / "orphan.stale.md").exists()


def test_update_cli_runs_from_project_directory(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "cli_project"
    create_new_project(project)
    (project / "src" / "math.hat").write_text("fn double(x:i64) i64 { ::add(x x) }\n")

    monkeypatch.chdir(project)
    result = runner.invoke(app, ["update"])

    assert result.exit_code == 0
    assert "Documentation synchronized successfully" in result.stdout
    assert (project / "docs" / "math.md").exists()
