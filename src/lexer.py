import re
from dataclasses import dataclass

KEYWORDS = {'int', 'return', 'if', 'else', 'while'}

TOKEN_SPEC = [
    ('WHITESPACE', r'[ \t\r\n]+'),
    ('COMMENT',    r'//.*|/\*[\s\S]*?\*/'),
    ('INT',        r'\d+'),
    ('IDENT',      r'[A-Za-z_][A-Za-z0-9_]*'),
    ('OP',         r'==|!=|<=|>=|\+\+|--|&&|\|\||[+\-*/%<>=!&|^~]'),
    ('PUNC',       r'[(){},;\[\]]'),
    ('STRING',     r'"([^"\\]|\\.)*"'),
    ('MISMATCH',   r'.'),
]

TOKEN_RE = re.compile('|'.join(f'(?P<{n}>{p})' for n, p in TOKEN_SPEC), re.MULTILINE)

@dataclass
class Token:
    kind: str
    value: str
    line: int
    col: int

def tokenize(text):
    line = 1
    col = 1
    pos = 0
    while pos < len(text):
        m = TOKEN_RE.match(text, pos)
        if not m:
            raise SyntaxError(f'Unexpected char at {line}:{col}')
        kind = m.lastgroup
        val = m.group(kind)
        if kind == 'WHITESPACE':
            nl = val.count('\n')
            if nl:
                line += nl
                col = len(val.rsplit('\n', 1)[-1]) + 1
            else:
                col += len(val)
        elif kind == 'COMMENT':
            nl = val.count('\n')
            if nl:
                line += nl
                col = len(val.rsplit('\n', 1)[-1]) + 1
            else:
                col += len(val)
        elif kind == 'IDENT':
            if val in KEYWORDS:
                yield Token('KW', val, line, col)
            else:
                yield Token('IDENT', val, line, col)
            col += len(val)
        elif kind == 'INT':
            yield Token('INT', val, line, col)
            col += len(val)
        elif kind == 'OP':
            yield Token('OP', val, line, col)
            col += len(val)
        elif kind == 'PUNC':
            yield Token('PUNC', val, line, col)
            col += len(val)
        elif kind == 'STRING':
            yield Token('STRING', val, line, col)
            col += len(val)
        elif kind == 'MISMATCH':
            raise SyntaxError(f'Unexpected token {val!r} at {line}:{col}')
        pos = m.end()
    yield Token('EOF', '', line, col)