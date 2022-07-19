import inspect
from os.path import dirname
import sys
import maya.cmds as mc


def buildModulesHp(doCleanCtr, doCgCtr, doMirrorCtr, doVisCtr, doMatchIKFKCtr, doSaveCtr, *args):

    doClean = mc.menuItem(doCleanCtr, q=True, cb=True)
    doCg =  mc.menuItem(doCgCtr, q=True, cb=True)
    doMirror = mc.menuItem(doMirrorCtr, q=True, cb=True)
    doVis = mc.menuItem(doVisCtr, q=True, cb=True)
    doMatchIKFK = mc.menuItem(doMatchIKFKCtr, q=True, cb=True)
    saveCtr = mc.menuItem(doSaveCtr, q=True, cb=True)
    print 'building module : clean=', doClean, 'cg=', doCg, 'mirrorCtrl=', doMirror, 'linkVis=', doVis, 'IKFKMatch=', doMatchIKFK, 'savScene=', saveCtr,

    from ellipse_rig import buildRig
    reload(buildRig)
    buildRig.doBuildRig(cleanScene=doClean, doCg=doCg, linkMirror=doMirror, connMenuHideGrp=doVis, mathcIkFk=doMatchIKFK, pipe=saveCtr)
    print 'builded',


def reloadModules(moduleName):
    moduleInfos = sys.modules[moduleName]
    modulePath = (moduleInfos.__file__)
    moduleDir = dirname(modulePath)
    userPath = moduleDir
    print 'HERE' , userPath
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

def reopenCurrentScene(*args, **kwargs):
    scenePath = mc.file(q=True, sn=True) or 'unknow'
    if scenePath == 'unknow':
        scenePath = mc.file(q=True, loc=True)
    if scenePath == 'unknow':
        mc.warning('your scene isn t saved')
    else:
        mc.file(scenePath, open=True, f=True)
