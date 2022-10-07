"""Memory"""

import pre_hhat.types as types
import pre_hhat.grammar.ast as gast


class Memory:
    def __init__(self, name=None):
        self.name = name
        if name is not None:
            self.stack = self._start()
        else:
            self.stack = dict()

    def init(self, name):
        if self.name is None:
            self.name = name
            self.stack = self._start()

    def _start(self):
        stack = {"name": self.name, "var": dict()}
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
            isinstance(var_name, (str, gast.AST, types.SingleStr))
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
                        for k in value:
                            self.stack["var"][key[0]]["data"] += k
                else:
                    self.stack["var"][key[0]][key[1]] = value
        if key in self.stack["var"].keys():
            for k in self.stack["var"][key]["data"]:
                self.stack["var"][key]["data"][k] = value

    def __getitem__(self, item):
        if isinstance(item, tuple):
            if item[0] in self.stack.keys():
                return self.stack[item[0]].get(item[1], types.SingleNull())
            if item[0] in self.stack["var"].keys():
                if item[1] in self.stack["var"][item[0]].keys():
                    return (self.stack["var"][item[0]][item[1]],)
                if item[1] in self.stack["var"][item[0]]["data"]:
                    return tuple(self.stack["var"][item[0]]["data"][item[1]])
                if item[1] == "indices":
                    return self.stack["var"][item[0]]["data"].indices
                if isinstance(item[1], tuple):
                    res = ()
                    for k in item[1]:
                        if not types.is_circuit(self.stack["var"][item[0]]["type"]()):
                            res += (self.stack["var"][item[0]]["data"][k.value[0]],)
                        else:
                            _len = self.stack["var"][item[0]]["len"]
                            if k < self.stack["var"][item[0]]["len"]:
                                res += k,
                    return res
            self.add_var(item[0], item[1])
            return tuple(self.stack["var"][item[0]])
        if item in self.stack.keys():
            return self.stack[item],
        if item in self.stack["var"].keys():
            if not types.is_circuit(self.stack["var"][item]["type"]):
                return tuple(self.stack["var"][item]["data"].value)
            return self.stack["var"][item]["data"],
        return False

    def __contains__(self, item):
        if isinstance(item, tuple):
            if item[0] in self.stack["var"].keys():
                return item[1] in self.stack["var"][item[0]]["data"].indices
            return False
        return item in self.stack["var"].keys()

    def __repr__(self):
        vals = "\n"
        vals += " "*15 + "=[Memory Stack]=\n|"
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
    def __init__(self, name=None, data=None):
        if name == "main":
            self.table = {"main": ()}
        elif name == "func":
            if data is not None:
                self.table = {"func": data}
            else:
                self.table = {"func": dict()}
        else:
            self.table = {"main": (), "func": dict()}
        self._name = self.__class__.__name__

    def has_func_params(self, name, data):
        vals = ()
        for k in self.table["func"][name].keys():
            if len(data) > 0 and len(k) > 0:
                for p1, p2 in zip(k, data):
                    if isinstance(p2[1](), types.ArrayType):
                        if p1[1].value[0] == p2[1]:
                            if len(p1[1]) == 2:
                                if p1[1].value[1] == p2[2]:
                                    vals += p1,
                            if not p2[-1]:
                                vals += p1,
                    elif isinstance(p2[1](), types.SingleType):
                        if isinstance(p2[1](), p1[1].value[0]().value_type):
                            if len(p1[1]) == 2:
                                if p1[1].value[1] == types.SingleInt(1):
                                    vals += p1,
                            else:
                                vals += p1,
                return (True, vals) if len(vals) > 0 else (False, ())
            else:
                return True, ()
        return False, ()

    def _prepare_func_data(self, data):
        name = data[0]
        func_type = data[1].value
        params = data[2].value if data[2].name == "params" else ()
        body = data[3:][0].value if data[2].name == "params" else data[2:][0].value
        if name not in self:
            self.table["func"].update({name: {params: {"data": body, "type": func_type, "return": types.SingleNull()}}})
        else:
            has_params, _ = self.has_func_params(name, params)
            if not has_params:
                self.table["func"][name].update({params: {"data": body, "type": func_type, "return": types.SingleNull()}})
            else:
                raise ValueError(f"{self._name}: var {name} already has params {params}.")

    def write_return(self, name, args, data):
        if name in self:
            if args in self.table["func"][name].keys():
                print(f"name={name} | args? {args in self.table['func'][name].keys()}")
                print(data)
                print(self.table["func"][name][args])
                self.table["func"][name][args]["return"] = data
                return
        raise ValueError(f"{self._name}: have no var {name} or has no params {args}.")

    def flush_return(self, name, args):
        val = self.table["func"][name][args]["return"]
        self.table["func"][name][args]["return"] = types.SingleNull()
        return val

    def __getitem__(self, item):
        if item == "main":
            return self.table["main"]
        if item in self.table["func"].keys():
            return self.table["func"][item]
        if item == "func":
            return self.table["func"]
        if isinstance(item, tuple):
            if item[0] in self:
                if len(item) == 2:
                    # this branch is used to retrieve data using exact or external args for function
                    has_params, args = self.has_func_params(item[0], item[1])
                    if has_params:
                        data = self.table["func"][item[0]][args]["data"]
                        return data, args
                if len(item) == 3:
                    # this branch will be used to get things like 'return' data
                    if item[1] in self.table["func"][item[0]].keys():
                        # the args (item[1]) are exactly the function parameters
                        if item[2] == "return":
                            return self.flush_return(item[0], item[1])
        raise ValueError(f"{self._name}: error when getting data from symbol table. Data: {item}")

    def __setitem__(self, key, value):
        if isinstance(value, (types.BaseGroup, gast.AST, tuple)):
            if key == "main":
                self.table["main"] = value
            else:
                if len(key) == 3:
                    self.write_return(key[0], key[1], value)
                else:
                    self._prepare_func_data(value)

    def __iadd__(self, other):
        if isinstance(other, (types.BaseGroup, gast.AST)):
            self.table["main"] = other
        elif isinstance(other, tuple):
            self.table["func"].update({other[0]: other[1]})
        return self

    def __contains__(self, item):
        return item in self.table["func"].keys()

    def __repr__(self):
        return f"{self.table}"
