# coding: utf-8

import maya.cmds as mc
from functools import partial
from ellipse_rig.library import lib_names,lib_rigs,lib_shapes,lib_curves,lib_sets,lib_connectNodes
reload(lib_names)
reload(lib_rigs)
reload(lib_shapes)
reload(lib_curves)
reload(lib_sets)
reload(lib_connectNodes)
class RopeGuide(object):

    def createRig(self,selObj,matchObj=None,side=None,numbObj=None):
        '''
        :param selObj:
        :param matchObj:
        :param side:
        :param numObj:
        :return:
        '''
        # init incAttr
        incVal = lib_names.incPart(self.nIncAttr)
        ''' names '''
        nRIG = lib_names.name_format(prefix=lib_names.type_name('rig'), name=self.name, nFunc=self.nFunc, incPart=incVal)
        nSurfAttach = lib_names.name_format(prefix='surfAttach', name=self.name, nFunc=self.nFunc, incPart=incVal)
        nLoft = lib_names.name_format(prefix='loft', name=self.name, nFunc=self.nFunc, incPart=incVal)
        nRopeGrp = lib_names.name_format(prefix="rig", name=self.name, nFunc=self.nFunc + 'Int', nSide=self.side, incPart=incVal)
        nRopeMaster = lib_names.name_format(prefix=self.prefix, name=self.name, nFunc=self.nFuncMaster, nSide=self.side, incPart=incVal)
        ''' create '''
        RIG = lib_rigs.createObj(partial(mc.group, **{'n': nRIG, 'em': True}), refObj=selObj, incPart=incVal)
        surfAttach = lib_rigs.createObj(partial(mc.group, **{'n': nSurfAttach, 'em': True}), father=RIG, refObj=selObj, incPart=None)
        ropeMaster = lib_rigs.createController(name=nRopeMaster, shape=lib_rigs.Shp([self.typeSquare],
                                                                                    color=self.valColorMasterCtr, size=0.8), match=lib_rigs.Match(pos=selObj), father=RIG, refObj=selObj, attributes={"drawStyle": 2}, incPart=incVal)
        ropeGrp = lib_rigs.createObj(partial(mc.group, **{'n': nRopeGrp, 'em': True}), father=RIG, refObj=selObj, incPart=incVal)

        # number of subdivide part
        getCtr =[]; getRoot =[]; getSk =[]; getIkSk =[]
        valMove=[0, round((float(8 - 1) / float(numbObj - 1)), 3), 0]
        for eachObj in range(numbObj):
            incValMove = ((eachObj*valMove[0]),(eachObj*valMove[1]),(eachObj*valMove[2]))
            ''' names '''
            nRope = lib_names.name_format(prefix=self.prefix, name=self.name, nFunc=self.nFunc,
                                          inc=str(eachObj+1), nSide=self.side, incPart=incVal)
            ''' create '''
            rope=lib_rigs.createController(name=nRope,
                                           shape=lib_rigs.Shp([self.typeSquare], color=self.valColorCtr, size=0.3),
                                           match=lib_rigs.Match(pos=incValMove), father=ropeMaster['c'], refObj=selObj, incPart=incVal)
            # add ctr IK and ctr knot
            if eachObj == 0 or eachObj == (numbObj-1):
                ''' names '''
                nIkRope = lib_names.name_format(prefix=lib_names.type_name('ik'), name=self.name, nFunc=self.nFunc + 'Ik',
                                                inc=str(eachObj+1), nSide=self.side, incPart=incVal)
                nKnot = lib_names.name_format(prefix=self.prefix, name=self.name, nFunc='Knot', inc=str(eachObj + 1), nSide=self.side, incPart=incVal)
                ''' create '''
                ikCtr= lib_rigs.createController(name=nIkRope, shape=lib_rigs.Shp([self.typeSquare],
                                                                                  color=self.valColorCtrIK, size=0.5), match=lib_rigs.Match(pos=incValMove), father=ropeMaster['c'], refObj=selObj, incPart=incVal)

                knotCtr = lib_rigs.createController(name=nKnot, shape=lib_rigs.Shp([self.typeSquare],
                                                                                   color=self.valColorKnotCtr, size=0.2), match=lib_rigs.Match(pos=incValMove), father=rope['c'], refObj=selObj, incPart=incVal)
                mc.move(0,0.5,0,knotCtr['root'],r=True)
                if eachObj == 0:
                    mc.move(0,-1, 0, knotCtr['root'], r=True)
                getIkSk.append(ikCtr['sk'])
            getCtr.append(rope['c'])
            getRoot.append(rope['root'])
            getSk.append(rope['sk'])
        # curves and loft
        concLst = [getCtr[0]]
        concLst.append(getCtr[-1])
        getCrv = lib_curves.createDoubleCrv(objLst=concLst, axis='Z', offset=0.2)
        loft = lib_curves.createLoft(name=nLoft, objLst=getCrv['crv'], father=surfAttach, deleteCrv=True)
        mc.skinCluster(getIkSk,loft,tsb=1,mi=1)
        getRoot.append(loft)
        lib_connectNodes.surfAttach(selObj=getRoot, parentInSA=True, parentSA=surfAttach)
        mc.select(cl=True)


    def __init__(self,name='',side='',*args):
        self.name = 'rope'
        self.typeSquare= "square"
        self.valColorCtr = "yellow"
        self.valColorCtrIK = "red4"
        self.valColorMasterCtr = "brown24"
        self.valColorKnotCtr = "yellow22"
        self.rotShape = [0,0,0]
        self.prefix = lib_names.type_name('tpl')
        self.nFunc = lib_names.type_name('tpl')
        self.nFuncMaster = lib_names.type_name('mtrTpl')
        self.side = side
        self.nIncAttr = lib_names.type_name('rig') + '_' + self.name + 'Tpl' + '_' + '1'

    def generate(self,selObj=None, matchObj=None,side=None,numbObj=None, *args):
        tplRope = self.createRig(selObj,matchObj=matchObj,side=side,numbObj=numbObj)
        return tplRope


