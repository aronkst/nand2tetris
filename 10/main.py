import glob
import sys
from compilation_engine import CompilationEngine


def main():
    argument = sys.argv[1]
    if argument.endswith('.jack'):
        load_file(argument)
    else:
        if argument.endswith('/'):
            argument = argument[0:-1]
        files = glob.glob('%s/*.jack' % argument)
        for file in files:
            load_file(file)


def load_file(jack_filename):
    jack_file = open(jack_filename, 'r')
    xml_filename = jack_filename.replace('.jack', '.xml')
    xml_file = open(xml_filename, 'a')
    compilation_engine = CompilationEngine(jack_file, xml_file)
    compilation_engine.compile_class()
    compilation_engine.save()
    jack_file.close()
    xml_file.close()
