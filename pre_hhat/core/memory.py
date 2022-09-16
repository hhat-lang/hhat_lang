"""Memory"""
from pre_hhat.grammar.ast import AST
from pre_hhat.types.groups import (BaseGroup, Gate, GateArray)
from pre_hhat.types.builtin import (SingleInt, SingleStr, SingleBool, SingleNull,
                                    ArrayBool, ArrayInt, ArrayStr, ArrayCircuit)


class Memory:
    def __init__(self, func_type, name=None):
        if func_type in ['main', 'func']:
            self.func_type = func_type
            self.name = name
            self.stack = self._start()
        else:
            raise ValueError(f"{self.__class__.__name__}: wrong func_type; must be main or func.")

    def _start(self):
        stack = {'func_type': self.func_type,
                 'var': dict(),
                 'return': SingleNull()}
        if self.func_type != 'main' and self.name is not None:
            stack.update({'name': self.name})
        return stack

    @staticmethod
    def _init_var(type_expr):
        if isinstance(type_expr, tuple):
            if len(type_expr) == 2:
                _type = type_expr[0]
                _len = type_expr[1]
                _fixed_size = SingleBool('T')
            else:
                _type = type_expr[0]
                _len = SingleInt(1)
                _fixed_size = SingleBool('F')
        else:
            _type = type_expr
            _len = SingleInt(1)
            _fixed_size = SingleBool('F')
        return {'type': _type,
                'len': _len,
                'fixed_size': _fixed_size,
                'data': SingleNull()}

    def add_var(self, var_name, type_expr):
        if isinstance(var_name, (str, SingleStr)) and var_name not in self.stack['var'].keys():
            self.stack['var'].update({var_name: self._init_var(type_expr)})
        else:
            raise ValueError(f"{var_name} cannot be (re)set in memory.")

    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            if key[0] in self.stack['var'].keys():
                if isinstance(key[1], (int, SingleInt)):
                    k1_keys = key[1] in self.stack['var'][key[0]]['data'].keys()
                    v_len = len(value) == self.stack['var'][key[0]]['len'].value[0]
                    if k1_keys and v_len:
                        self.stack['var'][key[0]]['data'][key[1]] = value
                    elif not self.stack['var'][key[0]]['fixed_size']:
                        self.stack['var'][key[0]]['data'][key[1]] = value
                        self.stack['var'][key[0]]['len'] = len(self.stack['var'][key[0]]['data'])
                else:
                    self.stack['var'][key[0]][key[1]] = value
        if key == 'return':
            self.stack['return'] = value

    def __getitem__(self, item):
        if isinstance(item, tuple):
            if item[0] in self.stack.keys():
                return self.stack[item[0]].get(item[1], SingleNull())
            self.add_var(item[0], item[1])
            return self.stack['var'][item[0]]
        if item in self.stack.keys():
            return self.stack[item]
        raise ValueError(f"No {item} found in memory.")


class SymbolTable:
    def __init__(self):
        self.table = {'main': None, 'func': dict()}

    def __getitem__(self, item):
        if item == 'main':
            return self.table['main']
        if item in self.table['func'].keys():
            return self.table['func'][item]
        raise ValueError(f"{self.__class__.__name__}: error when getting data from symbol table.")

    def __setitem__(self, key, value):
        if isinstance(value, (BaseGroup, AST, tuple)):
            if key == 'main':
                self.table['main'] = value
            else:
                self.table['func'].update({key: value})

    def __iadd__(self, other):
        if isinstance(other, (BaseGroup, AST)):
            self.table['main'] = other
        elif isinstance(other, tuple):
            self.table['func'].update({other[0]: other[1]})
        return self

    def __repr__(self):
        return f"{self.table}"
