class CodeWriter:
    def __init__(self, file):
        self._file = file
        self._asm_text = ''
        self._if_label_count = 0
        self._return_label_count = 0
        self._filename = ''
        self._function_label_name = ''

    def set_file_name(self, filename):
        self._filename = filename

    def write_arithmetic(self, command):
        if command in ['add', 'sub', 'and', 'or']:
            self._binary(command)
        elif command in ['neg', 'not']:
            self._unary(command)
        elif command in ['eq', 'gt', 'lt']:
            self._compare(command)

    def write_push(self, segment, index):
        if segment == 'constant':
            self._write_many(['@%d' % index, 'D=A', '@SP', 'A=M', 'M=D', '@SP',
                              'M=M+1'])
        elif segment in ['local', 'argument', 'this', 'that']:
            command_push = segment.upper()
            if segment == 'local':
                command_push = 'LCL'
            elif segment == 'argument':
                command_push = 'ARG'
            self._write_many(['@%s' % command_push, 'A=M'])
            for _ in range(index):
                self._write_one('A=A+1')
            self._write_many(['D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1'])
        elif segment in ['temp', 'pointer']:
            command_push = 0
            if segment == 'temp':
                command_push = 5
            elif segment == 'pointer':
                command_push = 3
            self._write_one('@%d' % command_push)
            for _ in range(index):
                self._write_one('A=A+1')
            self._write_many(['D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1'])
        if segment == 'static':
            self._write_many(['@%s.%d' % (self._filename, index), 'D=M', '@SP',
                              'A=M', 'M=D', '@SP', 'M=M+1'])

    def write_pop(self, segment, index):
        if segment in ['local', 'argument', 'this', 'that']:
            command_pop = segment.upper()
            if segment == 'local':
                command_pop = 'LCL'
            elif segment == 'argument':
                command_pop = 'ARG'
            self._write_many(['@SP', 'M=M-1', 'A=M', 'D=M',
                              '@%s' % command_pop, 'A=M'])
            for _ in range(index):
                self._write_one('A=A+1')
            self._write_one('M=D')
        elif segment in ['temp', 'pointer']:
            command_pop = 0
            if segment == 'temp':
                command_pop = 5
            elif segment == 'pointer':
                command_pop = 3
            self._write_many(['@SP', 'M=M-1', 'A=M', 'D=M',
                              '@%d' % command_pop])
            for _ in range(index):
                self._write_one('A=A+1')
            self._write_one('M=D')
        if segment == 'static':
            self._write_many(['@SP', 'M=M-1', 'A=M', 'D=M',
                              '@%s.%d' % (self._filename, index), 'M=D'])

    def write_label(self, label):
        label = self._function_label(label)
        self._write_one('(%s)' % label)

    def write_goto(self, label):
        label = self._function_label(label)
        self._write_many(['@%s' % label, '0;JMP'])

    def write_if(self, label):
        label = self._function_label(label)
        self._write_many(['@SP', 'M=M-1', 'A=M', 'D=M', '@%s' % label,
                          'D;JNE'])

    def write_function(self, function_name, num_vars):
        self._function_label_name = function_name
        self._write_many(['(%s)' % function_name, 'D=0'])
        for _ in range(num_vars):
            self._write_many(['@SP', 'A=M', 'M=D', '@SP', 'M=M+1'])

    def write_call(self, function_name, num_args):
        label = self._return_label()
        self._write_many(['@%s' % label, 'D=A', '@SP', 'A=M', 'M=D', '@SP',
                          'M=M+1'])
        self._write_call_value('@LCL')
        self._write_call_value('@ARG')
        self._write_call_value('@THIS')
        self._write_call_value('@THAT')
        self._write_many(['@SP', 'D=M', '@5', 'D=D-A', '@%d' % num_args,
                          'D=D-A', '@ARG', 'M=D', '@SP', 'D=M', '@LCL', 'M=D',
                          '@%s' % function_name, '0;JMP', '(%s)' % label])

    def write_return(self):
        self._write_many(['@LCL', 'D=M', '@R13', 'M=D', '@5', 'D=A', '@R13',
                          'A=M-D', 'D=M', '@R14', 'M=D', '@SP', 'M=M-1', 'A=M',
                          'D=M', '@ARG', 'A=M', 'M=D', '@ARG', 'D=M+1', '@SP',
                          'M=D', '@R13', 'AM=M-1', 'D=M', '@THAT', 'M=D',
                          '@R13', 'AM=M-1', 'D=M', '@THIS', 'M=D', '@R13',
                          'AM=M-1', 'D=M', '@ARG', 'M=D', '@R13', 'AM=M-1',
                          'D=M', '@LCL', 'M=D', '@R14', 'A=M', '0;JMP'])

    def write_init(self):
        self._write_many(['@256', 'D=A', '@SP', 'M=D'])
        self.write_call('Sys.init', 0)

    def write_comment(self, command):
        self._write_one('// %s' % command)

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
        label1 = self._if_label()
        label2 = self._if_label()
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

    def _write_call_value(self, value):
        self._write_many([value, 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1'])

    def _write_one(self, code):
        self._asm_text += '%s\n' % code

    def _write_many(self, codes):
        for code in codes:
            self._write_one(code)

    def _if_label(self):
        self._if_label_count += 1
        return 'IF_LABEL_%d' % self._if_label_count

    def _return_label(self):
        self._return_label_count += 1
        return 'RETURN_LABEL_%d' % self._return_label_count

    def _function_label(self, label):
        if self._function_label_name == '':
            return '%s' % label
        else:
            return '%s$%s' % (self._function_label_name, label)
