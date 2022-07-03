"""Symbolic for Pre Evaluation"""

from copy import deepcopy

"""
AST = tuple of objects (new_ast) 

FuncScopeTable - splits into 'main' and other functions funcs. i.e.: {'main': {}, 'funcs': {}}
VarScopeTable
BranchScopeTable



example:

func int Sum (int x, int y) ( return (add(x y)) )

main null X: ( 
 int a = (:3, :print('aoa'), :add(5), :print)
 int(3) b = (:10, 0:add(5), (1 2):add(-5), :print, (0 1):print('oi'))
 print(Sum(a b))
)

Program(
        Function(Token(function), (FuncTemplate(Symbol(Sum), Type(int), Params(...), Body(...)))),
        Function(Token(main), (FuncTemplate(Symbol(X), Type(null), Body(...)))),
        ...
        )

PreEvaluator -> 
(
    FST = {'main': {'X': (main's AST)},
           'funcs': {'Sum': (func's AST)}}
    VST = {'main': {'X': {'a': {'len': 1, 'type': 'int', 'data': {0: current_value}}},
                     {'b': {'len': 3, 'type': 'int', 'data': {0: cur, 1: cur, 2: cur}
                }},
            'funcs': {}}
    BST = {0: (AST body1 + exit_cond_body), ...}
)

Evaluator -> 
(
    AST = (FST(main(X)),)
)
"""


class FST:
    table = {'main': dict(), 'func': dict(), 'cur': dict(), 'scope': dict()}

    @staticmethod
    def set_default():
        return {'type': None, 'params': (), 'body': (), 'return': ()}

    def create(self, name=None, func=None):
        if name is None and func is None:
            if not self.table['cur']:
                self.table['cur'] = self.set_default()
        else:
            if name not in self.table['scope'].keys() and func in ['main', 'func']:
                self.table['scope'].update({name: func})
                self.table[func].update({name: self.set_default()})

    def add(self, value, name=None, key=None):
        if name is None:
            if key is not None:
                self.table['cur'][key] = value
            else:
                raise ValueError("Key must be 'type', 'params', 'body' or 'return'.")
        else:
            _func = self.table['scope'].get(name, False)
            if isinstance(_func, str):
                if key is not None:
                    self.table[_func][name][key] = value
                else:
                    self.table[_func][name] = value

    def is_func(self, name):
        return name in self.table['scope'].keys()

    def move_cur_to(self, name):
        _func = self.table['scope'].get(name, False)
        if _func:
            _new_data = deepcopy(self.table['cur'])
            self.table[_func][name] = _new_data
            self.free_cur()

    def free_cur(self):
        self.table['cur'] = self.set_default()

    def append(self, name, func, ext_table):
        if name not in self.table['scope'].keys():
            self.create(name, func)
            self.add(value=ext_table, name=name)
            self.move_cur_to(name)

    def __repr__(self):
        return f"{self.table}"


class Memory:
    def __init__(self):
        self.data = {}

    def set_default(self):
        return {'cur': {}, 'func': {}, 'main': {}}

    def set_var_mem(self, type_data=None):
        if type_data in ['bool', 'int', 'float', 'str']:
            return {'type': type_data, 'len': 1, 'data': {}}
        if type_data in ['circuit']:
            return {'type': type_data, 'len': 1, 'data': []}
        if type_data in ['hashmap', 'measurement']:
            return {'type': type_data, 'len': 1, 'data': {}}
        if type in [None, 'null']:
            return {'type': None, 'len': 0, 'data': {}}

    def set_var_data(self, type_data, len_data=None):
        if type_data == 'null':
            return {}
        if type_data == 'bool':
            if not len_data:
                return {0: None}
            return {k: None for k in range(len_data)}
        if type_data == 'int':
            if not len_data:
                return {0: 0}
            return {k: 0 for k in range(len_data)}
        if type_data == 'float':
            if not len_data:
                return {0: 0.0}
            return {k: 0.0 for k in range(len_data)}
        if type_data == 'str':
            if not len_data:
                return {0: ''}
            return {k: '' for k in range(len_data)}
        if type_data == 'circuit':
            return []
        if type_data in ['hashmap', 'measurement']:
            return {}
        return {}

    def start(self):
        if not self.data:
            self.data = self.set_default()
        else:
            raise ValueError("Memory already started.")

    def restart(self):
        self.data = self.set_default()

    def create(self, scope, name, var=None, type_data=None):
        if scope in self.data.keys():
            if name in self.data[scope].keys():
                if var not in self.data[scope][name].keys() and var is not None:
                    self.data[scope][name].update({var: self.set_var_mem(type_data)})
                    self.data[scope][name][var]['data'] = self.set_var_data(type_data)
            else:
                if var:
                    self.data[scope].update({name: {var: self.set_var_mem(type_data)}})
                else:
                    self.data[scope].update({name: {}})

                if type_data:
                    self.data[scope][name][var]['data'] = self.set_var_data(type_data)

    def write(self, scope, name, var, value, index=None, prop=None):
        if scope in self.data.keys():
            if name in self.data[scope].keys():
                if var in self.data[scope][name].keys():
                    if prop is None and index is not None:
                        if self.data[scope][name][var]['type'] not in ['circuit']:
                            if index in self.data[scope][name][var]['data'].keys():
                                if self.data[scope][name][var]['type'] in ['int', 'float', 'str']:
                                    self.data[scope][name][var]['data'][index] = value
                                elif self.data[scope][name][var]['type'] in ['hashmap',
                                                                             'measurement']:
                                    self.data[scope][name][var]['data'].update({index: value})
                            else:
                                if self.data[scope][name][var]['type'] in ['hashmap',
                                                                           'measurement']:
                                    self.data[scope][name][var]['data'].update({index: value})
                        else:
                            if isinstance(value, list):
                                self.data[scope][name][var]['data'].extend(value)
                            else:
                                self.data[scope][name][var]['data'].append(value)
                    elif prop is not None:
                        if prop in self.data[scope][name][var].keys():
                            self.data[scope][name][var][prop] = value
                            if prop == 'len':
                                type_data = self.data[scope][name][var]['type']
                                self.data[scope][name][var]['data'] = self.set_var_data(
                                    type_data=type_data,
                                    len_data=value)
                    else:
                        if self.data[scope][name][var]['type'] in ['circuit']:
                            if isinstance(value, list):
                                self.data[scope][name][var]['data'].extend(value)
                            else:
                                self.data[scope][name][var]['data'].append(value)
                        else:
                            if self.data[scope][name][var]['len'] == 1:
                                self.data[scope][name][var]['data'][0] = value

    def append(self, scope, name, var, index, value):
        if scope in self.data.keys():
            if name in self.data[scope].keys():
                if index in self.data[scope][name][var]['data'].keys():
                    self.data[scope][name][var]['data'][index] += value

    def read(self, scope, name, var, index=None, prop=None):
        if scope in self.data.keys():
            if name in self.data[scope].keys():
                if var in self.data[scope][name].keys():
                    if index is None and prop is None:
                        if self.data[scope][name][var]['type'] not in ['circuit', 'hashmap',
                                                                       'measurement']:
                            res = tuple(k for k in self.data[scope][name][var]['data'].values())
                            if len(res) > 1:
                                return res,
                            return res
                        return tuple(self.data[scope][name][var]['data'])
                    if prop in self.data[scope][name][var].keys():
                        return self.data[scope][name][var][prop]
                    if self.data[scope][name][var]['type'] not in ['circuit']:
                        if index in self.data[scope][name][var]['data'].keys():
                            if self.data[scope][name][var]['type'] in ['hashmap', 'measurement']:
                                return {index: self.data[scope][name][var]['data'][index]}
                            return self.data[scope][name][var]['data'][index]
                    return tuple(self.data[scope][name][var]['data'])
        raise ValueError(f"Error reading var '{var}'.")

    def copy(self, from_var, to_var):
        valid_keys = {'scope', 'name', 'var', 'data', 'len', 'type'}
        from_valid_set = set(from_var.keys()).symmetric_difference(valid_keys)
        to_valid_set = set(to_var.keys()).symmetric_difference(valid_keys)
        if not from_valid_set and not to_valid_set:
            if from_var['type'] == to_var['type']:
                from_data = self.data[from_var['scope']][from_var['name']][from_var['var']]
                to_data = self.data[to_var['scope']][to_var['name']][to_var['var']]
                to_data['data'] = deepcopy(from_data['data'])
                to_data['len'] = from_data['len']
            else:
                raise ValueError("From var e to var are no the same type.")
        else:
            raise ValueError(f"No valid from and to var to copy.")

    def get_idx(self, scope, name, var):
        if self.data[scope][name][var]['type'] not in ['circuit']:
            return tuple(k for k in self.data[scope][name][var]['data'].keys())
        else:
            return tuple(k for k in range(self.data[scope][name][var]['len']))

    def return_prop_or_idx(self, scope, name, var, data):
        if scope in self.data.keys():
            if name in self.data[scope].keys():
                if var in self.data[scope][name].keys():
                    if data in self.data[scope][name][var].keys():
                        return self.data[scope][name][var][data]
                    if data in self.data[scope][name][var]['data'].keys():
                        return self.data[scope][name][var]['data'][data]
        raise ValueError(f"Something got wrong here: {scope}->{name}->{var}->{data}.")

    def is_func(self, name):
        return name in self.data['func'].keys() or name in self.data['main'].keys()

    def is_var(self, scope, name, var):
        if scope in self.data.keys():
            if name in self.data[scope].keys():
                return var in self.data[scope][name].keys()
        return False

    def move(self, from_scope, to_scope):
        _from_scope = deepcopy(self.data[from_scope])
        self.data[to_scope] = _from_scope
        self.free(scope=from_scope)

    def free(self, scope=None, name=None):
        if scope is None:
            if name is None:
                self.data = self.set_default()
        else:
            if name is None:
                self.data[scope] = dict()
            else:
                self.data[scope][name] = dict()

    def __repr__(self):
        return f"{self.data}"
