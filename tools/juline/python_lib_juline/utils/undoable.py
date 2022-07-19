import sys
import maya.cmds as mc

def undoable(function):
    """ a decorator that will make commands undoable in maya """
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