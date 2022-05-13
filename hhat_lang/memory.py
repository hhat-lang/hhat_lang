"""Memory emulator """

import yaml


class BiHashMap:

    def __init__(self, value: dict = None):
        self.data = {}
        self.data_repr = {}
        if isinstance(value, dict):
            self.data = value
            self.data_repr = value
            self.data.update({v: k for k, v in value.items()})

    def __setitem__(self, key, value):
        self.data[key] = value
        self.data[value] = key
        self.data_repr[key] = value

    def __getitem__(self, item):
        return self.data[item]

    def __delitem__(self, key):
        key2 = self.data[key]
        del self.data[key]
        del self.data[key2]
        del self.data_repr[key]

    def remove(self, key):
        self.__delitem__(key)

    def pop(self, key):
        self.__delitem__(key)

    def __repr__(self):
        res = [{k, v} for k, v in self.data_repr.items()]
        return '{' + f"{res}".strip('[').strip(']') + '}'


class Memory:
    """
    Memory emulator class

    - contains a count int number to serve as global reference for the data
    - metadata with overall information of the program being run
    - stats for various stats if turned on
    - ref for storing the information regarding the origin of the data
    - mem for storing the actual data

    ----------------------
    ref should look like:
    key = ( 'func_or_main_name',
            'attribute_name',
            'type'
            )
    value = int (defined during attr assignment and count value)
    ----------------------
    mem should look like:
    key = int from the ref value
    value = data
    ----------------------
    """
    
    def __init__(self, do_debug=False):
        self.count = 1
        self.mem_ref = {}
        self.mem_data = {}
        self.do_debug = do_debug

    def dprint(self, *msg, **msgs):
        if self.do_debug:
            print(*msg, **msgs)

    def place_right_value(self, key):
        if key[-1] == int:
            return 0

        if key[-1] == str:
            return ''

        if key[-1] == float:
            return 0.0

        if key[-1] == None:
            return None

        if key[-1] in [list, 'any']:
            return 0

    def enforce_mem_creation(self, key):
        if key[1] is None or key[2] is None:
            return True
            
        return False

    def __setitem__(self, key, value):
        if isinstance(value, key[-1]) or key[-1] in ['any', list] or self.enforce_mem_creation(key):
            self.dprint(f'MEMORY WARNING SET: MEM_REF KEY={key}', end='')
            _no_key = not self.mem_ref.get(key)
            if self.mem_ref.get(key):
                self.mem_data[self.mem_ref[key]] = value
            else:
                self.mem_ref[key] = self.count
                self.mem_data[self.count] = value
            self.dprint(f' TO VALUE={value} ON MEMORY DATA SLOT={self.mem_ref[key]}')
            if _no_key:
                self.dprint(f'MEMORY WARNING SET: INCREMENTING COUNT')
                self.count += 1
        else:
            raise ValueError("Wrong value type for the attribute.")

    def __getitem__(self, item):
        if isinstance(item, tuple):
            if self.mem_ref.get(item):
                self.dprint(f'MEMORY WARNING GET: MEM_REF KEY={item} ATTEMPT TO RETRIEVE | VALUE={self.mem_data[self.mem_ref[item]]} | SLOT={self.mem_ref[item]}')
                return self.mem_data[self.mem_ref[item]]
            self.mem_ref[item] = self.count
            self.mem_data[self.count] = self.place_right_value(item)
            self.dprint(f'MEMORY WARNING GET: MEM_REF KEY={item} ATTEMPT TO RETRIEVE | VALUE={self.mem_data[self.mem_ref[item]]} | SLOT={self.mem_ref[item]}')
            self.dprint(f'MEMORY WARNING SET: INCREMENTING COUNT')
            self.count += 1
            return self.mem_data[self.mem_ref[item]]
        if isinstance(item, int):
            return self.mem_data[item]
        raise ValueError("Wrong value for memory reference.")

    def __delitem__(self, key):
        if isinstance(key, tuple):
            _value = self.mem_ref[key]
            del self.mem_ref[key]
            del self.mem_data[_value]
        elif isinstance(key, int):
            _value = self.mem_data[key]
            del self.mem_data[key]
            del self.mem_ref[_value]
        else:
            raise ValueError("Wrong value for memory reference.")

    def __repr__(self):
        _mem_state = f'| MEMORY STATE |'
        _mem_title = '-'*len(_mem_state) + '\n' + _mem_state + '\n' + '-'*len(_mem_state)
        _mem_ref = f'\nMEM_REF' + '-'*43 + f'\n{self.format_mem_str()}\n' + '-'*50
        _mem_data = f'MEM_DATA' + '-'*42 + f'\n{yaml.dump(self.mem_data, default_flow_style=False)}' + '-'*50
        return f"\n{_mem_title}\n{_mem_ref}\n{_mem_data}\n"

    def format_mem_str(self):
        _format = ""
        for k, v in self.mem_ref.items():
            _format += f"{k}: {v}\n"
        return _format

    def pop(self, item):
        self.__delitem__(item)

    def get(self, item):
        res = self.mem_ref.get(item, False)
        self.dprint(f'** Memory.get({item}) => {res} **')
        return res
