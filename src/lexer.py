"""
PLY-based lexer wrapped in a TokenScanner class.
Requires: ply (pip install ply)
"""
import ply.lex as lex
import re


class TokenScanner:
    """Lexical analyzer for scanning and tokenizing source code using PLY."""

    # keyword -> token name map
    keywords = {
        'if': 'IF', 'else': 'ELSE', 'while': 'WHILE', 'for': 'FOR',
        'int': 'INT', 'float': 'FLOAT', 'return': 'RETURN', 'print': 'PRINT'
    }

    # token names (must include all token names used by PLY)
    tokens = [
        'IDENTIFIER', 'INTEGER', 'DECIMAL',
        'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'MOD',
        'EQUALS', 'EQUAL_TO', 'NOT_EQUAL', 'LESS', 'LESS_EQ', 'GREATER', 'GREATER_EQ',
        'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'SEMICOLON', 'COMMA',
    ] + list(keywords.values())

    # simple tokens (single-char or simple regex); these will be compiled by PLY too
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_MULTIPLY = r'\*'
    t_DIVIDE = r'/'
    t_MOD = r'%'
    # NOTE: do NOT define single '=' here as a function is used for precedence below
    # t_EQUALS = r'='
    t_LESS = r'<'
    t_GREATER = r'>'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_SEMICOLON = r';'
    t_COMMA = r','
    t_ignore = ' \t'  # spaces and tabs ignored

    _code = ''
    scanner = None

    def __init__(self):
        self.token_stream = []
        self.issues = []
        self.initialize()

    def initialize(self):
        """Create the PLY lexer instance for this object."""
        
        self.scanner = lex.lex(module=self)

  
    def t_COMMENT_SINGLE(self, t):
        r'//.*'
        pass

    def t_COMMENT_MULTI(self, t):
        r'/\*(.|\n)*?\*/'
        t.lexer.lineno += t.value.count('\n')
        pass

  
    def t_EQUAL_TO(self, t):
        r'=='
        t.type = 'EQUAL_TO'
        return t

    def t_NOT_EQUAL(self, t):
        r'!='
        t.type = 'NOT_EQUAL'
        return t

    def t_LESS_EQ(self, t):
        r'<='
        t.type = 'LESS_EQ'
        return t

    def t_GREATER_EQ(self, t):
        r'>='
        t.type = 'GREATER_EQ'
        return t

    # Handle plain equals (assignment) as a function too, to be safe
    def t_EQUALS(self, t):
        r'='
        t.type = 'EQUALS'
        return t

    #
    # Numbers: decimal must be tested before integer (function order matters)
    #
    def t_DECIMAL(self, t):
        r'\d+\.\d+'
        try:
            t.value = float(t.value)
        except ValueError:
            self.issues.append(f"Invalid decimal literal '{t.value}' at line {t.lineno}")
            t.value = 0.0
        return t

    def t_INTEGER(self, t):
        r'\d+'
        try:
            t.value = int(t.value)
        except ValueError:
            self.issues.append(f"Invalid integer literal '{t.value}' at line {t.lineno}")
            t.value = 0
        return t

    #
    # Identifiers and keywords
    #
    def t_IDENTIFIER(self, t):
        r'[A-Za-z_][A-Za-z_0-9]*'
        if t.value in self.keywords:
            t.type = self.keywords[t.value]
        else:
            t.type = 'IDENTIFIER'
        return t

    #
    # Newlines: keep track of lineno
    #
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    #
    # Error handling
    #
    def t_error(self, t):
        ch = t.value[0]
        col = self._compute_column(t.lexpos)
        msg = f"Invalid character {ch!r} at line {t.lineno}, column {col}"
        self.issues.append(msg)
        t.lexer.skip(1)

    #
    # Utility: compute human readable column from lexpos using stored source
    #
    def _compute_column(self, lexpos):
        if not self._code:
            return lexpos
        last_nl = self._code.rfind('\n', 0, lexpos)
        if last_nl < 0:
            return lexpos + 1
        return lexpos - last_nl

    #
    # Main scanning API
    #
    def scan(self, code):
       
        # reset state
        self.token_stream = []
        self.issues = []
        self._code = code
        self.scanner.input(code)
        self.scanner.lineno = 1

        while True:
            tok = self.scanner.token()
            if not tok:
                break
            col = self._compute_column(tok.lexpos)
            self.token_stream.append({
                'kind': tok.type,
                'val': tok.value,
                'ln': tok.lineno,
                'col': col,
                'pos': tok.lexpos
            })

        return self.token_stream, self.issues


if __name__ == '__main__':
    sample = r'''
    // sample program
    int main() {
      int x;
      x = 10;
      x = x + 2 * (3 + 4);
      return x;
    }
    '''
    scanner = TokenScanner()
    toks, issues = scanner.scan(sample)
    print("TOKENS:")
    for t in toks:
        print(t)
    if issues:
        print("\nISSUES:")
        for it in issues:
            print(it)