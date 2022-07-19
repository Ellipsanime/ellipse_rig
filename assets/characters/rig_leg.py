# coding: utf-8



import maya.cmds as mc
from functools import partial

from ellipse_rig.library import lib_glossary as gloss
from ellipse_rig.library import lib_rigs as libRig
from ellipse_rig.library import lib_rigPreset as libRgPreset
from ellipse_rig.library import lib_curves,lib_sets,lib_connectNodes,lib_attributes,lib_shapes
from ellipse_rig.library import lib_baseRig
from ellipse_rig.assets.asset_base import guide_world,rig_world
from ellipse_rig.assets.characters import guide_base

reload(gloss)
reload(libRig)
reload(libRgPreset)
reload(lib_curves)
reload(lib_sets)
reload(lib_connectNodes)
reload(lib_attributes)
reload(lib_shapes)
reload(lib_baseRig)
reload(guide_world)
reload(guide_base)

rig_world.RigWorld().createRig()  # instance class charGuide and run method createRig

class Leg(rig_world.RigWorld):

    def __init__(self, name='spine', tplInfo='tplInfo', *args):
        rig_world.RigWorld.__init__(self)
        self.name = name
        self.info = tplInfo
        self.typeCircle = "circle"
        self.typeSquare = "square"
        self.shpRotIk = (0,45,0)

    def createLeg(self):
        # FILTER BY TPL INFO_______________________________________
        lsInfo = gloss.Inspect_tplInfo(lFilter=[self.info,self.name])