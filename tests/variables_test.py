from . import *

assert compute("[var x 7]") == 7
assert compute("x") == 7
assert compute("VERSION") == "lispy version 0.0.1 2023-07-06"
assert compute("[var is_user true]") is True
