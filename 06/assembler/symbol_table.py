class SymbolTable:
    def __init__(self, text):
        self._text = text
        self._lines = self._text.splitlines()

        self._next_variable = 16
        self.symbols = {
            'SP': 0,
            'LCL': 1,
            'ARG': 2,
            'THIS': 3,
            'THAT': 4,
            'R0': 0,
            'R1': 1,
            'R2': 2,
            'R3': 3,
            'R4': 4,
            'R5': 5,
            'R6': 6,
            'R7': 7,
            'R8': 8,
            'R9': 9,
            'R10': 10,
            'R11': 11,
            'R12': 12,
            'R13': 13,
            'R14': 14,
            'R15': 15,
            'SCREEN': 16384,
            'KBD': 24576
        }

        self._set_symbols()
        self._set_variables()

    def _contains(self, value):
        return value in self.symbols

    def _add(self, key, value):
        self.symbols[key] = value

    def _add_symbol(self, symbol, line):
        if not self._contains(symbol):
            self._add(symbol, line)

    def _add_variable(self, variable):
        if not self._contains(variable):
            self._add(variable, self._next_variable)
            self._next_variable += 1

    def _set_symbols(self):
        line_number = 0
        for line in self._lines:
            if line[0] == '(':
                symbol = line.replace('(', '').replace(')', '')
                self._add_symbol(symbol, line_number)
            else:
                line_number += 1

    def _set_variables(self):
        for line in self._lines:
            if line[0] == '@' and not line[1].isdigit():
                variable = line.replace('@', '')
                self._add_variable(variable)
