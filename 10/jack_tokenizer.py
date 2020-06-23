import re
from constants import (Type, Keyword, Symbol)


class JackTokenizer():
    def __init__(self, jack_file):
        self._jack_file = jack_file
        self._line_contains_comment = False
        self._tokens = self._tokens_splited()
        self._token = None

    def has_more_tokens(self):
        return len(self._tokens) > 0

    def advance(self):
        if self.has_more_tokens():
            self._token = self._tokens.pop(0)

    def token_type(self):
        return self._token_type(self._token)

    def keywork(self):
        if self.token_type() == Type.KEYWORD:
            return self._token

    def symbol(self):
        if self.token_type() == Type.SYMBOL:
            if self._token == '&':
                return '&amp;'
            elif self._token == '<':
                return '&lt;'
            elif self._token == '>':
                return '&gt;'
            else:
                return self._token

    def int_val(self):
        if self.token_type() == Type.INT_CONST:
            return int(self._token)

    def string_val(self):
        if self.token_type() == Type.STRING_CONST:
            return self._token[1:-1]

    def indetifier(self):
        if self.token_type() == Type.IDENTIFIER:
            return self._token

    def token(self):
        if self.token_type() == Type.KEYWORD:
            return self.keywork()
        elif self.token_type() == Type.SYMBOL:
            return self.symbol()
        elif self.token_type() == Type.INT_CONST:
            return self.int_val()
        elif self.token_type() == Type.STRING_CONST:
            return self.string_val()
        else:
            return self.indetifier()

    def next_token(self, index=0):
        if len(self._tokens) > index:
            return self._tokens[index]

    def next_token_type(self, index=0):
        if len(self._tokens) > index:
            return self._token_type(self._tokens[index])

    def _token_type(self, token):
        if token in self._keyword_class_array():
            return Type.KEYWORD
        elif token in self._symbol_class_array():
            return Type.SYMBOL
        elif token.isnumeric():
            return Type.INT_CONST
        elif token.startswith('"') and token.endswith('"'):
            return Type.STRING_CONST
        else:
            return Type.IDENTIFIER

    def _jack_code(self):
        return self._jack_file.read()

    def _clear_jack_code(self):
        new_jack_code = ''
        for line in self._jack_code().splitlines():
            line = line.strip()
            if self._line_contains_comment:
                if '*/' in line:
                    self._line_contains_comment = False
                continue
            if line == '' or line[0:2] == '//':
                continue
            if '/*' in line and '*/' in line:
                continue
            if '/*' in line:
                self._line_contains_comment = True
                continue
            if '//' in line:
                line = line.split('//')[0]
            line = line.strip()
            new_jack_code += '%s\n' % line
        return new_jack_code[0:-1]

    def _tokens_splited(self):
        regex = '(\bclass\b|\bconstructor\b|\bfunction\b|\bmethod\b|' \
            '\bfield\b|\bstatic\b|\bvar\b|\bint\b|\bchar\b|\bboolean\b|' \
            '\bvoid\b|\btrue\b|\bfalse\b|\bnull\b|\bthis\b|\blet\b|' \
            '\bdo\b|\bif\b|\belse\b|\bwhile\b|\breturn\b|\\{|\\}|\\(|' \
            '\\)|\\[|\\]|\\.|\\,|\\;|\\+|\\-|\\*|\\/|\\&|\\||\\<|\\>|' \
            '\\=|\\~|\\ |".*?"|\n)'
        pattern = re.compile(regex)
        tokens = re.split(pattern, self._clear_jack_code())
        tokens = list(filter(lambda t: t != '', tokens))
        tokens = list(filter(lambda t: t != ' ', tokens))
        tokens = list(filter(lambda t: t != '\n', tokens))
        return tokens

    def _keyword_class_array(self):
        return [value for name, value in vars(Keyword).items()
                if not name.startswith('_')]

    def _symbol_class_array(self):
        return [value for name, value in vars(Symbol).items()
                if not name.startswith('_')]
