# coding: utf-8

import sys

import traceback

# usage: after an except:
# except Exception as e:
#    print ExceptionUtils.FormatException()

def FormatException():
    """
    Returns a formated string describing the exception (usefull from within a decorator as the standard error
    message doesn't point to the decorated function

    :return: Formated string
    :rtype: str
    """
    sep = '|'
    exc_type, exc_obj, tb = sys.exc_info()
    stack = traceback.extract_tb(tb)
    stack_line = stack[-1]
    error_str = '\n ' + '_' * 120 + '\n'
    error_str += '| *** ERROR TRACEBACK'
    error_str += '\n|' + '-' * 120 + '\n'
    error_str += "{sep} *** Exception {type}: {error}\n".format(
        sep=sep,
        type=exc_obj.__class__.__name__,
        error=exc_obj)

    error_str = error_str + "\n|\tCall Stack:"
    for st in reversed(stack):
        call = st[2]
        ln = st[1]
        spc1 = ' ' * (30 - len(call))
        spc2 = ' ' * (5 - len(str(ln)))
        error_str = error_str + ' \n|\t{call},{spc1}line: {line} of {spc2}{file}'.format(
            call=call,
            spc1=spc1,
            line=ln,
            spc2=spc2,
            file=st[0])

    error_str += '\n|' + '_' * 120 + '\n\n'

    return error_str
