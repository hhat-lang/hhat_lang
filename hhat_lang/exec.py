from hhat_lang.interpreter import parse_code, Analysis, Eval
from hhat_lang.interpreter.post_ast import R
from hhat_lang.syntax_trees import AST
from hhat_lang import __version__
import click


def read_file(file: str) -> str:
    if file.endswith(".hat"):
        return open(file, "r").read()


def execute_parsing_code(c: str, verbose: bool = False) -> AST:
    pc_ = parse_code(c)
    if verbose:
        print("-" * 80)
        print(f"- code:\n{c}")
        print("-" * 80)
        print(f"- parsed code:\n{pc_}\n")
    return pc_


def execute_analysis(pc: AST, verbose: bool = False) -> R:
    if verbose:
        print("-" * 80)
        print(f"- analysis (pre-evaluation):")
    analysis = Analysis(pc)
    res_ = analysis.run()
    print("\n")
    return res_


def execute_eval(c: R) -> None:
    ev_ = Eval(c)
    print("- executing code:\n")
    ev_.run()


def run_codes(c: str, verbose: bool = False) -> None:
    pc_ = execute_parsing_code(c, verbose)
    pev_ = execute_analysis(pc_, verbose)
    print("-" * 80)
    execute_eval(pev_)


@click.group(invoke_without_command=True, context_settings=dict(ignore_unknown_options=True))
@click.argument("file", type=click.Path(exists=True), required=False)
@click.option("-v", "--version", "version", is_flag=True)
@click.option("--verbose", "verbose", is_flag=True)
def main(file, version, verbose):
    if version:
        click.echo(f"H-hat version {__version__}")
    else:
        if file:
            code_text = read_file(file)
            run_codes(code_text, verbose=verbose)
        else:
            # TODO: make a REPL?
            pass
