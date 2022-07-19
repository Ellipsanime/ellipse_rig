import sys
import maya.cmds as mc
import maya.mel as mel
import json

# WEIGHT TOOLS__________________________________________________________________________________________________________
def weightsTools(*args):
    if mc.window("weightsUi", q=1, exists=1) == True:
        mc.deleteUI("weightsUi")

    mc.window("weightsUi", width=250, height=200, mxb=False, mnb=True)
    mc.columnLayout("weightMainLayout", width=350, height=100, parent="weightsUi")
    mc.text(label="Copy/Paste json", width=350, height=50, align="center")
    mc.textFieldButtonGrp("FileNameDisplay", columnWidth=[[1, 0], [2, 300]], width=350, height=25, label="File: ",
                          buttonLabel="File", buttonCommand=jsonGetFileName)

    mc.rowLayout("weightBtnLayout", numberOfColumns=2, width=350, height=50, parent="weightsUi")

    mc.button("CopyB", width=165, label="Copy Weights", command=copySkin, parent="weightBtnLayout")
    mc.button("PasteB", width=165, label="Paste Weights", command=pasteSkin, parent="weightBtnLayout")
    mc.showWindow("weightsUi")
#weightsTools()

# JSON__________________________________________________________________________________________________________________
def jsonGetFileName(*args):
    jsonFilter = "*.json"
    fileNameDir = mc.fileDialog2(fileFilter=jsonFilter, dialogStyle=2)[0]
    if fileNameDir != "":
        mc.textFieldButtonGrp("FileNameDisplay", e=1, text=fileNameDir)

# COPY SKINNING_________________________________________________________________________________________________________
def copySkin(*args):
    pathFile = mc.textFieldButtonGrp("FileNameDisplay",q=1, text=1)
    # get list selection
    lsObj = mc.ls(sl=True)
    # get skinCluster
    skinCls = mc.listConnections(mc.ls(lsObj[0],o=True)[0],t="skinCluster")[0]
    # list vertex
    lsVtx = mc.filterExpand(lsObj,sm=(31,28,36,47,46))
    # joints influences
    lsJntInf = [mc.skinCluster(skinCls,q=True,wi=True) for each in lsVtx]
    # values skinning
    lsValSkin =[[mc.skinPercent(skinCls, lsVtx[i], query=True,t=jt) for jt in jnt] for i, jnt in enumerate(lsJntInf)]
    # zip list
    lsZip = zip(*lsValSkin)
    # concat list
    lsConcat=[sum(each) for each in lsZip]
    # result new skin
    valSkin =[round(float(each/(len(lsValSkin))),5) for each in lsConcat]
    infoSk = zip(lsJntInf[0],valSkin)
    # create json
    with open(pathFile, "w") as jsonFile:
        json.dump(infoSk, jsonFile, indent=2)
    return pathFile

# PASTE SKINNING________________________________________________________________________________________________________
def pasteSkin(*args):
    pathFile = mc.textFieldButtonGrp("FileNameDisplay",q=1, text=1)
    try:
        with open(pathFile, 'r') as jsonFile:
            readJson =  json.load(jsonFile)
            # get list selection
            lsObj = mc.ls(sl=True)
            # get skinCluster
            skinCls = mc.listConnections(mc.ls(lsObj[0], o=True)[0], t="skinCluster")[0]
            # list vertex
            lsVtx = mc.filterExpand(lsObj, sm=(31, 28, 36, 47, 46))
            # disable weight normalisation
            mc.setAttr(skinCls + ".normalizeWeights", 0)
            # paste skin values
            for i, eachPoint in enumerate(lsVtx):
                for j, jnt in enumerate(readJson):
                    mc.skinPercent(skinCls, eachPoint, r=False, transformValue=[(jnt[0],jnt[1])])
            # re-Enable weight normalisation
            mc.setAttr(skinCls + ".normalizeWeights", 1)
            mc.skinPercent(skinCls, normalize=True)
    except:
        mc.error("Could not read {0}".format(pathFile))

# RETURN SKIN CLUSTER___________________________________________________________________________________________________
def returnSkinCluster(mesh, silent=False):
    skinCluster = "please select object"
    if mesh != []:
        try:
            shp = mc.listRelatives(mesh, s=True)[0]
            if mc.objectType(shp) == 'mesh':
                skinCluster = mel.eval('findRelatedSkinCluster("%s");' % shp)
                if not skinCluster:
                    if silent == False:
                        mc.confirmDialog(title='Error', message='no SkinCluster found on: %s!' % shp, button=['Ok'],
                                           defaultButton='Ok', cancelButton='Ok', dismissString='Ok')
                    else:
                        skinCluster = None
        except:
            skinCluster = mc.warning("object's not a mesh")
    else:
        skinCluster = mc.warning("please select object")
    return skinCluster
"""
from ellipse_rig.tools.fran import tool_weights
reload(tool_weights)
returnSkin = tool_weights.returnSkinCluster(mc.ls(sl=True))
"""

# GET INFLUENCE JOINT___________________________________________________________________________________________________
def getJntsSk(mesh=None):
    '''returns all joints that influence mesh'''
    skinClusterName = returnSkinCluster(mesh, silent=True)
    if skinClusterName != None:
        jointInfls = mc.skinCluster(skinClusterName, q=True, inf=True)
        return jointInfls
"""
infJnt = tool_weights.getJntsSk(mesh=mc.ls(sl=True))
"""


# RESET SKIN JOINT______________________________________________________________________________________________________
def resetSkJnts(lsJnt=None):
    '''recomputes all prebind matrices in this pose, joints will stay in place while the mesh goes back to bindpose'''
    # http://leftbulb.blogspot.nl/2012/09/resetting-skin-deformation-for-joint.html
    for joint in lsJnt:
        skinClusterPlugs = mc.listConnections(joint + ".worldMatrix[0]", type="skinCluster", p=1)
        if skinClusterPlugs:
            for skinClstPlug in skinClusterPlugs:
                index = skinClstPlug[skinClstPlug.index("[") + 1: -1]
                skinCluster = skinClstPlug[: skinClstPlug.index(".")]
                curInvMat = mc.getAttr(joint + ".worldInverseMatrix")
                mc.setAttr(skinCluster + ".bindPreMatrix[%s]" % index, type="matrix", *curInvMat)
        else:
            mc.warning("no skinCluster attached to %s!" % joint)
"""
lsObj=mc.ls(sl=True);resetSkinJnt = lib_skinning.SkinningTools();
print resetSkinJnt.resetSkinnedJoints(lsJnt =lsObj)
"""



