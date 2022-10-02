"""Memory"""

import pre_hhat.types as types

from pre_hhat.grammar.ast import AST


class Memory:
    def __init__(self, name=None):
        if name is not None:
            self.stack = self._start()
            self.name = name
        else:
            self.name = None
            self.stack = dict()

    def init(self, name):
        if self.name is None:
            self.name = name
            self.stack = self._start()

    def _start(self):
        stack = {"name": self.name, "var": dict(), "return": types.SingleNull()}
        return stack

    @staticmethod
    def _init_var(type_expr, var_name):
        if isinstance(type_expr, tuple):
            if len(type_expr) == 2:
                _type = type_expr[0]
                _len = type_expr[1]
                _fixed_size = types.SingleBool("T")
                if not types.is_circuit(_type):
                    values = [
                        _type().value_type(_type().default[0])
                        for k in range(_len.value[0])
                    ]
                    _data = _type(*values, var=var_name)
                else:
                    _data = _type(*[None for _ in range(_len.value[0])], var=var_name)
            else:
                _type = type_expr[0]
                _len = types.SingleInt(1)
                _fixed_size = types.SingleBool("F")
                _data = _type(_type().value_type(type_expr[0]().default[0]), var=var_name)
        else:
            _type = type_expr
            _len = types.SingleInt(1)
            _fixed_size = types.SingleBool("F")
            _data = type_expr(type_expr.value_type(type_expr.default), var=var_name)
        return {"type": _type, "len": _len, "fixed_size": _fixed_size, "data": _data}

    def add_var(self, var_name, type_expr):
        if (
            isinstance(var_name, (str, AST, types.SingleStr))
            and var_name not in self.stack["var"].keys()
        ):
            self.stack["var"].update({var_name: self._init_var(type_expr.value, var_name)})
        if types.is_circuit(self.stack["var"][var_name]["type"]) and not var_name.value[0].startswith("@"):
            raise ValueError(f"{self.__class__.__name__}: circuit variable MUST have '@' suffix.")

    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            if key[0] in self.stack["var"].keys():
                if isinstance(key[1], int):
                    print("RED ALERT")
                    exit()
                if isinstance(key[1], types.SingleInt):
                    k1_keys = key[1] in self.stack["var"][key[0]]["data"].indices
                    if k1_keys:
                        if not types.is_circuit(self.stack["var"][key[0]]["type"]()):
                            self.stack["var"][key[0]]["data"][key[1]] = value
                        else:
                            self.stack["var"][key[0]]["data"] += value
                    elif not self.stack["var"][key[0]]["fixed_size"]:
                        if not types.is_circuit(self.stack["var"][key[0]]["type"]()):
                            self.stack["var"][key[0]]["data"][key[1]] += value
                            self.stack["var"][key[0]]["len"] = len(self.stack["var"][key[0]]["data"])
                        else:
                            self.stack["var"][key[0]]["data"] += value
                            self.stack["var"][key[0]]["len"] = self.stack["var"][key[0]]["len"] + types.SingleInt(1)
                elif isinstance(key[1], tuple):
                    if not types.is_circuit(self.stack["var"][key[0]]["type"]):
                        if len(key[1]) == len(value):
                                for idx, v in zip(key[1], value):
                                    self.stack["var"][key[0]]["data"][idx] = v
                        else:
                            for idx in key[1]:
                                self.stack["var"][key[0]]["data"][idx] = value
                    else:
                        print(f'mem ? {value} {type(value)}')
                        for k in value:
                            self.stack["var"][key[0]]["data"] += k

                else:
                    self.stack["var"][key[0]][key[1]] = value
        if key in self.stack["var"].keys():
            for k in self.stack["var"][key]["data"]:
                self.stack["var"][key]["data"][k] = value
        if key == "return":
            self.stack["return"] = value

    def __getitem__(self, item):
        if isinstance(item, tuple):
            if item[0] in self.stack.keys():
                return self.stack[item[0]].get(item[1], types.SingleNull())
            if item[0] in self.stack["var"].keys():
                if item[1] in self.stack["var"][item[0]].keys():
                    return (self.stack["var"][item[0]][item[1]],)
                if item[1] in self.stack["var"][item[0]]["data"]:
                    print(f'mem {item[0]} {item[1]}')
                    return tuple(self.stack["var"][item[0]]["data"][item[1]])
                if item[1] == "indices":
                    return self.stack["var"][item[0]]["data"].indices
                if isinstance(item[1], tuple):
                    res = ()
                    for k in item[1]:
                        if not types.is_circuit(self.stack["var"][item[0]]["type"]()):
                            print(f'{self.stack["var"][item[0]]}')
                            print(f'mem2 var {item[0]} get k ={k.value[0]} | get val={self.stack["var"][item[0]]["data"][k.value[0]]}')
                            res += (self.stack["var"][item[0]]["data"][k.value[0]],)
                        else:
                            _len = self.stack["var"][item[0]]["len"]
                            if k < self.stack["var"][item[0]]["len"]:
                                res += k,
                    print(f'mem2 {item[0]}({item[1]}) res={res}')
                    print(f'mem2 {self.stack["var"][item[0]]["data"]}')
                    return res
            self.add_var(item[0], item[1])
            return tuple(self.stack["var"][item[0]])
        if item in self.stack.keys():
            return tuple(self.stack[item])
        if item in self.stack["var"].keys():
            if not types.is_circuit(self.stack["var"][item]["type"]):
                return tuple(self.stack["var"][item]["data"].value)
            return self.stack["var"][item]["data"],
        # raise ValueError(f"No {item} found in memory.")
        return False

    def __contains__(self, item):
        if isinstance(item, tuple):
            if item[0] in self.stack["var"].keys():
                return item[1] in self.stack["var"][item[0]]["data"].indices
            return False
        return item in self.stack["var"].keys()

    def __repr__(self):
        vals = " "*15 + "=[Memory Stack]=\n|"
        vals += "-"*50 + "\n"
        vals += f"| * name: {self.stack['name']}\n|"
        for k, v in self.stack["var"].items():
            vals += f" * var: {k}\n|" + " "*6
            vals += f"* type: {v['type']}\n|" + " "*6
            vals += f"* len: {v['len']}\n|" + " "*6
            vals += f"* fixed_size: {v['fixed_size']}\n|" + " "*6
            vals += f"* data: {v['data']}\n|"
        vals += f" * return: {self.stack['return']}\n|"
        vals += "-"*50
        return f"\n{vals}\n"


class SymbolTable:
    def __init__(self):
        self.table = {"main": None, "func": dict()}

    def __getitem__(self, item):
        if item == "main":
            return self.table["main"]
        if item in self.table["func"].keys():
            return self.table["func"][item]
        if item == "func":
            return self.table["func"]
        raise ValueError(f"{self.__class__.__name__}: error when getting data from symbol table.")

    def __setitem__(self, key, value):
        if isinstance(value, (types.BaseGroup, AST, tuple)):
            if key == "main":
                self.table["main"] = value
            else:
                self.table["func"].update({key: value})

    def __iadd__(self, other):
        if isinstance(other, (types.BaseGroup, AST)):
            self.table["main"] = other
        elif isinstance(other, tuple):
            self.table["func"].update({other[0]: other[1]})
        return self

    def __repr__(self):
        return f"{self.table}"
