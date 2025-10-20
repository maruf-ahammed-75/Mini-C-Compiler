from src.lexer import tokenize

code = '''
int main() {
    int x = 10;
    return x;
}
'''

for tok in tokenize(code):
    print(tok)
