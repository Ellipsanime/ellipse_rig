
# coding: utf-8
# Copyright (c) 2019 Juline BRETON

import os

from ...utils.maya_widget import MayaWidget, load_ui
from ...utils import comment
# import for PyQt
from PySide2.QtCore import QSize, Qt, SIGNAL
from PySide2.QtGui import QIcon, QColor
from PySide2.QtWidgets import QListWidgetItem, QPushButton
import maya.cmds as mc

class SetupQCheckWidget(MayaWidget):
    def __init__(self, parent=None, title='Check Name'):
        MayaWidget.__init__(self, parent=parent)

        self.ui = load_ui(os.path.join(os.path.dirname(__file__), 'stp_qcheck_toolbox.ui'))
        self.main_layout.addWidget(self.ui)

        # SET INTERFACE
        self.title = title
        self.details = "Hierarchy"
        self.info_message = "Check the TOP LEVEL Hierarchy\n" \
                            "MOD:ALL\n" \
                            "    > MOD:Hierarchy\n" \
                            "    > WORLD\n" \
                            "    > RIG\n" \
                            "[RIGHT CLICK] select in the viewport the object(s) select in the list"
        ### COLOR CODE
        self.black = ["rgb(0, 0, 0);", '/ico/off_light.png']
        self.alpha = "rgba(0, 0, 0, 0)"
        self.orange = ["rgb(238, 161, 28)", '/ico/orange_light.png']
        self.green = ["rgb(15, 157, 88)", '/ico/green_light.png']
        self.red = ["rgb(236, 87, 71)", '/ico/red_light.png']
        self.blue = ["rgb(46, 132, 221)", '/ico/blue_light.png']

        self.add_btn_add_attr()

        self.set_check_tab()
        self.ui.btn_show_details.clicked.connect(self.switch_to_btn_hide)
        self.ui.btn_hide_details.clicked.connect(self.switch_to_btn_show)

        # SET BUTTONS
        self.ui.btn_check.clicked.connect(self.check)
        self.ui.btn_fix.clicked.connect(self.fix)
        self.ui.btn_attr.clicked.connect(add_attr_master_all)

        # If you want an action on the right click
        self.ui.ls_details.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.ls_details.connect(self.ui.ls_details, SIGNAL("customContextMenuRequested(QPoint)"), self.right_click)

    def right_click(self):
        '''
        Select in the viewport the object(s) select in the list
        '''
        selected_items = self.ui.ls_details.selectedItems()
        ls_selected_items = []
        if selected_items:
            for item in selected_items:
                ls_selected_items.append(item.text())
        mc.select(ls_selected_items)

    def switch_to_btn_hide(self):
        '''
        Auto switch de button icon
        '''
        self.ui.btn_show_details.hide()
        self.ui.btn_hide_details.show()
        self.ui.tabWidget.show()
        self.ui.ls_details.show()
        self.ui.btn_attr.show()

    def switch_to_btn_show(self):
        '''
        Auto switch de buton icon
        '''
        self.ui.btn_show_details.show()
        self.ui.btn_hide_details.hide()
        self.ui.tabWidget.hide()
        self.ui.btn_attr.hide()

    def set_comment(self, text, color, nb=[]):
        '''
        :param text: :str: the comment on the line edit
        :param color: :var: choose it in the COLOR CODE
        :param nb: :list: self.ui.btn_state_1 and/or self.ui.btn_state_1 ; set the button(s) you want to change icon
        :return:
        '''
        self.ui.line_comment.setText(text)
        self.ui.line_comment.setStyleSheet("background-color:" + self.alpha + "; color:" + color[0])
        if not nb:
            nb = [self.ui.btn_state_1]
        for btn in nb:
            btn.setIcon(QIcon(os.path.dirname(__file__) + color[1]))
            btn.setIconSize(QSize(15, 15))

    def set_state_color(self, nb, color):
        '''
        :param nb: self.ui.btn_state_1 or self.ui.btn_state_1 ; set the button you want to change icon
        :param color: :var: choose it in the COLOR CODE
        :return:
        '''
        if color == 'off':
            nb.setIcon(QIcon(os.path.dirname(__file__) + '/ico/off_light.png'))
            nb.setIconSize(QSize(15, 15))
        if color == 'orange':
            nb.setIcon(QIcon(os.path.dirname(__file__) + '/ico/orange_light.png'))
            nb.setIconSize(QSize(15, 15))
        if color == 'red':
            nb.setIcon(QIcon(os.path.dirname(__file__) + '/ico/red_light.png'))
            nb.setIconSize(QSize(15, 15))
        if color == 'blue':
            nb.setIcon(QIcon(os.path.dirname(__file__) + '/ico/blue_light.png'))
            nb.setIconSize(QSize(15, 15))
        if color == 'green':
            nb.setIcon(QIcon(os.path.dirname(__file__) + '/ico/green_light.png'))
            nb.setIconSize(QSize(15, 15))

    def add_btn_add_attr(self):
        self.ui.btn_attr = QPushButton("Add attr MASTER ALL")
        self.ui.lay_vertical.addWidget(self.ui.btn_attr)

    def set_check_tab(self):
        '''
        Setup UI
        '''
        self.ui.lbl_check_name.setText(self.title)
        self.ui.lbl_check_name.setToolTip(self.info_message)
        self.ui.lbl_help.setText(self.info_message)
        self.ui.tabWidget.setTabText(0, self.details)
        self.ui.btn_show_details.setIcon(QIcon(os.path.dirname(__file__) + '/ico/plus_grey_75.png'))
        self.ui.btn_show_details.setIconSize(QSize(15, 15))
        self.ui.btn_hide_details.setIcon(QIcon(os.path.dirname(__file__) + '/ico/minus_grey_75.png'))
        self.ui.btn_hide_details.setIconSize(QSize(15, 15))
        self.switch_to_btn_show()
        self.set_comment(text="", color=self.black, nb=[self.ui.btn_state_1, self.ui.btn_state_2])
        self.ui.ls_details.hide()

    def check(self):
        '''
        Here Your check fonction
        '''
        print "Checking " + self.title + "......"
        self.set_comment(text="Checking...", color=self.black, nb=[self.ui.btn_state_1, self.ui.btn_state_2])
        self.ui.ls_details.clear()

        # just for exemple:
        ERROR = ""
        SOMETHING_TO_CHECK = ""
        ls_problem = []


        if self.ui.cb_check.isChecked():
            wrongParent = wrongHierarchie_check()
            if ERROR: # If ERROR
                self.switch_to_btn_hide()
                item = QListWidgetItem()
                item.setText("Write what you want to add in the listWidget OR NOT")
                item.setTextColor(QColor(236, 87, 71)) # Set item color red
                self.ui.ls_details.addItem(item)
                self.set_comment(text="ERROR", color=self.red)

            elif wrongParent:
                self.switch_to_btn_hide()
                item = QListWidgetItem()
                item.setText(self.details)
                for problem in wrongParent:
                    item = QListWidgetItem()
                    item.setText(problem)
                    self.ui.ls_details.addItem(item)
                self.set_comment(text="Need fix", color=self.orange, nb=[self.ui.btn_state_1])

            else: # Everithing is OK
                self.set_comment(text="", color=self.black, nb=[self.ui.btn_state_1])
                self.set_comment(text="Good job !", color=self.green, nb=[self.ui.btn_state_2])
            print "======> Check " + self.title + " Finished"

            if self.ui.cb_auto_fix.isChecked(): # If Auto Fix is checked FIX ALL
                self.fix()
        else: # If check box > check is not check
            print self.title + " Not checked"
            self.set_comment(text="", color=self.black, nb=[self.ui.btn_state_1, self.ui.btn_state_2])

    def fix(self):
        """
        Here Your fix fonction
        if something selected in listWidget: PARTIAL FIX
        else: FIX ALL
        """
        print "Fixing " + self.title + "......"
        try:
            selected_items = self.ui.ls_details.selectedItems()
            ls_selected_items = []
            if selected_items:  # If something is selected in the listWidget = PARTIAL FIX
                print "If something is selected in the listWidget"
                for item in selected_items:
                    ls_selected_items.append(item.text())
                    item.setTextColor(QColor(0, 166, 81))
                    self.ui.ls_details.setItemSelected(item, False)

                ###
                wrongHierarchie_fix(ls_selected_items)
                ###

                self.set_comment(text="Partial Fixed", color=self.blue, nb=[self.ui.btn_state_2])
                print "======> Partial Fix " + self.title + " Finished"

            else: # FIX ALL
                wrongHierarchie_fix()
                self.set_comment(text="Fixed", color=self.green, nb=[self.ui.btn_state_2])
                print "======> Fix " + self.title + " Finished"
        except:
            self.set_comment(text="ERROR", color=self.red, nb=[self.ui.btn_state_2])
            print "======> Fix " + self.title + " ERROR <======"

## Juline
# A améliorer :
# _ Checker si plusieurs ref dans la scene
# _ si attr deleteMe pas ne pas le flagger (ex : trash)
# _ Si asset avec ref multiple pop up windows pour choisir le top node (+ajout d'un attribut MASTER_ALL(bool))

# FOR PROPS
# Author Pierre FABAREZ
#Constant
MOD_ALL = 'MOD:ALL'
MOD_GEO = 'MOD:GEO'
MOD_LOC = 'MOD:LOC'
MOD_FUR = 'MOD:FUR'
MOD_SHP = 'MOD:SHP'

RIG_GRP = 'RIG'
RIG_ADD = 'RIG_ADD'
WORLD = 'WORLD'

CAMERAS = ['persp', 'top', 'front', 'side']
INIT_HIERARCHIE = ['TRASH', 'MOD:ALL']
INIT_ALL_CHILD = [MOD_GEO, MOD_LOC, WORLD, RIG_GRP, MOD_FUR, MOD_SHP]


# Check Wrong Hierarchie
def wrongHierarchie_check():
    wrongParent = []
    if not mc.objExists(MOD_ALL):
        return

    # check Scene Hierarchie
    sceneInit = mc.ls(assemblies=True, cameras=False)
    sceneInit = list(set(sceneInit) - set(CAMERAS))

    for item in sceneInit:
        if not item in INIT_HIERARCHIE:
            wrongParent.append(item)

    # Check ALL Child hierarchie
    allChild = mc.listRelatives(MOD_ALL, children=True)
    wrongParent.extend(list(set(allChild) - set(INIT_ALL_CHILD)))

    if mc.objExists(RIG_ADD):
        RIG_ADD_parent = mc.listRelatives(RIG_ADD, parent=True) or []

        if RIG_ADD_parent and RIG_ADD_parent[0] != RIG_GRP:
            wrongParent.append(RIG_ADD)

    return wrongParent


def wrongHierarchie_fix(*args):
    mc.scriptEditorInfo(sw=True, sr=True)
    for item in INIT_ALL_CHILD:
        try:
            mc.parent(item, MOD_ALL)
        except:
            continue

    try:
        mc.parent(RIG_ADD, RIG_GRP)

    except:
        pass

# Author Juline BRETON
### PROPS ###
# 1_ Check si plusieurs Refs
#    > Définir le MASTER ALL (+ ajout d'un attribut boolean')
# 2_ Check Hi BASE
#    > WWF
#    > Hi MOD
# 3_ Flag WRONG Hi
#

TOP_NODE = "ALL"
attr_master_all = "MASTER_ALL"

def get_ref_count():
    """
    :return: nb of reference, ls ref node
    """
    ls_ref_node = mc.ls(sl=False, type='reference') or []
    return len(ls_ref_node), ls_ref_node

def get_master_all():
    # check if attr master_top_node exist
    # else check nb ref
    nb_ref, ls_ref_node = get_ref_count()
    if nb_ref == 0:
        return TOP_NODE
    elif nb_ref == 1:
        # check if ref have group ALL
        name_space = mc.referenceQuery(ls_ref_node[0], namespace=True)
        if mc.objExists(name_space + ':' + TOP_NODE):
            master_top_node = name_space + ':' + TOP_NODE
            add_attr_master_all(master_top_node)
            return master_top_node
    else:
        print "Add pop up windows for select the MASTER REF\n" \
              "For the moment : You can add a master all attribute on the group all you want as the master all"



def add_attr_master_all(node=None):
    if not node:
        node = mc.ls(sl=True)[0]

    if TOP_NODE not in node:
        if 'cg_all' not in node:
            comment.format_comment("""Please select a group named "ALL" or "cg_all" """)

    else:
        if not mc.objExists(node + '.' + attr_master_all):
            mc.addAttr(node, longName=attr_master_all, attributeType='bool', keyable=False, defaultValue=True, force=True)
        else:
            mc.setAttr(node + '.' + attr_master_all, True)


#def check_rig_hi():


