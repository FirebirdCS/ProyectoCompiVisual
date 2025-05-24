from Buffer import Buffer
from LexicalDict import LexicalDict
from SemanticAnalyzer import SemanticAnalyzer
from Sintax_ import Sintax_
from Semantico import Semantico

if __name__ == '__main__':
    buffer = Buffer()
    lexer = LexicalDict()
    sintax = Sintax_()
    semantic = Semantico()

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
