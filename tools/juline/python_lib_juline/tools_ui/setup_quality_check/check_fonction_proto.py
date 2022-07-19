# coding: utf-8

dic_check = {}
dic_check['STATE'] = ""
dic_check['ERROR'] = ""
dic_check['NEED_FIX'] = []
dic_check['OK'] = None


def fonction_check():
    if "ERROR":
        dic_check['STATE'] = "ERROR"
        dic_check['ERROR'] = "ERROR comment"
    elif "NEED_FIX":
        dic_check['STATE'] = "NEED_FIX"
        dic_check['NEED_FIX'] = []  # list of items to add in QListWidget
    else:
        dic_check['STATE'] = "OK"

    return dic_check

def fonction_fix(ls_problem=[]):
    if not ls_problem:
        dic_check = fonction_check()
        ls_problem = dic_check['NEED_FIX']
    for problem in ls_problem:
        print "fix the", problem