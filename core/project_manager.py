import maya.cmds as mc
from maya import OpenMayaUI as omui
import maya.OpenMaya as OpenMaya
import os, sys, glob, json
from functools import partial



def projectsPaths():
    dicPaths = {}
    dicPaths['Smurf04'] = {}
    dicPaths['Smurf04']['SMAB'] = r'C:\Users\feine\Desktop\04_FAB\ASSETS'
    dicPaths['Smurf04']['FACE'] = r'T:\03_FAB\00_ASSETS\MOD\CHR'

    dicPaths['Belfort'] = {}
    dicPaths['Belfort']['SMAB'] = r'X:\04_FABRICATION\ASSETS'
    dicPaths['Belfort']['FACE'] = r'X:\04_FABRICATION\ASSETS\CHR'

    dicPaths['Marsu'] = {}
    dicPaths['Marsu']['SMAB'] = r'C:\Users\feine\Desktop\04_FAB\ASSETS'
    dicPaths['Marsu']['FACE'] = r'X:\04_FABRICATION\ASSETS\CHR'
    return dicPaths


def getProject():
    pathDir = os.path.dirname(__file__)
    pathJson = os.path.join(pathDir, 'projectName.json')
    jsonFile = glob.glob(pathJson)
    if jsonFile:
        jsonDatas = {}
        with open(jsonFile[0], "r") as file:
            jsonDatas = json.load(file)
            return jsonDatas['projectName']
    else:
        return None

def checkProject(nChecker, nProjectMenu, initBtn, saveBtn, pubBtn, toolName, *args):
    pathDir = os.path.dirname(__file__)
    pathJson = os.path.join(pathDir, 'projectName.json')
    jsonFile = glob.glob(pathJson)
    if jsonFile:
        jsonDatas = {}
        with open(jsonFile[0], "r") as file:
             jsonDatas = json.load(file)
        setProject(nChecker, nProjectMenu, jsonDatas['projectName'], jsonDatas['projectColor'], initBtn, saveBtn, pubBtn, toolName, doJsn=False)
        mc.menuItem('projSet_'+jsonDatas['projectName'],e=True, radioButton=True)
        return jsonDatas['projectName']
    else:
        return None



def updateUi(projSeted, btn1, btn2, btn3, toolName, *args):
    print 'updating :', projSeted
    if toolName == 'SMAB':
        print 'updating ZE SMAB'
        mc.menuItem(btn1, e=True, c='tools_smab_v3.scene_manager.initWipVAni(prod="{}")'.format(projSeted))
        mc.menuItem(btn2, e=True, c='tools_smab_v3.scene_manager.saveNewRev(prod="{}")'.format(projSeted))
        mc.menuItem(btn3, e=True, c='tools_smab_v3.scene_manager.pubScene("{}")'.format(projSeted))
        inChk = mc.menuItem(btn1, q=True, c=True)
        savChk = mc.menuItem(btn2, q=True, c=True)
        pubChk = mc.menuItem(btn3, q=True, c=True)

        print 'initCmd : ', inChk
        print 'svaeCmd : ', savChk
        print 'pubCmd : ',pubChk

    #elif toolName == 'FACE':
        #mc.button(btn1, e=True, c='tools_facialShapes_v3.scene_manager.saveNewRev(prod="{}")'.format(projSeted))
        #mc.button(btn2, e=True, c='tools_facialShapes_v3.linkTargets_v2(ctrl, listSel, "{}")'.format(projSeted))


        #inChk = mc.button(btn1, q=True, c=True)
        #savChk = mc.button(btn2, q=True, c=True)


        #print 'btn1 : ', inChk
        #print 'btn2 : ', savChk


    #chk = mc.menuItem(initBtn, q=True, c=True)
    #print 'Here :', chk
    #project_manager.checkProject(nWin, nProjectMenu)
    #partial(project_manager.setProject, nWin, nProjectMenu, projSeted, [0.6, 0.75, 0.9])


def setProject(nChecker, nProjectMenu, nProject, prodColor, initBtn, saveBtn, pubBtn, toolName, doJsn=True,  *args):
    mc.menu(nProjectMenu, e=True, l=nProject)
    title = mc.window(nChecker, q=True, t=True).split('    ~-    ')[0]
    mc.window(nChecker, e=True, t=title+'    ~-    '+nProject.upper())
    pathDir = os.path.dirname(__file__)
    pathParent = os.path.split(pathDir)[0]
    pathIcon = os.path.join(pathParent, 'icons', 'ic_projects', nProject+'.jpg')
    if doJsn == True:
        jSonDatas = {'projectName': nProject, 'projectColor':prodColor}
        with open(os.path.join(pathDir, 'projectName.json'), "w") as file:
            json.dump(jSonDatas, file)


    updateUi(nProject, initBtn, saveBtn, pubBtn, toolName)
    ####TESTE
    #Special cases for different Maya versions
    try:
        from shiboken2 import wrapInstance
    except ImportError:
        from shiboken import wrapInstance

    try:
        from PySide2.QtGui import QIcon
        from PySide2.QtWidgets import QWidget
    except ImportError:
        from PySide.QtGui import QIcon, QWidget


    # Get a pointer and convert it to Qt Widget object
    qw = omui.MQtUtil.findWindow(nChecker)
    widget = wrapInstance(long(qw), QWidget)

    # Create a QIcon object
    icon = QIcon(pathIcon)

    # Assign the icon
    widget.setWindowIcon(icon)


    #print 'project seted to :', nProject,
#################################################################################################
