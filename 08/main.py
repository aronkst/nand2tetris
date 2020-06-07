import glob
import os
import sys
from code_writer import CodeWriter
from constants import (C_ARITHMETIC, C_PUSH, C_POP, C_LABEL, C_GOTO, C_IF,
                       C_FUNCTION, C_RETURN, C_CALL)
from parser import Parser


def main():
    argument = sys.argv[1]
    if argument.endswith('.vm'):
        asm_filename = argument.replace('.vm', '.asm')
        asm_file = open(asm_filename, 'a')
        code_writer = CodeWriter(asm_file)
        open_vm_file(argument, code_writer)
        code_writer.close()
    else:
        if argument.endswith('/'):
            argument = argument[0:-1]
        foldername = os.path.basename(argument)
        asm_file = open('%s/%s.asm' % (argument, foldername), 'a')
        code_writer = CodeWriter(asm_file)
        code_writer.write_comment('write init')
        code_writer.write_init()
        files = glob.glob('%s/*.vm' % argument)
        for file in files:
            open_vm_file(file, code_writer)
        code_writer.close()


def open_vm_file(vm_filename, code_writer):
    vm_file = open(vm_filename, 'r')
    name = os.path.basename(vm_file.name).split('.')[0]
    code_writer.set_file_name(name)
    parser = Parser(vm_file)
    while parser.has_more_commands():
        parser.advance()
        code_writer.write_comment(parser.comment())
        if parser.command_type() == C_ARITHMETIC:
            code_writer.write_arithmetic(parser.arg1())
        elif parser.command_type() == C_PUSH:
            code_writer.write_push(parser.arg1(), parser.arg2())
        elif parser.command_type() == C_POP:
            code_writer.write_pop(parser.arg1(), parser.arg2())
        elif parser.command_type() == C_LABEL:
            code_writer.write_label(parser.arg1())
        elif parser.command_type() == C_GOTO:
            code_writer.write_goto(parser.arg1())
        elif parser.command_type() == C_IF:
            code_writer.write_if(parser.arg1())
        elif parser.command_type() == C_FUNCTION:
            code_writer.write_function(parser.arg1(), parser.arg2())
        elif parser.command_type() == C_CALL:
            code_writer.write_call(parser.arg1(), parser.arg2())
        elif parser.command_type() == C_RETURN:
            code_writer.write_return()
    parser.close()
