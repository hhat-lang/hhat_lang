from hhat_lang.exec import run_codes


code_list = [
    # teleport example
    """
    "test":=text:@encode:=@q1:@shape:=@q2:@sync:=@q3
    .[@q1 @q2]:@shuffle:=@q4:cast(bin):/[=res1:nez:=n1:@sign(=+@q3[n1]) =res2:nez:=n2:@not(=+@q3[n2])]
    @q3:cast(str):=teleported-text:print
    """,
    # data encoding example
    # """
    # 8:=data:@encode:=@q1:cast(int):print
    # .[1 1]:sum:print
    # """,
    # """
    #     .[2 3 4]:sum:print:=z:print
    #     .[5 7 11]:.(sum times):print
    #     .[68 9]:sum(12 35):print
    #     .[45 56 67]:.(sum:=n times(n):=m):print
    #     4:@shuffle:=@q1
    #     1:print
    #     .[1 1]:sum:.(@shuffle:=@q2 y)
    #     @q1:@sync:=@q3
    #     .[@q2:@sync:=@q4 .[z y]:sum:print]:sum:print
    #     1
    #     /* this
    #     is
    #     a
    #     comment
    #     */
    #     "test":=text:@encode:=@q1:@shape:=@q2:@sync:=@q3
    #     .[@q1 @q2]:@shuffle:cast(bin):/[=res1:nez:=n1:@q3[n1]:@sign =res2:nez:=n2:@q3[n2]:@not]
    #     @q3:cast(str):=teleported-text:print
    # """,
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
