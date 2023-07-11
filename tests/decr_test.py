from . import *

assert (
    compute(
        """
[var result 1]

[-- result]

result
"""
    )
    == "0"
)
