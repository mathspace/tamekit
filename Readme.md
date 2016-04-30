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
