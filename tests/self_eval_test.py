from . import *

expressions = [
    ("1234", 1234),
    ("+31.", 31.0),
    ("-.01", -0.01),
    ('"some text"', "some text"),
    ("-1 /* some C-style comment */", -1),
]

for expr, result in expressions:
    assert compute(expr) == result
