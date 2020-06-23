class Type:
    KEYWORD = 'keyword'
    SYMBOL = 'symbol'
    IDENTIFIER = 'identifier'
    INT_CONST = 'integerConstant'
    STRING_CONST = 'stringConstant'


class Keyword:
    CLASS = 'class'
    CONSTRUCTOR = 'constructor'
    FUNCTION = 'function'
    METHOD = 'method'
    FIELD = 'field'
    STATIC = 'static'
    VAR = 'var'
    INT = 'int'
    CHAR = 'char'
    BOOLEAN = 'boolean'
    VOID = 'void'
    TRUE = 'true'
    FALSE = 'false'
    NULL = 'null'
    THIS = 'this'
    LET = 'let'
    DO = 'do'
    IF = 'if'
    ELSE = 'else'
    WHILE = 'while'
    RETURN = 'return'


class Symbol:
    LEFT_CURLY_BRACKET = '{'
    RIGHT_CURLY_BRACKET = '}'
    LEFT_ROUND_BRACKET = '('
    RIGHT_ROUND_BRACKET = ')'
    LEFT_BOX_BRACKET = '['
    RIGHT_BOX_BRACKET = ']'
    DOT = '.'
    COMMA = ','
    SEMI_COLON = ';'
    PLUS = '+'
    MINUS = '-'
    MULTI = '*'
    DIV = '/'
    AND = '&'
    PIPE = '|'
    LESS_THAN = '<'
    GREATER_THAN = '>'
    EQUAL = '='
    TILDE = '~'


class Kind:
    STATIC = 'static'
    FIELD = 'field'
    ARG = 'arg'
    VAR = 'var'


class Segment:
    CONST = 'constant'
    ARG = 'argument'
    LOCAL = 'local'
    STATIC = 'static'
    THIS = 'this'
    THAT = 'that'
    POINTER = 'pointer'
    TEMP = 'temp'


class Command:
    ADD = 'add'
    SUB = 'sub'
    NEG = 'neg'
    EQ = 'eq'
    GT = 'gt'
    LT = 'lt'
    AND = 'and'
    OR = 'or'
    NOT = 'not'
