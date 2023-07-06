import io
import sys


def _print_test(fn, arg):
    # Redirect the standard output
    output = io.StringIO()
    sys.stdout = output

    # Call the function
    fn(arg)

    # Retrieve the printed output
    result = output.getvalue().strip()

    # Restore the standard output
    sys.stdout = sys.__stdout__
    output = None

    return result


########################################

from . import *

# Function to test `compute`

# Run assertions
assert _print_test(compute, "[print 1]") == "1"
assert _print_test(compute, '[print "some text"]') == "some text"
assert _print_test(compute, '[print +41.]') == "41.0"
