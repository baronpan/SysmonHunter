from termcolor import cprint

def log_error(s):
    cprint(s, 'red')

def log_warn(s):
    cprint(s, 'yellow')

def log_print(s):
    cprint(s, 'white')

def log_debug(s):
    cprint(s, 'grey')

def log_success(s):
    cprint(s, 'green')

def log_error_u(s):
    cprint(s.encode('utf-8'), 'red')

def log_warn_u(s):
    cprint(s.encode('utf-8'), 'yellow')

def log_print_u(s):
    cprint(s.encode('utf-8'), 'white')

def log_debug_u(s):
    cprint(s.encode('utf-8'), 'grey')

def log_success_u(s):
    cprint(s.encode('utf-8'), 'green')