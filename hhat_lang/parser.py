from core_ast import *
from data_ast import *
from rply import ParserGenerator
from tokens import tokens


pg = ParserGenerator(list(tokens.keys()))


parser = pg.build()
#fim!
