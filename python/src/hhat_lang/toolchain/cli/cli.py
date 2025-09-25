from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich import print
from rich.console import Console
from rich.panel import Panel

from hhat_lang.toolchain.project.new import (
    create_new_file,
    create_new_project,
    create_new_type_file,
)
from hhat_lang.toolchain.project.run import run_project


def get_proj_dir() -> Path:
    current = Path().absolute()
    while current != current.parent:
        if (current / "src" / "main.hat").exists():
            return current
        current = current.parent
    raise ValueError("Not inside a H-hat project directory or src/main.hat missing")


app = typer.Typer(
    name="hat",
    help="Command line interface for H-hat language toolchain",
    no_args_is_help=True,
)

console = Console()


def version_callback(value: bool):
    if value:
        print("[blue]H-hat Language Toolchain[/blue] version 0.1.0")
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
):
    """
    H-hat Language Toolchain - A quantum programming language toolchain

    Use 'hat help <command>' for detailed information about a command.
    """
    pass


@app.command()
def help(command: Optional[str] = typer.Argument(None, help="Command to get help for")):
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
    project_name: Optional[str] = typer.Argument(
        None, help="Name of the project to create"
    ),
    file_name: str = typer.Option(None, "--file", "-f", help="Create a new file"),
    type_file: str = typer.Option(None, "--type", "-t", help="Create a new type file"),
):
    """
    Create a new project, file, or type file.

    This command can create:
    - A new H-hat project with required structure
    - A new .hat file within a project
    - A new type definition file within a project

    Examples:
        hat new myproject           # Create a new project
        hat new -f module/myfile    # Create a new file (and directories if needed)
        hat new -t custom_type      # Create a new type file
    """
    try:
        if project_name and not (file_name or type_file):
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
                        str(e)
                        + "\n\nPlease make sure you're inside a H-hat project directory.",
                        title="⚠ Error",
                        border_style="red",
                    )
                )
                raise typer.Exit(1)
            else:
                file_path = Path(file_name)
                if (proj_dir / f"{file_path}.hat").is_file():
                    raise FileExistsError(f"File {file_path}.hat already exists")
                if file_path.parent != Path("."):
                    file_path.parent.mkdir(parents=True, exist_ok=False)
                create_new_file(proj_dir, f"{file_path}.hat")
                console.print(
                    Panel(
                        f"File [bold]{file_name}.hat[/bold] created successfully!",
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
                        str(e)
                        + "\n\nPlease make sure you're inside a H-hat project directory.",
                        title="⚠ Error",
                        border_style="red",
                    )
                )
                raise typer.Exit(1)

        else:
            console.print(
                Panel(
                    "Please specify what to create (project, file, or type)\n\n"
                    "Examples:\n"
                    "  hat new myproject           # Create a new project\n"
                    "  hat new -f module/myfile    # Create a new file\n"
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
def run():
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


def main():
    """Entry point for the CLI"""
    app()
