from copy import deepcopy
import pre_hhat.types as types
import pre_hhat.operators as oper
import pre_hhat.grammar.ast as gast
import pre_hhat.core.memory as memory


# noinspection PyStatementEffect,PyArgumentList
class Exec:
    def __init__(self):
        self.func = dict()
        self._ast_nodes = {
            "id": self.node_id,
            "args": self.node_args,
            "args2": self.node_args2,
            "key_arg": self.node_key_arg,
            "value": self.node_value,
            "pipe": self.node_pipe,
            "caller": self.node_caller,
            "value_expr": self.node_value_expr,
            "index_expr": self.node_index_expr,
            "assign_expr": self.node_assign_expr,
            "assign": self.node_assign,
            "gen_call": self.node_gen_call,
            "collect": self.kw_collect,
            "var_assign": self.node_var_assign,
            "type_expr": self.node_type_expr,
            "var_decl": self.node_var_decl,
            "protocol": self.node_protocol,
        }
        self._roles = {
            types.ArrayType: self.data_types,
            types.SingleType: self.literals,
            tuple: self.role_tuple,
            dict: self.role_dict,
        }

    def get_node(self, node, stack):
        # print(f"* get node={node}\n* node type={type(node)}\n* stack={stack}\n")
        return self._roles.get(type(node), self._get_ast_node(node))(node, stack)

    def _get_ast_node(self, node):
        if isinstance(node, types.SingleType):
            return self.literals
        if isinstance(node, types.ArrayType):
            return self.data_types
        return self._ast_nodes[node.name] if isinstance(node, gast.AST) else None

    def _get_value_type(self, data):
        if isinstance(data().value_type, tuple):
            return data
        return data().value_type

    def _wrap_args(self, data, stack):
        res = ()
        for k in data:
            if isinstance(k, gast.AST):
                print(k.value[0], type(k.value[0]), k, stack["mem"][k])
                res += (k,
                        (stack["mem"][k, "type"] + stack["mem"][k, "len"] + stack["mem"][k, "fixed_size"])
                        ),
            elif isinstance(k, types.SingleType):
                res += (k, k.name),
            elif isinstance(k, oper.Operators):
                raise NotImplementedError("need to implement operators in args.")
            else:
                print(f"wrap_args: val={k} | type={type(k)}")
                res += (k, k.name),
        return res

    def node_protocol(self, code, stack):

        return stack

    def kw_collect(self, code, stack):
        collect = oper.Collector(code.value)
        res = collect(stack)
        return stack

    def role_dict(self, code, stack):
        print("got into role dict")
        for k, v in code.items():
            if k == "main":
                stack["scope"] = "main"
                stack["mem"].init("main")
                stack = self.get_node(v, stack)
            else:
                break
        return stack

    def role_tuple(self, code, stack):
        old_stack = deepcopy(stack)
        for k in code:
            stack = self.get_node(k, stack)

        if stack["upstream"]:
            return stack
        return old_stack

    def literals(self, code, stack):
        stack["res"] += (code,)
        return stack

    def data_types(self, code, stack):
        print("DATA TYPES!!")
        return stack

    def circuit_type(self, code, stack):
        print('circuit type?')
        return stack

    def node_id(self, code, stack):
        if code in stack["mem"]:
            stack["res"] += stack["mem"][code]
        else:
            print(f"where's code {code} from?")
        return stack

    def node_args(self, code, stack):
        for n, k in enumerate(code):
            stack = self.get_node(k, stack)
        return stack

    def node_args2(self, code, stack):
        for k in code:
            stack = self.get_node(k[0], stack)
            stack = self.get_node(k[1], stack)
        return stack

    def node_key_arg(self, code, stack):
        key_arg = code.value
        stack["index"] += (stack["res"][-1])
        return stack

    def node_value(self, code, stack):
        stack = self.get_node(code.value, stack)
        return stack

    def node_caller(self, code, stack):
        prev_res = stack["res"]
        stack["res"] = ()
        self.get_node(code.value[0], stack)
        if stack["var"]:
            if not stack["index"]:
                stack["index"] = stack["mem"][stack["var"], "indices"]
            if isinstance(code.value[1], oper.Print):
                var_index = stack["mem"][stack["var"]]
            else:
                var_index = stack["mem"][stack["var"], stack["index"]]
            res = code.value[1](
                *(stack["res"], var_index),
                # value_type=stack["mem"][stack["var"], "type"][0],
                value_type=self._get_value_type(stack["mem"][stack["var"], "type"][0]),
                stack=stack,
            )
            # if res:
            #     print(f'* caller res={res} type={type(res)} vals={[type(p) for p in res]}')
            #     for k, idx in zip(res, stack["index"]):
            #         stack["mem"][stack["var"], idx] = k[0]
        else:
            res = code.value[1](*(stack["res"]))

        if res:
            stack["res"] = prev_res + res
            # print(f'* caller var?={stack["var"]} | res?={res} | stack res={stack["res"]}')
        else:
            stack["res"] = prev_res
        return stack

    def node_pipe(self, code, stack):
        # print(f"[PIPE] code {code} {code.value} {type(code.value)}")
        for k in code:
            # print(f"[PIPE] entering {stack['var']} memory: {k}")
            stack["mem"][stack["var"], stack["index"]] = k,
        # print(f"[PIPE] {stack['var']} memory: {stack['mem'][stack['var']]}")
        return stack

    def node_value_expr(self, code, stack):
        # print("here value expr")
        for k in code:
            # print(f"* value expr {k} | var={stack['var']} | index,res={stack['index']}, {stack['res']}")
            if not stack["index"]:
                stack["index"] = stack["mem"][stack["var"], "indices"]
            if isinstance(k, oper.Operators):
                var_index = stack["mem"][stack["var"], stack["index"]]
                # print(f"var {stack['var']} indices values: {var_index}")
                res = k(
                    *((types.SingleNull(),) + stack["res"], var_index),
                    # value_type=stack["mem"][stack["var"], "type"][0],
                    value_type=self._get_value_type(stack["mem"][stack["var"], "type"][0]),
                    stack=stack
                )
                if res:
                    stack["res"] += res
                    # for p, idx in zip(res, stack["index"]):
                    #     stack["mem"][stack["var"], idx] = p
            # if isinstance(k, oper.Operators):
            #     print("HUH?")
            #     res = k(
            #         *(stack["res"] + stack["index"]),
            #         value_type=stack["mem"][stack["var"], "type"][0],
            #         stack=stack
            #     )
            #     if res:
            #         # print(f"value expr oper res: {res}")
            #         stack["mem"][stack["var"], stack["index"]] = res
            else:
                stack = self.get_node(k, stack)
                # print(f'* value expr after else: var={stack["var"]} | res={stack["res"]}')
        # stack = self.get_node(code.value, stack)
        return stack

    def node_index_expr(self, code, stack):
        # print('* index_expr?')
        for k in code:
            if isinstance(k, types.SingleInt):
                stack["index"] += (k,)
            else:
                res = stack["res"]
                stack["res"] = ()
                stack = self.get_node(k, stack)
                # print(f'* index_expr res={stack["res"]} type={type(stack["res"][0])}')
                stack["index"] += stack["res"]
                # print(f'* index: {stack["index"]}')
                stack["res"] = res
        return stack

    def node_assign_expr(self, code, stack):
        stack["index"] = ()
        stack["res"] = ()
        if len(code.value) == 1:
            if not stack["index"]:
                stack["index"] = stack["mem"][stack["var"], "indices"]
            if isinstance(code.value[0], oper.Operators):
                var_index = stack["mem"][stack["var"], stack["index"]]
                # print(f"var {stack['var']} indices values: {var_index}")
                res = code.value[0](
                    *((types.SingleNull(),) + var_index),
                    # value_type=stack["mem"][stack["var"], "type"][0],
                    value_type=self._get_value_type(stack["mem"][stack["var"], "type"][0]),
                    stack=stack,
                )
                # print("* assign expr after oper?")
                if res:
                    stack["res"] = res
                    for k, idx in zip(res, stack["index"]):
                        stack["mem"][stack["var"], idx] = k
            else:
                stack = self.get_node(code.value[0], stack)
                # print(f'* assign exp var={stack["var"]} | index={stack["index"]} | res={stack["res"]}')
                # attempt to make it work:
                for p, idx in zip(stack["res"], stack["index"]):
                    stack["mem"][stack["var"], idx] = p
                # stack["mem"][stack["var"], stack["index"]] = stack["res"]
                # print(stack["mem"][stack["var"]])
        elif len(code.value) == 2:
            stack = self.get_node(code.value[0], stack)
            stack = self.get_node(code.value[1], stack)
            # print(f'* assign expr code=2 {stack["var"]} | index={stack["index"]} | res={stack["res"]}')
            # attempt to make it work:
            for p, idx in zip(stack["res"], stack["index"]):
                stack["mem"][stack["var"], idx] = p
        else:
            print("else?")

        # print(f'* assign expr: var={stack["var"]} | data={stack["mem"][stack["var"]]}')
        stack["index"] = ()
        stack["res"] = ()
        return stack

    def node_assign(self, code, stack):
        for k in code:
            stack = self.get_node(k, stack)
        return stack

    def node_gen_call(self, code, stack):
        if len(code.value[0].value) > 0:
            stack = self.get_node(code.value[0], stack)
        # print('* gen_call start')
        if stack["var"]:
            if isinstance(code.value[1], oper.Operators):
                res = code.value[1](
                    *((types.SingleNull(),) + stack["res"]),
                    # value_type=stack["mem"][stack["var"], "type"][0],
                    value_type=self._get_value_type(stack["mem"][stack["var"], "type"][0]),
                    stack=stack
                )
            else:
                if code.value[1] in self.func:
                    args = self._wrap_args(code.value[0], stack)
                    func_stack = self.new_stack(code.value[1])
                    func_stack = self.get_node(self.func[code.value[1], args], func_stack)
                    func_return = func_stack["mem"]["return"]
                    res = []
                else:
                    res = []
        else:
            if isinstance(code.value[1], oper.Operators):
                res = code.value[1](*((types.SingleNull(),) + stack["res"]), stack=stack)
            else:
                # print(f"func here!? {code.value[1]}({code.value[0]}) -> {self.func}")
                if code.value[1] in self.func:
                    old_res = stack["res"]
                    old_idx = stack["index"]
                    stack["res"] = ()
                    stack["index"] = ()

                    args = self._wrap_args(code.value[0], stack)

                    func_stack = self.new_stack(code.value[1])
                    func_stack = self.get_node(self.func[code.value[1], args], func_stack)
                    func_return = func_stack["mem"]["return"]

                    stack["res"] = old_res
                    stack["index"] = old_idx
                    res = []
                else:
                    # print("not func ):")
                    res = []
        if res:
            stack["res"] += res
        return stack

    def node_var_assign(self, code, stack):
        # print(code, type(code), code.value, type(code.value))
        # stack["var"] = code.value
        var = stack["var"]
        # print(f'* var assign {code} start')
        for n, k in enumerate(code):
            if n == 0:
                stack["var"] = k
            else:
                stack = self.get_node(k, stack)
        stack["var"] = var
        stack["res"] = ()
        stack["index"] = ()
        return stack

    def node_type_expr(self, code, stack):

        return stack

    def node_var_decl(self, code, stack):
        var = stack["var"]
        for n, k in enumerate(code):
            if n == 0:
                stack["var"] = k
            elif n == 1:
                stack["mem"][stack["var"], k]
            else:
                stack = self.get_node(k, stack)
        stack["var"] = var
        return stack

    @staticmethod
    def new_stack(name=None):
        return {
            "var": None,
            "res": (),
            "index": (),
            "scope": None,
            "mem": memory.Memory() if name is None else memory.Memory(name),
            "collect": None,
            "upstream": False,
        }

    def walk_tree(self, code, stack=None, funcs=None):
        stack = self.new_stack() if stack is None else stack
        self.func = funcs if funcs is not None else dict()
        return self.get_node(code, stack)
