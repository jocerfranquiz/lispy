from . import *

assert compute("[+ 1 2]") == "3"
assert compute("[+ [+ 3 4] 2]") == "9"
assert compute("[* 1 2]") == "2"
assert compute("[+ [* 3 4] 2]") == "14"
