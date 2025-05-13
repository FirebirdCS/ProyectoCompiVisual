from Buffer import Buffer
from LexicalDict import LexicalDict
from SemanticAnalyzer import SemanticAnalyzer

if __name__ == '__main__':
    buffer = Buffer()
    lexer = LexicalDict()

    tokens = []
    lexemes = []

    for chunk in buffer.load_buffer():
        t, lex, _, _ = lexer.tokenize(chunk)
        tokens += t
        lexemes += lex

    print('\nTokens generados:', tokens, '\n')
    print("Iniciando análisis semántico...\n")

    semantic_analyzer = SemanticAnalyzer(tokens, lexemes)
    semantic_analyzer.parse()
