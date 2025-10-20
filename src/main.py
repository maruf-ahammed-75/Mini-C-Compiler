from lexer import TokenScanner
from parser import SyntaxProcessor

code = '''
int main() {
    int x = 10;
    int y = 20;
    int z = x + y;
    print(z);
    return 0;
}
'''

# Test Lexer
print("=" * 50)
print("LEXICAL ANALYSIS")
print("=" * 50)
scanner = TokenScanner()
tokens, lex_issues = scanner.scan(code)

print("\n=== TOKENS ===")
for tok in tokens:
    print(f"Token(kind='{tok['kind']}', value={tok['val']!r}, line={tok['ln']}, col={tok['col']})")

if lex_issues:
    print("\n=== LEXER ISSUES ===")
    for issue in lex_issues:
        print(issue)

# Test Parser
print("\n" + "=" * 50)
print("SYNTAX ANALYSIS")
print("=" * 50)

# Create token input string for parser
scanner2 = TokenScanner()
scanner2.scan(code)
parser = SyntaxProcessor()
parser.initialize()

# Parse using the lexer
lexer = scanner2.scanner
result = parser.processor.parse(code, lexer=lexer)

print("\n=== AST ===")
for node in parser.ast:
    print(node)

print("\n=== INTERMEDIATE REPRESENTATION ===")
for i, instr in enumerate(parser.ir_instructions):
    print(f"{i}: {instr}")

print("\n=== SYMBOL TABLE ===")
parser.registry.show()

if parser.issues:
    print("\n=== PARSER ISSUES ===")
    for issue in parser.issues:
        print(issue)