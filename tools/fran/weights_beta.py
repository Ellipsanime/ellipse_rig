# coding=utf-8
import sys
import maya.cmds as mc
import maya.mel as mel
import json
import maya.OpenMaya as OpenMaya
import traceback



class Weight():

    valWeight = [1,1,1]

    def __init__(self):
        self.tmp ='tmp'



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

    # weightsTools()

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
        print infoSk
        return pathFile

    getWeights =classMethod()