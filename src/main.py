from lexer import TokenScanner

code = '''
int main() {
    int x = 10;
    return x;
}
'''

scanner = TokenScanner()
tokens, issues = scanner.scan(code)

print("=== TOKENS ===")
for tok in tokens:
    print(f"Token(kind='{tok['kind']}', value={tok['val']!r}, line={tok['ln']}, col={tok['col']})")

if issues:
    print("\n=== ISSUES ===")
    for issue in issues:
        print(issue)