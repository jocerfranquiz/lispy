from . import *

expressions = [
    ("1234", "1234"),
    ("+31.", "31.0"),
    ("-.01", "-0.01"),
    ('[quote ["some text"]]', '["some text"]'),
    ('[quote ["  some text   "]]', '[" some text "]'),  # this is weird
    ('[quote [some    text]]', "[some text]"),  # this is weird
    # TODO comments
    # ("10 /* some C-style comment */", "10"),
]

for expr, result in expressions:
    assert compute(expr) == result
