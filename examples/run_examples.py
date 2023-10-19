from hhat_lang.exec import run_codes


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
        run_codes(code, verbose=True)
        print('='*80)
    print("***[END]***")
