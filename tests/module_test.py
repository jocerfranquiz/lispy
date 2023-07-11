from . import *

assert (
    compute(
        """
[module Math
    [begin

        [def abs [value]
            [if [< value 0]
                [- value]
                value]]

        [def square [x]
          [* x x]]

        [var MAX_VALUE 1000]
    ]
]

[[prop Math abs] [- 10]]
"""
    )
    == "10"
)

assert (
    compute(
        """
[var _abs [prop Math abs]]
[_abs [- 10]]
"""
    )
    == "10"
)

assert (
    compute(
        """
[prop Math MAX_VALUE]
"""
    )
    == "1000"
)
