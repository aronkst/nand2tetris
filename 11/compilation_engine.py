from constants import (Type, Keyword, Symbol, Segment, Kind, Command)
from jack_tokenizer import JackTokenizer
from symbol_table import SymbolTable
from vm_writer import VmWriter


class CompilationEngine():
    def __init__(self, jack_file, vm_file):
        self._jack_tokenizer = JackTokenizer(jack_file)
        self._vm_file = vm_file
        self._vm_text = ''
        self._xml_text = ''
        self._symbol_table = SymbolTable()
        self._vm_writer = VmWriter(self._vm_file)
        self._class_name = None
        self._label_count = 0
        self._compiled_class_name = ''

    def compile_class(self):
        self._write_start('class')
        self._compile_keyword()
        self._write('IdentifierInfo', 'category: class')
        self._compiled_class_name = self._compile_identifier()
        self._compile_symbol()
        while self._what_next_token([Keyword.STATIC, Keyword.FIELD]):
            self.compile_class_var_dec()
        while self._what_next_token([Keyword.CONSTRUCTOR, Keyword.FUNCTION,
                                     Keyword.METHOD]):
            self.compile_subroutine_dec()
        self._compile_symbol()
        self._write_end('class')

    def compile_class_var_dec(self):
        self._write_start('classVarDec')
        token = self._compile_keyword()
        kind = None
        if token == Keyword.STATIC:
            kind = Kind.STATIC
        elif token == Keyword.FIELD:
            kind = Kind.FIELD
        type_token = self._jack_tokenizer.next_token()
        if self._what_next_token([Keyword.INT, Keyword.CHAR, Keyword.BOOLEAN]):
            self._compile_keyword()
        else:
            self._write('IdentifierInfo', 'category: class')
            self._compile_identifier()
        self._compile_var_name(declaration=True, type=type_token, kind=kind)
        while self._what_next_token([Symbol.COMMA]):
            self._compile_symbol()
            self._compile_var_name(declaration=True, type=type_token,
                                   kind=kind)
        self._compile_symbol()
        self._write_end('classVarDec')

    def compile_subroutine_dec(self):
        self._symbol_table.start_subroutine()
        self._write_start('subroutineDec')
        token = self._compile_keyword()
        if self._jack_tokenizer.next_token() == Keyword.VOID:
            self._compile_keyword()
        else:
            self._jack_tokenizer.next_token()
            if self._what_next_token([Keyword.INT, Keyword.CHAR,
                                      Keyword.BOOLEAN]):
                self._compile_keyword()
            else:
                self._write('IdentifierInfo', 'category: class')
                self._compile_identifier()
        self._write('IdentifierInfo', 'category: subroutine')
        subroutine_name = self._compile_identifier()
        self._compile_symbol()
        if token == Keyword.METHOD:
            self._symbol_table.define('$this', self._compiled_class_name,
                                      Kind.ARG)
        self.compile_parameter_list()
        self._compile_symbol()
        self.compile_subroutine_body(subroutine_name, token)
        self._write_end('subroutineDec')

    def compile_parameter_list(self):
        self._write_start('parameterList')
        if (
                self._jack_tokenizer.next_token() in [Keyword.INT,
                                                      Keyword.CHAR,
                                                      Keyword.BOOLEAN] or
                self._jack_tokenizer.next_token_type() == Type.IDENTIFIER
           ):
            type_token = self._jack_tokenizer.next_token()
            if self._what_next_token([Keyword.INT, Keyword.CHAR,
                                      Keyword.BOOLEAN]):
                self._compile_keyword()
            else:
                self._write('IdentifierInfo', 'category: class')
                self._compile_identifier()
            self._compile_var_name(declaration=True, type=type_token,
                                   kind=Kind.ARG)
            while self._what_next_token([Symbol.COMMA]):
                self._compile_symbol()
                type_token = self._jack_tokenizer.next_token()
                if self._what_next_token([Keyword.INT, Keyword.CHAR,
                                          Keyword.BOOLEAN]):
                    self._compile_keyword()
                else:
                    self._write('IdentifierInfo', 'category: class')
                    self._compile_identifier()
                self._compile_var_name(declaration=True, type=type_token,
                                       kind=Kind.ARG)
        self._write_end('parameterList')

    def compile_subroutine_body(self, subroutine_name, subroutine_token):
        self._write_start('subroutineBody')
        self._compile_symbol()
        local_num = 0
        while self._what_next_token([Keyword.VAR]):
            var_num = self.compile_var_dec()
            local_num += var_num
        self._vm_writer.write_function(
            '%s.%s' % (self._compiled_class_name, subroutine_name),
            local_num
        )
        if subroutine_token == Keyword.METHOD:
            self._vm_writer.write_push(Segment.ARG, 0)
            self._vm_writer.write_pop(Segment.POINTER, 0)
        elif subroutine_token == Keyword.CONSTRUCTOR:
            self._vm_writer.write_push(
                Segment.CONST,
                self._symbol_table.var_count(Kind.FIELD)
            )
            self._vm_writer.write_call('Memory.alloc', 1)
            self._vm_writer.write_pop(Segment.POINTER, 0)
        elif subroutine_token == Keyword.FUNCTION:
            pass
        self.compile_statements()
        self._compile_symbol()
        self._write_end('subroutineBody')
        return local_num

    def compile_var_dec(self):
        self._write_start('varDec')
        self._compile_keyword()
        type_token = self._jack_tokenizer.next_token()
        if self._what_next_token([Keyword.INT, Keyword.CHAR, Keyword.BOOLEAN]):
            self._compile_keyword()
        else:
            self._write('IdentifierInfo', 'category: class')
            self._compile_identifier()
        self._compile_var_name(declaration=True, type=type_token,
                               kind=Kind.VAR)
        var_num = 1  # TODO
        while self._what_next_token([Symbol.COMMA]):
            self._compile_symbol()
            self._compile_var_name(declaration=True, type=type_token,
                                   kind=Kind.VAR)
            var_num += 1
        self._compile_symbol()
        self._write_end('varDec')
        return var_num

    def compile_statements(self):
        self._write_start('statements')
        while self._what_next_token([Keyword.LET, Keyword.IF, Keyword.WHILE,
                                     Keyword.DO, Keyword.RETURN]):
            if self._what_next_token([Keyword.LET]):
                self.compile_let()
            elif self._what_next_token([Keyword.IF]):
                self.compile_if()
            elif self._what_next_token([Keyword.WHILE]):
                self.compile_while()
            elif self._what_next_token([Keyword.DO]):
                self.compile_do()
            elif self._what_next_token([Keyword.RETURN]):
                self.compile_return()
        self._write_end('statements')

    def compile_let(self):
        self._write_start('letStatement')
        self._compile_keyword()
        let_var = self._compile_var_name(let=True)
        if self._what_next_token([Symbol.LEFT_BOX_BRACKET]):
            self._compile_symbol()
            self.compile_expression()
            self._compile_symbol()
            self._compile_symbol()
            kind = self._symbol_table.kind_of(let_var)
            if kind == Kind.ARG:
                self._vm_writer.write_push(
                    Segment.ARG,
                    self._symbol_table.index_of(let_var)
                )
            elif kind == Kind.VAR:
                self._vm_writer.write_push(
                    Segment.LOCAL,
                    self._symbol_table.index_of(let_var)
                )
            elif kind == Kind.FIELD:
                self._vm_writer.write_push(
                    Segment.THIS,
                    self._symbol_table.index_of(let_var)
                )
            elif kind == Kind.STATIC:
                self._vm_writer.write_push(
                    Segment.STATIC,
                    self._symbol_table.index_of(let_var)
                )
            self._vm_writer.write_arithmetic(Command.ADD)
            self._vm_writer.write_pop(Segment.TEMP, 2)
            self.compile_expression()
            self._vm_writer.write_push(Segment.TEMP, 2)
            self._vm_writer.write_pop(Segment.POINTER, 1)
            self._vm_writer.write_pop(Segment.THAT, 0)
            self._compile_symbol()
        else:
            self._compile_symbol()
            self.compile_expression()
            self._compile_symbol()
            kind = self._symbol_table.kind_of(let_var)
            if kind == Kind.VAR:
                self._vm_writer.write_pop(
                    Segment.LOCAL,
                    self._symbol_table.index_of(let_var)
                )
            elif kind == Kind.ARG:
                self._vm_writer.write_pop(
                    Segment.ARG,
                    self._symbol_table.index_of(let_var)
                )
            elif kind == Kind.FIELD:
                self._vm_writer.write_pop(
                    Segment.THIS,
                    self._symbol_table.index_of(let_var)
                )
            elif kind == Kind.STATIC:
                self._vm_writer.write_pop(
                    Segment.STATIC,
                    self._symbol_table.index_of(let_var)
                )
        self._write_end('letStatement')

    def compile_if(self):
        self._write_start('ifStatement')
        self._compile_keyword()
        self._compile_symbol()
        self.compile_expression()
        self._compile_symbol()
        self._vm_writer.write_arithmetic(Command.NOT)
        l1 = self._new_label()
        l2 = self._new_label()
        self._vm_writer.write_if(l1)
        self._compile_symbol()
        self.compile_statements()
        self._compile_symbol()
        self._vm_writer.write_goto(l2)
        self._vm_writer.write_label(l1)
        if self._what_next_token([Keyword.ELSE]):
            self._compile_keyword()
            self._compile_symbol()
            self.compile_statements()
            self._compile_symbol()
        self._vm_writer.write_label(l2)
        self._write_end('ifStatement')

    def compile_while(self):
        self._write_start('whileStatement')
        l1 = self._new_label()
        l2 = self._new_label()
        self._compile_keyword()
        self._vm_writer.write_label(l1)
        self._compile_symbol()
        self.compile_expression()
        self._compile_symbol()
        self._vm_writer.write_arithmetic(Command.NOT)
        self._vm_writer.write_if(l2)
        self._compile_symbol()
        self.compile_statements()
        self._compile_symbol()
        self._vm_writer.write_goto(l1)
        self._vm_writer.write_label(l2)
        self._write_end('whileStatement')

    def compile_do(self):
        self._write_start('doStatement')
        self._compile_keyword()
        if self._what_next_token([Symbol.LEFT_ROUND_BRACKET], 1):
            self._write('IdentifierInfo', 'category: subroutine')
            subroutine_name = self._compile_identifier()
            self._compile_symbol()
            self._vm_writer.write_push(Segment.POINTER, 0)
            arg_num = self.compile_expression_list()
            self._compile_symbol()
            self._vm_writer.write_call(
                '%s.%s' % (self._compiled_class_name, subroutine_name),
                arg_num + 1
            )
        else:
            identifier_str = self._jack_tokenizer.next_token()
            if self._symbol_table.kind_of(identifier_str):
                instance_name = self._compile_var_name(call=True)
                self._compile_symbol()
                self._write('IdentifierInfo', 'category: subroutine')
                subroutine_name = self._compile_identifier()
                self._compile_symbol()
                kind = self._symbol_table.kind_of(instance_name)
                if kind == Kind.ARG:
                    self._vm_writer.write_push(
                        Segment.ARG,
                        self._symbol_table.index_of(instance_name)
                    )
                elif kind == Kind.VAR:
                    self._vm_writer.write_push(
                        Segment.LOCAL,
                        self._symbol_table.index_of(instance_name)
                    )
                elif kind == Kind.FIELD:
                    self._vm_writer.write_push(
                        Segment.THIS,
                        self._symbol_table.index_of(instance_name)
                    )
                elif kind == Kind.STATIC:
                    self._vm_writer.write_push(
                        Segment.STATIC,
                        self._symbol_table.index_of(instance_name)
                    )
                arg_num = self.compile_expression_list()
                self._compile_symbol()
                self._vm_writer.write_call(
                    '%s.%s' % (
                        self._symbol_table.type_of(instance_name),
                        subroutine_name
                    ),
                    arg_num + 1
                )
            else:
                self._write('IdentifierInfo', 'category: class')
                class_name = self._compile_identifier()
                self._compile_symbol()
                self._write('IdentifierInfo', 'category: subroutine')
                subroutine_name = self._compile_identifier()
                self._compile_symbol()
                arg_num = self.compile_expression_list()
                self._compile_symbol()
                self._vm_writer.write_call(
                    '%s.%s' % (class_name, subroutine_name),
                    arg_num
                )
        self._compile_symbol()
        self._write_end('doStatement')
        self._vm_writer.write_pop(Segment.TEMP, 0)

    def compile_return(self):
        self._write_start('returnStatement')
        self._compile_keyword()
        if not self._what_next_token([Symbol.SEMI_COLON]):
            self.compile_expression()
        else:
            self._vm_writer.write_push(Segment.CONST, 0)
        self._compile_symbol()
        self._vm_writer.write_return()
        self._write_end('returnStatement')

    def compile_expression(self):
        self._write_start('expression')
        self.compile_term()
        while self._what_next_token([Symbol.PLUS, Symbol.MINUS, Symbol.MULTI,
                                     Symbol.DIV, Symbol.AND, Symbol.PIPE,
                                     Symbol.LESS_THAN, Symbol.GREATER_THAN,
                                     Symbol.EQUAL]):
            token = self._compile_symbol()
            self.compile_term()
            if token == Symbol.PLUS:
                self._vm_writer.write_arithmetic(Command.ADD)
            elif token == Symbol.MINUS:
                self._vm_writer.write_arithmetic(Command.SUB)
            elif token == Symbol.MULTI:
                self._vm_writer.write_call('Math.multiply', 2)
            elif token == Symbol.DIV:
                self._vm_writer.write_call('Math.divide', 2)
            elif token == Symbol.AND:
                self._vm_writer.write_arithmetic(Command.AND)
            elif token == Symbol.PIPE:
                self._vm_writer.write_arithmetic(Command.OR)
            elif token == Symbol.LESS_THAN:
                self._vm_writer.write_arithmetic(Command.LT)
            elif token == Symbol.GREATER_THAN:
                self._vm_writer.write_arithmetic(Command.GT)
            elif token == Symbol.EQUAL:
                self._vm_writer.write_arithmetic(Command.EQ)
        self._write_end('expression')

    def compile_term(self):
        self._write_start('term')
        if self._what_next_token_type([Type.INT_CONST]):
            value = self._compile_integer_constant()
            self._vm_writer.write_push(Segment.CONST, value)
        elif self._what_next_token_type([Type.STRING_CONST]):
            value = self._compile_string_constant()
            self._vm_writer.write_push(Segment.CONST, len(value))
            self._vm_writer.write_call('String.new', 1)
            for v in value:
                self._vm_writer.write_push(Segment.CONST, ord(v))
                self._vm_writer.write_call('String.appendChar', 2)
        elif self._what_next_token([Keyword.NULL]):
            self._compile_keyword()
            self._vm_writer.write_push(Segment.CONST, 0)
        elif self._what_next_token([Keyword.THIS]):
            self._compile_keyword()
            self._vm_writer.write_push(Segment.POINTER, 0)
        elif self._what_next_token([Keyword.TRUE]):
            self._compile_keyword()
            self._vm_writer.write_push(Segment.CONST, 0)
            self._vm_writer.write_arithmetic(Command.NOT)
        elif self._what_next_token([Keyword.FALSE]):
            self._compile_keyword()
            self._vm_writer.write_push(Segment.CONST, 0)
        elif self._what_next_token_type([Type.IDENTIFIER]):
            if self._what_next_token([Symbol.LEFT_BOX_BRACKET], 1):
                self._compile_var_name()
                self._compile_symbol()
                self.compile_expression()
                self._vm_writer.write_arithmetic(Command.ADD)
                self._vm_writer.write_pop(Segment.POINTER, 1)
                self._vm_writer.write_push(Segment.THAT, 0)
                self._compile_symbol()
            elif self._what_next_token([Symbol.LEFT_ROUND_BRACKET, Symbol.DOT],
                                       1):
                if self._what_next_token([Symbol.LEFT_ROUND_BRACKET], 1):
                    self._write('IdentifierInfo', 'category: subroutine')
                    subroutine_name = self._compile_identifier()
                    self._compile_symbol()
                    self._vm_writer.write_push(Segment.POINTER, 0)
                    arg_num = self.compile_expression_list()
                    self._compile_symbol()
                    self._vm_writer.write_call(
                        '%s.%s' % (self._compiled_class_name, subroutine_name),
                        arg_num + 1
                    )
                else:
                    identifier_str = self._jack_tokenizer.next_token()
                    if self._symbol_table.kind_of(identifier_str):
                        instance_name = self._compile_var_name(call=True)
                        self._compile_symbol()
                        self._write('IdentifierInfo', 'category: subroutine')
                        subroutine_name = self._compile_identifier()
                        self._compile_symbol()
                        kind = self._symbol_table.kind_of(instance_name)
                        if kind == Kind.ARG:
                            self._vm_writer.write_push(
                                Segment.ARG,
                                self._symbol_table.index_of(instance_name)
                            )
                        elif kind == Kind.VAR:
                            self._vm_writer.write_push(
                                Segment.LOCAL,
                                self._symbol_table.index_of(instance_name)
                            )
                        elif kind == Kind.FIELD:
                            self._vm_writer.write_push(
                                Segment.THIS,
                                self._symbol_table.index_of(instance_name)
                            )
                        elif kind == Kind.STATIC:
                            self._vm_writer.write_push(
                                Segment.STATIC,
                                self._symbol_table.index_of(instance_name)
                            )
                        arg_num = self.compile_expression_list()
                        self._compile_symbol()
                        self._vm_writer.write_call(
                            '%s.%s' % (
                                self._symbol_table.type_of(instance_name),
                                subroutine_name
                            ),
                            arg_num + 1
                        )
                    else:
                        self._write('IdentifierInfo', 'category: class')
                        class_name = self._compile_identifier()
                        self._compile_symbol()
                        self._write('IdentifierInfo', 'category: subroutine')
                        subroutine_name = self._compile_identifier()
                        self._compile_symbol()
                        arg_num = self.compile_expression_list()
                        self._compile_symbol()
                        self._vm_writer.write_call(
                            '%s.%s' % (class_name, subroutine_name),
                            arg_num
                        )
            else:
                self._compile_var_name()
        elif self._what_next_token([Symbol.LEFT_ROUND_BRACKET]):
            self._compile_symbol()
            self.compile_expression()
            self._compile_symbol()
        elif self._what_next_token([Symbol.TILDE]):
            self._compile_symbol()
            self.compile_term()
            self._vm_writer.write_arithmetic(Command.NOT)
        elif self._what_next_token([Symbol.MINUS]):
            self._compile_symbol()
            self.compile_term()
            self._vm_writer.write_arithmetic(Command.NEG)
        self._write_end('term')

    def compile_expression_list(self):
        self._write_start('expressionList')
        arg_num = 0
        if not self._what_next_token([Symbol.RIGHT_ROUND_BRACKET]):
            self.compile_expression()
            arg_num += 1
            while self._what_next_token([Symbol.COMMA]):
                self._compile_symbol()
                self.compile_expression()
                arg_num += 1
        self._write_end('expressionList')
        return arg_num

    def save(self):
        self._vm_writer.save()

    def _what_next_token(self, values, index=0):
        return self._jack_tokenizer.next_token(index) in values

    def _what_next_token_type(self, values, index=0):
        return self._jack_tokenizer.next_token_type(index) in values

    def _compile_symbol(self):
        self._jack_tokenizer.advance()
        value = self._jack_tokenizer.token()
        self._write('symbol', value)
        return value

    def _compile_keyword(self):
        self._jack_tokenizer.advance()
        value = self._jack_tokenizer.token()
        self._write('keyword', value)
        return value

    def _compile_identifier(self):
        self._jack_tokenizer.advance()
        value = self._jack_tokenizer.token()
        self._write('identifier', value)
        return value

    def _compile_integer_constant(self):
        self._jack_tokenizer.advance()
        value = self._jack_tokenizer.token()
        self._write('integerConstant', value)
        return value

    def _compile_string_constant(self):
        self._jack_tokenizer.advance()
        value = self._jack_tokenizer.token()
        self._write('stringConstant', value)
        return value

    def _compile_var_name(self, declaration=False, type=None, kind=None,
                          let=False, call=False):
        if declaration:
            self._symbol_table.define(self._jack_tokenizer.next_token(), type,
                                      kind)
        elif let:
            pass
        elif call:
            pass
        else:
            kind = self._symbol_table.kind_of(
                self._jack_tokenizer.next_token()
            )
            if kind == Kind.ARG:
                self._vm_writer.write_push(
                    Segment.ARG,
                    self._symbol_table.index_of(
                        self._jack_tokenizer.next_token()
                    )
                )
            elif kind == Kind.VAR:
                self._vm_writer.write_push(
                    Segment.LOCAL,
                    self._symbol_table.index_of(
                        self._jack_tokenizer.next_token()
                    )
                )
            elif kind == Kind.FIELD:
                self._vm_writer.write_push(
                    Segment.THIS,
                    self._symbol_table.index_of(
                        self._jack_tokenizer.next_token()
                    )
                )
            elif kind == Kind.STATIC:
                self._vm_writer.write_push(
                    Segment.STATIC,
                    self._symbol_table.index_of(
                        self._jack_tokenizer.next_token()
                    )
                )

        self._write(
            'IdentifierInfo',
            'declaration: %s, kind: %s, index: %d' % (
                declaration,
                self._symbol_table.kind_of(self._jack_tokenizer.next_token()),
                self._symbol_table.index_of(self._jack_tokenizer.next_token())
            )
        )
        return self._compile_identifier()

    def _write(self, element, value):
        self._xml_text += '<{}> {} </{}>\n'.format(element, value, element)

    def _write_start(self, element):
        self._xml_text += '<%s>\n' % element

    def _write_end(self, element):
        self._xml_text += '</%s>\n' % element

    def _new_label(self):
        self._label_count += 1
        return 'LABEL_%d' % self._label_count
