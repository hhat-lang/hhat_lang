"""Memory emulator"""

import time


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
    key = ( 'origin_program_name',  # not necessary for now
            'current_program_name',  # not necessary for now
            'func_or_main_name',
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
    def __init__(self, program_name: str = None, do_stats: bool = False):
        self.count = 0
        self.mem_ref = {}
        self.mem_data = {}
        self.metadata = self.gen_metadata(program_name)
        if do_stats:
            self.stats = self.gen_stats()

    def __setitem__(self, key, value):
        if isinstance(value, key[-1]):
            self.mem_ref[key] = self.count
            self.mem_data[self.count] = value
            self.count += 1
        else:
            raise ValueError("Wrong value type for the attribute.")

    def __getitem__(self, item):
        if isinstance(item, tuple):
            if self.mem_ref.get(item):
                return self.mem_ref[item]
            self.mem_ref[item] = self.count
            self.mem_data[self.count] = None
            self.count += 1
            return None
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

    def pop(self, item):
        self.__delitem__(item)

    def gen_metadata(self, program_name):
        _metadata = {'program': program_name if program_name else hex(time.time_ns())}
        _metadata.update({'imports': ()})
        _metadata.update({'functions': ()})
        _metadata.update({'main': ()})
        return _metadata

    def gen_stats(self):
        _stats = {}
        return _stats
