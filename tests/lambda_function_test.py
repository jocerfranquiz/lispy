from . import *

assert (
    compute(
        """
[def on_click [callback]
    [begin
        [var x 10]
        [var y 20]
        [callback [+ x y]]
    ]
]

[on_click
    [lambda [data] [* data 10]]
]
"""
    )
    == 300
)
assert (
    compute(
        """
[ [lambda [x] [* x x]] 2 ]
"""
    )
    == 4
)
assert (
    compute(
        """
[var square [lambda [x] [* x x]] ]

[square 3]
"""
    )
    == 9
)
