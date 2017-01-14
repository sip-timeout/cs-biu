class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class StringMapper(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.string_to_int = dict()
        self.int_to_string = dict()
        self.cur_idx = 0
        print 'init'

    def get_int(self, string):
        if string not in self.string_to_int:
            self.string_to_int[string] = self.cur_idx
            self.int_to_string[self.cur_idx] = string
            self.cur_idx += 1
        return self.string_to_int[string]

    def get_string(self, int_rep):
        return self.int_to_string[int_rep]
