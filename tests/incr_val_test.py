from . import *

assert (
    compute(
        """
[var result 0]

[+= result 5]
    
result
"""
    )
    == 5
)
