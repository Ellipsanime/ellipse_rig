# coding: utf-8

import maya.cmds as mc
from functools import partial

from ellipse_rig.library import lib_names,lib_rigs,lib_shapes,lib_sets
from ellipse_rig.library import lib_baseRig
from ellipse_rig.assets.asset_base import guide_world
from ellipse_rig.assets.asset_base import guide_info

reload(lib_rigs)
reload(lib_names)
reload(lib_shapes)
reload(lib_sets)
reload(lib_baseRig)
reload(guide_world)
reload(guide_info)

guide_world.GuideWorld().createRig()  # instance class charGuide and run method createRig
guide_info.Info()  # instance class charGuide and run method createRig


class BallGuide(guide_info.Info):


    def __init__(self,name='snake',side='',selObj=None,obj=mc.ls(sl=True),*args):

        guide_info.Info.__init__(self,name=name,side=side,selObj=selObj)
        self.name = 'ball'
        self.typeSphere= "sphere"
        self.typeArrow = "arrowSingle2"
        self.valColorCtr = "green"
        self.rotShape = [0,0,0]
        self.prefix = lib_names.type_name('tpl')
        self.nFunc = lib_names.type_name('tpl')
        self.side = side
        self.nIncAttr = self.prefix + '_' + self.name + 'Tpl'+'_'+'1'
        self.selObj = selObj
        self.size = (1,1,1)

    def createBall(self):
        '''
        :param selObj:
        :param matchObj:
        :return:
        '''
        # TEMPLATE INFO INCREMENTATION_________________________________________
        dic = guide_info.Info.infoInc(self)


        # init incAttr
        incVal = lib_names.incPart(self.nIncAttr)
        ''' names '''
        nBall = lib_names.name_format(prefix=self.prefix, name=self.name, nFunc=self.nFunc, nSide=self.side, incPart=incVal)
        ''' create '''
        """
        ball=lib_rigs.createController(name=nBall, shape=lib_rigs.Shp([self.typeSphere, self.typeArrow],
        color=self.valColorCtr, size=1.1), match=lib_rigs.Match(pos=matchObj, rot=matchObj), refObj=selObj, incPart=incVal)
        """

        ball=lib_rigs.createController(name=nBall,shape=lib_rigs.Shp([self.typeSphere, self.typeArrow], color=self.valColorCtr,
            size=self.size, rotShp=self.rotShape),match=self.selObj, attrInfo=dic['infoName'], father=None,
            attributs={"drawStyle": 2}, worldScale=self.nWorld)


        # add to SET:Meshs ###
        createSet = ''
        if self.selObj == []:
            print "no Object"
        else:
            print
            for eachObj in self.selObj:
                shapeAttrib = mc.listRelatives(eachObj, s=True)[0]
                getType = mc.objectType(shapeAttrib)
                if getType in "mesh":
                    createSet = lib_sets.createSetProps(target=eachObj, name=ball['c'])
            # add Attrib on control tpl
            mc.addAttr(ball['c'], ln="Link", dt="string")
            mc.setAttr(ball['c'] + ".Link", createSet['setChild'], type="string")

        return ball