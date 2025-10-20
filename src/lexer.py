"""
Improved PLY-based lexer wrapped in a TokenScanner class.

Notes / changes made compared to the original:
- Reworked important tokens (==, !=, <=, >=, decimal) as functions so PLY preserves correct matching order.
- Kept comment rules as functions so comment patterns take precedence over the DIVIDE token.
- Track the input source in self._code so we can compute column (human-friendly) positions.
- t_error now reports line and column and appends a clear message to self.issues.
- tokenize() renamed to scan() (keeps your API) and returns tokens with 'kind','val','ln','col','pos'.
- Defensive: initialize() constructs the lexer once. initialize() is called automatically from __init__.
- Added example usage in the docstring below.

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

    # state to hold the last scanned source text so we can compute columns
    _code = ''
    scanner = None

    def __init__(self):
        self.token_stream = []
        self.issues = []
        # Build lexer
        self.initialize()

    def initialize(self):
        """Create the PLY lexer instance for this object."""
        # PLY will inspect 'self' for t_* attributes and tokens list.
        # Using lex.lex(module=self) is supported.
        self.scanner = lex.lex(module=self)

    #
    # Comment rules: functions so they take precedence over the DIVIDE token
    #
    def t_COMMENT_SINGLE(self, t):
        r'//.*'
        # ignore single line comments; update line number handled by newline rule if present in comment
        pass

    def t_COMMENT_MULTI(self, t):
        r'/\*(.|\n)*?\*/'
        # update line number to account for newlines inside the comment
        t.lexer.lineno += t.value.count('\n')
        pass

    #
    # Multi-character / precedence-critical tokens (functions to guarantee ordering)
    #
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
        # map reserved words to token types
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
        # newlines are not returned as tokens

    #
    # Error handling
    #
    def t_error(self, t):
        # t is a LexToken; t.value is the rest of the input string starting at lexpos
        ch = t.value[0]
        # compute column
        col = self._compute_column(t.lexpos)
        msg = f"Invalid character {ch!r} at line {t.lineno}, column {col}"
        self.issues.append(msg)
        # skip the offending character and continue
        t.lexer.skip(1)

    #
    # Utility: compute human readable column from lexpos using stored source
    #
    def _compute_column(self, lexpos):
        if not self._code:
            return lexpos
        # lexpos is index in the input string
        last_nl = self._code.rfind('\n', 0, lexpos)
        if last_nl < 0:
            return lexpos + 1
        return lexpos - last_nl

    #
    # Main scanning API
    #
    def scan(self, code):
        """
        Scan source code and return token stream plus any lexing issues.

        Returns:
            (token_stream, issues)
            token_stream: list of dicts with keys:
               - kind: token type name (e.g. 'IDENTIFIER', 'INT', 'PLUS', 'IF', ...)
               - val: token value (int/float/str)
               - ln: line number (1-based)
               - col: column number (1-based)
               - pos: lexpos (0-based index into the source)
        """
        # reset state
        self.token_stream = []
        self.issues = []
        self._code = code
        self.scanner.input(code)
        # ensure line numbers start at 1
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
    # quick manual test / demo
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