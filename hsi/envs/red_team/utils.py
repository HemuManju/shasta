import asyncio


def async_func(f):
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(
            None, f, *args, *kwargs)

    return wrapped
