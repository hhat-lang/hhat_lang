from hhat_parsing import parse_code
from hhat_pre_eval import PreEval
from hhat_eval import Eval
from hhat_semantics import Analysis


def parsing(c):
    pc_ = parse_code(c)
    print(f"- code:\n{c}\n")
    print(f"- parsed code:\n{pc_}\n")
    return pc_


def pre_evaluating(pc):
    # pev_ = PreEval(pc)
    # res_ = pev_.run()
    print(f"- pre-evaluation:")
    analysis = Analysis(pc)
    res_ = analysis.run()
    print("\n")
    return res_


def evaluating(c):
    ev_ = Eval(c)
    print("- executing code:\n")
    ev_.run()


def run_codes(c):
    pc_ = parsing(c)
    pev_ = pre_evaluating(pc_)
    print("-" * 80)
    evaluating(pev_)


code_list = [
    """
    [2 3 4]:(sum times):print
    [10 20]:sum(2):print
    [50 60]:(sum:n times(n):m times):print
    """,
    # "[0 1]:sum [2 3 4]:times [5 6]:sum:print [7 8]:(sum times):print",
    # "[0 1]:(@init:@q1 @sync(@q1):@q2)",
    # "[0 1 2 3]:(@init:@ampl:@q1 @sync(@q1):@fflip(pi over(pi 2)):@q2)"
]


if __name__ == "__main__":
    print("***[START]***")
    print("="*80)
    for code in code_list:
        # parsing(code)
        run_codes(code)
        print('='*80)
    print("***[END]***")
