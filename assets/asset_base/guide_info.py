import maya.cmds as mc
from functools import partial

from ellipse_rig.library import lib_glossary as gloss
from ellipse_rig.library import lib_rigs as libRig
from ellipse_rig.library import lib_curves,lib_sets,lib_connectNodes,lib_attributes,lib_shapes
from ellipse_rig.library import lib_baseRig
from ellipse_rig.assets.asset_base import guide_world

reload(gloss)
reload(libRig)
reload(lib_curves)
reload(lib_sets)
reload(lib_connectNodes)
reload(lib_attributes)
reload(lib_shapes)
reload(lib_baseRig)
reload(guide_world)

guide_world.GuideWorld().createRig()  # instance class charGuide and run method createRig


class Info(guide_world.GuideWorld):

    def __init__(self,name='default',side='',selObj=None,**kwargs):
        guide_world.GuideWorld.__init__(self, selObj=selObj)
        self.selObj = selObj
        self.name = name
        self.side = side
        self.rotShape = [0,0,0]

    def infoInc(self):
        # TEMPLATE INFO INCREMENTATION________________________________________
        dic = {}
        # NAME________________________________________________________________
        nInfo= gloss.name_format(prefix=gloss.lexicon('tplInfo'),name=self.name, nSide=self.side,incInfo=True)
        # CREATE INFO_________________________________________________________
        libRig.createObj(partial(mc.group, **{'n': nInfo, 'em': True}),father=self.nWorld, refObj=self.selObj)
        incVal =gloss.get_inc(selObj=nInfo, slideSplit=2)
        # CREATE ATTRIBUTES INFO INCREMENTATION AND UPDATE OR DEL ____________
        #mc.addAttr(nInfo, longName='infoBase', numberOfChildren=4, attributeType='compound')
        mc.addAttr(nInfo, ln=gloss.lexiconAttr('moduleDataTpl'), at="bool", dv=1)
        mc.setAttr(nInfo + ".%s"%gloss.lexiconAttr('moduleDataTpl'), e=True, k=True)
        mc.addAttr(nInfo, ln=gloss.lexiconAttr('moduleType'), dt="string")
        mc.setAttr(nInfo + ".%s"%gloss.lexiconAttr('moduleType'),self.name, type="string")
        mc.addAttr(nInfo, ln=gloss.lexiconAttr('attrParent'), at="message")
        mc.setAttr(nInfo + ".%s"%gloss.lexiconAttr('attrParent'), e=True)
        mc.addAttr(nInfo, ln=gloss.lexiconAttr('attrChild'), at="message")
        mc.setAttr(nInfo + ".%s"%gloss.lexiconAttr('attrChild'), e=True)
        mc.addAttr(nInfo, ln=gloss.lexiconAttr('moduleMirror'), at="message")
        mc.setAttr(nInfo + ".%s"%gloss.lexiconAttr('moduleMirror'), e=True)

        mc.addAttr(nInfo, ln=gloss.lexiconAttr('buildCg'), at="bool", dv=1)
        mc.setAttr(nInfo + ".%s"%gloss.lexiconAttr('buildCg'), e=True, k=True)

        mc.addAttr(nInfo, ln='incInfo', dt="string")
        mc.addAttr(nInfo, ln='infPart', dt="string")
        mc.addAttr(nInfo, ln='updateSk', dt="string")
        val = str(self.side)
        mc.addAttr(nInfo, longName='side', dataType="string")
        if self.side:
            mc.setAttr(nInfo + '.side', self.side, type="string")
        else:
            mc.setAttr(nInfo + '.side', 'None', type="string")
        if self.side == '': val = 'empty'
        mc.addAttr(nInfo, ln='update', at="enum", en="%s:%s" % (self.name, val), k=True)
        mc.setAttr(nInfo + '.incInfo', incVal, type="string")
        mc.setAttr(nInfo + '.infPart', nInfo, type="string")
        mc.setAttr(nInfo + '.updateSk', 'partToDel', type="string")
        mc.setAttr(nInfo + '.update', e=True, cb=True)
        if self.side is not'':
            mc.addAttr(nInfo, ln='sym',dt='string',multi=True) # add master control
            mc.setAttr(nInfo+'.sym[0]',nInfo,type='string')
        dic['infoName'] = nInfo
        dic['incVal'] = incVal
        return dic

