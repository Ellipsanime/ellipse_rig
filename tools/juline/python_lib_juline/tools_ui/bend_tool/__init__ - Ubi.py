# coding: utf-8
# Copyright (c) 2018 Ubisoft Juline BRETON

from ump.common.ui import UMP_Widget
from ump.common.ui.qt_abstraction import load_ui, QIcon, QtCore, QPalette, Qt, QTreeWidgetItem, QItemSelectionModel, QBrush
import os
import maya.cmds as mc
from llc.autorig.library import ctrlShapesLib as shpLib
from llc.autorig.library import functionsLib

class UbiBend(UMP_Widget):

    def __init__(self, parent=None):
        UMP_Widget.__init__(self, 'Ubi Bend', parent=parent)
        self.setWindowTitle('Ubi Vis Bend')
        self.ui = load_ui(os.path.join(os.path.dirname(__file__), 'ubi_bend.ui'))
        self.main_layout.addWidget(self.ui)
        self.setWindowIcon(QIcon(os.path.dirname(__file__) + '/bend.png'))

        self.mesh = []

        self.ui.btn_createTpl.clicked.connect(self.create_tpl_bend)
        self.ui.btn_set.clicked.connect(self.set_ctrl)
        self.ui.btn_set.clicked.connect(self.set_meshListEnable)
        self.ui.btn_add.clicked.connect(self.add_mesh)
        self.ui.btn_remove.clicked.connect(self.remove_mesh)
        self.ui.btn_applyBend.clicked.connect(self.ubi_bend)


    def create_tpl_bend(self):
        nameBend = "tpl_" + self.ui.le_bendName.text() + "Bend"
        nameTpl = "tpl_" + self.ui.le_bendName.text()
        if not mc.objExists(nameBend):
            crvUp = mc.curve(degree=1, point=[(0, 0, 0),(0, 1.7, 0), (-0.15, 1.5, 0), (0, 1.7, 0), (0.15, 1.5, 0)])
            mc.rename(crvUp, nameTpl + "Up")
            crvBend = mc.curve(degree=3, point=[(1, -1.164382, 0), (0.856465, -1.138047, 0), (0.602879, -1.06209, 0), (0.233167, -0.726591, 0), (0.0437403, -0.236882, 0),
                                                (0.0437403, 0.236882, 0), (0.233167, 0.726591, 0), (0.602879, 1.06209, 0), (0.856465, 1.138047, 0), (1, 1.164382, 0)])
            mc.rename(crvBend, nameTpl + "Curvature")
            crvAim = mc.curve(degree=1, point=[(0, 0, 0),(0.5, 0, 0)])
            mc.rename(crvAim, nameTpl + "Aim")
            mc.select(clear=True)
            jnt = mc.joint()
            mc.rename(jnt, nameBend)
            mc.parent(nameTpl + "AimShape", nameBend, relative=True, shape=True)
            mc.delete(nameTpl + "Aim")
            mc.setAttr(nameTpl + "AimShape.overrideEnabled", 1)
            shpLib.set_color(nameTpl + 'AimShape', 'RGB', 'red')
            mc.parent(nameTpl + "UpShape", nameBend, relative=True, shape=True)
            mc.delete(nameTpl + "Up")
            mc.setAttr(nameTpl + "UpShape.overrideEnabled", 1)
            shpLib.set_color(nameTpl + 'UpShape', 'RGB', 'green')
            mc.parent(nameTpl + "CurvatureShape", nameBend, relative=True, shape=True)
            mc.delete(nameTpl + "Curvature")
            mc.setAttr(nameTpl + "CurvatureShape.overrideEnabled", 1)
            shpLib.set_color(nameTpl + 'CurvatureShape', 'RGB', 'blue')
        else :
            print "tpl_" + self.ui.le_bendName.text() + "Bend already exist"

    def set_ctrl(self):
        if len(mc.ls(sl=1)) != 1:
            print 'Please select only one controller'
        else:
            self.ui.le_ctrlName.setText(mc.ls(sl=1)[0])

    def set_meshListEnable(self):
        self.ui.gb_mesh.setEnabled(True)
        self.ui.listW_meshs.clear()

    def add_mesh(self):
        for node in mc.ls(sl=1):
            if node in self.mesh:
                continue
            self.ui.listW_meshs.addItem(node)
            self.mesh.append(node)

    def remove_mesh(self):
        for item in self.ui.listW_meshs.selectedItems():
            self.ui.listW_meshs.removeItemWidget(item)
            for i, x in enumerate(self.mesh):
                if x == item.text():
                    self.mesh.pop(i)
                    break
            self.ui.listW_meshs.clear()
            for node in self.mesh:
                self.ui.listW_meshs.addItem(node)

    @functionsLib.undoable
    def ubi_bend(self):
        # select a mesh and a controller
        #sel = mc.ls(sl=1)
        #ctrl = [c for c in sel if c.startswith("c_")][0]
        #mshs = [x for x in sel if x.split(":")[-1].startswith("msh_")]
        ctrl = self.ui.le_ctrlName.text()
        print 'ctrl : ', ctrl
        mshs = self.mesh

        if not ctrl or not mshs:
            print "You have to select a controller and a mesh"
            return

        mc.addAttr(ctrl, longName = "ubi_bend", attributeType = "float", minValue = -10, maxValue = 10, keyable=True)
        mc.addAttr(ctrl, longName = "ubi_highBound", attributeType = "float", minValue = 0, maxValue = 10, defaultValue = 5, keyable=True)
        mc.addAttr(ctrl, longName = "ubi_lowBound", attributeType = "float", minValue = 0, maxValue = 10, defaultValue = 5, keyable=True)
        mc.setAttr(ctrl+".scaleX", lock=True, keyable=False, channelBox=False)
        mc.setAttr(ctrl+".scaleY", lock=True, keyable=False, channelBox=False)
        mc.setAttr(ctrl+".scaleZ", lock=True, keyable=False, channelBox=False)
        mc.setAttr(ctrl+".rotateX", lock=True, keyable=False, channelBox=False)
        mc.setAttr(ctrl+".rotateZ", lock=True, keyable=False, channelBox=False)
        mc.setAttr(ctrl+".translateX", lock=True, keyable=False, channelBox=False)
        mc.setAttr(ctrl+".translateZ", lock=True, keyable=False, channelBox=False)


        nodeBend = mc.nonLinear(mshs, name="bend_" + ctrl.split('Bend')[0][2:], type="bend")
        bend = mc.rename(nodeBend[0], "bend_" + ctrl.split('Bend')[0][2:])
        handle = mc.rename(nodeBend[1], "hdl_" + ctrl.split('Bend')[0][2:])
        ptConst = mc.parentConstraint(ctrl, handle, maintainOffset=False)
        mc.delete(ptConst)

        # creation DVK on bend attrs
        mc.setAttr(ctrl+".ubi_bend", 10)
        mc.setAttr(bend+".curvature", 180)
        mc.setDrivenKeyframe(bend, attribute="curvature", currentDriver=ctrl+".ubi_bend")
        mc.setAttr(ctrl+".ubi_bend", -10)
        mc.setAttr(bend+".curvature", -180)
        mc.setDrivenKeyframe(bend, attribute="curvature", currentDriver=ctrl+".ubi_bend")
        mc.setAttr(ctrl+".ubi_highBound", 0)
        mc.setAttr(bend+".highBound", 0)
        mc.setDrivenKeyframe(bend, attribute="highBound", currentDriver=ctrl+".ubi_highBound")
        mc.setAttr(ctrl+".ubi_highBound", 10)
        mc.setAttr(bend+".highBound", 2)
        mc.setDrivenKeyframe(bend, attribute="highBound", currentDriver=ctrl+".ubi_highBound")
        mc.setAttr(ctrl+".ubi_lowBound", 0)
        mc.setAttr(bend+".lowBound", 0)
        mc.setDrivenKeyframe(bend, attribute="lowBound", currentDriver=ctrl+".ubi_lowBound")
        mc.setAttr(ctrl+".ubi_lowBound", 10)
        mc.setAttr(bend+".lowBound", -2)
        mc.setDrivenKeyframe(bend, attribute="lowBound", currentDriver=ctrl+".ubi_lowBound")
        # set default value
        mc.setAttr(ctrl+".ubi_bend", 0)
        mc.setAttr(ctrl+".ubi_lowBound", 5)
        mc.setAttr(ctrl+".ubi_highBound", 5)

        #creation et rangement du hook
        hook = mc.createNode("transform", name=ctrl.replace("c", "hook"))
        decM = mc.createNode("decomposeMatrix", name=ctrl.replace("c", "dM"))
        mc.connectAttr(ctrl+".worldMatrix[0]", decM+".inputMatrix", force=True)
        mc.connectAttr(decM+".outputTranslate", hook+".t", force=True)
        mc.connectAttr(decM+".outputRotate", hook+".r", force=True)
        mc.connectAttr(decM+".outputScale", hook+".s", force=True)
        mc.connectAttr(decM+".outputShear", hook+".shear", force=True)
        mc.parent(handle, hook)

        #on check si un grp DEFORMERS existe sinon on le cree
        if "DEFORMERS" in mc.ls():
            pass
        else:
            mc.createNode("transform", name="DEFORMERS")

        #on check si un grp BENDS existe sinon on le cree et on parent le tout
        if "BENDS" in mc.ls():
            grpBend = "BENDS"
        else:
            grpBend = mc.createNode("transform", name="BENDS")
        mc.parent(hook, grpBend)
        if mc.listRelatives("DEFORMERS", children=True) is None:
            mc.parent("BENDS", "DEFORMERS")

def colorTpl():
    mc.setAttr("tpl_upShape.overrideEnabled", 1)
    mc.setAttr("tpl_upShape.overrideColor", 14)
    mc.setAttr("tpl_curvatureShape.overrideEnabled", 1)
    mc.setAttr("tpl_curvatureShape.overrideColor", 6)
    mc.setAttr("tpl_aimShape.overrideEnabled", 1)
    mc.setAttr("tpl_aimShape.overrideColor", 13)

def ctrlBend():
    c = mc.ls(sl=True)
    crv = mc.curve(degree=1, point=[(-0.666838, 0, 0), (0, 0, 0), (0.666838, 0, 0), (0.764495, 0, 0.235763), (1.000258, 0, 0.333419), (1.236021, 0, 0.235763), (1.333677, 0, 0),
                                    (1.236021, 0, -0.235763), (0.764495, 0, 0.235763), (1.236021, 0, -0.235763), (1.000258, 0, -0.333419), (0.764495, 0, -0.235763),
                                    (1.236021, 0, 0.235763), (0.764495, 0, -0.235763), (0.666838, 0, 0), (-0.666838, 0, 0), (-0.764495, 0, -0.235763), (-1.000258, 0, -0.333419),
                                    (-1.236021, 0, -0.235763), (-0.764495, 0, 0.235763), (-1.236021, 0, -0.235763), (-1.333677, 0, 0), (-1.236021, 0, 0.235763),
                                    (-0.764495, 0, -0.235763), (-1.236021, 0, 0.235763), (-1.000258, 0, 0.333419), (-0.764495, 0, 0.235763), (-0.666838, 0, 0)])
    const = mc.parentConstraint(c, crv)
    mc.delete(const)
    shpDel = mc.listRelatives(c, shapes=True)
    mc.delete(shpDel)
    shp = mc.listRelatives(crv, shapes=True)
    mc.parent(shp, c, relative=True, shape=True)

