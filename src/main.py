#!/usr/bin/env python3
import argparse
import sys
from lexer import TokenScanner
from parser import SyntaxProcessor


def run_file(path, show_tokens=True, show_ir=True, show_ast=True, show_symbols=True):
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()

    scanner = TokenScanner()
    tokens, lex_issues = scanner.scan(code)

    if show_tokens:
        print('--- LEXER TOKENS ---')
        for t in tokens:
            print(f"{t['ln']:4}:{t['col']:3} {t['kind']:12} {t['val']!r}")
        print()

    if lex_issues:
        print('--- LEXER ISSUES ---')
        for it in lex_issues:
            print(it)
        print()

    proc = SyntaxProcessor()
    parse_result = proc.process(code)

    if proc.issues:
        print('--- PARSER / SEMANTIC ISSUES ---')
        for it in proc.issues:
            print(it)
        print()

    if show_ir:
        print('--- INTERMEDIATE REPRESENTATION (IR) ---')
        for i, instr in enumerate(proc.ir_instructions):
            print(f"{i:04}: {instr}")
        print()

    if show_ast:
        print('--- PARSE RESULT / AST (top-level) ---')
        print(parse_result)
        print()

    if show_symbols:
        print('--- SYMBOL TABLE DUMP ---')
        # uses the registry instance inside the SyntaxProcessor
        proc.registry.show(include_values=True)
        print()


def run_stdin(show_tokens=True, show_ir=True, show_ast=True, show_symbols=True):
    code = sys.stdin.read()
    # PLY needs the lexer/parser initialized per module; reuse run_file logic by writing to a temp path is unnecessary:
    scanner = TokenScanner()
    tokens, lex_issues = scanner.scan(code)

    if show_tokens:
        print('--- LEXER TOKENS ---')
        for t in tokens:
            print(f"{t['ln']:4}:{t['col']:3} {t['kind']:12} {t['val']!r}")
        print()

    if lex_issues:
        print('--- LEXER ISSUES ---')
        for it in lex_issues:
            print(it)
        print()

    proc = SyntaxProcessor()
    parse_result = proc.process(code)

    if proc.issues:
        print('--- PARSER / SEMANTIC ISSUES ---')
        for it in proc.issues:
            print(it)
        print()

    if show_ir:
        print('--- INTERMEDIATE REPRESENTATION (IR) ---')
        for i, instr in enumerate(proc.ir_instructions):
            print(f"{i:04}: {instr}")
        print()

    if show_ast:
        print('--- PARSE RESULT / AST (top-level) ---')
        print(parse_result)
        print()

    if show_symbols:
        print('--- SYMBOL TABLE DUMP ---')
        proc.registry.show(include_values=True)
        print()


def main():
    ap = argparse.ArgumentParser(description='Run lexer + parser + symbol table for the mini language.')
    ap.add_argument('file', nargs='?', help='Source file to process (reads stdin if omitted)')
    ap.add_argument('--no-tokens', action='store_true', help='Do not display lexer tokens')
    ap.add_argument('--no-ir', action='store_true', help='Do not display generated IR')
    ap.add_argument('--no-ast', action='store_true', help='Do not display parse result / AST')
    ap.add_argument('--no-symbols', action='store_true', help='Do not display symbol table dump')
    args = ap.parse_args()

    show_tokens = not args.no_tokens
    show_ir = not args.no_ir
    show_ast = not args.no_ast
    show_symbols = not args.no_symbols

    if args.file:
        run_file(args.file, show_tokens, show_ir, show_ast, show_symbols)
    else:
        run_stdin(show_tokens, show_ir, show_ast, show_symbols)


if __name__ == '__main__':
    main()