from . import *

assert (
    compute(
        """
[import math]

[[prop math abs] [- 10]]
"""
    )
    == 10
)

assert (
    compute(
        """
[var _abs [prop math abs]]

[_abs [- 10]]
"""
    )
    == 10
)

assert (
    compute(
        """
[prop math PI]
"""
    )
    == 3.141592653589793
)
