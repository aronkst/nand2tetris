from constants import (Type, Keyword, Symbol)
from jack_tokenizer import JackTokenizer


class CompilationEngine():
    def __init__(self, jack_file, xml_file):
        self._jack_tokenizer = JackTokenizer(jack_file)
        self._xml_file = xml_file
        self._xml_text = ''

    def compile_class(self):
        self._write_start('class')
        self._compile_keyword()
        self._compile_identifier()
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
        self._compile_keyword()
        if self._what_next_token([Keyword.INT, Keyword.CHAR, Keyword.BOOLEAN]):
            self._compile_keyword()
        elif self._what_next_token_type([Type.IDENTIFIER]):
            self._compile_identifier()
        self._compile_identifier()
        while self._what_next_token([Symbol.COMMA]):
            self._compile_symbol()
            self._compile_identifier()
        self._compile_symbol()
        self._write_end('classVarDec')

    def compile_subroutine_dec(self):
        self._write_start('subroutineDec')
        self._compile_keyword()
        if self._what_next_token([Keyword.VOID]):
            self._compile_keyword()
        else:
            if self._what_next_token([Keyword.INT, Keyword.CHAR,
                                      Keyword.BOOLEAN]):
                self._compile_keyword()
            elif self._what_next_token_type([Type.IDENTIFIER]):
                self._compile_identifier()
        self._compile_identifier()
        self._compile_symbol()
        self.compile_parameter_list()
        self._compile_symbol()
        self.compile_subroutine_body()
        self._write_end('subroutineDec')

    def compile_parameter_list(self):
        self._write_start('parameterList')
        if (
               self._what_next_token([Keyword.INT, Keyword.CHAR,
                                      Keyword.BOOLEAN]) or
               self._what_next_token_type([Type.IDENTIFIER])
           ):
            if self._what_next_token([Keyword.INT, Keyword.CHAR,
                                      Keyword.BOOLEAN]):
                self._compile_keyword()
            elif self._what_next_token_type([Type.IDENTIFIER]):
                self._compile_identifier()
            self._compile_identifier()
            while self._what_next_token([Symbol.COMMA]):
                self._compile_symbol()
                if self._what_next_token([Keyword.INT, Keyword.CHAR,
                                          Keyword.BOOLEAN]):
                    self._compile_keyword()
                elif self._what_next_token_type([Type.IDENTIFIER]):
                    self._compile_identifier()
                self._compile_identifier()
        self._write_end('parameterList')

    def compile_subroutine_body(self):
        self._write_start('subroutineBody')
        self._compile_symbol()
        while self._what_next_token([Keyword.VAR]):
            self.compile_var_dec()
        self.compile_statements()
        self._compile_symbol()
        self._write_end('subroutineBody')

    def compile_var_dec(self):
        self._write_start('varDec')
        self._compile_keyword()
        if self._what_next_token([Keyword.INT, Keyword.CHAR, Keyword.BOOLEAN]):
            self._compile_keyword()
        elif self._what_next_token_type([Type.IDENTIFIER]):
            self._compile_identifier()
        self._compile_identifier()
        while self._what_next_token([Symbol.COMMA]):
            self._compile_symbol()
            self._compile_identifier()
        self._compile_symbol()
        self._write_end('varDec')

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
        self._compile_identifier()
        if self._what_next_token([Symbol.LEFT_BOX_BRACKET]):
            self._compile_symbol()
            self.compile_expression()
            self._compile_symbol()
        self._compile_symbol()
        self.compile_expression()
        self._compile_symbol()
        self._write_end('letStatement')

    def compile_if(self):
        self._write_start('ifStatement')
        self._compile_keyword()
        self._compile_symbol()
        self.compile_expression()
        self._compile_symbol()
        self._compile_symbol()
        self.compile_statements()
        self._compile_symbol()
        if self._what_next_token([Keyword.ELSE]):
            self._compile_keyword()
            self._compile_symbol()
            self.compile_statements()
            self._compile_symbol()
        self._write_end('ifStatement')

    def compile_while(self):
        self._write_start('whileStatement')
        self._compile_keyword()
        self._compile_symbol()
        self.compile_expression()
        self._compile_symbol()
        self._compile_symbol()
        self.compile_statements()
        self._compile_symbol()
        self._write_end('whileStatement')

    def compile_do(self):
        self._write_start('doStatement')
        self._compile_keyword()
        if self._what_next_token([Symbol.LEFT_ROUND_BRACKET], 1):
            self._compile_identifier()
            self._compile_symbol()
            self.compile_expression_list()
            self._compile_symbol()
        else:
            self._compile_identifier()
            self._compile_symbol()
            self._compile_identifier()
            self._compile_symbol()
            self.compile_expression_list()
            self._compile_symbol()
        self._compile_symbol()
        self._write_end('doStatement')

    def compile_return(self):
        self._write_start('returnStatement')
        self._compile_keyword()
        if not self._what_next_token([Symbol.SEMI_COLON]):
            self.compile_expression()
        self._compile_symbol()
        self._write_end('returnStatement')

    def compile_expression(self):
        self._write_start('expression')
        self.compile_term()
        while self._what_next_token([Symbol.PLUS, Symbol.MINUS, Symbol.MULTI,
                                     Symbol.DIV, Symbol.AND, Symbol.PIPE,
                                     Symbol.LESS_THAN, Symbol.GREATER_THAN,
                                     Symbol.EQUAL]):
            self._compile_symbol()
            self.compile_term()
        self._write_end('expression')

    def compile_term(self):
        self._write_start('term')
        if self._what_next_token_type([Type.INT_CONST]):
            self._compile_integer_constant()
        elif self._what_next_token_type([Type.STRING_CONST]):
            self._compile_string_constant()
        elif self._what_next_token([Keyword.NULL, Keyword.THIS, Keyword.TRUE,
                                    Keyword.FALSE]):
            self._compile_keyword()
        elif self._what_next_token_type([Type.IDENTIFIER]):
            if self._what_next_token([Symbol.LEFT_BOX_BRACKET], 1):
                self._compile_identifier()
                self._compile_symbol()
                self.compile_expression()
                self._compile_symbol()
            elif self._what_next_token([Symbol.LEFT_ROUND_BRACKET, Symbol.DOT],
                                       1):
                if self._what_next_token([Symbol.LEFT_ROUND_BRACKET], 1):
                    self._compile_identifier()
                    self._compile_symbol()
                    self.compile_expression_list()
                    self._compile_symbol()
                else:
                    self._compile_identifier()
                    self._compile_symbol()
                    self._compile_identifier()
                    self._compile_symbol()
                    self.compile_expression_list()
                    self._compile_symbol()
            else:
                self._compile_identifier()
        elif self._what_next_token([Symbol.LEFT_ROUND_BRACKET]):
            self._compile_symbol()
            self.compile_expression()
            self._compile_symbol()
        elif self._what_next_token([Symbol.TILDE, Symbol.MINUS]):
            self._compile_symbol()
            self.compile_term()
        self._write_end('term')

    def compile_expression_list(self):
        self._write_start('expressionList')
        if not self._what_next_token([Symbol.RIGHT_ROUND_BRACKET]):
            self.compile_expression()
            while self._what_next_token([Symbol.COMMA]):
                self._compile_symbol()
                self.compile_expression()
        self._write_end('expressionList')

    def save(self):
        self._xml_file.write(self._xml_text)

    def _what_next_token(self, values, index=0):
        return self._jack_tokenizer.next_token(index) in values

    def _what_next_token_type(self, values, index=0):
        return self._jack_tokenizer.next_token_type(index) in values

    def _compile_symbol(self):
        self._jack_tokenizer.advance()
        self._write('symbol', self._jack_tokenizer.token())

    def _compile_keyword(self):
        self._jack_tokenizer.advance()
        self._write('keyword', self._jack_tokenizer.token())

    def _compile_identifier(self):
        self._jack_tokenizer.advance()
        self._write('identifier', self._jack_tokenizer.token())

    def _compile_integer_constant(self):
        self._jack_tokenizer.advance()
        self._write('integerConstant', self._jack_tokenizer.token())

    def _compile_string_constant(self):
        self._jack_tokenizer.advance()
        self._write('stringConstant', self._jack_tokenizer.token())

    def _write(self, element, value):
        self._xml_text += '<{}> {} </{}>\n'.format(element, value, element)

    def _write_start(self, element):
        self._xml_text += '<%s>\n' % element

    def _write_end(self, element):
        self._xml_text += '</%s>\n' % element
