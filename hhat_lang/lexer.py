from rply import LexerGenerator
from hhat_lang.tokens import tokens

# generate lexer
lg = LexerGenerator()
[lg.add(*token) for token in tokens.items()]

# whitespaces
lg.ignore(r"\s+")

# comments
lg.ignore(r"(\/\*.*\*\/)|(\/-.*-\/)")

# build lexer
lexer = lg.build()
