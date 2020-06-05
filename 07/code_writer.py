import os
from constants import C_PUSH, C_POP


class CodeWriter:
    def __init__(self, file):
        self._file = file
        self._filename = os.path.basename(self._file.name).split('.')[0]
        self._label_count = 0
        self._asm_text = ''

    def write_arithmetic(self, command):
        if command in ['add', 'sub', 'and', 'or']:
            self._binary(command)
        elif command in ['neg', 'not']:
            self._unary(command)
        elif command in ['eq', 'gt', 'lt']:
            self._compare(command)

    def write_push_pop(self, command, segment, index):
        if command == C_PUSH:
            if segment == 'constant':
                self._write_many(['@%d' % index, 'D=A', '@SP', 'A=M', 'M=D',
                                  '@SP', 'M=M+1'])
            elif segment in ['local', 'argument', 'this', 'that']:
                command_push_pop = segment.upper()
                if segment == 'local':
                    command_push_pop = 'LCL'
                elif segment == 'argument':
                    command_push_pop = 'ARG'
                self._write_many(['@%s' % command_push_pop, 'A=M'])
                for _ in range(index):
                    self._write_one('A=A+1')
                self._write_many(['D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1'])
            elif segment in ['temp', 'pointer']:
                command_push_pop = 0
                if segment == 'temp':
                    command_push_pop = 5
                elif segment == 'pointer':
                    command_push_pop = 3
                self._write_one('@%d' % command_push_pop)
                for _ in range(index):
                    self._write_one('A=A+1')
                self._write_many(['D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1'])
            if segment == 'static':
                self._write_many(['@%s.%d' % (self._filename, index), 'D=M',
                                  '@SP', 'A=M', 'M=D', '@SP', 'M=M+1'])
        elif command == C_POP:
            if segment in ['local', 'argument', 'this', 'that']:
                command_push_pop = segment.upper()
                if segment == 'local':
                    command_push_pop = 'LCL'
                elif segment == 'argument':
                    command_push_pop = 'ARG'
                self._write_many(['@SP', 'M=M-1', 'A=M', 'D=M',
                                  '@%s' % command_push_pop, 'A=M'])
                for _ in range(index):
                    self._write_one('A=A+1')
                self._write_one('M=D')
            elif segment in ['temp', 'pointer']:
                command_push_pop = 0
                if segment == 'temp':
                    command_push_pop = 5
                elif segment == 'pointer':
                    command_push_pop = 3
                self._write_many(['@SP', 'M=M-1', 'A=M', 'D=M',
                                  '@%d' % command_push_pop])
                for _ in range(index):
                    self._write_one('A=A+1')
                self._write_one('M=D')
            if segment == 'static':
                self._write_many(['@SP', 'M=M-1', 'A=M', 'D=M',
                                  '@%s.%d' % (self._filename, index), 'M=D'])

    def close(self):
        self._file.write(self._asm_text[0:-1])
        self._file.close()

    def _binary(self, command):
        command_binary = ''
        if command == 'add':
            command_binary = 'D=D+M'
        elif command == 'sub':
            command_binary = 'D=M-D'
        elif command == 'and':
            command_binary = 'D=D&M'
        elif command == 'or':
            command_binary = 'D=D|M'
        self._write_many(['@SP', 'M=M-1', 'A=M', 'D=M', '@SP', 'M=M-1', 'A=M',
                          command_binary, '@SP', 'A=M', 'M=D', '@SP', 'M=M+1'])

    def _unary(self, command):
        command_unary = ''
        if command == 'neg':
            command_unary = 'M=-M'
        elif command == 'not':
            command_unary = 'M=!M'
        self._write_many(['@SP', 'A=M-1', command_unary])

    def _compare(self, command):
        label1 = self._label()
        label2 = self._label()
        command_compare = ''
        if command == 'eq':
            command_compare = 'JEQ'
        elif command == 'gt':
            command_compare = 'JGT'
        elif command == 'lt':
            command_compare = 'JLT'
        self._write_many(['@SP', 'M=M-1', 'A=M', 'D=M', '@SP', 'M=M-1', 'A=M',
                          'D=M-D', '@%s' % label1, 'D;%s' % command_compare,
                          'D=0', '@%s' % label2, '0;JMP', '(%s)' % label1,
                          'D=-1', '(%s)' % label2, '@SP', 'A=M', 'M=D', '@SP',
                          'M=M+1'])

    def _write_one(self, code):
        self._asm_text += code + '\n'

    def _write_many(self, codes):
        for code in codes:
            self._write_one(code)

    def _label(self):
        self._label_count += 1
        return 'LABEL' + str(self._label_count)
