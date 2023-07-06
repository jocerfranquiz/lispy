from . import *

assert (
    compute(
        """
[var result 0]

[++ result]
    
result
"""
    )
    == 1
)
