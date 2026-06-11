from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich import print
from rich.console import Console
from rich.panel import Panel

from hhat_lang.toolchain.project.new import (
    create_new_const_file,
    create_new_fn_file,
    create_new_project,
    create_new_type_file,
)
from hhat_lang.toolchain.project.run import run_project
from hhat_lang.toolchain.project.update import update_project
from hhat_lang.toolchain.project.utils import get_proj_dir

app = typer.Typer(
    name="hat",
    help="[bold royal_blue1]Command line interface for H-hat language toolchain[/bold royal_blue1]",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console()


def _get_update_dir(path: Path | None = None) -> Path:
    current = path or Path().absolute()
    while current != current.parent:
        if (current / "src").is_dir():
            return current
        current = current.parent
    return path or Path().absolute()


def version_callback(value: bool) -> None:
    if value:
        print("[bold royal_blue1]H-hat Language Toolchain[/] version [bold royal_blue1]0.1.0[/]")
        raise typer.Exit()


@app.callback()
def common(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """
    H-hat Language Toolchain - A quantum programming language toolchain

    Use 'hat help <command>' for detailed information about a command.
    """
    pass


@app.command()
def help(command: Optional[str] = typer.Argument(None, help="Command to get help for")) -> None:
    """
    Show help about commands.

    Examples:
        hat help          # Show all available commands
        hat help new      # Show help for the new command
        hat help run      # Show help for the run command
    """
    if command is None:
        console.print(
            Panel.fit(
                "[bold]H-hat Language Toolchain[/bold]\n\n"
                "[bold]Available commands:[/bold]\n"
                "  [bold]new[/bold]     Create a new project, file, or type file\n"
                "  [bold]run[/bold]     Run the current H-hat project\n"
                "  [bold]update[/bold]  Check docs files and signatures\n"
                "  [bold]help[/bold]    Show this help message\n\n"
                "Use [bold]hat help <command>[/bold] for detailed information about a command.",
                title="hat - Command Line Interface",
                border_style="blue",
            )
        )
    else:
        # Simulate --help flag for the specified command
        sys.argv = ["hat", command, "--help"]
        try:
            app()
        except SystemExit:
            pass


@app.command()
def new(
    project_name: Optional[str] = typer.Argument(None, help="Name of the project to create"),
    file_name: str = typer.Option(None, "--file", "-f", help="Create a new file"),
    type_file: str = typer.Option(None, "--type", "-t", help="Create a new type file"),
    const_file: str = typer.Option(None, "--const", "-c", help="Create a new constant file"),
) -> None:
    """
    Create a new project, file, constant, or type file.

    This command can create:
    - A new H-hat project with required structure
    - A new .hat file within the project
    - A new type definition file within the project
    - A new constant definition file within the project

    Examples:
        hat new myproject           # Create a new project
        hat new -f myfile           # Create a new file
        hat new -t custom_type      # Create a new type file
        hat new -c some_constants   # Create a new constant file

    All new files can be created inside one or nested directories. Directories may
    exist or will be created.
    """

    try:
        if project_name and not (file_name or type_file or const_file):
            # Create new project
            create_new_project(Path(project_name))
            console.print(
                Panel(
                    f"Project [bold]{project_name}[/bold] created successfully!\n\n"
                    f"To get started, run:\n"
                    f"  cd {project_name}\n"
                    f"  hat run",
                    title="✓ Success",
                    border_style="green",
                )
            )

        elif file_name:
            try:
                proj_dir = get_proj_dir()
            except ValueError as e:
                console.print(
                    Panel(
                        str(e) + "\n\nPlease make sure you're inside a H-hat project directory.",
                        title="⚠ Error",
                        border_style="red",
                    )
                )
                raise typer.Exit(1)
            else:
                full_path = create_new_fn_file(proj_dir, Path(file_name))
                console.print(
                    Panel(
                        f"File [bold]{full_path}.hat[/bold] created successfully!",
                        title="✓ Success",
                        border_style="green",
                    )
                )

        elif type_file:
            proj_dir = get_proj_dir()
            try:
                create_new_type_file(proj_dir, Path(type_file))
                console.print(
                    Panel(
                        f"Type file [bold]{type_file}.hat[/bold] created successfully!",
                        title="✓ Success",
                        border_style="green",
                    )
                )
            except ValueError as e:
                console.print(
                    Panel(
                        str(e) + "\n\nPlease make sure you're inside a H-hat project directory.",
                        title="⚠ Error",
                        border_style="red",
                    )
                )
                raise typer.Exit(1)

        elif const_file:
            proj_dir = get_proj_dir()
            try:
                create_new_const_file(proj_dir, Path(const_file))
                console.print(
                    Panel(
                        f"Constant file [bold]{const_file}.hat[/bold] create successfully!",
                        title="✓ Success",
                        border_style="green",
                    )
                )
            except ValueError as e:
                console.print(
                    Panel(
                        str(e) + "\n\nPlease make sure you're inside a H-hat project directory.",
                        title="⚠ Error",
                        border_style="red",
                    )
                )
                raise typer.Exit(1)

        else:
            console.print(
                Panel(
                    "Please specify what to create (project, file, constant or type)\n\n"
                    "Examples:\n"
                    "  hat new myproject           # Create a new project\n"
                    "  hat new -f module/myfile    # Create a new file\n"
                    "  hat new -c const_file       # Create a new constant file\n"
                    "  hat new -t custom_type      # Create a new type file",
                    title="⚠ Missing Arguments",
                    border_style="yellow",
                )
            )
            raise typer.Exit(1)

    except FileExistsError as e:
        console.print(
            Panel(
                f"{str(e)}\n\nPlease choose a different name or remove the existing one.",
                title="⚠ Error",
                border_style="red",
            )
        )
        raise typer.Exit(1)
    except Exception as e:
        console.print(
            Panel(
                f"An unexpected error occurred: {str(e)}\n\n"
                "If this persists, please report it as an issue.",
                title="⚠ Error",
                border_style="red",
            )
        )
        raise typer.Exit(1)


@app.command()
def update() -> None:
    """
    Update the current H-hat project metadata and documentation files.

    This command must be executed from within a H-hat project directory. It
    currently checks whether every .hat code file under src/ has a matching .md
    documentation file under docs/, creating missing documentation files while
    preserving the source directory layout.

    Example:
        hat update    # Create missing docs for src/*.hat files
    """
    try:
        proj_dir = _get_update_dir()
        result = update_project(proj_dir)

        messages: list[str] = []
        if result.created_docs:
            created_files = "\n".join(
                f"  {doc_file.relative_to(proj_dir)}" for doc_file in result.created_docs
            )
            messages.append(
                f"Created {result.created_count} documentation file(s):\n{created_files}"
            )
        else:
            messages.append("All code files already have documentation counterparts.")

        if result.orphaned_docs:
            orphaned_files = "\n".join(
                f"  {doc.original_path.relative_to(proj_dir)} -> "
                f"{doc.orphan_path.relative_to(proj_dir)}"
                for doc in result.orphaned_docs
            )
            messages.append(
                f"Renamed {result.orphaned_doc_count} orphan documentation file(s):\n"
                f"{orphaned_files}"
            )

        if result.removed_signatures:
            removed_signature_lines = "\n".join(
                f"  {signature.doc_file.relative_to(proj_dir)} :: {signature.name}"
                for signature in result.removed_signatures
            )
            messages.append(
                f"Removed {result.removed_signature_count} stale documentation signature(s):\n"
                f"{removed_signature_lines}"
            )

        if result.updated_signatures:
            updated_lines = "\n".join(
                f"  {update.doc_file.relative_to(proj_dir)} :: "
                f"{update.signature.name} ({update.reason})"
                for update in result.updated_signatures
            )
            messages.append(
                f"Updated {result.updated_signature_count} documentation signature(s):\n"
                f"{updated_lines}"
            )

        if result.signature_mismatches:
            mismatch_lines = "\n".join(
                f"  {mismatch.doc_file.relative_to(proj_dir)} :: "
                f"{mismatch.signature.name} ({mismatch.reason})"
                for mismatch in result.signature_mismatches
            )
            messages.append(
                f"Unable to update {result.signature_mismatch_count} signature mismatch(es) "
                f"out of {result.checked_signature_count} checked signature(s):\n"
                f"{mismatch_lines}"
            )
            title = "⚠ Documentation signature mismatch"
            border_style = "yellow"
        else:
            messages.append(
                f"All {result.checked_signature_count} code signature(s) match documentation."
            )
            title = "✓ Documentation check complete"
            border_style = "green"

        console.print(
            Panel(
                "\n\n".join(messages),
                title=title,
                border_style=border_style,
            )
        )
        if result.signature_mismatches:
            raise typer.Exit(1)
    except typer.Exit:
        raise
    except ValueError as e:
        console.print(
            Panel(
                str(e) + "\n\nPlease make sure you're inside a H-hat project directory.",
                title="⚠ Error",
                border_style="red",
            )
        )
        raise typer.Exit(1)
    except Exception as e:
        console.print(
            Panel(
                f"An error occurred while updating the project: {str(e)}\n\n"
                "Please check your project structure and try again.",
                title="⚠ Error",
                border_style="red",
            )
        )
        raise typer.Exit(1)


@app.command()
def run() -> None:
    """
    Run the current H-hat project.

    This command must be executed from within a H-hat project directory
    that contains a main.hat file.

    Example:
        hat run    # Run the current project
    """
    try:
        # make sure we are in the proj dir, throw err if not
        get_proj_dir()
        run_project()
        console.print(
            Panel(
                "Project executed successfully!",
                title="✓ Success",
                border_style="green",
            )
        )
    except FileNotFoundError:
        console.print(
            Panel(
                "main.hat not found in current directory.\n\n"
                "Make sure you're in a H-hat project directory with a main.hat file.",
                title="⚠ Error",
                border_style="red",
            )
        )
        raise typer.Exit(1)
    except Exception as e:
        console.print(
            Panel(
                f"An error occurred while running the project: {str(e)}\n\n"
                "Please check your code for errors.",
                title="⚠ Error",
                border_style="red",
            )
        )
        raise typer.Exit(1)


def main() -> None:
    """Entry point for the CLI"""
    app()
