from constants import Kind


class SymbolTable:
    def __init__(self):
        self.static_table = {}
        self.field_table = {}
        self.arg_table = {}
        self.var_table = {}

    def start_subroutine(self):
        self.arg_table = {}
        self.var_table = {}

    def define(self, name, type, kind):
        index = self.var_count(kind)
        if kind == Kind.STATIC:
            self.static_table[name] = self._define_value(kind, type, index)
        elif kind == Kind.FIELD:
            self.field_table[name] = self._define_value(kind, type, index)
        elif kind == Kind.ARG:
            self.arg_table[name] = self._define_value(kind, type, index)
        elif kind == Kind.VAR:
            self.var_table[name] = self._define_value(kind, type, index)

    def var_count(self, kind):
        if kind == Kind.STATIC:
            return len(self.static_table)
        elif kind == Kind.FIELD:
            return len(self.field_table)
        elif kind == Kind.ARG:
            return len(self.arg_table)
        elif kind == Kind.VAR:
            return len(self.var_table)

    def kind_of(self, name):
        identifier = self._get_value(name)
        if identifier:
            return identifier['kind']

    def type_of(self, name):
        identifier = self._get_value(name)
        return identifier['type']

    def index_of(self, name):
        identifier = self._get_value(name)
        return identifier['index']

    def _define_value(self, kind, type, index):
        return {
            'kind': kind,
            'type': type,
            'index': index
        }

    def _get_value(self, name):
        if name in self.static_table:
            return self.static_table[name]
        elif name in self.field_table:
            return self.field_table[name]
        elif name in self.arg_table:
            return self.arg_table[name]
        elif name in self.var_table:
            return self.var_table[name]
