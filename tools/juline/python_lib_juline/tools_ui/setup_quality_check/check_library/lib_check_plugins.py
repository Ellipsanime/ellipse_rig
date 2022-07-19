# coding: utf-8
# AUTHOR : Juline BRETON

import sys
ELIE_PATH = [r"T:\00_PROGRAMMATION\PRIMARY"]
sys.path.append(ELIE_PATH)
from smurf.sanitycheck.maya import mayaPluginCheck
plugCheck = mayaPluginCheck.mayaPluginCheck()

from ....utils import comment
from ....library import attributesLib
reload(attributesLib)

import maya.cmds as mc

dic_check = {}
dic_check['STATE'] = ""
dic_check['ERROR'] = ""
dic_check['NEED_FIX'] = []
dic_check['OK'] = None

CG_ALL = 'cg_all'
ATTR_MASTER_CG = 'MASTER_CG'


def check_plugin_prp_chr():
    message = check_plugin()
    dic_check = {}
    if message:
        dic_check['STATE'] = "NEED_FIX"
        dic_check['NEED_FIX'] = message

    else:
        dic_check['STATE'] = "OK"

    return dic_check


def check_plugin():
    message = plugCheck.check()
    return message


def fix_plugin():
    plugCheck.resolve()


