# coding: utf-8

import maya.cmds as mc
import math as mat
from functools import partial
from functools import partial
from ellipse_rig.library import lib_glossary as gloss
from ellipse_rig.library import lib_rigs as libRig
from ellipse_rig.library import lib_shapes,lib_attributes
reload(gloss)
reload(libRig)
reload(lib_shapes)
reload(lib_attributes)

class RigWorld(object):


    def __init__(self,**kwargs):

        self.name = 'FLY'
        self.info = 'tplInfo'
        self.nAll = gloss.lexicon('all')
        self.nRig = gloss.lexicon('RIG')
        self.nSa = gloss.lexicon('SA')
        self.nWorldCenter = gloss.lexicon('world')+'Center'
        self.nWorld = gloss.lexicon('world')
        self.nSwitch = gloss.lexicon('switchs')
        self.nWalk = gloss.name_format(prefix=gloss.lexicon('c'),name=gloss.lexicon('walk'),incP='')
        self.nFly = gloss.name_format(prefix=gloss.lexicon('c'),name=gloss.lexicon('fly'),incP='')
        self.nScale = gloss.name_format(prefix=gloss.lexicon('c'),name=gloss.lexicon('scale'),incP='')
        self.nSclScale = gloss.name_format(prefix=gloss.lexicon('s'),name=gloss.lexicon('scale'),incP='')
        self.nRevScale = gloss.name_format(prefix=gloss.lexicon('rev'),name=gloss.lexicon('scale'),incP='')
        self.nLocFly = gloss.name_format(prefix=gloss.lexicon('loc'),name=gloss.lexicon('fly'),incP='')
        self.nExpSclWorld = gloss.name_format(prefix=gloss.lexicon('exp'),name=gloss.lexicon('scale'),nFunc=gloss.lexicon('world'),incP='')
        self.typeWorld = "circleArrow4"
        self.typeWalk = "crossArrow"
        self.typeFly = "fly"
        self.typeScale = "sphere"
        self.valColorWorld = "yellow"

    def createRig(self):
        '''
        :param selObj:
        :param matchObj:
        :return: list of controllers created or recuperated
        '''
        mc.namespace(set=':')
        # FILTER BY TPL INFO_______________________________________
        lsInfo = gloss.Inspect_tplInfo(lFilter=[self.info,self.name])
        getTplFly = mc.getAttr(lsInfo[0]+'.fly')
        getTplWorld = mc.getAttr(lsInfo[0]+'.world')
        sclW = mc.getAttr(getTplWorld +'.scale')[0]
        # CREATE ________________________________
        if mc.objExists(self.nWorld) == True:
            pass
        else:
            # CREATE ALL ________________________________
            all = libRig.createObj(partial(mc.group, **{'n':self.nAll, 'em': True}))
            # CREATE RIG ________________________________
            rig = libRig.createObj(partial(mc.group, **{'n':self.nRig, 'em': True}), father=self.nAll)
            # CREATE SA ________________________________
            sa = libRig.createObj(partial(mc.group, **{'n':self.nSa, 'em': True}), father=self.nRig)
            # CREATE WORLD CENTER ________________________________
            worldCenter = libRig.createObj(partial(mc.group, **{'n':self.nWorldCenter, 'em': True}), father=self.nRig)

            # CREATE WORLD ______________________________
            world = libRig.createObj(partial(mc.joint, **{'n':self.nWorld}), shape= libRig.Shp([self.typeWorld],
                                    size= (5*sclW[0],5*sclW[0],5*sclW[0])), father=all, attributs={"drawStyle": 2})
            # CREATE SWITCH_ALL _________________________
            switchAll = libRig.createObj(partial(mc.group, **{'n':self.nSwitch, 'em': True}), father=self.nAll)
            # CREATE WALK _______________________________
            walk = libRig.createController(name=self.nWalk, shape= libRig.Shp([self.typeWalk],
                                    size= (3*sclW[0],3*sclW[0],3*sclW[0]),color="yellow"), father=world, attributs={"drawStyle": 2})
            mc.setAttr(walk['root'] + ".segmentScaleCompensate", 0)
            # CREATE FLY_________________________________
            fly = libRig.createController(name=self.nFly, shape= libRig.Shp([self.typeFly],
                                    size= (2,2,2),color="yellow"),match=getTplFly, father=walk['c'], attributs={"drawStyle": 2})
            # CREATE SCALE ______________________________
            scale = libRig.createController(name=self.nScale, shape= libRig.Shp([self.typeScale],
                                    size= (0.5*sclW[0],0.5*sclW[0],0.5*sclW[0]),color="yellow"), father=fly['c'], attributs={"drawStyle": 2})
            # CREATE SCl_SCALE __________________________
            sclScale = libRig.createObj(partial(mc.group, **{'n':self.nSclScale, 'em': True}), father=scale['c'])
            # CREATE SCl_SCALE __________________________
            revScale = libRig.createObj(partial(mc.group, **{'n':self.nRevScale, 'em': True}), father=sclScale)
            # CREATE SCl_SCALE __________________________
            locFly = libRig.createObj(partial(mc.group, **{'n':self.nLocFly, 'em': True}), father=revScale)

            # CREATE ATTRIBUTE SCALE_____________________
            attrSquash = mc.addAttr(scale['c'], ln="squash", nn="Squash", at="double", min=0, max=1, dv=1)
            mc.setAttr(scale['c'] + ".squash", e=True, k=True)
            attrSeparator = mc.addAttr(scale['c'], ln="spaceSwitch", nn="Space Switch", at="enum", en=".:")
            mc.setAttr(scale['c'] + ".spaceSwitch", e=True, k=True)
            AttrFollowWorld = mc.addAttr(scale['c'], ln="followWorld", nn="Follow World", at="double", min=0,max=10, dv=0)
            mc.setAttr(scale['c'] + ".followWorld", e=True, k=True)
            # CREATE NODE CONNECTION SCALE_______________
            pairBlendScale = mc.createNode("pairBlend", n="pairBlend_scale")
            pos = mc.getAttr(scale['root'] + '.t')
            rot = mc.getAttr(scale['root'] + '.r')
            mc.setAttr(pairBlendScale + '.inTranslate1', *pos[0])
            mc.setAttr(pairBlendScale + '.inRotate1', *rot[0])
            parentConScale = mc.parentConstraint(world, scale['root'], mo=True)[0]

            mc.connectAttr((parentConScale + ".constraintTranslateX"), (pairBlendScale + ".inTranslateX2"), f=True)
            mc.connectAttr((parentConScale + ".constraintTranslateY"), (pairBlendScale + ".inTranslateY2"), f=True)
            mc.connectAttr((parentConScale + ".constraintTranslateZ"), (pairBlendScale + ".inTranslateZ2"), f=True)
            mc.connectAttr((parentConScale + ".constraintRotateX"), (pairBlendScale + ".inRotateX2"), f=True)
            mc.connectAttr((parentConScale + ".constraintRotateY"), (pairBlendScale + ".inRotateY2"), f=True)
            mc.connectAttr((parentConScale + ".constraintRotateZ"), (pairBlendScale + ".inRotateZ2"), f=True)

            mc.connectAttr((pairBlendScale + ".outTranslateX"), (scale['root'] + ".translateX"), f=True)
            mc.connectAttr((pairBlendScale + ".outTranslateY"), (scale['root'] + ".translateY"), f=True)
            mc.connectAttr((pairBlendScale + ".outTranslateZ"), (scale['root'] + ".translateZ"), f=True)
            mc.connectAttr((pairBlendScale + ".outRotateX"), (scale['root'] + ".rotateX"), f=True)
            mc.connectAttr((pairBlendScale + ".outRotateY"), (scale['root'] + ".rotateY"), f=True)
            mc.connectAttr((pairBlendScale + ".outRotateZ"), (scale['root'] + ".rotateZ"), f=True)

            MultDoubleScale = mc.createNode("multDoubleLinear", n="mltDb_scale")
            mc.connectAttr((scale['c'] + ".followWorld"), (MultDoubleScale + ".input1"));
            mc.connectAttr((MultDoubleScale + ".output"), (pairBlendScale + ".weight"))

            MultMatrix = mc.createNode("multMatrix", n="mltMtx_scale")
            DecompMatrix = mc.createNode("decomposeMatrix", n="decompMtx_scale")
            mc.connectAttr((scale['root'] + ".inverseMatrix"), (MultMatrix + ".matrixIn[0]"));
            mc.connectAttr((MultMatrix + ".matrixSum"), (DecompMatrix + ".inputMatrix"))
            mc.connectAttr((DecompMatrix + ".outputRotate"), (revScale + ".rotate"));
            mc.connectAttr((DecompMatrix + ".outputScale"), (revScale + ".scale"));
            mc.connectAttr((DecompMatrix + ".outputShear"), (revScale + ".shear"));
            mc.connectAttr((DecompMatrix + ".outputTranslate"), (revScale + ".translate"))
            mc.connectAttr((scale['c'] + ".inverseMatrix"), (MultMatrix + ".matrixIn[1]"))
            mc.select(cl=True)
            # EXPRESSION FOR SCALE_________________________
            expressionScale = "//world scale expression;\n" + "$sq = %s" % (
                scale['c'] + ".squash;\n") + "$sx = %s" % (scale['c'] + ".scaleX;\n") + "$sy = %s" % (
                scale['c'] + ".scaleY;\n") + "$sz = %s" % (scale['c'] + ".scaleZ;\n") + "%s=$sx;\n" % (
                sclScale + ".scaleX") + "%s=$sy;\n" % (sclScale + ".scaleY") + "%s=$sz;\n" % (
                sclScale + ".scaleZ")
            expressionScale2 = "%s\n" % (
                expressionScale) + "if ($sq>0);\n" + "{\n" + "$sqx = 1/sqrt(abs($sx));\n" + "$sqy = 1/sqrt(abs($sy));\n" + "$sqz = 1/sqrt(abs($sz));\n"
            expressionScale3 = "%s" % (expressionScale2) + "%s=$sq*($sx*$sqy*$sqz)+(1-$sq)*$sx;\n" % (
                sclScale + ".scaleX") + "%s=$sq*($sy*$sqx*$sqz)+(1-$sq)*$sy;\n" % (
                sclScale + ".scaleY") + "%s=$sq*($sz*$sqx*$sqy)+(1-$sq)*$sz;\n" % (
            sclScale + ".scaleZ") + "}"
            mc.expression(s="%s" % (expressionScale3), n=self.nExpSclWorld)
            # SNAP CVS FLY_________________________________
            lib_shapes.snapShpCv(shpRef=getTplFly, shpTarget=self.nFly)

            # NAME CG_____________________________________________
            cgAll = gloss.name_format(prefix=gloss.lexiconAttr('cg'), name=gloss.lexiconAttr('cgAll'))
            if mc.objExists(lsInfo[0]+'.%s'%cgAll):
                pass
            else:
                mc.addAttr(lsInfo[0], ln=cgAll,dt='string',multi=True) # add Cog Ctr
            mc.setAttr(lsInfo[0]+'.%s[0]'%(cgAll),world,type='string')
            mc.setAttr(lsInfo[0]+'.%s[1]'%(cgAll),walk['c'],type='string')
            mc.setAttr(lsInfo[0]+'.%s[2]'%(cgAll),fly['c'],type='string')

            # SET SKIN ALL PARTS_________________________________________
            mc.select(cl=True)
            nSetPart = gloss.name_format(prefix=gloss.lexicon('set'),name=gloss.lexicon('skin'),nFunc=gloss.lexicon('all'))
            if not mc.objExists(nSetPart):
                mc.sets(n=nSetPart, em=True)