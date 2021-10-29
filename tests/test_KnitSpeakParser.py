"""testing that symbol table is complete and parser is working as expected"""
from knitspeak_compiler.knitspeak_interpreter.knitspeak_interpreter import KnitSpeak_Interpreter
from knitspeak_compiler.knitspeak_interpreter.symbol_table import Symbol_Table


def test_symbol_table():
    table = Symbol_Table()
    table["cat"] = 1
    table["cat"] = 2


parser = KnitSpeak_Interpreter(True, True, True)


def test_basic_row():
    pattern = r"""1st and 2nd row k."""
    results = parser.interpret(pattern)
    print(results)


def test_range_row():
    pattern = r"""from 1st to 4th row k."""
    results = parser.interpret(pattern)
    print(results)
    pattern = r"""from rs 1st to 4th row k."""
    results = parser.interpret(pattern)
    print(results)
    pattern = r"""from ws 1st to 4th row k."""
    results = parser.interpret(pattern)
    print(results)

def test_all_side_rows():
    pattern = r"""all rs rows k. all ws rows p."""
    results = parser.interpret(pattern)
    print(results)


def test_flipped_row():
    pattern = r"""flipped 1st row k, p.
    flipped 2nd row p, k."""
    results = parser.interpret(pattern)
    print(results)


def test_repeats():
    pattern = r"""1st row knit 10."""
    results = parser.interpret(pattern)
    print(results)
    pattern = r"""1st row k 2, p 3."""
    results = parser.interpret(pattern)
    print(results)
    pattern = r"""1st row [k,p] 2, k, [k,p] 2."""
    results = parser.interpret(pattern)
    print(results)
    pattern = r"""1st row [k,p] to end."""
    results = parser.interpret(pattern)
    print(results)
    pattern = r"""1st row [k] to last st, p."""
    results = parser.interpret(pattern)
    print(results)
    pattern = r"""1st row [k] to last 2 sts, p 2."""
    results = parser.interpret(pattern)
    print(results)
    pattern = r"""1st row [[k,p] 2, k, [k,p] 2] to end."""
    results = parser.interpret(pattern)
    print(results)
    pattern = r"""1st row [k,p] to last 4 sts, [k,p] 2."""
    results = parser.interpret(pattern)
    print(results)


def test_cables():
    pattern = r"""1st row LC3|1P."""
    results = parser.interpret(pattern)
    print(results)


def test_closures():
    pattern = r"""n=1, from (n+1) to (n+3), from 5 to 7 rows k n, p (n=n+2)."""
    results = parser.interpret(pattern)
    print(results)