# coding: utf-8
# Copyright (c) 2019 Juline BRETON
#
#  Use pop up win for btn not already connected (load, update, remove)

import os

from ellipse_rig.tools.juline.python_lib_juline.utils.maya_widget import MayaWidget, load_ui
from ellipse_rig.tools.juline.python_lib_juline.utils import comment
from ellipse_rig.tools.juline.python_lib_juline.library import attributesLib
from ellipse_rig.assets.characters import guide_spine, guide_head, guide_eyes, guide_leg, guide_tool, guide_arm

from ellipse_rig.assets.characters.character_guide_ui import position_locator

from PySide2 import QtCore
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import qApp, QToolTip

import maya.cmds as mc

class CharacterGuide(MayaWidget):
    def __init__(self, parent=None):
        MayaWidget.__init__(self, name="Character GUIDE CREATOR", parent=parent)

        self.ui = load_ui(os.path.join(os.path.dirname(__file__), 'guide_creator.ui'))
        self.setWindowIcon(QIcon(os.path.dirname(__file__) + '/ico/skeleton2.png'))
        self.main_layout.addWidget(self.ui)

        ### SPINE ###
        self.ui.btn_build_spine.clicked.connect(self.build_spine)
        self.ui.btn_load_spine.clicked.connect(self.load_spine)
        self.ui.btn_update_spine.clicked.connect(self.update_spine)
        ### HEAD ###
        self.ui.btn_build_head.clicked.connect(self.build_head)
        self.ui.btn_load_head.clicked.connect(self.load_head)
        self.ui.btn_update_head.clicked.connect(self.update_head)
        ### EYES ###
        self.ui.btn_build_eye.clicked.connect(self.build_eye)
        ### LEG ###
        self.ui.btn_build_leg.clicked.connect(self.build_leg)
        self.ui.btn_load_leg.clicked.connect(self.load_leg)
        self.ui.btn_update_leg.clicked.connect(self.update_leg)
        ### ARM ###
        self.ui.btn_build_arm.clicked.connect(self.build_arm)
        self.ui.btn_load_arm.clicked.connect(self.load_arm)
        self.ui.btn_update_arm.clicked.connect(self.update_arm)
        ### SYMMETRISE ###
        self.ui.btn_symmetrise.clicked.connect(self.symmetrise)
        ### REMOVE ###
        self.ui.btn_remove.clicked.connect(self.remove)
        ### UPDATE RIG ###
        self.ui.btn_connect_rig.clicked.connect(self.connect_rig)
        ### REPARENT MODULE TO ###
        self.ui.btn_reparent_module.clicked.connect(self.reparent_module)

    def reload(self):
        from ellipse_rig.assets.characters import character_guide_ui
        from ellipse_rig.tools.juline.python_lib_juline.utils.maya_widget import get_maya_main_window

        reload(character_guide_ui)

        im = character_guide_ui.CharacterGuide(parent=get_maya_main_window())
        im.show()

    def find_tpl_info(self):
        if len(mc.ls(sl=True)) > 1:
            print 'Please select only one object'
        if len(mc.ls(sl=True)) == 1:
            obj = mc.ls(sl=True)[0]
            tpl_info = mc.getAttr(obj + '.infPart')
            module_type = mc.getAttr(tpl_info + '.moduleType')
            inc = mc.getAttr(tpl_info + '.incInfo')
            if mc.objExists(tpl_info + '.side'):
                side = mc.getAttr(tpl_info + '.side')
            else:
                #Search side with name TPL INFO
                if tpl_info.endswith('_L'):
                    side = 'L'
                elif tpl_info.endswith('_R'):
                    side = 'R'
                else:
                    side = 'None'
            return tpl_info, module_type, side, inc
        if len(mc.ls(sl=True)) == 0:
            print 'Please select something'
            return None

    def update_module(self, module_type, inc, side=None):
        reload(position_locator)
        # find TPL_info : via nom du module et incrementation
        if not side:
            tpl_info = 'tplInfo_' + module_type + '_' + inc
        else:
            tpl_info = 'tplInfo_' + module_type + '_' + inc + '_' + side
        # avec extra attr lister les ctrl cible
        ls_attr_mult = mc.listAttr(tpl_info, userDefined=True, multi=True)
        master_index = ls_attr_mult.index('masterTpl[0]')
        # create loc
        grp_loc_module = position_locator.create_module_group_locator(tpl_info)
        ls_loc_pos = []
        for attr in ls_attr_mult[master_index:]:
            tpl_ctrl = mc.listConnections(tpl_info + '.' + attr, destination=True)
            # skip attr infoNumbMb
            if not 'infoNumbMb' in attr:
                if 'endMb' in attr:
                    ls_endMb = mc.getAttr(tpl_info + '.' + attr)
                    # convert string to list
                    import ast
                    ls_endMb = ast.literal_eval(ls_endMb)
                    typ = type(ls_endMb)
                    if typ is not 'int':
                        for endMb in ls_endMb:
                            loc_pos = position_locator.create_locator_position(endMb)
                            ls_loc_pos.append(loc_pos)
                else:
                    loc_pos = position_locator.create_locator_position(tpl_ctrl[0])
                    ls_loc_pos.append(loc_pos)
        for loc in ls_loc_pos:
            mc.parent(loc, grp_loc_module)
        # transfert attribute parent, child and connect them
        reload(attributesLib)
        attributesLib.transfer_attr(tpl_info, grp_loc_module, 'parent', delete=False)
        attributesLib.transfer_attr(tpl_info, grp_loc_module, 'children', delete=False)

        # Delete module
        node_to_delete = mc.getAttr(tpl_info + '.delPart[0]')
        mc.delete(node_to_delete)

        # Rebuild module
        mc.select(clear=True)

        if module_type == 'spine':
            self.build_spine()
        elif module_type == 'head':
            self.build_head()
        elif module_type == 'leg':
            self.build_leg()
        elif module_type == 'arm':
            self.build_arm()

        attributesLib.transfer_connection(grp_loc_module, tpl_info, 'parent')
        attributesLib.transfer_connection(grp_loc_module, tpl_info, 'children')

        # Snap on locators
        ls_loc_dont_use = []
        for loc in ls_loc_pos:
            tpl = loc.replace('loc', 'tpl')
            if mc.objExists(tpl):
                position_locator.snap(tpl, loc)
            else:
                ls_loc_dont_use.append(loc)
        if ls_loc_dont_use:
            print 'Not use for snap :', ls_loc_dont_use

    def load_side(self, module_type, side):
        if module_type == 'spine':
            ls_btn = [self.ui.rBtn_spine_R, self.ui.rBtn_spine_L, self.ui.rBtn_spine_None]
        if module_type == 'head':
            ls_btn = [self.ui.rBtn_head_R, self.ui.rBtn_head_L, self.ui.rBtn_head_None]
        if module_type == 'eye':
            ls_btn = [self.ui.rBtn_eye_R, self.ui.rBtn_eye_L, self.ui.rBtn_eye_None]
        if module_type == 'leg':
            ls_btn = [self.ui.rBtn_leg_R, self.ui.rBtn_leg_L, self.ui.rBtn_leg_None]
        if module_type == 'arm':
            ls_btn = [self.ui.rBtn_arm_R, self.ui.rBtn_arm_L, self.ui.rBtn_arm_None]

        if side == 'R':
            ls_btn[0].setChecked(True)
        elif side == 'L':
            ls_btn[1].setChecked(True)
        elif side == 'None':
            ls_btn[2].setChecked(True)

    # SPINE #

    def build_spine(self):
        reload(guide_spine)
        for side_btn in [self.ui.rBtn_spine_R, self.ui.rBtn_spine_L, self.ui.rBtn_spine_None]:
            if side_btn.isChecked():
                if side_btn.text() == 'None':
                    spine_side = ''
                else:
                    spine_side = side_btn.text()
        spine_ik = self.ui.spine_ik.value()
        spine_sk = self.ui.spine_sk.value()
        if self.ui.l_spine_inc.text():
            incVal = self.ui.l_spine_inc.text()
        else:
            incVal = None
        guide = guide_spine.Spine(name='spine', side=spine_side, selObj=mc.ls(sl=True), numb=spine_ik, numbSk=spine_sk, incVal=incVal)
        dic = guide.createSpine()
        self.connect_rig(ls_tpl_info=[dic['infoName']])

    def load_spine(self):
        tpl_info, module_type, side, inc = self.find_tpl_info()
        if module_type:
            if module_type == 'spine':
                ls_ctrl = mc.getAttr(tpl_info + '.ctr[*]')
                self.ui.spine_ik.setValue(len(ls_ctrl))
                if mc.objExists(tpl_info + '.boxSk'):
                    ls_sk = mc.getAttr(tpl_info + '.boxSk[*]')
                else:
                    ls_sk = find_sk_box(tpl_info)
                self.ui.spine_sk.setValue(len(ls_sk))
                self.load_side('spine', side)
                self.ui.l_spine_inc.setText(inc)
            else:
                print 'The element selected is not a spine module but a module ', module_type

    def update_spine(self):
        self.update_module(module_type='spine', inc=self.ui.l_spine_inc.text())

    # HEAD #

    def build_head(self):
        reload(guide_head)
        for side_btn in [self.ui.rBtn_head_R, self.ui.rBtn_head_L, self.ui.rBtn_head_None]:
            if side_btn.isChecked():
                if side_btn.text() == 'None':
                    head_side = ''
                else:
                    head_side = side_btn.text()
        neck_ik = self.ui.neck_ik.value()
        neck_sk = self.ui.neck_sk.value()
        inc = self.ui.l_head_inc.text()
        guide = guide_head.Head(name='head', side=head_side, selObj=mc.ls(sl=True), numbNeck=neck_ik, numbSk=neck_sk, incVal=inc)
        dic = guide.createHead()
        self.connect_rig(ls_tpl_info=[dic['infoName']])

    def load_head(self):
        tpl_info, module_type, side, inc = self.find_tpl_info()

        print 'You just select a MODULE :', module_type
        if module_type:
            if module_type == 'head':
                tpl_info_parent = mc.listConnections(tpl_info + '.parent')
                mc.select(tpl_info_parent[0])
                self.load_head()

            elif module_type == 'neck':
                ls_ctrl = mc.getAttr(tpl_info + '.ctr[*]')
                self.ui.neck_ik.setValue(len(ls_ctrl))
                ls_sk = mc.getAttr(tpl_info + '.boxSk[*]')
                self.ui.neck_sk.setValue(len(ls_sk))
                self.load_side('head', side)
                self.ui.l_head_inc.setText(inc)
            else:
                print "Your head module parent is a " + module_type + " module"
                self.ui.neck_ik.setValue(0)
                self.ui.neck_sk.setValue(0)
            #else:
            #    print 'The element selected is not a neck module but a module ', module_type

    def update_head(self):
        comment.format_comment('This button is not connected', center=False, frame=False)
        self.update_module(module_type='head', inc=self.ui.l_head_inc.text())

    # EYE #

    def build_eye(self):
        reload(guide_eyes)
        for side_btn in [self.ui.rBtn_eye_R, self.ui.rBtn_eye_L, self.ui.rBtn_eye_None]:
            if side_btn.isChecked():
                if side_btn.text() == 'None':
                    eye_side = ''
                else:
                    eye_side = side_btn.text()
        guide = guide_eyes.Eyes(name='eye', side=eye_side, selObj=mc.ls(sl=True))
        guide.createEyes()

    # LEG #

    def build_leg(self):
        reload(guide_leg)
        for side_btn in [self.ui.rBtn_leg_R, self.ui.rBtn_leg_L]:
            if side_btn.isChecked():
                #if side_btn.text() == 'None':
                #    leg_side = ''
                #else:
                leg_side = side_btn.text()
        leg_ik = self.ui.leg_ik.value()
        leg_sk = self.ui.leg_sk.value()
        foot_roll = self.ui.foot_roll.value()
        foot_toes = self.ui.foot_toes.value()
        foot_phalange = self.ui.foot_phalange.value()
        inc = self.ui.l_leg_inc.text()
        guide = guide_leg.Leg(name='leg', side=leg_side, selObj=mc.ls(sl=True), numb=leg_ik, numbSk=leg_sk, numbMidMb=foot_roll,
                              numbEndMb=foot_toes, subDvEndMb=foot_phalange, incVal=inc)
        dic = guide.createLeg()
        self.connect_rig(ls_tpl_info=[dic['infoName']])

    def load_leg(self):
        tpl_info, module_type, side, inc = self.find_tpl_info()
        if module_type:
            if module_type == 'leg':
                self.ui.leg_ik.setValue(int(mc.getAttr(tpl_info + '.infoNumbMb[0]')))
                ls_sk = find_sk_box(tpl_info)
                self.ui.leg_sk.setValue(len(ls_sk))
                self.ui.foot_roll.setValue(int(mc.getAttr(tpl_info + '.infoNumbMb[1]')))
                self.ui.foot_toes.setValue(int(mc.getAttr(tpl_info + '.infoNumbMb[2]')))
                self.ui.foot_phalange.setValue(int(mc.getAttr(tpl_info + '.infoNumbMb[3]')))
                self.load_side('leg', side)
                self.ui.l_leg_inc.setText(inc)
            else:
                print 'The element selected is not a leg module but a module ', module_type

    def update_leg(self):
        tpl_info, module_type, side, inc = self.find_tpl_info()
        self.update_module(module_type=module_type, inc=inc, side=side)

    # ARM #

    def build_arm(self):
        reload(guide_arm)
        for side_btn in [self.ui.rBtn_arm_R, self.ui.rBtn_arm_L]:
            if side_btn.isChecked():
                arm_side = side_btn.text()
        arm_ik = self.ui.arm_ik.value()
        arm_sk = self.ui.arm_sk.value()
        hand_roll = self.ui.hand_roll.value()
        hand_finger = self.ui.hand_finger.value()
        hand_phalange = self.ui.hand_phalange.value()
        inc = self.ui.l_arm_inc.text()
        guide = guide_arm.Arm(name='arm', side=arm_side, selObj=mc.ls(sl=True), numb=arm_ik, numbSk=arm_sk, numbMidMb=hand_roll,
                              numbEndMb=hand_finger, subDvEndMb=hand_phalange, incVal=inc)
        dic = guide.createArm()
        self.connect_rig(ls_tpl_info=[dic['infoName']])

    def load_arm(self):
        tpl_info, module_type, side, inc = self.find_tpl_info()
        if module_type:
            if module_type == 'arm':
                self.ui.arm_ik.setValue(int(mc.getAttr(tpl_info + '.infoNumbMb[0]')))
                ls_sk = find_sk_box(tpl_info)
                self.ui.arm_sk.setValue(len(ls_sk))
                self.ui.hand_roll.setValue(int(mc.getAttr(tpl_info + '.infoNumbMb[1]')))
                self.ui.hand_finger.setValue(int(mc.getAttr(tpl_info + '.infoNumbMb[2]')))
                self.ui.hand_phalange.setValue(int(mc.getAttr(tpl_info + '.infoNumbMb[3]')))
                self.load_side('arm', side)
                self.ui.l_arm_inc.setText(inc)
            else:
                print 'The element selected is not a arm module but a module ', module_type

    def update_arm(self):
        tpl_info, module_type, side, inc = self.find_tpl_info()
        self.update_module(module_type=module_type, inc=inc, side=side)

    # GENERAL #

    def symmetrise(self):
        reload(guide_tool)
        guide_tool.symCtr(side='L')

    def remove(self):
        comment.format_comment('This button is not connected', center=False, frame=False)

    def connect_rig(self, ls_tpl_info=[]):
        if not ls_tpl_info:
            # Find ls tpl info
            ls_tpl_info = attributesLib.filter_attr(attrTarget='moduleDataTpl')
        for tpl_info in ls_tpl_info:
            # Find list attr multi
            ls_attr_mult = mc.listAttr(tpl_info, userDefined=True)
            if 'masterTpl' in ls_attr_mult:
                index = ls_attr_mult.index('masterTpl')
                for attr in ls_attr_mult[index:]:
                    # Ordre des attr = Ordre de creation / mise en place du rig = Info de placement
                    name_attr = tpl_info + '.' + attr
                    # Check type attr
                    if mc.getAttr(name_attr, type=True) == 'TdataCompound':
                        ls_get_attr_mult = mc.getAttr(name_attr + '[*]')
                        # Check type attr
                        size_attr = mc.getAttr(name_attr, size=True)
                        ls_attr_clean = []
                        if size_attr == 1:
                            ls_attr_clean = [ls_get_attr_mult]
                        elif size_attr > 1:
                            ls_attr_clean = clean_attr_setted_multiple_time(tpl_info, attr)

                        for i in range(len(ls_attr_clean)):
                            name_set = mc.getAttr(name_attr + '[' + str(i) + ']')
                            if mc.objExists(name_set):
                                print 'Connecting : ', name_set, '--->', name_attr + '[' + str(i) + ']'
                                if not mc.objExists(name_set + '.name'):
                                    mc.addAttr(name_set, longName='name', dataType='string')
                                    mc.setAttr(name_set + '.name', name_set, type='string')
                                mc.connectAttr(name_set + '.name', name_attr + '[' + str(i) + ']')

        # "tplSA_" + module + "Sk_" + incInfo + side > son nombre d'enfants = nombre de sk (pour setter l'outil)

    def reparent_module(self):
        parentModule(mc.ls(sl=True), follow=self.ui.cb_const_to_parent.isChecked())

def parentModule(lNodes, follow=True):
    father = lNodes[-1]
    lNodes.remove(father)
    for child in lNodes:
        anchor = mc.listRelatives(child, p=True)[0]
        lCnst = mc.listConnections(anchor, type='parentConstraint', d=True) or []
        if lCnst:
            mc.delete(lCnst[0])

        if follow:
            cnst = mc.parentConstraint(father, anchor, mo=True)[0]
            if not mc.attributeQuery('driver', n=anchor, ex=True):
                mc.addAttr(cnst, ln='driver', dt="string")
            if not mc.attributeQuery('driven', n=cnst, ex=True):
                mc.addAttr(cnst, ln='driven', dt="string")
            mc.connectAttr(father + '.message', cnst + '.driver', f=True)
            mc.connectAttr(child + '.message', cnst + '.driven', f=True)
        dataNode = mc.getAttr(child + '.infPart')
        id = mc.getAttr(dataNode + '.masterTpl', s=True)
        mc.setAttr(dataNode + '.masterTpl[' + str(id) + ']', child, type='string')
        dataNodeFather = mc.getAttr(father + '.infPart')
        mc.connectAttr(dataNodeFather + '.children', dataNode + '.parent', f=True)
        print 'SUCCES:', child, 'reparented to', father


def clean_attr_setted_multiple_time(tpl_info, attr):
    import maya.mel as mel

    name_attr_mult = tpl_info + '.' + attr
    ls_attr_ignored = ['infoNumbMb', 'endMb']

    if attr in ls_attr_ignored:
        print '................................... ATTR SKIPPED', name_attr_mult
        ls_attr_cleaned = []
        return ls_attr_cleaned

    print 'name_attr_mult', name_attr_mult
    ls_attr_mult = mc.getAttr(name_attr_mult + '[*]')
    ls_clean = []
    ls_index_to_del = []

    for i in range(len(ls_attr_mult)):
        attr_set = mc.getAttr(name_attr_mult + '[' + str(i) + ']')
        if attr_set in ls_clean:
            ls_index_to_del.append(i)
        else:
            ls_clean.append(attr_set)
    if ls_index_to_del:
        # Delete duplication attribute
        for i in ls_index_to_del:
            attr_to_del = name_attr_mult + '[' + str(i) + ']'
            mel.eval('AEremoveMultiElement ' + attr_to_del)

    ls_attr_cleaned = mc.getAttr(name_attr_mult, multiIndices=True) or []
    return ls_attr_cleaned

def find_sk_box(tpl_info):
    if mc.objExists(tpl_info + '.boxSk'):
        ls_sk = mc.getAttr(tpl_info + '.boxSk[*]')
        return ls_sk
    else:
        # lister le nombre de connexion sur le loft
        # tplLoft_armSk_1_RShape / tplInfo_arm_1_R
        module_type = mc.getAttr(tpl_info + '.moduleType')
        name_loft_sk = tpl_info.replace('Info', 'Loft').replace(module_type, module_type + 'Sk') + 'Shape'
        ls_sk = mc.listConnections(name_loft_sk + '.worldSpace[0]', source=True)
        return ls_sk