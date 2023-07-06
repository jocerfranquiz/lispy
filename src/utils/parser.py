import os
from lark import Lark, Transformer

path = os.path.dirname(os.path.abspath(__file__))
file = "grammar.lark"


# Define the grammar for expressions
with open(os.path.join(path, file), mode="r") as g:
    grammar = g.read()


# Define a transformer to build the nested structure
class CustomTransformer(Transformer):
    def array(self, items):
        return list(items)

    def atom(self, atom):
        return atom[0].value

    def integer(self, atom):
        return int(atom[0].value)

    def floating(self, atom):
        return float(atom[0].value)

    def string(self, atom):
        return str(atom[0].value)

    def start(self, expr):
        return expr[0]


# Create the parser
parser = Lark(grammar, parser='lalr', transformer=CustomTransformer())


# Parse the expression and return the resulting list
def parse(expr):
    return parser.parse(expr)


def test_parse():
    # Example usage
    expressions = [
        ("1234", 1234),
        ("+31.", 31.0),
        ("-.01", -0.01),
        ('"some text"', '"some text"'),
        ("[] /* some comment */", []),
        ("[]", []),
        ("[+ 1 2]", ['+', 1, 2]),
        ("[+ [* 2 3] 10.]", ['+', ['*', 2, 3], 10.0]),
        ("[var x 33]", ['var', 'x', 33]),
        ("[var a -33]", ['var', 'a', -33]),
        ("[var b +33]", ['var', 'b', 33]),
        ('[var x "some string"]', ['var', 'x', '"some string"']),
        (
            "[begin [var data 20] [var r -2.0] [set data [+ data r]] [data]]",
            [
                'begin',
                ['var', 'data', 20],
                ['var', 'r', -2.0],
                ['set', 'data', ['+', 'data', 'r']],
                ['data'],
            ],
        ),
    ]

    for expr, result in expressions:
        assert parse(expr) == result

    print("All assertions pass!")


if __name__ == "__main__":
    test_parse()
