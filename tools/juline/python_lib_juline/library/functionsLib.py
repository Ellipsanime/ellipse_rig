# coding: utf-8
import sys
import maya.cmds as mc

#from python_lib_juline.utils import exception_utils
from maya import OpenMaya
import maya.api.OpenMaya as OpenMayaP


def undoable(function):
    """ :author:  Remy Dereux
    a decorator that will make commands undoable in maya """
    def undo_function(*args, **kwargs):
        mc.undoInfo(openChunk=True)
        functionReturn = None
        try:
            functionReturn = function(*args, **kwargs)
        except:
            print sys.exc_info()[1]
        finally:
            mc.undoInfo(closeChunk=True)
            return functionReturn
    return undo_function

"""
from maya.setup.autorig.library import functionsLib
@functionsLib.undoable
"""
"""
def debug(function):
    try:
        function()
    except:
        print exception_utils.FormatException()
"""
def name_to_node_api2(name):
    #### convert name to openMayaPython object
    try:
        selectionList = OpenMayaP.MSelectionList()
        selectionList.add(name)
        return selectionList.getDagPath(0)
    except:
        raise RuntimgeError('maya.api.OpenMaya.MDagPath() failed on %s' % name)