import inspect
import sys
from os.path import dirname
#moduleName = 'ellipse_rig'
moduleName = 'badgers2_rig_tools'
moduleInfos = sys.modules[moduleName]
modulePath = (moduleInfos.__file__)
moduleDir = dirname(modulePath)
print moduleDir

def resetSessionForScript(userPath=None):
    if userPath is None:
      userPath = dirname(__file__)
    userPath = userPath.lower()
    toDelete = []
    for key, module in sys.modules.iteritems():
      try:
          moduleFilePath = inspect.getfile(module).lower()

          if moduleFilePath == userPath:
              continue
          if moduleFilePath.startswith(userPath):
              print "Removing %s" % key
              toDelete.append(key)
      except:
          pass
    for module in toDelete:
        del (sys.modules[module])
#resetSessionForScript(userPath=moduleDir)