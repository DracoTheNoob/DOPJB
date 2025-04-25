LOGGING_ENABLED: bool = False


def info(*args):
    if LOGGING_ENABLED:
        for i, arg in enumerate(args):
            print(arg, end=' ' if i != 0 else '\n')
