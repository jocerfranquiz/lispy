from . import *

assert compute("[var x 7]") == "7"
assert compute("x") == "7"
assert compute("VERSION") == "tea version 0.0.2 2023-07-11"
assert compute("[var is_user true]") == "True"
