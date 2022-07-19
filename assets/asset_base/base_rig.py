# coding: utf-8

import maya.cmds as mc
from functools import partial

from ellipse_rig.library import lib_names,lib_rigs,lib_shapes
reload(lib_rigs)
reload(lib_names)
reload(lib_shapes)

class RigWorld(object):

    def createRig(self,selObj,matchObj):
        '''
        :param selObj:
        :param matchObj:
        :return: list of controllers created or recuperated
        '''
        ''' names '''
        nALL = lib_names.name_format(prefix=lib_names.type_name('all'))
        nRIG = lib_names.name_format(prefix=lib_names.type_name('rig'))
        nWORLD = lib_names.name_format(prefix=lib_names.type_name('world'))
        nGRP_SWITCH = lib_names.name_format(prefix=lib_names.type_name('all'), name=lib_names.type_name('switch'))
        nROOT_WALK = lib_names.name_format(prefix=lib_names.type_name('root'), name='walk')
        nCTR_WALK = lib_names.name_format(prefix=lib_names.type_name('c'), name='walk')
        nROOT_FLY = lib_names.name_format(prefix=lib_names.type_name('root'), name='fly')
        nCTR_FLY = lib_names.name_format(prefix=lib_names.type_name('c'), name='fly')

        ''' create '''
        dic = {}
        # create ALL
        topNode = lib_rigs.createObj(partial(mc.group, **{'n': nALL, 'em': True}))
        # create RIG
        createRootRig = lib_rigs.createObj(partial(mc.group, **{'n': nRIG, 'em': True}), father=topNode)
        # create World
        ctrWorld = lib_rigs.createObj(partial(mc.joint, **{'n': nWORLD}), shape= lib_rigs.Shp([self.typeSquare], size= 1.2), match=lib_rigs.Match(pos=matchObj, rot=matchObj),
                                      father=topNode, refObj=selObj, attributes={"drawStyle": 2})
        # create Switch Global
        rootSwitchs = lib_rigs.createObj(partial(mc.createNode, 'transform', **{'n': nGRP_SWITCH}), father=topNode, refObj=selObj)
        # create Walk
        createRootWalk = lib_rigs.createObj(partial(mc.group, **{'n': nROOT_WALK, 'em': True}),
                                            match=lib_rigs.Match(pos=matchObj, rot=matchObj), father=ctrWorld, refObj=selObj)
        ctrWalk = lib_rigs.createObj(partial(mc.joint, **{'n': nCTR_WALK}), shape= lib_rigs.Shp([self.typeCircle], color=self.valColorWalk),
                                     match=lib_rigs.Match(pos=matchObj, rot=matchObj), father=createRootWalk, refObj=selObj, attributes={"drawStyle": 2})
        # Create Fly
        createRootFly = lib_rigs.createObj(partial(mc.group, **{'n': nROOT_FLY, 'em': True}),
                                           match=lib_rigs.Match(pos=matchObj, rot=matchObj), father=ctrWalk, refObj=selObj)
        ctrFly = lib_rigs.createObj(partial(mc.joint, **{'n': nCTR_FLY}), shape= lib_rigs.Shp([self.typeCircle], color=self.valColorFly, size= 0.8),
                                    match=lib_rigs.Match(pos=matchObj, rot=matchObj), father=createRootFly, refObj=matchObj, attributes={"drawStyle": 2})


        dic["ALL"] = topNode
        dic["RIG"] = createRootRig
        dic["WORLD"] = ctrWorld
        dic["SWITCH"] = rootSwitchs
        dic["rootWalk"] = createRootWalk
        dic["cWalk"] = ctrWalk
        dic["rootFly"] = createRootFly
        dic["cFly"] = ctrFly

        #for each in range(4):
        #    ctrName = names_lib.name_format(prefix=names_lib.type_name('c'),name='toto',incABC=None)
        #    rigs_lib.createController(name=ctrName,shapeCtr=rigs_lib.Shp(["square"],color=names_lib.type_color("red"),size= 0.5), match=rigs_lib.Match(pos=matchObj,rot=matchObj),refObj=selObj)
        return dic

    def __init__(self,side='', *args):

        self.typeSquare = "square"
        self.typeCircle = "circle"
        self.valColorWorld = "yellow"
        self.valColorWalk = "brown24"
        self.valColorFly = "red"
        self.valColorScale = "red"
        self.rotShapeFK = [0, 0, 0]
        self.side = side


    def generate(self,selObj=None,matchObj=None):
        ## Creation du World
        createWorld = self.createRig(selObj,matchObj)
        return createWorld