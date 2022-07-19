# coding: utf-8
"""
Author
------
Juline BRETON : julinebreton@gmail.com
"""

import os
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QLabel, QPushButton, QVBoxLayout

from ...utils.maya_widget import MayaWidget, load_ui
from ...utils import comment

import qcheck_widget, qcheck_vis_attr, qcheck_template, check_turtle_plug, qcheck_hierarchy,\
    qcheck_proto
from check_library import lib_check_base_hierarchy, lib_check_cg, lib_check_plugins, lib_check_controller, \
    clean_before_publish
# import qcheck_ctrl_in_cg, check_expert_mode,
import maya.cmds as mc

reload(qcheck_proto)
reload(lib_check_cg)
reload(lib_check_controller)


class SetupQCheckWindow(MayaWidget):
    """
    UI of the Sanity & Quality check for the setup departement
    """
    def __init__(self, parent=None):
        MayaWidget.__init__(self, name="Quality Check Setup          v1.0.0", parent=parent)

        self.ui = load_ui(os.path.join(os.path.dirname(__file__), 'setup_quality_check_main_win.ui'))
        self.setWindowIcon(QIcon(os.path.dirname(__file__) + '/ico/traffic-light.png'))
        self.main_layout.addWidget(self.ui)

        # COLOR CODE
        self.black = "rgb(0, 0, 0);"
        self.alpha = "rgba(0, 0, 0, 0)"
        self.orange = "rgb(238, 161, 28)"
        self.green = "rgb(15, 157, 88)"
        self.red = "rgb(236, 87, 71)"

        # SANITY CHECK #################################################################################################
        self.ui_hi = \
            qcheck_proto.SetupQCheckWidget(parent=self, title='Base Hierarchy',
                                           check=lib_check_base_hierarchy.check_base_hierarchy,
                                           fix=None, details="Wrong Hierarchy",
                                           info_message="Check the TOP LEVEL Hierarchy\n"
                                                        "MOD:ALL\n"
                                                        "    > MOD:Hierarchy\n"
                                                        "    > WORLD\n"
                                                        "    > RIG\n"
                                                        "[RIGHT CLICK] select in the viewport the object(s) "
                                                        "select in the list",
                                           click_r=mc.select,
                                           ico=os.path.dirname(__file__) + '/ico/outliner.png',
                                           option=["Add Attr MASTER_ALL", lib_check_base_hierarchy.add_attr_master_all])

        self.ui_ctrl_in_cg = \
            qcheck_proto.SetupQCheckWidget(parent=self, title='Ctrl in CG',
                                           check=lib_check_controller.check_ctrl_in_cg,
                                           fix=lib_check_controller.fix_cg_in_ctrl, details="List ctrl without CG",
                                           info_message="Check if ctrl have CG\n"
                                                        "[FIX]"
                                                        "   If a cg_assetName exist : connect the lonely ctrl inside\n"
                                                        "   Else : create cg_assetName parent to cg_all and add ctrl "
                                                        "inside\n"
                                                        "[RIGHT CLICK] "
                                                        "select in the viewport the object(s) select in the list",
                                           click_r=mc.select,
                                           ico=os.path.dirname(__file__) + '/ico/set.png')

        self.ui_cg = \
            qcheck_proto.SetupQCheckWidget(parent=self, title='CG Hierarchy',
                                           check=lib_check_cg.check_cg_hierarchy_prp_chr,
                                           fix=lib_check_cg.fix_cg_hierarchy, details="CG Hierarchy",
                                           info_message="Check if cg_all exist\n"
                                                        "Check if the TOP ControlGroup is cg_all\n"
                                                        "[RIGHT CLICK] "
                                                        "select in the viewport the object(s) select in the list",
                                           click_r=mc.select,
                                           ico=os.path.dirname(__file__) + '/ico/cg_hi.png',
                                           option=['Add attr CG MASTER', lib_check_cg.add_attr_master_cg])

        self.ui_bind_pose = \
            qcheck_proto.SetupQCheckWidget(parent=self, title='Set Bind Pose',
                                           check=lib_check_controller.check_set_bind_pose,
                                           fix=lib_check_controller.fix_set_bind_pose, details="Missing Bind Pose",
                                           info_message="Check if the BindPose is set on all extra attributes keyable\n"
                                                        "[PARTIAL FIX] on a controller not only an attribute\n"
                                                        "[RIGHT CLICK] select in the viewport the object(s) "
                                                        "select in the list",
                                           click_r=mc.select)

        self.ui_reset_bind_pose = \
            qcheck_proto.SetupQCheckWidget(parent=self, title='Reset Bind Pose',
                                           check=lib_check_controller.check_reset_bind_pose,
                                           fix=None, details="Not in Bind Pose",
                                           info_message="Check if the ctrl are in BindPose\n"
                                                        "[RIGHT CLICK] select in the viewport the object(s) "
                                                        "select in the list\n"
                                                        "[MANUAL FIX NEEDED] because a user check is necesary :\n"
                                                        "Use the DagMenu reset all",
                                           click_r=mc.select)

        self.ui_vis = qcheck_vis_attr.SetupQCheckWidget(parent=self, title='Switch Vis Attr')

        self.ui_plugin = \
            qcheck_proto.SetupQCheckWidget(parent=self, title='Clean Plugins',
                                           check=lib_check_plugins.check_plugin_prp_chr,
                                           fix=lib_check_plugins.fix_plugin,
                                           details="Plugins to cleaned",
                                           info_message="Clean Plugins",
                                           click_r=None,
                                           ico=os.path.dirname(__file__) + '/ico/puzzle_green.png')

        self.ui_shape_name = \
            qcheck_proto.SetupQCheckWidget(parent=self, title='Shapes Name',
                                           check=lib_check_controller.check_shape_name,
                                           fix=lib_check_controller.fix_shape_name,
                                           details="Check the shape(s) name on transform.nodeType == control",
                                           info_message="Wrong Shapes Name",
                                           click_r=mc.select,
                                           ico=None)

        # LINE EDIT FOR PUBLISH #######################################################################################
        self.ui_label_publish = load_ui(os.path.join(os.path.dirname(__file__), 'label_center.ui'))
        self.ui_label_publish.label_text.setText(".......... FOR PUBLISH ..........")
        self.ui_label_publish.label_text.setStyleSheet("color: rgb(255, 255, 255);")

        # QUALITY CHECK ###############################################################################################

        # Simple Check For PROP & CHAR
        # self.ui_expert = qcheck_proto.SetupQCheckWidget(parent=self, title='Expert Mode',
        #                                                 check=lib_check_setup.check_expert_mode,
        #                                                 fix=lib_check_setup.fix_expert_mode,
        #                                                 details="", info_message="Set expertMode False",
        #                                                 ico=os.path.dirname(__file__) + '/ico/star.png',
        #                                                 auto_fix=True)

        self.ui_hide_items = \
            qcheck_proto.SetupQCheckWidget(parent=self, title='Hide Items',
                                           check=clean_before_publish.check_items_to_hide,
                                           fix=clean_before_publish.fix_items_to_hide,
                                           click_r=mc.select,
                                           info_message="Hide deformers type ['deformBend', 'deformFlare',\n"
                                                        "'deformSine', 'deformSquash', 'deformTwist',\n"
                                                        "'deformWave', 'clusterHandle', 'lattice',\n"
                                                        "'baseLattice', 'blendShape', 'wrap', 'wire']"
                                                        "\n        &        \n "
                                                        "rig node ['locator', 'nurbsSurface', \n"
                                                        "'nurbsCurve', 'follicle', 'distanceDimShape']",
                                           auto_fix=False)
        # FOR PROP scene WIP
        # self.ui_mesh_not_in_ref

        self.add_check_tab()
        self.ui.btn_check_all.clicked.connect(self.check_all)

        self.ui.btn_print_fix.setIcon(QIcon(os.path.dirname(__file__) + '/ico/love.png'))
        self.ui.btn_print_fix.clicked.connect(self.clear_ui)

        self.ls_check = [self.ui_hi, self.ui_ctrl_in_cg, self.ui_cg, self.ui_bind_pose, self.ui_reset_bind_pose,
                         self.ui_plugin, self.ui_hide_items, self.ui_shape_name]  # , self.ui_expert

    def clear_ui(self):
        print "  \n__ __ __ __ __ CLEAR UI __ __ __ __ __\n   "
        for check in self.ls_check:
            check.clear_ui()

    def add_check_tab(self):
        # for PRP & CHR
        ls_sanity_check = [self.ui_hi, self.ui_ctrl_in_cg, self.ui_cg, self.ui_bind_pose, self.ui_reset_bind_pose,
                           self.ui_plugin]
        ls_quality_check = [self.ui_hide_items, self.ui_shape_name]  # , self.ui_expert
        for ui in ls_sanity_check:
            self.ui.lay_vertical.addWidget(ui)

        self.ui.lay_vertical.addWidget(self.ui_label_publish)

        for ui in ls_quality_check:
            self.ui.lay_vertical.addWidget(ui)

    def check_all(self):
        # First clear tool + PRINT name asset + name check
        self.clear_ui()
        scene_path = mc.file(q=True, sceneName=True)
        asset_name = scene_path.split("/")[-1].split('_')[2]
        print "\n \n \n"
        print comment.format_comment('                      CHECK SETUP                      \nASSET : ' + asset_name,
                                     center=True)
        for check in self.ls_check:
            check.check()

        print "  \n....................CHECK SETUP FINISH....................\n   "
