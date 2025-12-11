from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest
from hhat_lang.toolchain.cli.cli import app
from typer.testing import CliRunner

runner = CliRunner()


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for tests"""
    original_cwd = os.getcwd()
    temp_dir = "temp"
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
    assert "help" in result.stdout


def test_help_specific_command():
    """Test help for a specific command shows detailed information"""
    result = runner.invoke(app, ["help", "new"])
    assert result.exit_code == 0
    assert "Create a new project, file, or type file" in result.stdout
    assert "--file" in result.stdout
    assert "--type" in result.stdout


def test_create_new_project(temp_dir):
    """Test creating a new project succeeds"""
    result = runner.invoke(app, ["new", "testproject"])
    assert result.exit_code == 0
    assert "created successfully" in result.stdout
    assert (Path() / "testproject").exists()
    assert (Path() / "testproject" / "src" / "main.hat").exists()
    assert (Path() / "testproject" / "src" / "hat_docs" / "main.hat.md").exists()


def test_create_project_exists(temp_dir):
    """Test creating a project fails when directory exists"""
    runner.invoke(app, ["new", "testproject"])
    # Try to create it again
    result = runner.invoke(app, ["new", "testproject"])
    assert result.exit_code == 1
    assert "Error" in result.stdout
    assert "exists" in result.stdout


def test_create_file_in_project(temp_dir):
    """Test creating a new file inside a project directory"""
    runner.invoke(app, ["new", "testproject"])
    os.chdir("testproject")
    # Create a new file
    result = runner.invoke(app, ["new", "-f", "module/testfile"])
    assert result.exit_code == 0
    assert "created successfully" in result.stdout
    assert (Path() / "src" / "module" / "testfile.hat").exists()
    assert not (Path() / "src" / "module" / "testfile").exists()
    assert (Path() / "src" / "hat_docs" / "module" / "testfile.hat.md").exists()


def test_create_file_default_under_src(temp_dir):
    """Creating a file with no path goes into src/ by default"""
    runner.invoke(app, ["new", "proj"])
    os.chdir("proj")
    result = runner.invoke(app, ["new", "-f", "simple"])
    assert result.exit_code == 0
    assert (Path() / "src" / "simple.hat").exists()
    assert (Path() / "src" / "hat_docs" / "simple.hat.md").exists()


def test_create_file_with_src_prefix_and_extension(temp_dir):
    """Specifying a src/ path with .hat should not duplicate the extension"""
    runner.invoke(app, ["new", "proj"])
    os.chdir("proj")
    result = runner.invoke(app, ["new", "-f", "src/foo.hat"])
    assert result.exit_code == 0
    assert (Path() / "src" / "foo.hat").exists()
    assert not (Path() / "src" / "foo.hat.hat").exists()
    assert (Path() / "src" / "hat_docs" / "foo.hat.md").exists()


def test_create_file_outside_project(temp_dir):
    """Test creating a file fails outside project directory"""
    result = runner.invoke(app, ["new", "-f", "testfile"])
    assert result.exit_code == 1
    assert "Error" in result.stdout
    assert "project directory" in result.stdout


def test_create_file_escape_scope(temp_dir):
    """Creating a file with a path outside project should fail"""
    runner.invoke(app, ["new", "proj"])
    os.chdir("proj")
    result = runner.invoke(app, ["new", "-f", "../bad"])
    assert result.exit_code == 1
    assert "outside the project directory" in result.stdout


def test_create_existing_file(temp_dir):
    """Test creating a file fails when it already exists"""
    runner.invoke(app, ["new", "testproject"])
    os.chdir("testproject")
    runner.invoke(app, ["new", "-f", "testfile"])
    result = runner.invoke(app, ["new", "-f", "testfile"])
    assert result.exit_code == 1
    assert "Error" in result.stdout
    assert "already exists" in result.stdout


def test_create_type_file(temp_dir):
    """Test creating a new type file inside a project directory"""
    runner.invoke(app, ["new", "testproject"])
    os.chdir("testproject")
    result = runner.invoke(app, ["new", "-t", "customtype"])
    assert result.exit_code == 0
    assert "created successfully" in result.stdout
    assert (Path() / "src" / "hat_types" / "customtype.hat").exists()
    assert (Path() / "src" / "hat_docs" / "hat_types" / "customtype.hat.md").exists()


def test_create_type_file_with_full_path(temp_dir):
    """Type file path including src/hat_types should be mirrored"""
    runner.invoke(app, ["new", "proj"])
    os.chdir("proj")
    result = runner.invoke(app, ["new", "-t", "src/hat_types/subdir/foo"])
    assert result.exit_code == 0
    assert (Path() / "src" / "hat_types" / "subdir" / "foo.hat").exists()
    assert (
        Path() / "src" / "hat_docs" / "hat_types" / "subdir" / "foo.hat.md"
    ).exists()


def test_create_type_file_src_prefix(temp_dir):
    """If path starts with src/ but not hat_types/, it is placed under hat_types"""
    runner.invoke(app, ["new", "proj"])
    os.chdir("proj")
    result = runner.invoke(app, ["new", "-t", "src/foo"])
    assert result.exit_code == 0
    assert (Path() / "src" / "hat_types" / "foo.hat").exists()
    assert (Path() / "src" / "hat_docs" / "hat_types" / "foo.hat.md").exists()


def test_create_type_file_escape_scope(temp_dir):
    """Creating a type file outside project should fail"""
    runner.invoke(app, ["new", "proj"])
    os.chdir("proj")
    result = runner.invoke(app, ["new", "-t", "../bad"])
    assert result.exit_code == 1
    assert "outside the project directory" in result.stdout


def test_run_project(temp_dir):
    """Test running a project with empty main.hat"""
    runner.invoke(app, ["new", "testproject"])
    os.chdir("testproject")
    # Run the project
    result = runner.invoke(app, ["run"])
    assert result.exit_code == 1  # expect an error
    assert "Error" in result.stdout
    assert "no implementation yet" in result.stdout


def test_run_outside_project(temp_dir):
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
