from . import *

assert compute("[+ 1 5]") == 6
assert compute("[+ [+ 2 3] 5]") == 10
assert compute("[+ [* 2 3] 5]") == 11

assert compute("[> 1 5]") is False
assert compute("[< 1 5]") is True
assert compute("[>= 5 5]") is True
assert compute("[<= 5 5]") is True
assert compute("[= 5 5]") is True
