from . import *

assert (
    compute(
        """
[var result 5]

[-= result 5]

result
"""
    )
    == "0"
)
