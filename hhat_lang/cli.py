"""Console script for hhat_lang."""
import sys

import click

from hhat_lang.evaluator import Code


@click.command()
def main(args=None):
    """Console script for hhat_lang."""
    c = "main null C: (int a=(:add(1 1), :print))"
    code_exec = Code(c)
    code_exec.run()
    # click.echo("See click documentation at https://click.palletsprojects.com/")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
