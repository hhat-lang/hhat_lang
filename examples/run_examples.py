from hhat_lang.exec import run_codes


code_list = [
    """
        .[2 3 4]:sum:print:=z:print
        .[5 7 11]:.(sum times):print
        .[68 9]:sum(12 35):print
        .[45 56 67]:.(sum:=n times(n):=m):print
        4:@shuffle:=@q1
        1:print
        .[1 1]:sum:.(@shuffle:=@q2 y)
        @q1:@sync:=@q3
        //.[@q2:@sync:=@q4 .[z y]:sum:print]:sum:print
        1
        /( this
        is
        a
        comment
        )/
    """,
    # """
    # .[2 3 4]:.(sum times):print
    # .[10 20]:sum(2):print
    # .[50 60]:.(sum:n times(n):m times):print
    # 8:@shuffle:@q1:print
    # .[4]:print
    # .[634]:j:print
    # """,
    # ".[0 1]:sum .[2 3 4]:times .[5 6]:sum:print .[7 8]:.(sum times):print",
]


if __name__ == "__main__":
    print("***[START]***")
    print("="*80)
    for code in code_list:
        run_codes(code, verbose=True)
        print('='*80)
    print("***[END]***")
