from hhat_ast import AST


class Data:
    def __init__(self, data: AST):
        self.value = data.value
        self.type = data.type
        self.ast_type = data.ast_type
        # self.args = data.args
        # if len(self.args) > 0:
        #     self._iter = self.args
        # else:
        #     self._iter = self.value,

    # def __iter__(self):
    #     yield from self._iter

    def __repr__(self):
        if self.value:
            value = str(self.value)
            # args = f"[{len(self.args)}]" if len(self.args) > 0 else ""
        else:
            # value = "(" + " ".join(str(k) for k in self.args) + ")"
            value = "?"
            # args = ""
        return value  # + args


class PreEval:
    def __init__(self, parsed_code):
        self.code = parsed_code

    def run(self):
        return format_code(self.code)


def format_code(code):
    if isinstance(code, AST):
        if len(code) > 0:
            if code.ast_type in ["program", "expr", "array"]:
                return format_code(code.args),
            elif code.ast_type == "oper":
                return ((Data(code),) + format_code(code.args),)
            else:
                raise ValueError(f"{code.ast_type=} invalid.")
        else:
            return Data(code),
    if isinstance(code, tuple):
        res = ()
        for k in code:
            res += format_code(k)
        return res
