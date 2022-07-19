# coding: utf-8
# Copyright (c) 2018 Juline BRETON

import os
import sys
import pprint

# pathTeamShare = r'T:\90_TEAM_SHARE\Juline\TOOLS'
# if not pathTeamShare in sys.path:
#     sys.path.append(pathTeamShare)

from ...utils.maya_widget import MayaWidget, load_ui, get_maya_main_window
from ...utils import open_ui

from PySide2 import QtCore
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import qApp

import maya.cmds as mc

# import TOOLS to connect to the toolbox
# python_lib_juline.library
from ...library import functionsLib, shapesLib, nurbsAttach, attributesLib
from ...library import ctrlShapesLib as shpLib
from ...utils import comment
# foundation_rig.library
from ......library import lib_namespace

reload(shapesLib)


class GuguBox(MayaWidget):
    def __init__(self, parent=None):
        MayaWidget.__init__(self, name="Setup Toolbox", parent=parent)

        self.ui = load_ui(os.path.join(os.path.dirname(__file__), 'gugu_box.ui'))

        self.setWindowIcon(QIcon(os.path.dirname(__file__) + '/ico/tool.png'))
        self.main_layout.addWidget(self.ui)
        self.set_ico()

        ### TOOLS ###
        self.ui.btn_attr.clicked.connect(open_attr_box)
        # self.ui.btn_constraint.clicked.connect(open_constraint_tool)
        self.ui.btn_bend.clicked.connect(open_bend_tool)
        self.ui.btn_select.clicked.connect(self.select_list)

        ########## RIG
        # self.ui.btn_wwf.clicked.connect(crt_wwf_hierarchy)
        # self.ui.btn_trash.clicked.connect(crt_trash)
        # self.ui.btn_setNamespace.clicked.connect(set_namespace)
        # self.ui.btn_dgdirty.clicked.connect(dgdirty)
        # self.ui.btn_checkSetup.clicked.connect(check_setup)
        self.ui.btn_nurbsAttach.clicked.connect(self.create_nurbs_attach)
        # self.ui.btn_hook.clicked.connect(self.create_hook)
        # self.ui.btn_neutraliseParent.clicked.connect(self.neutralise_parent)
        self.ui.btn_rigAdd.clicked.connect(crt_rig_add)

        # Filter attribute______________________________________________________________________________________________
        self.ui.btn_get_list_attr.clicked.connect(self.get_list_attr)
        self.ui.btn_get_list_state.clicked.connect(self.get_list_attr_state)

        ########## SHAPE TOOL
        self.ui.btn_shpToTransform.clicked.connect(self.shape_to_transform)
        self.ui.cb_instance.clicked.connect(self.set_interface)
        ######## COLOR
        #### BASE
        self.ui.btn_yellow.clicked.connect(self.set_color_btn)
        self.ui.btn_red.clicked.connect(self.set_color_btn)
        self.ui.btn_blue.clicked.connect(self.set_color_btn)
        self.ui.btn_green.clicked.connect(self.set_color_btn)
        self.ui.btn_black.clicked.connect(self.set_color_btn)
        self.ui.btn_brown24.clicked.connect(self.set_color_btn)
        #### CUSTOM
        self.ui.btn_orange.clicked.connect(self.set_color_btn)
        self.ui.btn_magenta.clicked.connect(self.set_color_btn)
        self.ui.btn_blueA.clicked.connect(self.set_color_btn)
        self.ui.btn_greenApple.clicked.connect(self.set_color_btn)
        self.ui.btn_purple.clicked.connect(self.set_color_btn)
        ######## FORM
        self.ui.btn_circle.clicked.connect(self.set_form_btn)
        self.ui.btn_square.clicked.connect(self.set_form_btn)
        self.ui.btn_squareRounded.clicked.connect(self.set_form_btn)
        self.ui.btn_fly.clicked.connect(self.set_form_btn)
        self.ui.btn_arrowDoubleCrv2.clicked.connect(self.set_form_btn)
        self.ui.btn_sphere.clicked.connect(self.set_form_btn)
        self.ui.btn_pinSimple.clicked.connect(self.set_form_btn)
        self.ui.btn_arrowSingle.clicked.connect(self.set_form_btn)
        self.ui.btn_arrowDouble.clicked.connect(self.set_form_btn)

        ######## NAME
        self.ui.btn_rnmCtrlShp.clicked.connect(rnm_ctrl_shp)

        ######## CURVE
        self.ui.btn_shiftCrv.clicked.connect(self.shift_curve)

        ######## SPACE SWITCH
        self.ui.btn_setCtrlSpaceSwitch.clicked.connect(self.set_ctrl_space_switch)
        self.ui.btn_setSpaceSwitch.clicked.connect(self.crt_space_switch)

        ######## JOINT DRAW
        self.ui.btn_jtSelected.clicked.connect(set_joint_draw_sel)
        self.ui.btn_allJt.clicked.connect(set_joint_draw_all)
        self.ui.btn_showJtOrient.clicked.connect(show_joint_orient)
        self.ui.btn_hideJtOrient.clicked.connect(hide_joint_orient)

        ######## HANDLE
        self.ui.btn_hideHdl.clicked.connect(set_handle_hide)
        self.ui.btn_showHdl.clicked.connect(set_handle_show)

        ########## INTERFACE
        self.ui.btn_win_pink.clicked.connect(self.set_win_pink)
        self.ui.btn_win_orange.clicked.connect(self.set_win_orange)
        self.ui.btn_win_blue.clicked.connect(self.set_win_blue)
        self.ui.btn_win_green.clicked.connect(self.set_win_green)
        self.ui.btn_win_grey.clicked.connect(self.set_win_grey)

    def set_ico(self):
        ## TOOLS ##
        self.ui.btn_visSwitch.setIcon(QIcon(os.path.dirname(__file__) + '/ico/eye-illuminati.png'))
        self.ui.btn_visSwitch.setIconSize(QtCore.QSize(25, 25))
        self.ui.btn_attr.setIcon(QIcon(os.path.dirname(__file__) + '/ico/switch.png'))
        self.ui.btn_attr.setIconSize(QtCore.QSize(20, 20))
        self.ui.btn_bend.setIcon(QIcon(os.path.dirname(__file__) + '/ico/bend.png'))
        self.ui.btn_bend.setIconSize(QtCore.QSize(20, 20))
        self.ui.btn_squash.setIcon(QIcon(os.path.dirname(__file__) + '/ico/squash4.png'))
        self.ui.btn_squash.setIconSize(QtCore.QSize(20, 20))
        self.ui.btn_renamer.setIcon(QIcon(os.path.dirname(__file__) + '/ico/renamer_l.png'))
        self.ui.btn_renamer.setIconSize(QtCore.QSize(20, 20))
        self.ui.btn_locTool.setIcon(QIcon(os.path.dirname(__file__) + '/ico//ico/locatorBlue.png'))
        self.ui.btn_locTool.setIconSize(QtCore.QSize(20, 20))
        ## RIG ##
        self.ui.btn_shpToTransform.setIcon(QIcon(os.path.dirname(__file__) + '/ico/shpToTrsf.png'))
        self.ui.btn_shpToTransform.setIconSize(QtCore.QSize(25, 25))
        self.ui.btn_wwf.setIcon(QIcon(os.path.dirname(__file__) + '/ico/wwf.png'))
        self.ui.btn_wwf.setIconSize(QtCore.QSize(30, 30))
        self.ui.btn_rigAdd.setIcon(QIcon(os.path.dirname(__file__) + '/ico/rigAdd_green2.png'))
        self.ui.btn_rigAdd.setIconSize(QtCore.QSize(25, 25))
        self.ui.btn_dgdirty.setIcon(QIcon(os.path.dirname(__file__) + '/ico/magic_pink.png'))
        self.ui.btn_dgdirty.setIconSize(QtCore.QSize(30, 30))
        self.ui.btn_checkSetup.setIcon(QIcon(os.path.dirname(__file__) + '/ico/check.png'))
        self.ui.btn_checkSetup.setIconSize(QtCore.QSize(20, 20))
        self.ui.btn_nurbsAttach.setIcon(QIcon(os.path.dirname(__file__) + '/ico/nurbsAttach_green.png'))
        self.ui.btn_nurbsAttach.setIconSize(QtCore.QSize(30, 30))
        self.ui.btn_hook.setIcon(QIcon(os.path.dirname(__file__) + '/ico/hook.png'))
        self.ui.btn_hook.setIconSize(QtCore.QSize(25, 25))
        self.ui.btn_trash.setIcon(QIcon(os.path.dirname(__file__) + '/ico/poubelle_green.png'))
        self.ui.btn_trash.setIconSize(QtCore.QSize(20, 20))
        ## FORM SHAPE ##
        self.ui.btn_circle.setIcon(QIcon(os.path.dirname(__file__) + '/ico/circle_blue.png'))
        self.ui.btn_circle.setIconSize(QtCore.QSize(45, 45))
        self.ui.btn_square.setIcon(QIcon(os.path.dirname(__file__) + '/ico/square_blue.png'))
        self.ui.btn_square.setIconSize(QtCore.QSize(45, 45))
        self.ui.btn_squareRounded.setIcon(QIcon(os.path.dirname(__file__) + '/ico/squareSmooth_blue.png'))
        self.ui.btn_squareRounded.setIconSize(QtCore.QSize(45, 45))
        self.ui.btn_sphere.setIcon(QIcon(os.path.dirname(__file__) + '/ico/sphere_blue.png'))
        self.ui.btn_sphere.setIconSize(QtCore.QSize(45, 45))
        self.ui.btn_pinSimple.setIcon(QIcon(os.path.dirname(__file__) + '/ico/pinSimple_blue.png'))
        self.ui.btn_pinSimple.setIconSize(QtCore.QSize(50, 50))
        self.ui.btn_fly.setIcon(QIcon(os.path.dirname(__file__) + '/ico/fly_blue.png'))
        self.ui.btn_fly.setIconSize(QtCore.QSize(45, 45))
        self.ui.btn_arrowDoubleCrv2.setIcon(QIcon(os.path.dirname(__file__) + '/ico/arrowDoubleCrv2_blue.png'))
        self.ui.btn_arrowDoubleCrv2.setIconSize(QtCore.QSize(40, 40))
        self.ui.btn_arrowSingle.setIcon(QIcon(os.path.dirname(__file__) + '/ico/arrow_blue.png'))
        self.ui.btn_arrowSingle.setIconSize(QtCore.QSize(40, 40))
        self.ui.btn_arrowDouble.setIcon(QIcon(os.path.dirname(__file__) + '/ico/arrowDbl_blue.png'))
        self.ui.btn_arrowDouble.setIconSize(QtCore.QSize(40, 40))
        ## CURVES ##
        self.ui.btn_shiftCrv.setIcon(QIcon(os.path.dirname(__file__) + '/ico/shuffle.png'))
        self.ui.btn_shiftCrv.setIconSize(QtCore.QSize(20, 20))

        ## INTERFACE ##
        self.ui.btn_win_pink.setIcon(QIcon(os.path.dirname(__file__) + '/ico/win_pink.png'))
        self.ui.btn_win_pink.setIconSize(QtCore.QSize(30, 30))
        self.ui.btn_win_green.setIcon(QIcon(os.path.dirname(__file__) + '/ico/win_green.png'))
        self.ui.btn_win_green.setIconSize(QtCore.QSize(30, 30))
        self.ui.btn_win_orange.setIcon(QIcon(os.path.dirname(__file__) + '/ico/win_orange.png'))
        self.ui.btn_win_orange.setIconSize(QtCore.QSize(30, 30))
        self.ui.btn_win_blue.setIcon(QIcon(os.path.dirname(__file__) + '/ico/win_blue.png'))
        self.ui.btn_win_blue.setIconSize(QtCore.QSize(30, 30))
        self.ui.btn_win_grey.setIcon(QIcon(os.path.dirname(__file__) + '/ico/win_grey.png'))
        self.ui.btn_win_grey.setIconSize(QtCore.QSize(30, 30))

    @functionsLib.undoable
    def shape_to_transform(self):
        shpLib.shape_to_transforms(mc.ls(sl=True)[0], mc.ls(sl=True)[1:len(mc.ls(sl=True))], replace=self.ui.rbtn_shpReplace.isChecked(),
                                 delState=self.ui.cb_delete.isChecked(), location=self.ui.rBtn_shpInPlace.isChecked(),
                                 instance=self.ui.cb_instance.isChecked())

    def set_interface(self):
        if self.ui.cb_instance.isChecked():
            self.ui.cb_delete.setChecked(False)
            #self.ui.cb_delete.setStyleSheet('color: rgb(128, 128, 128)')
            self.ui.cb_delete.setStyleSheet('QCheckBox{color: rgb(128, 128, 128)} QCheckBox::indicator{background-color: rgb(76, 76, 76)}')
            self.ui.cb_delete.setEnabled(False)
        else:
            self.ui.cb_delete.setEnabled(True)
            self.ui.cb_delete.setStyleSheet('color: none')

    def set_color_btn(self):
        label = self.sender()
        set_color_shape(label.text())

    def set_form_btn(self):
        label = self.sender()
        self.set_form_shape(label.text())

    @functionsLib.undoable
    def set_form_shape(self, form):
        sel = mc.ls(sl=True)
        crv = shpLib.shp_form(form, 'RGB', 'blue5', name=None)
        shpLib.shape_size(crv, size=[self.ui.dsb_sizeX.value(), self.ui.dsb_sizeY.value(), self.ui.dsb_sizeZ.value()],
                          rotShp=[self.ui.dsb_rotX.value(), self.ui.dsb_rotY.value(), self.ui.dsb_rotZ.value()])
        if sel:
            shpLib.shape_to_transforms(crv, sel, replace=True, delState=True, location=False, instance=False)

    def select_list(self):
        text = self.ui.le_select.text()
        all = mc.ls(sl=False, long=True)
        ls_text = []
        for obj in all:
            short = obj.split("|")[-1]
            if self.ui.cb_selectType.currentIndex() == 0:
                if text in short:
                    ls_text.append(obj)
            elif self.ui.cb_selectType.currentIndex() == 1:
                if short.startswith(text):
                    ls_text.append(obj)
            elif self.ui.cb_selectType.currentIndex() == 2:
                if short.endswith(text):
                    ls_text.append(obj)
        mc.select(ls_text)

    ########## RIG

    @functionsLib.undoable
    def create_nurbs_attach(self):
        if self.ui.cb_parentInSA.isChecked():
            nurbsAttach.nurbs_attach(parentInSA=True)
        else:
            nurbsAttach.nurbs_attach(parentInSA=False)

    # Filter attribute fonctions________________________________________________________________________________________

    def get_list_attr(self):
        attr = self.ui.le_get_list_attr.text()
        if attr:
            ls_attr_wanted = attributesLib.filter_attr(attrTarget=attr, searchList=None, typ='transform', extra=False)
            print "\n\nLength list = {}".format(len(ls_attr_wanted))
            pprint.pprint(ls_attr_wanted)
            if self.ui.check_box_select.isChecked():
                mc.select(ls_attr_wanted)

        else:
            print comment.format_comment("Please, enter the attribute name you are looking for")

    def get_list_attr_state(self):
        attr = self.ui.le_get_list_attr.text()
        if self.ui.cb_box_attr_type.currentIndex() == 0:  # Integer
            state = int(self.ui.le_get_list_attr_state.text())
        if self.ui.cb_box_attr_type.currentIndex() == 1:  # Float
            state = float(self.ui.le_get_list_attr_state.text())
        if self.ui.cb_box_attr_type.currentIndex() == 2:  # String
            state = self.ui.le_get_list_attr_state.text()

        if attr and state is not None:
            ls_attr_wanted = attributesLib.get_attr_state(attrTarget=attr, stateTarget=state, typ='transform')
            print "\n\nLength list = {}".format(len(ls_attr_wanted))
            pprint.pprint(ls_attr_wanted)
            if self.ui.check_box_select.isChecked():
                mc.select(ls_attr_wanted)

        elif not attr and state is None:
            print comment.format_comment("Please, enter the attribute and the state you are looking for")
        elif not attr:
            print comment.format_comment("Please, enter the attribute name you are looking for")
        elif state is None:
            print comment.format_comment("Please, enter the state you are looking for")

    ########## SPACE SWITCH

    def set_ctrl_space_switch(self):
        obj = self.set_obj()
        if obj:
            self.ui.le_ctrlSpaceSwitch.clear()
            self.ui.le_ctrlSpaceSwitch.setText(obj[0])

    def set_obj(self):
        if len(mc.ls(sl=True)) > 1:
            print 'Please select ONLY one object'
            return []
        elif len(mc.ls(sl=True)) == 0:
            print 'Please select one object'
            return []
        else:
            obj = mc.ls(sl=True)
            return obj

    @functionsLib.undoable
    def crt_space_switch(self):
        if self.ui.rBtn_parent.isChecked():
            cnst_type = 'parent'
        elif self.ui.rBtn_point.isChecked():
            cnst_type = 'point'
        elif self.ui.rBtn_orient.isChecked():
            cnst_type = 'orient'
        crtSpaceSwitch(mc.ls(sl=True), self.ui.le_ctrlSpaceSwitch.text(), cnst_type)


    #####  CURVE  #####
    def shift_curve(self):
        """
        use pymel
        :param way: sens de rotation des indexs
        petoc = polyEdgeToCurve
        :return:
        """
        way = self.ui.cb_reverse.isChecked()
        curve = mc.ls(sl=True)[0]
        curveShape = mc.listRelatives(curve, shapes=True)[0]
        petoc = mc.listConnections(curveShape + '.create', destination=True)[0]

        mc.select(petoc)
        petc = pm.selected()[0]
        components = petc.inputComponents.get()
        if way:
            components = components[-2:-1] + components[:-1]
        else:
            components = components[1:] + components[1:2]
        attr = [len(components)] + components
        petc.inputComponents.set(attr, type="componentList")
        mc.select(curve)


    ########## INTERFACE

    def set_win_orange(self):
        qApp.setStyleSheet("QMenuBar{background-color: rgb(235,90,25); color: rgb(255,255,255);}")

    def set_win_pink(self):
        qApp.setStyleSheet("QMenuBar{background-color: rgb(255,85,155); color: rgb(255,255,255);}")

    def set_win_blue(self):
        qApp.setStyleSheet("QMenuBar{background-color: rgb(0,130,215); color: rgb(255,255,255);}")

    def set_win_green(self):
        qApp.setStyleSheet("QMenuBar{background-color: rgb(20,165,65); color: rgb(255,255,255);}")

    def set_win_grey(self):
        qApp.setStyleSheet("QMenuBar{background-color: rgb(76,76,76); color: rgb(255,255,255);}")

@functionsLib.undoable
def set_color_shape(color):
    sel = mc.ls(sl=True) or []
    for obj in sel:
        lShp = mc.listRelatives(obj, shapes=True) or []
        for shp in lShp:
            shpLib.set_color(shp, colorType='RGB', color=color)
        if mc.nodeType(obj) == 'nurbsCurve' or 'transform':
            shpLib.set_color(obj, colorType='RGB', color=color)

def rnm_ctrl_shp():
    print 'RENAME SHAPE'
    if mc.ls(sl=True):
        ls_ctrl = mc.ls(sl=True)
    else:
        ls_ctrl = mc.ls(type='transform')
    all_controls = []
    #if mc.attributeQuery('nodeType', node=o, ex=True) and mc.getAttr(o + '.nodeType') == 'control':
    for obj in ls_ctrl:
        if obj.startswith('c_') or ':c_' in obj:
            all_controls.append(obj)
    shapesLib.rename_shapes(all_controls)

def set_joint_draw(target, state=2):
    if target == 'all':
        lTarget = mc.ls(type='joint', allPaths=True) or []
    elif target == 'sel':
        lTarget = mc.ls(sl=True)
    for sk in lTarget:
        if not mc.listConnections(sk + '.drawStyle', connections=True, destination=True, source=False):
            if not mc.getAttr(sk + '.drawStyle', lock=True):
                mc.setAttr(sk + '.drawStyle', state)

def set_joint_draw_sel():
    set_joint_draw(target='sel')

def set_joint_draw_all():
    set_joint_draw(target='all')

def set_handle_hide():
    for obj in mc.ls(sl=True) or []:
        mc.setAttr(obj + '.displayHandle', 0)

def set_handle_show():
    for obj in mc.ls(sl=True) or []:
        mc.setAttr(obj + '.displayHandle', 1)


##### JOINT #####
def show_joint_orient():
    for obj in mc.ls(sl=True):
        if mc.nodeType(obj) == 'joint':
            mc.setAttr(obj + '.jointOrientX', channelBox=True)
            mc.setAttr(obj + '.jointOrientY', channelBox=True)
            mc.setAttr(obj + '.jointOrientZ', channelBox=True)

def hide_joint_orient():
    for obj in mc.ls(sl=True):
        if mc.nodeType(obj) == 'joint':
            mc.setAttr(obj + '.jointOrientX', channelBox=False)
            mc.setAttr(obj + '.jointOrientY', channelBox=False)
            mc.setAttr(obj + '.jointOrientZ', channelBox=False)



############## SPACE SWITCH ##############
def getSwitchNode(ctrl):
    '''
    get networkNode for spaceSwitch options or create it
    '''
    node = ctrl
    nspace = ''
    if ':' in ctrl:
        node = lib_namespace.getNodeName(ctrl)
        nspace = lib_namespace.getNspaceFromObj(ctrl) + ':'
    switchNode = ''
    nSwitchNode = 'menu_spaceSwitch' + node[len(node.split('_')[0]):][1].capitalize() + node[len(
        node.split('_')[0]) + 2:].replace('_', '')
    if not mc.attributeQuery('menuSpaceSwitch', node=ctrl, ex=True):
        mc.addAttr(ctrl, ln='menuSpaceSwitch', at='message')
    if mc.connectionInfo(ctrl + '.menuSpaceSwitch', id=True):
        switchNode = mc.listConnections(ctrl + '.menuSpaceSwitch')[0]
    if not switchNode:
        switchNode = mc.createNode('network', n=nSwitchNode)
        mc.connectAttr(switchNode + '.message', ctrl + '.menuSpaceSwitch', f=True)
        if not mc.attributeQuery('targets', node=switchNode, ex=True):
            mc.addAttr(switchNode, ln='targets', dt='string', multi=True)
            mc.setAttr(switchNode + '.targets[0]', 'Root', type='string')
        if not mc.attributeQuery('attrs', node=switchNode, ex=True):
            mc.addAttr(switchNode, ln='attrs', dt='string', multi=True)
            mc.setAttr(switchNode + '.attrs[0]', '', type='string')
        if not mc.attributeQuery('constraint', node=switchNode, ex=True):
            mc.addAttr(switchNode, ln='constraint', at='message')

    return switchNode

def crtSpaceSwitch(lTargets, ctrl, cnst_type):
    '''
    create constraint,  add and connect followsAttr ofrom ctrl to constraint attr weight
    '''
    if len(lTargets) > 4:
        print 'you can not give more than 4 targets'
    else:
        node = ctrl
        nspace = ''
        if ':' in ctrl:
            node = lib_namespace.getNodeName(ctrl)
            nspace = lib_namespace.getNspaceFromObj(ctrl) + ':'
        root = nspace + 'root' + node[len(node.split('_')[0]):]
        # root = mc.listRelatives(ctrl, p=True)[0]
        switchNode = getSwitchNode(ctrl)
        for target in lTargets:
            if cnst_type == 'parent':
                cnst = mc.parentConstraint(target, root, mo=True)[0]
            elif cnst_type == 'orient':
                cnst = mc.orientConstraint(target, root, mo=True)[0]
            elif cnst_type == 'point':
                cnst = mc.pointConstraint(target, root, mo=True)[0]
            if not mc.isConnected(cnst + '.message', switchNode + '.constraint'):
                mc.connectAttr(cnst + '.message', switchNode + '.constraint')
            nAttr = target
            if ':' in target:
                nAttr = lib_namespace.getNodeName(target)
            if '_' in nAttr:
                nAttr = nAttr[len(nAttr.split('_')[0]):][1].capitalize() + nAttr[len(nAttr.split('_')[0]) + 2:].replace(
                    '_', '')
            if not mc.attributeQuery('follow' + nAttr, node=ctrl, ex=True):
                mc.addAttr(ctrl, ln='follow' + nAttr, at='float', min=0, max=10, keyable=True)
            mc.setAttr(ctrl + '.follow' + nAttr, k=True, cb=True)
            mc.setAttr(ctrl + '.follow' + nAttr, keyable=True)
            mDL = mc.createNode('multDoubleLinear', n='mDL_follow' + nAttr)
            mc.connectAttr(ctrl + '.follow' + nAttr, mDL + '.input1', f=True)
            mc.setAttr(mDL + '.input2', 0.1)
            cnstGraph = getCnstGraph(root)
            weghtAtttr = cnstGraph[cnst]['driverAttr'][target]
            if not mc.isConnected(mDL + '.output', cnst + '.' + weghtAtttr):
                mc.connectAttr(mDL + '.output', cnst + '.' + weghtAtttr, f=True)
            id = mc.getAttr(switchNode + '.targets', size=True)
            mc.setAttr(switchNode + '.targets[' + str(id) + ']', nAttr, type='string')
            mc.setAttr(switchNode + '.attrs[' + str(id) + ']', 'follow' + nAttr, type='string')

    # add SetBindPose


############## TOOLS ##############


def open_attr_box():
    from ...tools_ui import attribute_box
    ui = attribute_box.AttrBox(parent=get_maya_main_window())
    ui.show()

#def open_vis_tool():
#    #from python_lib_juline.tools_ui import constraint_tool
#    open_ui.open_ui(constraint_tool.ConstraintTool)

def open_bend_tool():
    print 'Bend'
    from ...tools_ui import bend_tool
    ui = bend_tool.BendTool(parent=get_maya_main_window())
    ui.show()

#def open_squash_tool():
#    #from ...tools_ui import constraint_tool
#    open_ui.open_ui(constraint_tool.ConstraintTool)

#def open_renamer():
#    #from ...tools_ui import constraint_tool
#    open_ui.open_ui(constraint_tool.ConstraintTool)

#def open_loc_tool():
#    #from ...tools_ui import constraint_tool
#    open_ui.open_ui(constraint_tool.ConstraintTool)

#def open_constraint_tool():
#    from ...tools_ui import constraint_tool
#    reload(constraint_tool)
#    ui = constraint_tool.ConstraintTool(parent=get_maya_main_window())
#    ui.show()


def getCnstGraph(node):
    ## DKATZ
    dicLCnst = {}
    lCnst = node
    if not mc.nodeType(node, i='constraint'):
        lCnst = list(set(mc.listConnections(node, type='constraint')))
    for cnst in lCnst:
        dicCnst = {}
        dicDrivers = {}
        dicCnst['type'] = mc.objectType(cnst)
        dicCnst['driven'] = list(set(mc.listConnections(cnst, d=True, s=False, type='transform')))
        if cnst in dicCnst['driven']:
            dicCnst['driven'].remove(cnst)
        incTrgt = mc.getAttr(cnst + '.target', size=True)
        for i in range(0, incTrgt):
            attr = mc.connectionInfo(cnst + '.target[' + str(i) + '].targetWeight', sfd=True).split('.')[-1]
            driver = mc.connectionInfo(cnst + '.target[' + str(i) + '].targetParentMatrix', sfd=True).split('.')[0]
            dicDrivers[driver] = attr
        dicCnst['drivers'] = dicDrivers.keys()
        dicCnst['driverAttr'] = dicDrivers
        dicLCnst[cnst] = dicCnst
    return dicLCnst


def crt_rig_add(offset=2, parent="ALL|RIG", bBox=None,
                       worldConstraint=True):
    if not mc.objExists("ALL|RIG"):
        mc.createNode('transform', n="RIG", p="ALL")
    if not bBox:
        bBox = get_bounding_box("ALL")
    rigAdd = mc.curve(n="c_rigAdd", d=1,
                        p=[(0.75, 0, 0), (1, 0.25, 0), (1.25, 0, 0), (1, -0.25, 0), (0.75, 0, 0), (1, 0, 0.25),
                           (1.25, 0, 0), (1, 0, -0.25), (1, 0.25, 0), (1, 0, 0.25), (1, -0.25, 0), (1, 0, -0.25),
                           (0.75, 0, 0), (0, 0, 0), (-0.75, 0, 0), (-1, 0.25, 0), (-1.25, 0, 0), (-1, -0.25, 0),
                           (-0.75, 0, 0), (-1, 0, 0.25), (-1.25, 0, 0), (-1, 0, -0.25), (-1, 0.25, 0),
                           (-1, 0, 0.25), (-1, -0.25, 0), (-1, 0, -0.25), (-0.75, 0, 0), (0, 0, 0), (0, 0.75, 0),
                           (0, 1, -0.25), (0, 1.25, 0), (0, 1, 0.25), (0, 0.75, 0), (-0.25, 1, 0), (0, 1.25, 0),
                           (0.25, 1, 0), (0, 1, 0.25), (-0.25, 1, 0), (0, 1, -0.25), (0.25, 1, 0), (0, 0.75, 0),
                           (0, 0, 0), (0, -0.75, 0), (0, -1, -0.25), (0, -1.25, 0), (0, -1, 0.25), (0, -0.75, 0),
                           (-0.25, -1, 0), (0, -1.25, 0), (0.25, -1, 0), (0, -1, -0.25), (-0.25, -1, 0),
                           (0, -1, 0.25), (0.25, -1, 0), (0, -0.75, 0), (0, 0, 0), (0, 0, -0.75), (0, 0.25, -1),
                           (0, 0, -1.25), (0, -0.25, -1), (0, 0, -0.75), (-0.25, 0, -1), (0, 0, -1.25),
                           (0.25, 0, -1), (0, 0.25, -1), (-0.25, 0, -1), (0, -0.25, -1), (0.25, 0, -1),
                           (0, 0, -0.75), (0, 0, 0), (0, 0, 0.75), (0, 0.25, 1), (0, 0, 1.25), (0, -0.25, 1),
                           (0, 0, 0.75), (-0.25, 0, 1), (0, 0, 1.25), (0.25, 0, 1), (0, 0.25, 1), (-0.25, 0, 1),
                           (0, -0.25, 1), (0.25, 0, 1), (0, 0, 0.75)])
    lBaseAttr = ['.tx', '.ty', '.tz', '.rx', '.ry', '.rz', '.sx', '.sy', '.sz', '.v']
    for attr in lBaseAttr:
        mc.setAttr(rigAdd + attr, lock=True, keyable=False, channelBox=False)
    shp = set_shape(rigAdd, 6)
    root = mc.createNode('transform', n="c_rigAdd")
    mc.parent(rigAdd, root)
    mc.setAttr(root + '.t', (bBox['maxX'] + bBox['minX']) / 2, bBox['maxY'] + offset,
                 (bBox['maxZ'] + bBox['minZ']) / 2)
    mc.parent(root, parent)
    world_name = "ALL|WORLD"
    if worldConstraint and mc.objExists(world_name):
        mc.parentConstraint(world_name, root, mo=True)
        mc.scaleConstraint(world_name, root, mo=True)


def get_bounding_box(obj="ALL"):
    if not mc.objExists(obj):
        return None

    bBox = mc.exactWorldBoundingBox(obj)
    lKeys = ['minX', 'minY', 'minZ', 'maxX', 'maxY', 'maxZ']
    dicBbox = {}
    for i in range(0, len(bBox)):
        dicBbox[lKeys[i]] = bBox[i]
    return dicBbox


def set_shape(obj, color):
    shp = mc.listRelatives(obj, s=True)[0]
    newShp = mc.rename(shp, obj+'Shape')
    mc.setAttr(newShp+'.overrideEnabled', 1)
    mc.setAttr(newShp+'.overrideColor', color)
    return newShp