# coding: utf-8
# Copyright (c) 2017 Juline BRETON

__author__ = "Juline"
__refactor_date__ = 20180611
__refactor_author__ = "Juline"

import os
import string
import maya.cmds as mc
from llc.maya.setup.autorig.library import dictLib, julineLib, attributesLib, functionsLib

#from ump.common.ui import UMP_Widget
#from ump.common.ui.qt_abstraction import load_ui, QTreeWidgetItem, Qt, QIcon, QtCore, QListWidgetItem, QRegExpValidator, \
    QRegExp, QBrush, QColor

#from ump.common import exception_utils
from llc.maya.setup.toolbox import warningWin
from llc.maya.tools.switch_toolbox import switch_fonction

reload(julineLib)
reload(dictLib)
reload(attributesLib)
reload(warningWin)
reload(switch_fonction)


class AttrToolBox(UMP_Widget):

    def __init__(self, parent=None):
        UMP_Widget.__init__(self, "Gugu Attribute ToolBox", parent=parent)
        self.setWindowTitle('Gugu Attribute ToolBox')
        self.ui = load_ui(os.path.join(os.path.dirname(__file__), 'guguAttrBox.ui'))
        self.main_layout.addWidget(self.ui)

        self.set_ico()
        self.set_ui()
        self.warningIco = os.path.dirname(__file__) + '/ico/katz.png'

        self.obj = []

        ## CREATE
        self.ui.rBtn_keyable.clicked.connect(self.set_ui)
        self.ui.rBtn_displayable.clicked.connect(self.set_ui)
        self.set_step()

        # ----------------------------- FLOAT ----------------------------- #
        self.ui.cb_min.clicked.connect(self.set_ui)
        self.ui.cb_max.clicked.connect(self.set_ui)
        self.ui.cbb_presetFloat.currentIndexChanged.connect(self.float_preset)
        #self.ui.btn_addFloat.clicked.connect(self.add_float)
        self.ui.btn_addFloat.clicked.connect(self.typ_attr)
        # ---------------------------- BOOLEAN --------------------------- #
        self.ui.btn_addBool.clicked.connect(self.add_bool)
        # ---------------------------- CUSTOM ---------------------------- #
        self.ui.btn_addCustomAttr.clicked.connect(self.add_custom)
        # ----------------------------- ENUM ----------------------------- #
        self.ui.btn_addEnum.clicked.connect(self.add_enum)
        self.ui.lw_enum.clicked.connect(self.sel_enum)
        self.ui.lw_enum.currentItemChanged.connect(self.sel_enum)
        self.ui.le_enumName.returnPressed.connect(self.add_enum)
        self.ui.le_enumRename.returnPressed.connect(self.rename_enum)
        # ----------------------------- EDIT ----------------------------- #
        self.ui.btn_addPrefix.clicked.connect(self.add_enum_prefix)
        self.ui.btn_enumUp.clicked.connect(self.move_enum_up)
        self.ui.btn_enumDn.clicked.connect(self.move_enum_dn)
        self.ui.btn_enumDel.clicked.connect(self.del_enum)
        self.ui.btn_enumRename.clicked.connect(self.rename_enum)
        self.ui.btn_addAttrEnum.clicked.connect(self.typ_attr)

        ## EDIT EXISTING ATTRIBUTE
        self.ui.btn_loadObj.clicked.connect(self.load_obj)
        self.ui.btn_editAttr.clicked.connect(self.load_attr)
        self.ui.btn_updateAttr.clicked.connect(self.update_attr)
        self.ui.btn_delAttr.clicked.connect(self.delete_attr)
        self.ui.btn_copyAttr.clicked.connect(self.copy_attr)
        self.ui.btn_transferAttr.clicked.connect(self.transfer_attr)
        self.ui.btn_hideAttr.clicked.connect(self.hide_attr)
        self.ui.btn_showAttr.clicked.connect(self.show_attr)
        self.ui.btn_lockAttr.clicked.connect(self.lock_attr)
        self.ui.btn_unlockAttr.clicked.connect(self.unlock_attr)

        ## BASE ATTR
        self.ui.btn_lock.clicked.connect(self.lock)
        self.ui.btn_unlock.clicked.connect(self.lock)
        self.ui.btn_lockNhide.clicked.connect(self.lock_hide)
        self.ui.btn_show.clicked.connect(self.show_on)

    def typ_attr(self):
        typAttr = self.sender()
        typAttrStr = typAttr.text()
        self.crt_attr(typAttrStr)

    def set_ico(self):
        self.ui.cbBox_prefix.setItemIcon(0, QIcon(os.path.dirname(__file__) + '/ico/light.png'))
        self.ui.cbBox_prefix.setItemIcon(1, QIcon(os.path.dirname(__file__) + '/ico/mod.png'))
        self.ui.cbBox_prefix.setItemIcon(2, QIcon(os.path.dirname(__file__) + '/ico/colors.png'))
        self.ui.cbBox_prefix.setItemIcon(3, QIcon(os.path.dirname(__file__) + '/ico/ubi.png'))
        self.ui.cbBox_prefix.setItemIcon(4, QIcon(os.path.dirname(__file__) + '/ico/none.png'))
        self.ui.btn_addBool.setIcon(QIcon(os.path.dirname(__file__) + '/ico/switch2.png'))
        self.ui.btn_addBool.setIconSize(QtCore.QSize(25, 25))
        self.ui.btn_addFloat.setIcon(QIcon(os.path.dirname(__file__) + '/ico/float.png'))
        self.ui.btn_addFloat.setIconSize(QtCore.QSize(25, 25))
        ## ENUM
        self.ui.btn_addEnum.setIcon(QIcon(os.path.dirname(__file__) + '/ico/add.png'))
        self.ui.btn_addEnum.setIconSize(QtCore.QSize(10, 10))
        self.ui.btn_addPrefix.setIcon(QIcon(os.path.dirname(__file__) + '/ico/add.png'))
        self.ui.btn_addPrefix.setIconSize(QtCore.QSize(10, 10))
        self.ui.btn_enumUp.setIcon(QIcon(os.path.dirname(__file__) + '/ico/up.png'))
        self.ui.btn_enumDn.setIcon(QIcon(os.path.dirname(__file__) + '/ico/dn.png'))
        self.ui.btn_enumDel.setIcon(QIcon(os.path.dirname(__file__) + '/ico/poubelle.png'))
        self.ui.btn_loadObj.setIcon(QIcon(os.path.dirname(__file__) + '/ico/load.png'))
        self.ui.btn_enumRename.setIcon(QIcon(os.path.dirname(__file__) + '/ico/editText.png'))
        self.ui.btn_addAttrEnum.setIcon(QIcon(os.path.dirname(__file__) + '/ico/enum3.png'))
        self.ui.btn_addAttrEnum.setIconSize(QtCore.QSize(25, 25))
        ## CUSTOM
        self.ui.btn_addCustomAttr.setIcon(QIcon(os.path.dirname(__file__) + '/ico/add.png'))
        self.ui.btn_addCustomAttr.setIconSize(QtCore.QSize(10, 10))
        ## EDIT
        self.ui.btn_editAttr.setIcon(QIcon(os.path.dirname(__file__) + '/ico/edit.png'))
        self.ui.btn_updateAttr.setIcon(QIcon(os.path.dirname(__file__) + '/ico/update2.png'))
        self.ui.btn_updateAttr.setIconSize(QtCore.QSize(25, 25))
        self.ui.btn_delAttr.setIcon(QIcon(os.path.dirname(__file__) + '/ico/poubelle.png'))
        self.ui.treeW_extraAttr.resizeColumnToContents(1)
        self.ui.btn_copyAttr.setIcon(QIcon(os.path.dirname(__file__) + '/ico/copy.png'))
        self.ui.btn_copyAttr.setIconSize(QtCore.QSize(18, 18))
        self.ui.btn_transferAttr.setIcon(QIcon(os.path.dirname(__file__) + '/ico/transfer.png'))
        self.ui.btn_transferAttr.setIconSize(QtCore.QSize(25, 25))
        self.ui.btn_hideAttr.setIcon(QIcon(os.path.dirname(__file__) + '/ico/hide.png'))
        self.ui.btn_hideAttr.setIconSize(QtCore.QSize(20, 20))
        self.ui.btn_showAttr.setIcon(QIcon(os.path.dirname(__file__) + '/ico/show.png'))
        self.ui.btn_showAttr.setIconSize(QtCore.QSize(20, 20))
        self.ui.btn_lockAttr.setIcon(QIcon(os.path.dirname(__file__) + '/ico/lock.png'))
        self.ui.btn_lockAttr.setIconSize(QtCore.QSize(20, 20))
        self.ui.btn_unlockAttr.setIcon(QIcon(os.path.dirname(__file__) + '/ico/unlock.png'))
        self.ui.btn_unlockAttr.setIconSize(QtCore.QSize(20, 20))

    def set_ui(self):
        ## CREATE
        if self.ui.rBtn_keyable.isChecked():
            self.ui.cb_channelBox.setChecked(True)
            #self.ui.cb_delete.setStyleSheet('color: rgb(128, 128, 128)')
            self.ui.cb_channelBox.setStyleSheet('QCheckBox{color: rgb(128, 128, 128)} QCheckBox::indicator{background-color: rgb(76, 76, 76)}')
            self.ui.cb_channelBox.setEnabled(False)
        else:
            self.ui.cb_channelBox.setEnabled(True)
            self.ui.cb_channelBox.setStyleSheet('color: none')
        ## FLOAT
        if self.ui.cb_min.isChecked():
            self.ui.dsb_min.setStyleSheet('background-color: rgb(20, 41, 41); color: rgb(179, 179, 179)')
        else:
            self.ui.dsb_min.setStyleSheet('background-color: rgb(76, 76, 76); color: rgb(179, 179, 179)')
        if self.ui.cb_max.isChecked():
            self.ui.dsb_max.setStyleSheet('background-color: rgb(41, 20, 26); color: rgb(179, 179, 179)')
        else:
            self.ui.dsb_max.setStyleSheet('background-color: rgb(76, 76, 76); color: rgb(179, 179, 179)')
        ## ENUM
        #valid = QRegExpValidator(QRegExp('(\d|\w|_)*'))
        valid = QRegExpValidator(QRegExp('[a-zA-Z0-9_]*'))
        self.ui.le_enumName.setValidator(valid)
        self.ui.le_enumRename.setValidator(valid)
        self.ui.lEdit_name.setValidator(valid)

    def set_step(self):
        step = switch_fonction.get_step()
        if step == 'modeling':
            self.ui.cbBox_prefix.setCurrentIndex(1)
        elif step == 'surfacing':
            self.ui.cbBox_prefix.setCurrentIndex(2)
        elif step == 'setup':
            self.ui.cbBox_prefix.setCurrentIndex(3)
        else:
            self.ui.cbBox_prefix.setCurrentIndex(4)

    def float_preset(self):
        if self.ui.cbb_presetFloat.currentIndex() == 0:
            self.ui.cb_min.setChecked(False)
            self.ui.cb_max.setChecked(False)
            self.ui.dsb_default.setValue(0)
        elif self.ui.cbb_presetFloat.currentIndex() == 1:
            self.ui.dsb_default.setValue(0)
            self.ui.cb_min.setChecked(True)
            self.ui.dsb_min.setValue(-10)
            self.ui.cb_max.setChecked(True)
            self.ui.dsb_max.setValue(10)
        elif self.ui.cbb_presetFloat.currentIndex() == 2:
            self.ui.dsb_default.setValue(0)
            self.ui.cb_min.setChecked(True)
            self.ui.dsb_min.setValue(0)
            self.ui.cb_max.setChecked(True)
            self.ui.dsb_max.setValue(10)
        elif self.ui.cbb_presetFloat.currentIndex() == 3:
            self.ui.dsb_default.setValue(0)
            self.ui.cb_min.setChecked(True)
            self.ui.dsb_min.setValue(-1)
            self.ui.cb_max.setChecked(True)
            self.ui.dsb_max.setValue(1)
        elif self.ui.cbb_presetFloat.currentIndex() == 4:
            self.ui.dsb_default.setValue(0)
            self.ui.cb_min.setChecked(True)
            self.ui.dsb_min.setValue(0)
            self.ui.cb_max.setChecked(True)
            self.ui.dsb_max.setValue(1)
        self.set_ui()

    ## for ATTR Float / Enum / Bool
    def load_obj(self):
        self.ui.treeW_extraAttr.clear()
        obj = self.set_obj()
        if obj:
            self.ui.line_objLoaded.clear()
            self.ui.line_objLoaded.setText(obj[0])
            self.obj = obj[0]
            self.find_extra_attr(obj[0])

    def find_extra_attr(self, obj):
        try:
            lExtraAttr, lChannelBox = channel_box_attr(obj)
            for attr in lExtraAttr:
                item = QTreeWidgetItem()  ## on cree l'item de type QTreeWidgetItem
                item.setText(0, attr)
                self.ui.treeW_extraAttr.insertTopLevelItem(0, item)
                typAttr = mc.getAttr(obj + '.' + attr, type=True)
                if typAttr == 'long': # integer
                    self.ui.treeW_extraAttr.insertTopLevelItem(1, item.setText(1,'int'))
                else:
                    if typAttr == 'double':
                        self.ui.treeW_extraAttr.insertTopLevelItem(1, item.setText(1, 'float'))
                    else:
                        self.ui.treeW_extraAttr.insertTopLevelItem(1, item.setText(1, typAttr))
                if attr in lChannelBox:
                    self.ui.treeW_extraAttr.insertTopLevelItem(1, item.setText(2, 'True'))
                    item.setTextColor(2, QColor(0, 166, 81))
                else:
                    self.ui.treeW_extraAttr.insertTopLevelItem(1, item.setText(2, 'False'))
                    item.setTextColor(2, QColor(158, 11, 15))
                if mc.getAttr(obj + '.' + attr, lock=True):
                    self.ui.treeW_extraAttr.insertTopLevelItem(1, item.setText(3, 'Lock'))
                    item.setForeground(3, QBrush(Qt.black))
                else:
                    self.ui.treeW_extraAttr.insertTopLevelItem(1, item.setText(3, 'Free'))
        except:
            print exception_utils.FormatException()

    def attr_selected_info(self):
        selectedItem = self.ui.treeW_extraAttr.currentItem()
        attr = selectedItem.text(0)
        typ = selectedItem.text(1)
        if selectedItem.text(2) == 'True':
            key = 1
        else:
            key = 0
        return attr, typ, key

    def load_attr(self):
        attr, typ, key = self.attr_selected_info()
        self.ui.lEdit_name.clear()
        if attr.startswith('lgt_'):
            self.ui.lEdit_name.setText(attr.split('lgt_')[-1])
            self.ui.cbBox_prefix.setCurrentIndex(0)
        elif attr.startswith('mod_'):
            self.ui.lEdit_name.setText(attr.split('mod_')[-1])
            self.ui.cbBox_prefix.setCurrentIndex(1)
        elif attr.startswith('tex_'):
            self.ui.lEdit_name.setText(attr.split('tex_')[-1])
            self.ui.cbBox_prefix.setCurrentIndex(2)
        elif attr.startswith('ubi_'):
            self.ui.lEdit_name.setText(attr.split('ubi_')[-1])
            self.ui.cbBox_prefix.setCurrentIndex(3)
        else:
            self.ui.lEdit_name.setText(attr)
            self.ui.cbBox_prefix.setCurrentIndex(4)
        ## set channelBox / keyable / displayable
        objRef = self.ui.line_objLoaded.text()
        lChannelBox = mc.listAttr(objRef, channelBox=True, userDefined=True) or []
        if attr in lChannelBox:
            self.ui.cb_channelBox.setCheckState(Qt.Checked)
        else:
            self.ui.cb_channelBox.setCheckState(Qt.Unchecked)

        if mc.getAttr(objRef + '.' + attr, keyable=True):
            self.ui.rBtn_keyable.setChecked(Qt.Checked)
        else:
            self.ui.rBtn_displayable.setChecked(Qt.Checked)
        if typ == 'float':
            defVal = mc.attributeQuery(attr, node=self.obj, listDefault=True)
            self.ui.dsb_default.setValue(defVal[0])

            self.ui.cbb_presetFloat.setCurrentIndex(0)
            isMax = mc.attributeQuery(attr, node=self.obj, maxExists=True)
            if isMax:
                self.ui.cb_max.setCheckState(Qt.Checked)
                maxVal = mc.attributeQuery(attr, node=self.obj, maximum=True)
                self.ui.dsb_max.setValue(maxVal[0])
            else:
                self.ui.cb_max.setCheckState(Qt.Unchecked)
                self.ui.dsb_max.clear()
            isMin = mc.attributeQuery(attr, node=self.obj, minExists=True)
            if isMin:
                self.ui.cb_min.setCheckState(Qt.Checked)
                minVal = mc.attributeQuery(attr, node=self.obj, minimum=True)
                self.ui.dsb_min.setValue(minVal[0])
            else:
                self.ui.cb_min.setCheckState(Qt.Unchecked)
                self.ui.dsb_min.clear()
            defaultVal = mc.attributeQuery(attr, node=self.obj, listDefault=True)
            self.ui.dsb_default.setValue(defaultVal[0])

        if typ == 'enum':
            self.ui.lw_enum.clear()
            strEnum = mc.attributeQuery(attr, node=objRef, listEnum=True)[0]
            for i in range(strEnum.count(':')):
                if ':' in strEnum:
                    item = QListWidgetItem()
                    itemText = strEnum.split(':')[0]
                    strEnum = strEnum[len(strEnum.split(':')[0]) + 1:]
                    item.setText(itemText)
                    self.ui.lw_enum.addItem(item)
                    if not ':' in strEnum:
                        item = QListWidgetItem()
                        item.setText(strEnum)
                        self.ui.lw_enum.addItem(item)
        self.set_ui()

    def update_attr(self):
        attr, typ, key = self.attr_selected_info()
        print typ
        if typ == 'float':
            self.set_float(self.obj, attr)  ## setter keyable / channelBox / max / min
        if typ == 'enum':
            self.set_enum(self.obj, attr)
        self.load_obj()

    def find_name(self):
        name = self.ui.lEdit_name.text()
        if not name:
            warningWin.WarningPopUp(self.warningIco, 'Please set a name to your attribute', self, 12)
            return None
        if self.ui.cbBox_prefix.currentIndex() == 0:
            return 'lgt_' + name
        if self.ui.cbBox_prefix.currentIndex() == 1:
            return 'mod_' + name
        if self.ui.cbBox_prefix.currentIndex() == 2:
            return 'tex_' + name
        if self.ui.cbBox_prefix.currentIndex() == 3:
            return 'ubi_' + name

    def check_state_attr(self):
        key = self.ui.rBtn_keyable.isChecked()
        display = self.ui.rBtn_displayable.isChecked()
        channelBx = self.ui.cb_channelBox.isChecked()
        return key, display, channelBx

    @functionsLib.undoable
    def crt_attr(self, typAttr): ## WIP
        try:
            sel = mc.ls(sl=True)
            ## find name avec ou sans prefix
            attr = self.find_name()
            key, display, channelBx = self.check_state_attr()
            for obj in sel:
                if mc.objExists(obj+'.'+attr):
                    warningWin.WarningPopUp(self.warningIco, 'Attribute already exist', self, 12)

                else:
                    if typAttr == "Add Float":
                        mc.addAttr(obj, attributeType='float', shortName=attr, keyable=key)
                        self.set_float(obj, attr)

                    if typAttr == "Add Enum":
                        mc.addAttr(obj, attributeType='enum', shortName=attr, keyable=True, enumName='temp:')
                        if key is False:
                            mc.setAttr(obj+'.'+attr, keyable=False)
                        self.set_enum(obj, attr)

                    self.attr_accessibility(obj, attr)
        except:
            print exception_utils.FormatException()

    def set_float(self, obj, attr):
        try:
            objAttr = obj + '.' + attr

            mc.addAttr(objAttr, edit=True, defaultValue=self.ui.dsb_default.value())
            mc.setAttr(objAttr, self.ui.dsb_default.value())
            if self.ui.cb_max.isChecked():
                if self.ui.dsb_default.value() > self.ui.dsb_max.value():
                    warningWin.WarningPopUp(self.warningIco, 'You can not set a default value higher than your max value', self, 12)
                    return
                else:
                    mc.addAttr(objAttr, edit=True, hasMaxValue=True, maxValue=self.ui.dsb_max.value())
            else:
                if mc.addAttr(objAttr, query=True, hasMaxValue=True):
                    mc.addAttr(objAttr, edit=True, hasMaxValue=False)
            if self.ui.cb_min.isChecked():
                if self.ui.dsb_default.value() < self.ui.dsb_min.value():
                    warningWin.WarningPopUp(self.warningIco, 'You can not set a default value lower than your min value', self, 12)
                    return
                else:
                    mc.addAttr(objAttr, edit=True, hasMinValue=True, minValue=self.ui.dsb_min.value())
            else:
                if mc.addAttr(objAttr, query=True, hasMinValue=True):
                    mc.addAttr(objAttr, edit=True, hasMinValue=False)

            self.attr_accessibility(obj, attr)
        except:
            print exception_utils.FormatException()

    def attr_accessibility(self, obj, attr):
        key, display, channelBx = self.check_state_attr()
        if key:
            if not mc.getAttr(obj+'.'+attr, keyable=True):
                mc.setAttr(obj+'.'+attr, keyable=True)
        else:
            if channelBx:
                if mc.getAttr(obj+'.'+attr, keyable=True):
                    mc.setAttr(obj+'.'+attr, keyable=False, channelBox=True)
            else:
                if mc.getAttr(obj+'.'+attr, keyable=True):
                    mc.setAttr(obj+'.'+attr, keyable=False, channelBox=False)

    ## for ATTR Enum
    def add_enum(self):
        item = QListWidgetItem()
        if self.ui.le_enumName.text():
            item.setText(self.ui.le_enumName.text())
            self.ui.lw_enum.addItem(item)
            self.ui.le_enumName.clear()
        else:
            return

    def sel_enum(self):
        lItem = self.ui.lw_enum.selectedItems()
        for item in lItem:
            self.ui.le_enumRename.setText(item.text())
            return item

    def add_enum_prefix(self):
        prefix = self.ui.cbb_prefixEnum.currentIndex()
        lItem = self.ui.lw_enum.findItems("*", Qt.MatchWrap | Qt.MatchWildcard)
        if prefix == 0: # None
            # enlever le prefix s'il y en a un
            for i in range(len(lItem)):
                if '_' in lItem[i].text():
                    lItem[i].setText(lItem[i].text()[len(lItem[i].text().split('_')[0]) + 1:])
        if prefix == 1: # ABC
            ABC = string.ascii_uppercase
            for i in range(len(lItem)):
                lItem[i].setText(ABC[i] + '_' + lItem[i].text())
        if prefix == 2: # 123
            for i in range(0, len(lItem)):
                lItem[i].setText(str(i+1) + '_' + lItem[i].text())
        if prefix == 3: # CAP
            for i in range(0, len(lItem)):
                lItem[i].setText(lItem[i].text().upper())
        if prefix == 4: # min
            for i in range(0, len(lItem)):
                lItem[i].setText(lItem[i].text().lower())
        if prefix == 5: # Maj
            for i in range(0, len(lItem)):
                lItem[i].setText(lItem[i].text().capitalize())

    def move_enum_dn(self):
        lItem = self.ui.lw_enum.findItems("*", Qt.MatchWrap | Qt.MatchWildcard)
        itemSel = self.sel_enum()
        if self.ui.lw_enum.currentRow() + 1 < len(lItem):
            ind = self.del_enum()
            newItem = QListWidgetItem()
            newItem.setText(itemSel.text())
            self.ui.lw_enum.insertItem(ind + 1, newItem)
            self.ui.lw_enum.setCurrentItem(newItem)
        else:
            warningWin.WarningPopUp(self.warningIco, "It's already the last enum of the list", self, 12)

    def move_enum_up(self):
        itemSel = self.sel_enum()
        if self.ui.lw_enum.currentRow() != 0:
            ind = self.del_enum()
            newItem = QListWidgetItem()
            newItem.setText(itemSel.text())
            self.ui.lw_enum.insertItem(ind - 1, newItem)
            self.ui.lw_enum.setCurrentItem(newItem)
        else:
            warningWin.WarningPopUp(self.warningIco, "It's already the first enum of the list", self, 12)

    @functionsLib.undoable
    def del_enum(self):
        try:
            ind = self.ui.lw_enum.currentRow()
            self.ui.lw_enum.takeItem(ind)
            self.ui.le_enumRename.clear()
            return ind
        except:
            print exception_utils.FormatException()

    def rename_enum(self):
        lCurrentItem = self.ui.lw_enum.selectedItems()
        for currentItem in lCurrentItem:
            currentItem.setText(self.ui.le_enumRename.text())

    def set_enum(self, obj, attr):
        lItem = self.ui.lw_enum.findItems("*", Qt.MatchWrap|Qt.MatchWildcard)
        enum = []
        for item in lItem:
            enum.append(item.text() + ':')
        enumStr = ''
        for i in range(len(enum)):
            enumStr = enumStr + enum[i]
        mc.addAttr(obj+'.'+attr, edit=True, attributeType='enum', enumName=enumStr)
        self.attr_accessibility(obj, attr)

    def add_attribute(self, typ):
        sel = mc.ls(sl=True)
        ## find name avec ou sans prefix
        name = self.find_name()
        if not name:
            return
        for obj in sel:
            if typ == 'float':
                mc.addAttr(obj, attributeType='float', shortName=name)
                self.set_float(obj + '.' + name)
            if typ == 'enum':
                mc.addAttr(obj, attributeType='enum', shortName=name)
                self.set_enum(obj + '.' + name)

    def add_bool(self):
        sel = mc.ls(sl=True)
        ## find name avec ou sans prefix
        name = self.find_name()
        if not name:
            return
        key, display, channelBx = self.check_state_attr()
        for obj in sel:
            mc.addAttr(obj, attributeType='bool', shortName=name, keyable=key)
            if display:
                mc.setAttr(obj + '.' + name, channelBox=channelBx)

    def add_custom(self):
        custom = self.ui.cbb_customAttr.currentIndex()
        sel = mc.ls(sl=True)
        attr = self.find_name()
        if custom == 0:  # Off / On
            for obj in sel:
                mc.addAttr(obj, attributeType='enum', shortName=attr, enumName='OFF:ON', keyable=True)
        if custom == 1:  # Hide / Show
            for obj in sel:
                mc.addAttr(obj, attributeType='enum', shortName=attr, enumName='Hide:Show', keyable=True)

    @functionsLib.undoable
    def copy_attr(self):
        try:
            sel = mc.ls(sl=True)
            objRef = self.ui.line_objLoaded.text()
            attr, typ, key = self.attr_selected_info()
            #lChannelBox = mc.listAttr(objRef, channelBox=True, userDefined=True) or []
            lExtraAttr, lChannelBox = channel_box_attr(objRef)
            for obj in sel:
                if mc.objExists(obj+'.'+attr):
                    warningWin.WarningPopUp(self.warningIco, 'Sorry! the attribute : <b>'+attr+'</b> already existe on <b>'+obj, self, 12)

                elif typ == 'float':
                    mc.addAttr(obj, shortName=attr, defaultValue=mc.attributeQuery(attr, node=objRef, listDefault=True)[0], keyable=key)
                    if mc.attributeQuery(attr, node=objRef, minExists=True):
                        minVal = mc.attributeQuery(attr, node=objRef, minimum=True)[0]
                        mc.addAttr(obj + '.' + attr, edit=True, hasMinValue=True, minValue=minVal)
                    if mc.attributeQuery(attr, node=objRef, maxExists=True):
                        maxVal = mc.attributeQuery(attr, node=objRef, maximum=True)[0]
                        mc.addAttr(obj + '.' + attr, edit=True, hasMaxValue=True, maxValue=maxVal)

                elif typ == 'enum':
                    mc.addAttr(obj, attributeType=typ, shortName=attr, enumName=mc.attributeQuery(attr, node=objRef, listEnum=True)[0], keyable=key)

                elif typ == 'bool':
                    mc.addAttr(obj, attributeType=typ, shortName=attr, keyable=key)

                if attr in lChannelBox:
                    mc.setAttr(obj + '.' + attr, channelBox=True)
                mc.setAttr(obj + '.' + attr, mc.getAttr(objRef + '.' + attr))
            return objRef, attr, obj
        except:
            print exception_utils.FormatException()

    def transfer_attr(self):
        objRef, attr, obj = self.copy_attr()
        ## transferer connection
        lDest = mc.listConnections(objRef + '.' + attr, destination=True, source=False, plugs=True) or []
        for dest in lDest:
            mc.connectAttr(obj + '.' + attr, dest, force=True)
        lSource = mc.listConnections(objRef + '.' + attr, destination=False, source=True, plugs=True) or []
        for source in lSource:
            mc.connectAttr(source, obj + '.' + attr, force=True)
        mc.deleteAttr(objRef + '.' + attr)
        mc.select(objRef)
        self.load_obj()
        mc.select(obj)

    def delete_attr(self):
        objRef = self.ui.line_objLoaded.text()
        attr, typ, key = self.attr_selected_info()
        mc.deleteAttr(objRef + '.' + attr)
        mc.select(objRef)
        self.load_obj()

    def hide_attr(self):
        obj = self.ui.line_objLoaded.text()
        attr, typ, key = self.attr_selected_info()
        mc.setAttr(obj + '.' + attr, channelBox=False, keyable=False)

    def show_attr(self):
        obj = self.ui.line_objLoaded.text()
        attr, typ, key = self.attr_selected_info()
        mc.setAttr(obj + '.' + attr, channelBox=True, keyable=True)

    def lock_attr(self):
        obj = self.ui.line_objLoaded.text()
        attr, typ, key = self.attr_selected_info()
        mc.setAttr(obj + '.' + attr, lock=True)

    def unlock_attr(self):
        obj = self.ui.line_objLoaded.text()
        attr, typ, key = self.attr_selected_info()
        mc.setAttr(obj + '.' + attr, lock=False)

    def lock(self):
        sender = self.sender()
        sel = mc.ls(sl=1) or []
        if sender.text() == "Lock":
            lockOn = True ; lockOff = False
        if sender.text() == "Unlock":
            lockOn = False ; lockOff = True
        for x in sel:
            if self.ui.cb_rotX.isChecked():
                mc.setAttr(x + ".rx", lock=lockOn)
            else:
                mc.setAttr(x + ".rx", lock=lockOff)
            if self.ui.cb_rotY.isChecked():
                mc.setAttr(x + ".ry", lock=lockOn)
            else:
                mc.setAttr(x + ".ry", lock=lockOff)
            if self.ui.cb_rotZ.isChecked():
                mc.setAttr(x + ".rz", lock=lockOn)
            else:
                mc.setAttr(x + ".rz", lock=lockOff)
            if self.ui.cb_trsX.isChecked():
                mc.setAttr(x + ".tx", lock=lockOn)
            else:
                mc.setAttr(x + ".tx", lock=lockOff)
            if self.ui.cb_trsY.isChecked():
                mc.setAttr(x + ".ty", lock=lockOn)
            else:
                mc.setAttr(x + ".ty", lock=lockOff)
            if self.ui.cb_trsZ.isChecked():
                mc.setAttr(x + ".tz", lock=lockOn)
            else:
                mc.setAttr(x + ".tz", lock=lockOff)
            if self.ui.cb_sclX.isChecked():
                mc.setAttr(x + ".sx", lock=lockOn)
            else:
                mc.setAttr(x + ".sx", lock=lockOff)
            if self.ui.cb_sclY.isChecked():
                mc.setAttr(x + ".sy", lock=lockOn)
            else:
                mc.setAttr(x + ".sy", lock=lockOff)
            if self.ui.cb_sclZ.isChecked():
                mc.setAttr(x + ".sz", lock=lockOn)
            else:
                mc.setAttr(x + ".sz", lock=lockOff)

    def lock_hide(self):
        self.lock()
        sel = mc.ls(sl=1)
        for x in sel:
            if self.ui.cb_rotX.isChecked():
                mc.setAttr(x + ".rx", keyable=False, channelBox=False)
            if self.ui.cb_rotY.isChecked():
                mc.setAttr(x + ".ry", keyable=False, channelBox=False)
            if self.ui.cb_rotZ.isChecked():
                mc.setAttr(x + ".rz", keyable=False, channelBox=False)
            if self.ui.cb_trsX.isChecked():
                mc.setAttr(x + ".tx", keyable=False, channelBox=False)
            if self.ui.cb_trsY.isChecked():
                mc.setAttr(x + ".ty", keyable=False, channelBox=False)
            if self.ui.cb_trsZ.isChecked():
                mc.setAttr(x + ".tz", keyable=False, channelBox=False)
            if self.ui.cb_sclX.isChecked():
                mc.setAttr(x + ".sx", keyable=False, channelBox=False)
            if self.ui.cb_sclY.isChecked():
                mc.setAttr(x + ".sy", keyable=False, channelBox=False)
            if self.ui.cb_sclZ.isChecked():
                mc.setAttr(x + ".sz", keyable=False, channelBox=False)

    def show_on(self):
        sel = mc.ls(sl=1)
        for x in sel:
            if self.ui.cb_rotX.isChecked():
                mc.setAttr(x + ".rx", keyable=True, channelBox=True)
            if self.ui.cb_rotY.isChecked():
                mc.setAttr(x + ".ry", keyable=True, channelBox=True)
            if self.ui.cb_rotZ.isChecked():
                mc.setAttr(x + ".rz", keyable=True, channelBox=True)
            if self.ui.cb_trsX.isChecked():
                mc.setAttr(x + ".tx", keyable=True, channelBox=True)
            if self.ui.cb_trsY.isChecked():
                mc.setAttr(x + ".ty", keyable=True, channelBox=True)
            if self.ui.cb_trsZ.isChecked():
                mc.setAttr(x + ".tz", keyable=True, channelBox=True)
            if self.ui.cb_sclX.isChecked():
                mc.setAttr(x + ".sx", keyable=True, channelBox=True)
            if self.ui.cb_sclY.isChecked():
                mc.setAttr(x + ".sy", keyable=True, channelBox=True)
            if self.ui.cb_sclZ.isChecked():
                mc.setAttr(x + ".sz", keyable=True, channelBox=True)

    def set_obj(self):
        if len(mc.ls(sl=True)) > 1:
            warningWin.WarningPopUp(self.warningIco, 'Please select ONLY one object', self, 12)
            return []
        elif len(mc.ls(sl=True)) == 0:

            warningWin.WarningPopUp(self.warningIco, 'Please select one object', self, 12)
            return []
        else:
            obj = mc.ls(sl=True)
            return obj

def channel_box_attr(obj):
    lExtraAttr = mc.listAttr(obj, userDefined=True) or []
    lChannelBox = []
    for extraAttr in lExtraAttr:
        if mc.getAttr(obj + '.' + extraAttr, keyable=True, channelBox=True) or mc.getAttr(obj + '.' + extraAttr, keyable=False, channelBox=True):
            lChannelBox.append(extraAttr)
    return lExtraAttr, lChannelBox