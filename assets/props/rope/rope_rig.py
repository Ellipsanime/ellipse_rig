# coding: utf-8

from ellipse_rig.library import lib_names
from ellipse_rig.library import lib_rigs
import maya.cmds as mc
from functools import partial
from ellipse_rig.library import lib_names,lib_rigs,lib_shapes,lib_curves,lib_sets,lib_connectNodes
reload(lib_names)
reload(lib_rigs)
reload(lib_shapes)
reload(lib_curves)
reload(lib_sets)
reload(lib_connectNodes)

class RopeRig(object):

    def createRig(self,selObj,matchObj=None,side=None):
        '''
        :param selObj:
        :param matchObj:
        :param side:
        :param numObj:
        :return:
        '''
        if selObj != []:

            ############# BASE #############
            getRig = lib_names.InspectE(lFilter=['rig', self.name])
            dicRig ={}
            dicSurfAttach ={}
            for key,val in getRig.items():
                ''' names '''
                nRIG = lib_names.name_format(prefix=lib_names.type_name('rig'), name=self.name, incPart=key)
                nSurfAttach = lib_names.name_format(prefix='surfAttach', name=self.name, incPart=key)
                nRigAddRoot = lib_names.name_format(prefix=lib_names.type_name('root'), name='rig', nFunc=lib_names.type_name('add'), incPart=key)
                nRigAdd = lib_names.name_format(prefix=self.prefix, name='rig', nFunc=lib_names.type_name('add'), incPart=key)
                ''' create '''
                rig = lib_rigs.createObj(partial(mc.group, **{'n': nRIG, 'em': True}), refObj=val)
                dicRig[key]= rig
                surfAttach = lib_rigs.createObj(partial(mc.group, **{'n': nSurfAttach, 'em': True}), father=rig, refObj=selObj, incPart=False)
                dicSurfAttach[key]= surfAttach
                rigAddRoot = lib_rigs.createObj(partial(mc.group, **{'n': nRigAddRoot, 'em': True}), father=rig, refObj=selObj, incPart=False)
                rigAdd = lib_rigs.createObj(partial(mc.group, **{'n': nRigAdd, 'em': True}), shape= lib_rigs.Shp([self.typeRigAdd],
                                                                                                                 color=self.valColorRigAdd, size= 1), match=lib_rigs.Match(pos=matchObj, rot=matchObj), father=rigAddRoot, incPart=False)

            ############ IK #############
            getIK = lib_names.InspectE(lFilter=['ik', self.name])
            getLoftIk = ''
            dicIk ={}
            for j, (keyIk, valIk) in enumerate(getIK.items()):
                ''' names '''
                nLoft = lib_names.name_format(prefix='loft', name=self.name + "IK", incPart=keyIk)
                getIkSk = []
                getIkC = []
                for i, each in enumerate(valIk):
                    ''' names '''
                    nIK = lib_names.name_format(prefix=lib_names.type_name('ik'), name=self.name, nFunc=lib_names.type_name('ik'), inc=str(i + 1), incPart=keyIk)
                    ''' create '''
                    ik = lib_rigs.createController(name=nIK, shape=lib_rigs.Shp([self.typeSquare], color=self.valColorIK, size=1),
                                                   match=lib_rigs.Match(pos=valIk[i], rot=valIk[i]), father=dicRig.values()[j], refObj=[valIk[i]], incPart=keyIk)
                    getIkC.append(ik['c'])
                    getIkSk.append(ik['sk'])
                dicIk[keyIk]= getIkC
                getCrv = lib_curves.createDoubleCrv(objLst=valIk, axis='Z', offset=0.1)
                loft = lib_curves.createLoft(name=nLoft, objLst=getCrv['crv'], father=dicSurfAttach.values()[j], deleteCrv=True)
                mc.skinCluster(getIkSk, loft, tsb=1, mi=1)
                getLoftIk += loft
                mc.select(cl=True)
            ############# FK BASE #############
            getFk = lib_names.InspectE(lFilter=['root', self.name], lDel=['Ik', 'Knot', 'MtrTpl'])
            dicFk ={}
            for j, (keyIk, valIk) in enumerate(getFk.items()):
                ''' names '''
                nLoft = lib_names.name_format(prefix='loft', name=self.name + "FK", incPart=keyIk)
                getFkSk = []
                getRootFk = []
                for i, each in enumerate(valIk):
                    ''' names '''
                    nFk = lib_names.name_format(prefix=lib_names.type_name('c'), name=self.name, inc=str(i + 1), incPart=keyIk)
                    ''' create '''
                    fk = lib_rigs.createController(name=nFk, shape=lib_rigs.Shp([self.typeSquare], color=self.valColorFk, size=1),
                                                   match=lib_rigs.Match(pos=valIk[i], rot=valIk[i]), father=dicRig.values()[j], refObj=[valIk[i]], incPart=keyIk)
                    getFkSk.append(fk['sk'])
                    if each == valIk[0] or each == valIk[-1]:
                        getRootFk.append(fk['root'])
                dicFk[keyIk] = getRootFk
                getCrv = lib_curves.createDoubleCrv(objLst=valIk, axis='Z', offset=0.2)
                loft = lib_curves.createLoft(name=nLoft, objLst=getCrv['crv'], father=dicSurfAttach.values()[j], deleteCrv=True)
                mc.skinCluster(getFkSk, loft, tsb=1, mi=1)
            # connect FK
            for k, (keyIk, valIk) in enumerate(dicIk.items()):
                for i, each in enumerate(valIk):
                    mc.parent (dicFk.values()[k][i],each)



                #links_lib.surfAttach(selObj=getRoot, parentInSA=True, parentSA=dicSurfAttach.values()[j])
        else:
            mc.warning('Please Select Tpl Object or Object')


    def __init__(self, name='', side='', *args):
        self.name = 'rope'
        self.typeRigAdd = "rigAdd"
        self.valColorRigAdd = "blue"
        self.typeSquare = "square"
        self.valColorIK = "red4"
        self.valColorFk = "yellow"
        self.valColorCtrIK = "red4"
        self.valColorMasterCtr = "brown24"
        self.valColorKnotCtr = "yellow22"
        self.rotShape = [0, 0, 0]
        self.prefix = lib_names.type_name('c')
        self.side = side


    def generate(self, selObj=None, matchObj=None, side=None,*args):
        rope = self.createRig(selObj, matchObj=matchObj, side=side)
        return rope