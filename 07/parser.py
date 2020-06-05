from constants import C_ARITHMETIC, C_PUSH, C_POP, C_FUNCTION, C_CALL, C_RETURN


class Parser:
    def __init__(self, file):
        self._file = file
        self._command = None
        self._command_type = {
            'add': C_ARITHMETIC,
            'sub': C_ARITHMETIC,
            'neg': C_ARITHMETIC,
            'eq': C_ARITHMETIC,
            'gt': C_ARITHMETIC,
            'lt': C_ARITHMETIC,
            'and': C_ARITHMETIC,
            'or': C_ARITHMETIC,
            'not': C_ARITHMETIC,
            'push': C_PUSH,
            'pop': C_POP
        }
        self._commands = self._commands_splited()

    def has_more_commands(self):
        return len(self._commands) > 0

    def advance(self):
        self._command = self._commands.pop(0)

    def command_type(self):
        return self._command_type[self._command_splited()[0]]

    def arg1(self):
        if self.command_type() != C_RETURN:
            if self.command_type() == C_ARITHMETIC:
                return self._command_splited()[0]
            else:
                return self._command_splited()[1]

    def arg2(self):
        if self.command_type() in [C_PUSH, C_POP, C_FUNCTION, C_CALL]:
            return int(self._command_splited()[2])

    def _vm_code(self):
        return self._file.read()

    def _clear_vm_code(self):
        new_vm_code = ''
        for line in self._vm_code().splitlines():
            line = line.strip()
            if line == '' or line[0:2] == '//':
                continue
            new_vm_code += line + '\n'
        return new_vm_code[0:-1]

    def _commands_splited(self):
        return self._clear_vm_code().splitlines()

    def _command_splited(self):
        return self._command.split()
