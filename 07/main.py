import sys
from parser import Parser
from code_writer import CodeWriter
from constants import C_ARITHMETIC, C_PUSH, C_POP


def main():
    vm_filename = sys.argv[1]
    asm_filename = vm_filename.replace('.vm', '.asm')
    vm_file = open(vm_filename, 'r')
    asm_file = open(asm_filename, 'a')

    parser = Parser(vm_file)
    code_writer = CodeWriter(asm_file)

    while parser.has_more_commands():
        parser.advance()
        if parser.command_type() == C_ARITHMETIC:
            code_writer.write_arithmetic(parser.arg1())
        elif parser.command_type() == C_PUSH:
            code_writer.write_push_pop(C_PUSH, parser.arg1(), parser.arg2())
        elif parser.command_type() == C_POP:
            code_writer.write_push_pop(C_POP, parser.arg1(), parser.arg2())

    vm_file.close()
    code_writer.close()
