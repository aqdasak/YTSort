import contextlib
import io
from colorama import Fore as c, Style


def arg_parse(*args):
    return ' '.join(tuple(map(lambda x: str(x), args)))


def non_empty_input(arg):
    arg = c.LIGHTGREEN_EX + arg + c.RESET
    while True:
        inp = input(arg)
        if inp != '':
            return inp


def input_in_range(msg, a, b=None) -> float:
    if b is not None:
        if b <= a:
            raise ValueError('Upper bound should be greater than lower bound')
        lb = a
        ub = b
    else:
        if a <= 0:
            raise ValueError('Upper bound should be greater than 0')
        lb = 0
        ub = a

    while True:
        inp = non_empty_input(msg)
        try:
            inp = float(inp)
            if lb <= inp < ub:
                return inp
            print_warning(f'Warning: Input range is [{lb},{ub})')
        except:
            print_warning(f'Warning: Please input a number')


def print_info(*args):
    print(c.LIGHTYELLOW_EX + arg_parse(*args) + c.RESET)


def print_warning(*args):
    print(c.LIGHTRED_EX + arg_parse(*args) + c.RESET)


def print_heading(*args):
    print()
    print(Style.BRIGHT+c.LIGHTBLUE_EX, end='')
    st = arg_parse(*args)
    print(st)
    print('-'*len(st), end='')
    print(c.RESET + Style.NORMAL)


def capture_stdout(func) -> list:
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        func()
    output = f.getvalue()
    output = output.split('\n')
    output.remove('')
    return output
