# type: ignore[attr-defined]
from pre_hhat import version as hhat_version
from pre_hhat.grammar.cst import parsing_code
from pre_hhat.interpreter.pre_evaluator import PreEvaluator
from pre_hhat.interpreter.evaluator import Evaluator
from time import process_time
import click


# @click.command()
@click.group(invoke_without_command=True, context_settings=dict(ignore_unknown_options=True))
@click.argument("file", type=click.Path(exists=True), required=False)
@click.option("-v", "version", is_flag=True)
def hhat2(file, version):
    if version:
        click.echo(f"H-hat version {hhat_version}")
    else:
        code_ast = parsing_code(file, False, False, True, False)
        pre_eval = PreEvaluator(code_ast)
        table = pre_eval.walk_tree()
        print('-' * 20)
        print("*  Interpreter:")
        print("_" * 20)
        print()
        ev = Evaluator(table)
        t0 = process_time()
        ev.run()
        t1 = process_time()
        print("_" * 20)
        print(f"done in {round(t1 - t0, 6)}s.")


if __name__ == "__main__":
    hhat2()
