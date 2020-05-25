from pathlib import Path
from parser import Parser
from symbol_table import SymbolTable
from code import Code


def main():
    for path in Path('./../').rglob('*.asm'):
        filename = './' + str(path)
        new_filename = filename[0:-3] + 'hack'

        file = open(filename, 'r')
        text = file.read()
        file.close()

        parser = Parser(text)
        symbol_table = SymbolTable(parser.text)
        code = Code(parser.text, symbol_table.symbols)

        file = open(new_filename, 'a')
        file.write(code.text)
        file.close()


if __name__ == "__main__":
    main()
