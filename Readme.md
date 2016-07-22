[![Build Status](https://travis-ci.org/oxplot/tamekit.svg?branch=master)](https://travis-ci.org/oxplot/tamekit)
[![Coverage Status](https://coveralls.io/repos/github/oxplot/tamekit/badge.svg?branch=master)](https://coveralls.io/github/oxplot/tamekit?branch=master)

*tamekit* allows limiting the time a block of code takes to run:

    import tamekit

    @tamekit.timeout_after(2):
    def do_long_computation():
      ...

Above will raise a `TimeoutError` exception inside the decorated
function after 2 seconds. `timeout_after` also comes in context manager
form:

    with tamekit.timeout_after(2):
      ...

Note that `timeout_after()` uses CPython specific API to get the job
done.
