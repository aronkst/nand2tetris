class Code:
    def __init__(self, text, symbol_table):
        self.text = text
        self._lines = self.text.splitlines()

        self.symbol_table = symbol_table

        self._comp = {
            '0': '0101010',
            '1': '0111111',
            '-1': '0111010',
            'D': '0001100',
            'A': '0110000',
            '!D': '0001101',
            '!A': '0110001',
            '-D': '0001111',
            '-A': '0110011',
            'D+1': '0011111',
            'A+1': '0110111',
            'D-1': '0001110',
            'A-1': '0110010',
            'D+A': '0000010',
            'D-A': '0010011',
            'A-D': '0000111',
            'D&A': '0000000',
            'D|A': '0010101',
            'M': '1110000',
            '!M': '1110001',
            '-M': '1110011',
            'M+1': '1110111',
            'M-1': '1110010',
            'D+M': '1000010',
            'D-M': '1010011',
            'M-D': '1000111',
            'D&M': '1000000',
            'D|M': '1010101'
        }
        self._dest = {
            'M': '001',
            'D': '010',
            'MD': '011',
            'A': '100',
            'AM': '101',
            'AD': '110',
            'AMD': '111'
        }
        self._jump = {
            'JGT': '001',
            'JEQ': '010',
            'JGE': '011',
            'JLT': '100',
            'JNE': '101',
            'JLE': '110',
            'JMP': '111'
        }

        self._set_instructions()

    def _set_instructions(self):
        text = ''
        for line in self._lines:
            if '(' in line:
                continue
            value = ''
            if line[0] == '@':
                value = self._set_value(line)
            else:
                value = ''
                if '=' in line:
                    dest = line.split('=')[0]
                    value = self._dest[dest]
                else:
                    value = '000'
                if ';' in line:
                    jump = line.split(';')[1]
                    value = value + self._jump[jump]
                else:
                    value = value + '000'
                if '=' in line:
                    comp = line.split('=')[1]
                    if ';' in line:
                        comp = comp.split(';')[0]
                    value = self._comp[comp] + value
                else:
                    comp = line.split(';')[0]
                    value = self._comp[comp] + value
                value = '111' + value
            text = text + value + '\n'
        self.text = text[0:-1]

    def _set_value(self, line):
        line = line.replace('@', '')
        if line.isdigit():
            return '{0:b}'.format(int(line)).zfill(16)
        else:
            return '{0:b}'.format(int(self.symbol_table[line])).zfill(16)
