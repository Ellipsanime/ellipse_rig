# coding: utf-8

import maya.cmds as mc
from functools import partial
from ellipse_rig.library import lib_glossary as gloss
from ellipse_rig.library import lib_names,lib_rigs,lib_shapes,lib_sets,lib_connectNodes,lib_deformers
from ellipse_rig.library import lib_baseRig
from ellipse_rig.assets.asset_base import guide_world,rig_world
from ellipse_rig.assets.characters import guide_base

reload(gloss)
reload(lib_rigs)
reload(lib_names)
reload(lib_shapes)
reload(lib_sets)
reload(lib_connectNodes)
reload(lib_deformers)
reload(lib_baseRig)
reload(guide_world)
reload(guide_base)
reload(rig_world)
rig_world.RigWorld().createRig()  # instance class charGuide and run method createRig

class BallRig(rig_world.RigWorld):

    def __init__(self,name='ball',side='',tplInfo='tplInfo',selObj=None,matchObj=None,**kwargs):
        rig_world.RigWorld.__init__(self)
        self.info = tplInfo
        self.name = name
        self.typeCircle= "circle"
        self.valColorCtr = "red"
        self.valColorCtr2 = "blue"
        self.rotShape = [0,0,0]
        self.prefix = lib_names.type_name('c')
        self.side = side
        self.selObj = selObj
        self.matchObj = matchObj
        self.size = (1.5,1.5,1.5)
        self.size2 = (1.3,1.3,1.3)
        self.size3 = (1.1,1.1,1.1)

    def createRig(self):
        '''
        :param selObj:
        :param matchObj:
        :return:
        '''
        # FILTER BY TPL INFO_______________________________________
        lsInfo = gloss.Inspect_tplInfo(lFilter=[self.info,self.name])
        if self.selObj != []:
            for i, eachTpl in enumerate(lsInfo):
                incPart = mc.getAttr(eachTpl+'.incInfo')
                ''' names '''
                nRIG = lib_names.name_format(prefix=lib_names.type_name('rig'), name=self.name,incP=incPart)
                nAllSWITCH= lib_names.name_format(prefix=lib_names.type_name('all'), name='SWITCH',incP=incPart)
                nBallCtr = lib_names.name_format(prefix=self.prefix, name=self.name, nSide=self.side,incP=incPart)
                nBallCtr2 = lib_names.name_format(prefix=self.prefix, name=self.name + 'Rot', nSide=self.side,incP=incPart)
                nBallCtrSquash = lib_names.name_format(prefix=self.prefix, name=self.name, nFunc=lib_names.type_name('squash'), nSide=self.side,incP=incPart)
                nDEFORMER = lib_names.name_format(prefix=lib_names.type_name('DEFORMER'), nSide=self.side,incP=incPart)
                nBallSquash = lib_names.name_format(prefix=lib_names.type_name('squash'), name=self.name, nSide=self.side,incP=incPart)
                nHookSquash = lib_names.name_format(prefix=lib_names.type_name('hook'), name=self.name, nFunc=lib_names.type_name('squash'), nSide=self.side,incP=incPart)
                nSwitchRoot = lib_names.name_format(prefix=lib_names.type_name('root'), name=self.name, nFunc=lib_names.type_name('switch'), nSide=self.side,incP=incPart)

                ''' create '''
                dic = {}
                # create RIG
                RIG = lib_rigs.createObj(partial(mc.group, **{'n':nRIG, 'em': True}), refObj=self.matchObj)
                SWITCH = lib_rigs.createObj(partial(mc.group, **{'n':nAllSWITCH, 'em': True}), father=RIG, refObj=self.matchObj)
                # create CTR BALL
                ball=lib_rigs.createController(name=nBallCtr,shape=lib_rigs.Shp([self.typeCircle], color=self.valColorCtr,
                    size=self.size, rotShp=self.rotShape),match=self.matchObj, father=RIG,
                    attributs={"drawStyle": 2}, worldScale=self.nWorld)
                ball2=lib_rigs.createController(name=nBallCtr2,shape=lib_rigs.Shp([self.typeCircle], color=self.valColorCtr,
                    size=self.size2, rotShp=self.rotShape),match=self.matchObj, father=ball['c'],
                    attributs={"drawStyle": 2}, worldScale=self.nWorld)

                ballSquash=lib_rigs.createController(name=nBallCtrSquash,shape=lib_rigs.Shp([self.typeCircle], color=self.valColorCtr,
                    size=self.size3, rotShp=self.rotShape),match=self.matchObj,addInf=True, father=ball['c'],
                    attributs={"drawStyle": 2}, worldScale=self.nWorld)

                lib_connectNodes.connectAxis(ball2['c'], ballSquash['inf'], rot=False, scl=False)

                ## create DEFORMER
                DEFORMER= lib_rigs.createObj(partial(mc.group, **{'n':nDEFORMER, 'em': True}), father=RIG, refObj=self.matchObj)
                squash= lib_rigs.createObj(partial(mc.group, **{'n':nBallSquash, 'em': True}), refObj=self.matchObj)
                hookSquash= lib_rigs.createObj(partial(mc.group, **{'n':nHookSquash, 'em': True}), father=DEFORMER, childLst=[squash], refObj=self.matchObj)
                lib_connectNodes.connectMatrixAxis(driver=ballSquash['c'], slave=hookSquash)

                # create Switch for Attributs ###
                switchRoot = lib_rigs.createObj(partial(mc.group, **{'n': nSwitchRoot , 'em': True}), refObj=self.matchObj)
                shapeAttr = mc.createNode("nurbsCurve", p=switchRoot)
                trShape = mc.listRelatives(switchRoot, s=True)
                splitName = nSwitchRoot.split("_")
                nameSwitch = lib_names.renameSplit(selObj=nSwitchRoot, namePart=[splitName[0]], newNamePart=[lib_names.type_name('c')])
                mc.rename(trShape,nameSwitch)
                mc.parent(switchRoot, nAllSWITCH)
                # Squash
                lib_deformers.createSquash(self.selObj, nameSwitch, squash, skObjLst=[ball2['sk']], instanceShpLst=[ball['c'], ball2['c'], ballSquash['c']])
            else:
                mc.warning('Please Select Tpl Object or Object')

