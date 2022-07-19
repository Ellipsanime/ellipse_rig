# coding: utf-8

import maya.cmds as mc
from functools import partial
from ellipse_rig.library import lib_glossary as gloss
from ellipse_rig.library import lib_rigs,lib_shapes,lib_attributes
reload(gloss)
reload(lib_rigs)
reload(lib_shapes)
reload(lib_attributes)

class GuideWorld(object):

    def __init__(self,selObj=None,**kwargs):
        self.selObj = selObj
        self.nWorld = gloss.name_format(prefix=gloss.lexicon('tpl'),name=gloss.lexicon('world'),incP='')
        self.nWorldGrp = gloss.name_format(prefix=gloss.lexicon('tpl')+'Root',name=gloss.lexicon('world'),incP='')
        self.nFlyGrp = gloss.name_format(prefix=gloss.lexicon('tpl')+'Root',name=gloss.lexicon('fly'),incP='')
        self.nFly = gloss.name_format(prefix=gloss.lexicon('tpl'),name=gloss.lexicon('fly'),incP='')
        self.nInfoFly = gloss.name_format(prefix=gloss.lexicon('tplInfo'),name=gloss.lexicon('fly'),incP='')
        self.typeArrowQuad = "circleArrow4"
        self.typeFly = "fly"
        self.typeCircle = "circle"
        self.valColorWorld = "yellow"

    def createRig(self):
        '''
        :param selObj:
        :param matchObj:
        :return: list of controllers created or recuperated
        '''
        dicWorld = {}
        # CREATE WORLD AND FLY________________________________
        if mc.objExists(self.nWorld) == True:
            pass
        else:
            wordGuideGrp = lib_rigs.createObj(partial(mc.group, **{'n': self.nWorldGrp, 'em': True}))
            wordGuide =lib_rigs.createObj(partial(mc.joint, **{'n': self.nWorld}), shape= lib_rigs.Shp([self.typeArrowQuad],
                                          size= (5,5,5)), father=wordGuideGrp, refObj=self.selObj, attributs={"drawStyle": 2})
            flyGuideGrp = lib_rigs.createObj(partial(mc.group, **{'n': self.nFlyGrp, 'em': True}), father=wordGuide)
            flyGuide =lib_rigs.createObj(partial(mc.joint, **{'n': self.nFly}), shape= lib_rigs.Shp([self.typeFly],
                                         size= (3,3,3)), father=flyGuideGrp, refObj=self.selObj, attributs={"drawStyle": 2})
            lib_rigs.createObj(partial(mc.group, **{'n': self.nInfoFly, 'em': True}), father=wordGuide, refObj=self.selObj)
            # OFFSET FLY__________________________________________
            selShape = mc.listRelatives(flyGuide, s=True)[0]
            mc.move(0, 0, -3, mc.ls(selShape + '.cv[*]', fl=True), r=True)
            # HIDE AND LOCK ATTRIBUTES____________________________
            lib_attributes.lockAndHideAxis(wordGuide, transVis=True, rotVis=True)
            # ATTRIBUTES TO FLY AND INFO FLY______________________
            mc.addAttr(self.nFly, ln='infPart', dt="string")
            mc.setAttr(self.nFly + '.infPart', self.nInfoFly, type="string")
            mc.addAttr(self.nInfoFly, ln='fly', dt="string")
            mc.setAttr(self.nInfoFly + '.fly',self.nFly, type="string")
            mc.addAttr(self.nInfoFly, ln='world', dt="string")
            mc.setAttr(self.nInfoFly + '.world',self.nWorld, type="string")
            mc.addAttr(self.nInfoFly, ln=gloss.lexiconAttr('moduleDataTpl'), at="bool", dv=1)
            mc.setAttr(self.nInfoFly + ".%s"%gloss.lexiconAttr('moduleDataTpl'), e=True, k=True)
            mc.addAttr(self.nInfoFly, ln=gloss.lexiconAttr('moduleType'), dt="string")
            mc.setAttr(self.nInfoFly + ".%s"%gloss.lexiconAttr('moduleType'),gloss.lexicon('fly'), l=True,type="string")
            mc.addAttr(self.nInfoFly, ln=gloss.lexiconAttr('attrParent'), at="message")
            mc.setAttr(self.nInfoFly + ".%s"%gloss.lexiconAttr('attrParent'), e=True)
            mc.addAttr(self.nInfoFly, ln=gloss.lexiconAttr('attrChild'), at="message")
            mc.setAttr(self.nInfoFly + ".%s"%gloss.lexiconAttr('attrChild'), e=True)
            mc.addAttr(self.nInfoFly, ln=gloss.lexiconAttr('buildCg'), at="bool", dv=1)
            mc.setAttr(self.nInfoFly + ".%s"%gloss.lexiconAttr('buildCg'), e=True, k=True)

        dicWorld['grpW'] = self.nWorldGrp
        dicWorld['world'] = self.nWorld
        dicWorld['fly'] = self.nFly
        dicWorld['flyInfo'] = self.nInfoFly
        return dicWorld


'''
from ellipse_rig.assets.asset_base import base_guide
reload(base_guide)
guideWorld = base_guide.GuideWorld()
guideWorld.createRig()
'''
