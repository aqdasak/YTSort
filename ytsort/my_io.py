import contextlib
import io
from getpass import getpass
from typing import Callable
from colorama import Fore as c, Style


def is_int(num: str) -> bool:
    """Check if given string is integer or not"""
    try:
        int(num)
    except ValueError:
        return False
    return True


def arg_parse(*args) -> str:
    """Take arguments and return after joining them by a space."""
    return ' '.join([str(x) for x in args])


def take_input(arg):
    arg = c.LIGHTGREEN_EX + arg + c.RESET
    return input(arg)


def non_empty_input(arg):
    """Takes input until the input is not empty."""
    arg = c.LIGHTGREEN_EX + arg + c.RESET
    while True:
        inp = input(arg)
        if inp != '':
            return inp


def non_empty_getpass(arg) -> str:
    """Takes hidden input until the input is not empty."""
    arg = c.LIGHTGREEN_EX + arg + c.RESET
    while True:
        inp = getpass(arg)
        if inp != '':
            return inp


def input_in_range(msg, a, b=None) -> int:
    """
    Takes input until the input is not in range. Both `a` and `b` inclusive.

    Parameters
    ----------
    a: int
        Upper bound if `b` is not supplied, else lower bound
    b: int
        Upper bound if supplied

    If only `a` is supplied, 0 is lower bound and `a` is upper bound.
    If both `a` and `b` are supplied, `a` is lower bound and `b` is upper bound.
    """
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
            inp = int(inp)
            if lb <= inp <= ub:
                return inp
            print_warning(f'Warning: Input range is [{lb},{ub}]')
        except ValueError:
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


def capture_stdout(func: Callable) -> list:
    """
    Captures the standard output on running `func()` and returns it in a list with each line as its item.
    """
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        func()
    output = f.getvalue()
    output = output.split('\n')
    output.remove('')
    return output
