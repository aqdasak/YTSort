from colorama import Fore as c, Style


def arg_parse(*args):
    return ' '.join(tuple(map(lambda x: str(x), args)))


def non_empty_input(arg):
    arg = c.LIGHTGREEN_EX + arg + c.RESET
    while True:
        inp = input(arg)
        if inp != '':
            return inp


def print_info(*args):
    print(c.LIGHTYELLOW_EX + arg_parse(*args) + c.RESET)


def print_warning(*args):
    print(c.LIGHTRED_EX + arg_parse(*args) + c.RESET)


def print_heading(*args):
    print(Style.BRIGHT+c.LIGHTBLUE_EX, end='')
    st = '<< ' + arg_parse(*args) + ' >>'
    print(st)
    print('-'*len(st), end='')
    print(c.RESET + Style.NORMAL)
