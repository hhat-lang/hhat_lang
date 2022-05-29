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

    @classmethod
    def create(cls, name=None, func=None):
        if name is None and func is None:
            if not cls.table['cur']:
                cls.table['cur'] = cls.set_default()
        else:
            if name not in cls.table['scope'].keys() and func in ['main', 'func']:
                cls.table['scope'].update({name: func})
                cls.table[func].update({name: cls.set_default()})

    @classmethod
    def add(cls, value, name=None, key=None):
        if name is None:
            if key is not None:
                cls.table['cur'][key] = value
            else:
                raise ValueError("Key must be 'type', 'params', 'body' or 'return'.")
        else:
            _func = cls.table['scope'].get(name, False)
            if _func:
                cls.table[_func][name][key] = value

    @classmethod
    def move_cur_to(cls, name):
        _func = cls.table['scope'].get(name, False)
        if _func:
            _new_data = deepcopy(cls.table['cur'])
            cls.table[_func][name] = _new_data
            cls.free_cur()

    @classmethod
    def free_cur(cls):
        cls.table['cur'] = cls.set_default()

    @classmethod
    def __repr__(cls):
        return f"{cls.table}"


class Memory:
    data = {}

    def __init__(self):
        pass

    @classmethod
    def set_default(cls):
        return {'cur': {}, 'func': {}, 'main': {}}

    @classmethod
    def set_var_mem(cls, type_data=None):
        if type_data in ['bool', 'int', 'float', 'str']:
            return {'type': type_data, 'len': 1, 'data': {}}
        if type_data in ['circuit']:
            return {'type': type_data, 'len': 1, 'data': []}
        if type_data in ['hashmap', 'measurement']:
            return {'type': type_data, 'len': 1, 'data': {}}
        if type in [None, 'null']:
            return {'type': None, 'len': 0, 'data': {}}

    @classmethod
    def set_var_data(cls, type_data, len_data=None):
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

    @classmethod
    def start(cls):
        if not cls.data:
            cls.data = cls.set_default()
        else:
            raise ValueError("Memory already started.")

    @classmethod
    def restart(cls):
        cls.data = cls.set_default()

    @classmethod
    def create(cls, scope, name, var, type_data):
        if scope in cls.data.keys():
            if name in cls.data[scope].keys():
                if var not in cls.data[scope][name].keys():
                    cls.data[scope][name].update({var: cls.set_var_mem(type_data)})
                    cls.data[scope][name][var]['data'] = cls.set_var_data(type_data)
            else:
                cls.data[scope][name] = {var: cls.set_var_mem(type_data)}
                cls.data[scope][name][var]['data'] = cls.set_var_data(type_data)

    @classmethod
    def write(cls, scope, name, var, value, index=None, prop=None):
        if scope in cls.data.keys():
            if name in cls.data[scope].keys():
                if var in cls.data[scope][name].keys():
                    if prop is None and index is not None:
                        if cls.data[scope][name][var]['type'] not in ['circuit']:
                            if index in cls.data[scope][name][var]['data'].keys():
                                if cls.data[scope][name][var]['type'] in ['int', 'float', 'str']:
                                    cls.data[scope][name][var]['data'][index] = value
                                elif cls.data[scope][name][var]['type'] in ['hashmap', 'measurement']:
                                    cls.data[scope][name][var]['data'].update({index: value})
                            else:
                                if cls.data[scope][name][var]['type'] in ['hashmap', 'measurement']:
                                    cls.data[scope][name][var]['data'].update({index: value})
                        else:
                            cls.data[scope][name][var]['data'].append(value)
                    elif prop is not None:
                        if prop in cls.data[scope][name][var].keys():
                            cls.data[scope][name][var][prop] = value
                            if prop == 'len':
                                type_data = cls.data[scope][name][var]['type']
                                cls.data[scope][name][var]['data'] = cls.set_var_data(
                                    type_data=type_data,
                                    len_data=value)
                    else:
                        if cls.data[scope][name][var]['type'] in ['circuit']:
                            cls.data[scope][name][var]['data'].append(value)

    @classmethod
    def append(cls, scope, name, var, index, value):
        if scope in cls.data.keys():
            if name in cls.data[scope].keys():
                if index in cls.data[scope][name][var]['data'].keys():
                    cls.data[scope][name][var]['data'][index] += value

    @classmethod
    def read(cls, scope, name, var, index=None, prop=None):
        # print('{SYMBOLIC READ}', scope, name, var, index, prop)
        if scope in cls.data.keys():
            if name in cls.data[scope].keys():
                if var in cls.data[scope][name].keys():
                    if index is None and prop is None:
                        if cls.data[scope][name][var]['type'] not in ['circuit', 'hashmap', 'measurement']:
                            return tuple(k for k in cls.data[scope][name][var]['data'].values())
                        return tuple(cls.data[scope][name][var]['data'])
                    if prop in cls.data[scope][name][var].keys():
                        return cls.data[scope][name][var][prop]
                    if cls.data[scope][name][var]['type'] not in ['circuit']:
                        if index in cls.data[scope][name][var]['data'].keys():
                            return cls.data[scope][name][var]['data'][index]
                    return tuple(cls.data[scope][name][var]['data'])
        raise ValueError(f"Error reading var '{var}'.")

    @classmethod
    def get_idx(cls, scope, name, var):
        if cls.data[scope][name][var]['type'] not in ['circuit']:
            return tuple(k for k in cls.data[scope][name][var]['data'].keys())
        else:
            return tuple(k for k in range(cls.data[scope][name][var]['len']))


    @classmethod
    def move(cls, from_scope, to_scope):
        _from_scope = deepcopy(cls.data[from_scope])
        cls.data[to_scope] = _from_scope
        cls.free(scope=from_scope)

    @classmethod
    def free(cls, scope=None, name=None):
        if scope is None:
            if name is None:
                cls.data = cls.set_default()
        else:
            if name is None:
                cls.data[scope] = dict()
            else:
                cls.data[scope][name] = dict()

    def __repr__(self):
        return f"{self.data}"


