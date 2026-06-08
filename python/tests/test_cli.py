from __future__ import annotations

import os
import shutil
from pathlib import Path
import pytest
from click.utils import strip_ansi
from typer.testing import CliRunner
from hhat_lang.toolchain.cli.cli import app

runner = CliRunner()
_cwd = os.getcwd()


class temp_dir:
    def __init__(self, project_name: str):
        self.pn = project_name

    def __enter__(self):
        if self.pn:
            if not Path(self.pn).exists():
                os.mkdir(self.pn)
            os.chdir(self.pn)
        return self.pn

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(_cwd)
        if self.pn:
            shutil.rmtree(self.pn)


@pytest.fixture
def temp_dir2():
    """Provide a temporary directory for tests"""
    original_cwd = os.getcwd()
    temp_dir = "temp"
    if not Path(temp_dir).exists():
        os.mkdir(temp_dir)
    os.chdir(temp_dir)
    yield temp_dir
    os.chdir(original_cwd)
    shutil.rmtree(temp_dir)


def test_help_command():
    """Test the help command displays all available commands"""
    result = runner.invoke(app, ["help"])
    assert result.exit_code == 0
    assert "Available commands:" in result.stdout
    assert "new" in result.stdout
    assert "run" in result.stdout
    assert "update" in result.stdout
    assert "help" in result.stdout


def test_help_specific_command():
    """Test help for a specific command shows detailed information"""
    result = runner.invoke(app, ["help", "new"])
    output = strip_ansi(result.stdout)

    assert result.exit_code == 0
    assert "Create a new project, file, constant, or type file" in output
    assert "--file" in output
    assert "--type" in output


def test_create_new_project():
    with temp_dir("testproject1") as tp:
        """Test creating a new project succeeds"""
        result = runner.invoke(app, ["new", tp])
        assert result.exit_code == 0
        assert "created successfully" in result.stdout
        assert (Path() / tp).exists()
        assert (Path() / tp / "src" / "main.hat").exists()


def test_create_project_exists():
    with temp_dir("testproject2") as tp:
        """Test creating a project fails when directory exists"""
        runner.invoke(app, ["new", tp])
        # Try to create it again
        result = runner.invoke(app, ["new", tp])
        assert result.exit_code == 1
        assert "Error" in result.stdout
        print(f"{result.stdout}")
        assert "exists" in result.stdout


def test_create_file_in_project():
    with temp_dir("testproject3") as tp:
        """Test creating a new file inside a project directory"""
        runner.invoke(app, ["new", tp])
        os.chdir(tp)
        # Create a new file
        result = runner.invoke(app, ["new", "-f", "module/testfile"])
        assert result.exit_code == 0
        assert "created successfully" in result.stdout
        assert (Path() / "src" / "module" / "testfile.hat").exists()


def test_create_file_outside_project():
    with temp_dir(""):
        """Test creating a file fails outside project directory"""
        result = runner.invoke(app, ["new", "-f", "testfile4"])
        assert result.exit_code == 1
        assert "Error" in result.stdout
        assert "project directory" in result.stdout


def test_create_existing_file():
    with temp_dir("testproject5") as tp:
        """Test creating a file fails when it already exists"""
        runner.invoke(app, ["new", tp])
        os.chdir(tp)
        runner.invoke(app, ["new", "-f", "testfile"])
        result = runner.invoke(app, ["new", "-f", "testfile"])
        assert result.exit_code == 1
        assert "Error" in result.stdout
        assert "already exists" in result.stdout


def test_create_type_file():
    with temp_dir("testproject6") as tp:
        """Test creating a new type file inside a project directory"""
        runner.invoke(app, ["new", tp])
        os.chdir(tp)
        result = runner.invoke(app, ["new", "-t", "customtype"])
        assert result.exit_code == 0
        assert "created successfully" in result.stdout
        assert "customtype.hat" in result.stdout


def test_run_project():
    with temp_dir("testproject7") as tp:
        """Test running a project with empty main.hat"""
        runner.invoke(app, ["new", tp])
        os.chdir(tp)
        # Run the project
        result = runner.invoke(app, ["run"])
        assert result.exit_code == 1  # expect an error
        assert "Error" in result.stdout
        assert "no implementation yet" in result.stdout


def test_run_outside_project():
    with temp_dir(""):
        """Test running outside a project directory fails"""
        result = runner.invoke(app, ["run"])
        assert result.exit_code == 1
        assert "Error" in result.stdout
        # We don't test for the exact error message since it's wrapped in a panel
        # and the formatting might change


def test_version():
    """Test version flag shows version information"""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "H-hat Language Toolchain" in result.stdout
    assert "version" in result.stdout


def test_update_creates_missing_docs_for_code_files():
    with temp_dir("testproject8") as tp:
        runner.invoke(app, ["new", tp])
        os.chdir(tp)
        nested_file = Path("src") / "nested" / "sample.hat"
        nested_type_file = Path("src") / "hat_types" / "custom.hat"
        hidden_import_file = Path("src") / ".hat_imports" / "dependency.hat"
        nested_file.parent.mkdir(parents=True, exist_ok=True)
        nested_type_file.parent.mkdir(parents=True, exist_ok=True)
        hidden_import_file.parent.mkdir(parents=True, exist_ok=True)
        nested_file.write_text("fn sample () unit { }\n")
        nested_type_file.write_text("type custom { }\n")
        hidden_import_file.write_text("fn imported () unit { }\n")

        result = runner.invoke(app, ["update"])

        assert result.exit_code == 0
        assert "Created 2 documentation file" in result.stdout
        assert (Path("docs") / "nested" / "sample.md").exists()
        assert (Path("docs") / "hat_types" / "custom.md").exists()
        assert not (Path("docs") / ".hat_imports" / "dependency.md").exists()


def test_update_is_noop_when_docs_already_exist():
    with temp_dir("testproject9") as tp:
        runner.invoke(app, ["new", tp])
        os.chdir(tp)

        result = runner.invoke(app, ["update"])

        assert result.exit_code == 0
        assert "All source files already have documentation counterparts" in result.stdout


def test_update_reports_matching_signatures():
    with temp_dir("testproject10") as tp:
        runner.invoke(app, ["new", tp])
        os.chdir(tp)
        source_file = Path("src") / "math.hat"
        doc_file = Path("docs") / "math.md"
        source_file.write_text("fn sum (lhs:u32 rhs:u32) u32 { }\n")
        doc_file.write_text(
            "# math\n\n"
            "## sum\n\n"
            "### Signature\n"
            "- Name: sum\n"
            "- Type: u32\n"
            "- Kind: function\n"
            "- Paradigm: classical\n"
            "- Arguments:\n\n"
            "  | Argument | Type | Paradigm |\n"
            "  | :--- | :--- | :--- |\n"
            "  | lhs | u32 | classical |\n"
            "  | rhs | u32 | classical |\n\n"
            "### Documentation\n\n"
        )

        result = runner.invoke(app, ["update"])

        assert result.exit_code == 0
        assert "All documented signatures match source code" in result.stdout
        assert "Signature mismatch" not in result.stdout


def test_update_reports_signature_mismatches():
    with temp_dir("testproject11") as tp:
        runner.invoke(app, ["new", tp])
        os.chdir(tp)
        source_file = Path("src") / "hat_types" / "shapes.hat"
        doc_file = Path("docs") / "hat_types" / "shapes.md"
        source_file.write_text("type @point {\n    x:u32\n    @y:@u32\n}\n")
        doc_file.write_text(
            "# shapes\n\n"
            "## @point\n\n"
            "### Signature\n"
            "- Name: @point\n"
            "- Kind: struct\n"
            "- Paradigm: quantum\n"
            "- Members/Fields:\n\n"
            "  | Member/Field | Type | Paradigm |\n"
            "  | :--- | :--- | :--- |\n"
            "  | x | i32 | classical |\n"
            "  | @y | @u32 | quantum |\n\n"
            "### Documentation\n\n"
        )

        result = runner.invoke(app, ["update"])

        assert result.exit_code == 0
        assert "Updated 1 documented signature" in result.stdout
        assert "@point" in result.stdout
        assert "documentation signature differed from code" in result.stdout
        assert "Signature mismatch" not in result.stdout
        assert "| x | u32 | classical |" in doc_file.read_text()


def test_update_inserts_missing_signature_and_preserves_documentation():
    with temp_dir("testproject12") as tp:
        runner.invoke(app, ["new", tp])
        os.chdir(tp)
        source_file = Path("src") / "math.hat"
        doc_file = Path("docs") / "math.md"
        source_file.write_text("fn multiply (lhs:u32 rhs:u32) u32 { }\n")
        doc_file.write_text(
            "# math\n\n## multiply\n\n### Documentation\n\nKeep this explanation.\n"
        )

        result = runner.invoke(app, ["update"])
        updated_doc = doc_file.read_text()

        assert result.exit_code == 0
        assert "Updated 1 documented signature" in result.stdout
        assert "multiply (missing from documentation)" in result.stdout
        assert "### Signature" in updated_doc
        assert "- Name: multiply" in updated_doc
        assert "| lhs | u32 | classical |" in updated_doc
        assert "### Documentation\n\nKeep this explanation." in updated_doc


def test_update_creates_enum_signature_section():
    with temp_dir("testproject13") as tp:
        runner.invoke(app, ["new", tp])
        os.chdir(tp)
        source_file = Path("src") / "hat_types" / "choice.hat"
        doc_file = Path("docs") / "hat_types" / "choice.md"
        source_file.write_text("type choice {\n    named1\n    tagged1 { m1:u32 m2:u64 }\n}\n")
        doc_file.write_text("# choice\n\n")

        result = runner.invoke(app, ["update"])
        updated_doc = doc_file.read_text()

        assert result.exit_code == 0
        assert "Updated 1 documented signature" in result.stdout
        assert "| Variant | Type | Paradigm |" in updated_doc
        assert "| named1 | Named | classical |" in updated_doc
        assert "| tagged1 | Tagged | classical |" in updated_doc


def test_update_renames_docs_for_deleted_code_files():
    with temp_dir("testproject14") as tp:
        runner.invoke(app, ["new", tp])
        os.chdir(tp)
        orphan_doc = Path("docs") / "stale" / "deleted.md"
        renamed_orphan_doc = Path("docs") / "stale" / "orphan.deleted.md"
        orphan_doc.parent.mkdir(parents=True, exist_ok=True)
        orphan_doc.write_text("# deleted\n\n")

        result = runner.invoke(app, ["update"])

        assert result.exit_code == 0
        assert "Renamed 1 orphaned documentation file" in result.stdout
        assert "docs/stale/deleted.md -> docs/stale/orphan.deleted.md" in result.stdout
        assert not orphan_doc.exists()
        assert renamed_orphan_doc.exists()
        assert renamed_orphan_doc.read_text() == "# deleted\n\n"


def test_update_removes_stale_documented_signatures():
    with temp_dir("testproject15") as tp:
        runner.invoke(app, ["new", tp])
        os.chdir(tp)
        source_file = Path("src") / "math.hat"
        doc_file = Path("docs") / "math.md"
        source_file.write_text("fn keep () u32 { }\n")
        doc_file.write_text(
            "# math\n\n"
            "## keep\n\n"
            "### Signature\n"
            "- Name: keep\n"
            "- Type: u32\n"
            "- Kind: function\n"
            "- Paradigm: classical\n"
            "- Arguments:\n\n"
            "  | Argument | Type | Paradigm |\n"
            "  | :--- | :--- | :--- |\n\n"
            "### Documentation\n\n"
            "Keep this one.\n\n"
            "## deleted\n\n"
            "### Signature\n"
            "- Name: deleted\n"
            "- Type: u32\n"
            "- Kind: function\n"
            "- Paradigm: classical\n"
            "- Arguments:\n\n"
            "  | Argument | Type | Paradigm |\n"
            "  | :--- | :--- | :--- |\n\n"
            "### Documentation\n\n"
            "Remove this one.\n"
        )

        result = runner.invoke(app, ["update"])
        updated_doc = doc_file.read_text()

        assert result.exit_code == 0
        assert "Removed 1 stale documented signature" in result.stdout
        assert "deleted (missing from source code)" in result.stdout
        assert "## keep" in updated_doc
        assert "Keep this one." in updated_doc
        assert "## deleted" not in updated_doc
        assert "Remove this one." not in updated_doc


def test_update_generates_issue_example_function_signature_doc():
    with temp_dir("testproject16") as tp:
        runner.invoke(app, ["new", tp])
        os.chdir(tp)
        source_file = Path("src") / "some-file.hat"
        doc_file = Path("docs") / "some-file.md"
        source_file.write_text("fn some-fn (arg1:ty1 arg2:ty2 arg3:ty3) fn-ty { fn-body }\n")

        result = runner.invoke(app, ["update"])
        updated_doc = doc_file.read_text()

        assert result.exit_code == 0
        assert doc_file.exists()
        assert "# some-file" in updated_doc
        assert "## some-fn" in updated_doc
        assert "### Signature" in updated_doc
        assert "- Name: some-fn" in updated_doc
        assert "- Type: fn-ty" in updated_doc
        assert "- Kind: function" in updated_doc
        assert "- Paradigm: classical" in updated_doc
        assert "- Arguments:" in updated_doc
        assert "| Argument | Type | Paradigm |" in updated_doc
        assert "| arg1 | ty1 | classical |" in updated_doc
        assert "| arg2 | ty2 | classical |" in updated_doc
        assert "| arg3 | ty3 | classical |" in updated_doc
        assert "### Documentation" in updated_doc


def test_update_generates_issue_example_type_signature_doc():
    with temp_dir("testproject17") as tp:
        runner.invoke(app, ["new", tp])
        os.chdir(tp)
        source_file = Path("src") / "hat_types" / "some-file.hat"
        doc_file = Path("docs") / "hat_types" / "some-file.md"
        source_file.write_text(
            "type @some-struct-ty {\n"
            "    m1:ty1\n"
            "    @m2:@ty2\n"
            "}\n\n"
            "type some-enum-ty {\n"
            "    named1\n"
            "    tagged1 { m1:ty1 m2:ty2 }\n"
            "}\n"
        )

        result = runner.invoke(app, ["update"])
        updated_doc = doc_file.read_text()

        assert result.exit_code == 0
        assert doc_file.exists()
        assert "# some-file" in updated_doc
        assert "## @some-struct-ty" in updated_doc
        assert "- Name: @some-struct-ty" in updated_doc
        assert "- Kind: struct" in updated_doc
        assert "- Paradigm: quantum" in updated_doc
        assert "- Members/Fields:" in updated_doc
        assert "| Member/Field | Type | Paradigm |" in updated_doc
        assert "| m1 | ty1 | classical |" in updated_doc
        assert "| @m2 | @ty2 | quantum |" in updated_doc
        assert "## some-enum-ty" in updated_doc
        assert "- Name: some-enum-ty" in updated_doc
        assert "- Kind: enum" in updated_doc
        assert "- Paradigm: classical" in updated_doc
        assert "- Variants:" in updated_doc
        assert "| Variant | Type | Paradigm |" in updated_doc
        assert "| named1 | Named | classical |" in updated_doc
        assert "| tagged1 | Tagged | classical |" in updated_doc
        assert updated_doc.count("### Documentation") == 2


def test_update_runs_in_src_without_main_file():
    with temp_dir("testproject18") as tp:
        project = Path(tp).resolve()
        (project / "src").mkdir(parents=True)
        (project / "src" / "module.hat").write_text("fn module () unit { }\n")
        os.chdir(project / "src")

        result = runner.invoke(app, ["update"])

        assert result.exit_code == 0
        assert (project / "docs" / "module.md").exists()


def test_update_accepts_project_path_from_anywhere():
    with temp_dir("testproject19") as tp:
        project = Path(tp).resolve()
        (project / "src").mkdir(parents=True)
        (project / "src" / "standalone.hat").write_text("fn standalone () unit { }\n")

        result = runner.invoke(app, ["update", str(project.resolve())])

        assert result.exit_code == 0
        assert (project / "docs" / "standalone.md").exists()
