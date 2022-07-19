# coding: utf-8

import maya.cmds as mc
from functools import partial
import re

from ellipse_rig.library import lib_glossary as gloss
from ellipse_rig.library import lib_rigs as libRig
from ellipse_rig.library import lib_rigPreset as libRgPreset
from ellipse_rig.library import lib_curves, lib_sets, lib_connectNodes, lib_attributes, lib_shapes
from ellipse_rig.library import lib_baseRig
from ellipse_rig.assets.asset_base import guide_world, rig_world
from ellipse_rig.assets.characters import guide_base
from ellipse_rig.library.lib_constraints import crtHook
from ellipse_rig.library.lib_math import getNearestTrans
from ellipse_rig.library.lib_hierarchy import get_all_parents

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
reload(rig_world)

# instance class charGuide and run method createRig
rig_world.RigWorld().createRig()


def init_prefixes(prefix_list):
    prefix_dict = dict()
    for prefix_type in prefix_list:
        try:
            prefix_dict[prefix_type] = gloss.lexicon(prefix_type)
        except mc.warning:
            pass
    return prefix_dict


class Wing(rig_world.RigWorld):

    def __init__(self, name='wing', tplInfo='tplInfo', hook='', *args):
        rig_world.RigWorld.__init__(self)
        self.hook = hook
        self.name = name
        self.nameFeatherPart = 'feather'
        self.info = tplInfo
        self.typeArrow = "arrowQuadro2"
        self.typeCircle = "circle"
        self.typeSquare = "square"
        self.typePin = "sphere"
        self.shpRotIk = (0, 45, 0)
        self.rigAdd = "rigAdd"
        self.selTypeFkWing = 'roll'
        self.typeShapeIkPath = "arrowSingle2"
        self.typeShapeIkPath2 = "star"
        self.typeShapeIk = "square"
        self.typeShapeCtr = "circle"
        self.typeShapeFkBaseWing = "triangle"
        self.CtrSlide = "sphere"
        self.side = (mc.attributeQuery(
            "update", node=self.info, listEnum=1)[0]).split(":")[1]
        if self.side == 'empty':
            self.side = ''
        color = lib_shapes.side_color(side=self.side)
        self.valColorCtr = color["colorCtr"]
        self.valColorCtrIK = color["colorIk"]
        self.valColorMasterCtr = color["colorMaster"]
        self.nbCtr = 8
        worldScl = mc.getAttr("tpl_WORLD"+".scaleX")
        self.shpSizeIk = (0.7*worldScl, 0.7*worldScl, 0.7*worldScl)
        self.shpSizeIkMid = (0.5*worldScl, 0.5*worldScl, 0.5*worldScl)
        self.shpSizeFkInvert = 0.8*worldScl
        self.shpSizeCtrSoft = (1.2*worldScl, 1.2*worldScl, 1.2*worldScl)
        self.valScl = float(mc.getAttr("tpl_WORLD" + ".scaleX"))





    def aimOnNbs(self, loc, nbs, trgtNode, axis):
        aim = [1,0,0]
        if axis == 'Y':
            aim = [0,1,0]
        if axis == 'Z':
            aim = [0,0,1]
        locMov = mc.spaceLocator(n='moveAim')[0]
        mc.parent(locMov, loc)
        for attr in ['translate', 'rotate']:
                for chan in ['X', 'Y', 'Z']:
                    mc.setAttr(locMov+'.'+attr+chan, 0.0)
        mc.setAttr(locMov+'.translate'+axis, 100)
        locSnap = mc.spaceLocator(n='snaped')[0]
        cPOS =  mc.createNode('closestPointOnSurface')
        mc.connectAttr(nbs+'.worldSpace[0]', cPOS+'.inputSurface', f=True)

        startPoint = mc.xform(loc, q=True, ws=True, t=True)
        endPoint = mc.xform(locMov, q=True, ws=True, t=True)

        crvAim = mc.curve(n='aim',d=1, k=[0, 1], p=[startPoint, endPoint])
        projCrv = mc.projectCurve(crvAim, nbs, dx=aim[0], dy=aim[1], dz=aim[2], tol=0.0001, un=True)

        hitParam = mc.curveIntersect(crvAim, projCrv[0], ud=True, tol=.9, d=aim)
        if hitParam:
            hitPos = mc.pointOnCurve(crvAim, pr=float(hitParam.split(' ')[0]), p=True )
            mc.setAttr(locSnap+'.t', *hitPos)
        elif not hitParam:
            mc.delete(projCrv)
            newNbs = mc.extendSurface(nbs, ch=True, em=0, et=0, d=1, jn=100, rpo=False, es=2, ed=2)
            mc.setAttr(newNbs[-1]+'.distance', 10)
            projCrv = mc.projectCurve(crvAim, newNbs[0], dx=aim[0], dy=aim[1], dz=aim[2], tol=0.0001, un=True)
            hitParam = mc.curveIntersect(crvAim, projCrv[0], ud=True, tol=.9, d=aim)
            hitPos = mc.pointOnCurve(crvAim, pr=float(hitParam.split(' ')[0]), p=True)
            mc.setAttr(locSnap+'.t', *hitPos)
            nPOC = mc.createNode('nearestPointOnCurve')



            newCrvs = mc.intersect(nbs, newNbs[0], fs=True ,cos=False, o=True)
            lChild = mc.listRelatives(newCrvs[0], c=True)
            hitCrv = mc.attachCurve(*lChild, ch=False, m=0, kmk=False, rpo=True, bb=0.5, bki=False, o=True)[0]
            hitcvShp = mc.listRelatives(hitCrv, s=True)[0]
            mc.connectAttr(hitcvShp+'.worldSpace[0]', nPOC+'.inputCurve')
            mc.connectAttr(locSnap+'.t', nPOC+'.inPosition')
            nearestParam = mc.getAttr(nPOC+'.parameter')
            hitPos = mc.pointOnCurve(crvAim, pr=float(hitParam.split(' ')[0]), p=True)
            mc.setAttr(locSnap+'.t', *hitPos)
            mc.delete(newCrvs)
            mc.delete(nPOC)
            mc.delete(newNbs)





        mc.connectAttr(locSnap+'.t', cPOS+'.inPosition', f=True)
        paramU = mc.getAttr(cPOS+'.parameterU')
        paramV = mc.getAttr(cPOS+'.parameterV')
        mc.setAttr(trgtNode+'.parameterU', paramU)
        mc.setAttr(trgtNode+'.parameterV', paramV)
        for obj in [cPOS, locSnap, projCrv, crvAim, locMov]:
            try:
                mc.delete(obj)
            except:
                pass


    #aimOnNbs('vecOrig', 'nbsShape', 'Y')

    def createWing(self):
        worldScl = mc.getAttr("tpl_WORLD"+".scaleX")
        # INIT PREFIXES

        prefix_dict = init_prefixes(['sk', 'inf', 'rig',
                                     'sa', 'c', 'loft', 'add',
                                     'root', 'switch', 'aim',
                                     'upV', 'cv', 'cns', 'mltDiv',
                                     'mtxDcp', 'mltDblLin', 'dblLin',
                                     'rot', 'scale', 'cv', 'plMA',
                                     'NoTouch', 'cog', 'set', 'skin'])

        # FILTER BY TPL INFO_______________________________________
        lsInfo = gloss.Inspect_tplInfo(lFilter=[self.info, self.name])
        # []

        #lsInfoFeatherPart = gloss.Inspect_tplInfo(
        #    lFilter=['tplInfo', self.nameFeatherPart])
        #lsInfoFeatherPart = [infoNode for infoNode in lsInfoFeatherPart if self.side in infoNode]
        lsInfoFeatherPart = mc.listConnections("{}.children".format(self.info), d=True) or []
        # []

        # CREATE RIG TO LISTE INFO_________________________________
        dicBuf = {}
        dicSk = {}
        lCtrl = []
        lsAllRotBaseWing = []
        lsAllRotBackWing = []
        lsAllAttrRot = []
        lsAllInfBaseWing = []
        lsAllSABaseWing = []
        lsRIGWing = []

        # STEP WING__________________________________
        lsAllRotBaseWingStep = []
        lsAllRotBackWingStep = []
        lsAllSABaseWingStep = []
        lsAllInfBaseWingStep = []

        # GET INFO TO CREATE RIG________________________________
        incPart = mc.getAttr(self.info + '.incInfo')
        sclWorld = mc.getAttr("tpl_WORLD" + ".scaleX")
        # ('incPart', u'1')

        color = lib_shapes.side_color(side=self.side)
        valColorCtr = color["colorCtr"]
        valColorCtrIK = color["colorIk"]
        valColorMstCtr = color["colorMaster"]
        sbDvArm = [mc.getAttr(self.info + '.subDvArm[0]') for i in range(
            mc.getAttr(self.info + '.subDvArm[0]', mi=True, s=True))][0]

        lsTplIkBackWg = [mc.getAttr(self.info + '.ik[%s]' % i)
                         for i in range(mc.getAttr(self.info + '.ik', mi=True, s=True))]
        lsTplIkBaseWg = [mc.getAttr(self.info + '.ikBase[%s]' % i)
                         for i in range(mc.getAttr(self.info + '.ikBase', mi=True, s=True))]

        # lsTplIkBackWg' -> [u'tpl_wingBack1_1_L', u'tpl_wingBack2_1_L', u'tpl_wingBack3_1_L', u'tpl_wingBack4_1_L', u'tpl_wingBack5_1_L']

        all_tpl_dict = dict()
        for attr_name in ['featherLinesBack', 'featherLinesBase',
                          'lineCtrArm', 'lineCtrBack']:
            current_attr = '{}.{}'.format(self.info, attr_name)
            current_key = 'ls_{}Tpl'.format(attr_name)
            all_tpl_dict[current_key] = list()

            if mc.getAttr('{}[0]'.format(current_attr)) == "0":
                continue

            for i in range(mc.getAttr(current_attr, mi=True, s=True)):
                tpl_string = mc.getAttr('{}[{}]'.format(current_attr, i))
                tpl_list = re.findall(r"\w+", tpl_string)
                if attr_name in ['featherLinesBase']:
                    tpl_list = [mc.listConnections("{}.U".format(item),
                                                   d=True, t="joint")[0] for item in tpl_list]
                all_tpl_dict[current_key].append(tpl_list)

        # CREATE SYSTEM WING ################################

        # CREATE RIG WING GRP_____________________________________________________
        nRIGWing = gloss.name_format(
            prefix=prefix_dict['rig'], name=self.name, nSide=self.side, incP=incPart)
        rigWing = libRig.createObj(
            partial(mc.group, **{'n': nRIGWing, 'em': True}), match=None, father=None)
        lsRIGWing.append(rigWing)
        # CREATE RIG SA GRP_____________________________________________________
        nSaWing = gloss.name_format(prefix=prefix_dict['sa'], name=self.name,
                                    nSide=self.side, incP=incPart)
        saWing = libRig.createObj(
            partial(mc.group, **{'n': nSaWing, 'em': True}), match=None, father=self.hook)
        # CREATE RIG LOFT GRP_____________________________________________________
        nLoftWing = gloss.name_format(prefix=prefix_dict['loft'], name=self.name, nSide=self.side,
                                      incP=incPart)
        loftWing = libRig.createObj(partial(
            mc.group, **{'n': nLoftWing, 'em': True}), match=None, father=rigWing, attributs={"visibility": 0})

        nRigFeatherRot = gloss.name_format(prefix=prefix_dict['rig'], name='featherRot', nSide=self.side,
                                           incP=incPart)
        rigFeatherRot = libRig.createObj(partial(
            mc.group, **{'n': nRigFeatherRot, 'em': True}), match=None, father=rigWing)

        nHooksWing = gloss.name_format(prefix='hooks', name=self.name, nSide=self.side,
                                       incP=incPart)
        hooksWing = libRig.createObj(partial(mc.group, **{'n': nHooksWing, 'em': True}),
                                     match=None, father=rigWing)

        # CREATE SWITCH CTR_____________________________________________________
        nSwitchsRootWing = gloss.name_format(
            prefix=prefix_dict['root'], name=self.name, nFunc=prefix_dict['switch']+'Wing', nSide=self.side, incP=incPart)
        nSwitchsCtrWing = gloss.name_format(
            prefix=prefix_dict['c'], name=self.name, nFunc=prefix_dict['switch']+'Wing', nSide=self.side, incP=incPart)
        createSwitchsWing = mc.createNode("nurbsCurve", n=nSwitchsCtrWing)
        fatherWing = mc.listRelatives(createSwitchsWing, p=True)
        rootSwitchsWing = mc.rename(fatherWing, nSwitchsRootWing)
        mc.parent(rootSwitchsWing, rigWing)
        # ADD ATTRIBUTES TO SWITCH____________________________________________
        mc.addAttr(nSwitchsCtrWing, ln="wing_Option",
                   at="enum", en="_________")
        mc.setAttr(nSwitchsCtrWing + ".wing_Option", e=True, k=True)
        mc.addAttr(nSwitchsCtrWing, ln="constraintBody",
                   at="double", min=0, max=10, dv=0)
        mc.setAttr(nSwitchsCtrWing + ".constraintBody", e=True, k=True)
        # HIDE DEFAULT ATTRIBUTES ____________________________________________
        lib_attributes.hide_ctrl_hist(selObj=nSwitchsRootWing)

        lsRootFkBaseWing = []
        lsFkBaseWing = []
        lsBufWingBase = []
        lsAimHandCtr = []
        lsUpVHandCtr = []

        # CREATE CTR BASE_____________________________________________________
        for index, current_tpl in enumerate(lsTplIkBaseWg):
            # CREATE BUF_______________________________________________________
            nBufWingBase = gloss.name_format(
                prefix=prefix_dict['inf'], name=self.name+'BackToArm'+str(index+1), nSide=self.side, incP=incPart)
            bufWingBase = libRig.createObj(partial(
                mc.group, **{'n': nBufWingBase, 'em': True}), match=[current_tpl], father=rigWing)
            lsBufWingBase.append(bufWingBase)

            if current_tpl == lsTplIkBaseWg[-2]:
                lsRootFkBaseWing.append("")
                lsFkBaseWing.append("")
                # CREATE AIM CONSTRAINT OBJECTS TO CTR BASE_______________________
                valInfo = mc.getAttr(self.nWorld + '.scale')[0][0]
                nAimHandCtr = gloss.name_format(
                    prefix=prefix_dict['aim'], name=self.name, nFunc='HandCtrNb'+str(index+1), nSide=self.side, incP=incPart)
                aimHandCtr = libRig.createObj(partial(
                    mc.group, **{'n': nAimHandCtr, 'em': True}), match=[current_tpl], father=bufWingBase)
                nUpVHandCtr = gloss.name_format(prefix=gloss.lexicon(
                    'upV'), name=self.name, nFunc='HandCtrNb'+str(index+1), nSide=self.side, incP=incPart)
                upVHandCtr = libRig.createObj(partial(
                    mc.group, **{'n': nUpVHandCtr, 'em': True}), match=[current_tpl], father=bufWingBase)
                if self.side == 'L':
                    mc.move((1 * valInfo), 0, 0, upVHandCtr, ls=True)
                else:
                    mc.move(-(1 * valInfo), 0, 0, upVHandCtr, ls=True)
                aim = (0.0, 1.0, 0.0)
                upV = (0.0, 0.0, 1.0)
                lsAimHandCtr.append(aimHandCtr)
                lsUpVHandCtr.append(upVHandCtr)
            else:
                # NAME_______________________________________________________
                nFkBaseWing = gloss.name_format(prefix=prefix_dict['c'], name=self.name+str(
                    index+1), nFunc='Base', nSide=self.side, incP=incPart)
                fkBaseWing = libRig.createController(name=nFkBaseWing, shape=libRig.Shp(
                    [self.typeShapeFkBaseWing], color=valColorCtr, size=(1, 1, 1)), match=[current_tpl], father=None)
                mc.setAttr(fkBaseWing["c"] + ".segmentScaleCompensate", 0)
                if self.side == 'R':
                    mc.setAttr(fkBaseWing["root"]+'.scaleX', -1)
                lib_shapes.snapShpCv(shpRef=current_tpl,
                                     shpTarget=[fkBaseWing["c"]])
                lsRootFkBaseWing.append(fkBaseWing["root"])
                lsFkBaseWing.append(fkBaseWing["c"])
                # PARENT BUF_______________________________________________________
                mc.parent(fkBaseWing["root"], bufWingBase)

        lsRootFkBackWing = list()
        lsSkBackWingCtrHand = list()
        lsFkBackWing = list()
        # CREATE CTR BACK_____________________________________________________
        for i, current_tpl in enumerate(lsTplIkBackWg):
            # NAME_______________________________________________________
            nFkWing = gloss.name_format(
                prefix=prefix_dict['c'], name=self.name+str(i+1), nFunc='Back', nSide=self.side, incP=incPart)
            fkWing = libRig.createController(name=nFkWing, shape=libRig.Shp(
                [self.selTypeFkWing], color=valColorCtr, size=(0.5, 0.5, 0.5)), match=[current_tpl], father=None)
            mc.setAttr(fkWing["c"] + ".segmentScaleCompensate", 0)
            if self.side == 'R':
                mc.setAttr(fkWing["root"]+'.scaleX', -1)
            lib_shapes.snapShpCv(shpRef=current_tpl, shpTarget=[fkWing["c"]])

            # ADD ATTRIBUTES TO SWITCH____________________________________________
            mc.addAttr(nSwitchsCtrWing, ln="stretchPart%s" %
                       (i), at="double", min=0, max=10, dv=10)
            mc.setAttr(nSwitchsCtrWing + ".stretchPart%s" %
                       (i), e=True, k=True)

            # ADD SWITCH TO FK WING_________________________________________________
            mc.parent(nSwitchsCtrWing, fkWing["c"], s=True, add=True)
            lsFkBackWing.append(fkWing["c"])
            lsRootFkBackWing.append(fkWing["root"])

            # CREATE SK TO LOFT BACK CTR HAND_______________________________________________________
            if current_tpl == lsTplIkBackWg[-1] or current_tpl == lsTplIkBackWg[-3]:
                nSkLoftBackCtrHand = gloss.name_format(
                    prefix=prefix_dict['sk'], name=self.name+'loftBackHand'+str(i+1), nSide=self.side, incP=incPart)
                skLoftBackCtrHand = libRig.createObj(partial(mc.joint, **{'n': nSkLoftBackCtrHand}), match=[fkWing["c"]],
                                                     father=fkWing["c"], attributs={"jointOrientX": 0, "jointOrientY": 0,
                                                                                    "jointOrientZ": 0, "drawStyle": 2})
                lsSkBackWingCtrHand.append(skLoftBackCtrHand)

            if current_tpl != lsTplIkBackWg[-2]:
                mc.parent(fkWing["root"], lsFkBaseWing[i])

        lsLoftBase = []
        lsBfSkbaseWing = []

        for tpl_index, tpl_list in enumerate(all_tpl_dict['ls_lineCtrArmTpl']):
            # CREATE LOC TMP ON ARM_______________________________________________________
            count = 1
            lsLocTmp = []
            for i, current_tpl in enumerate(tpl_list[:int(sbDvArm)+1]):
                # find more efficient way to create locs and constraints
                parentCtrl = tpl_list[:int(sbDvArm)+2][i+1]

                locName = gloss.name_format(prefix='tmp', name=self.name+'Arm%s' % (
                    count), nFunc='Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
                locArmBase = libRig.createObj(
                    partial(mc.spaceLocator, **{'n': locName}), match=[current_tpl], father=None)
                lsLocTmp.append(locArmBase)

                locName = gloss.name_format(prefix='tmp', name=self.name+'Arm%s' % (
                    count+2), nFunc='Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
                locArm = libRig.createObj(
                    partial(mc.spaceLocator, **{'n': locName}), match=[current_tpl], father=None)
                lsLocTmp.append(locArm)

                parentCnsFollow = mc.parentConstraint(locArmBase, locArm, w=1)
                parentCnsFollow = mc.parentConstraint(parentCtrl, locArm, w=1)

                locName = gloss.name_format(prefix='tmp', name=self.name+'Arm%s' % (
                    count+1), nFunc='Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
                locArmAdd = libRig.createObj(
                    partial(mc.spaceLocator, **{'n': locName}), match=[current_tpl], father=None)
                lsLocTmp.append(locArmAdd)

                parentCnsFollow = mc.parentConstraint(
                    locArmBase, locArmAdd, w=1)
                parentCnsFollow = mc.parentConstraint(locArm, locArmAdd, w=1)

                locName = gloss.name_format(prefix='tmp', name=self.name+'Arm%s' % (
                    count+3), nFunc='Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
                locArmAdd2 = libRig.createObj(
                    partial(mc.spaceLocator, **{'n': locName}), match=[current_tpl], father=None)
                lsLocTmp.append(locArmAdd2)

                parentCnsFollow = mc.parentConstraint(locArm, locArmAdd2, w=1)
                parentCnsFollow = mc.parentConstraint(
                    parentCtrl, locArmAdd2, w=1)
                count += 4

            lsLocTmp.sort()

            lsSkBaseWing = []
            lsBufSkBaseWing = []

            # CREATE SK TO LOFT BASE_______________________________________________________
            for i, current_tpl in enumerate(lsLocTmp):
                current_name = '{}AttachLoft{}'.format(self.name, str(i + 1))
                nBufWing = gloss.name_format(prefix=prefix_dict['root'], name=current_name,
                                             nFunc='Layer%s' % (tpl_index + 1), nSide=self.side,
                                             incP=incPart)
                # CREATE_______________________________________________________
                bufWing = libRig.createObj(partial(
                    mc.group, **{'n': nBufWing, 'em': True}), match=[current_tpl], father=None)
                nSkLoftBase = gloss.name_format(prefix=prefix_dict['sk'], name=current_name,
                                                nFunc='Layer%s' % (tpl_index + 1), nSide=self.side,
                                                incP=incPart)
                skLoftBase = libRig.createObj(partial(mc.joint, **{'n': nSkLoftBase}), match=[current_tpl], father=bufWing,
                                              attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})
                lsSkBaseWing.append(skLoftBase)
                lsBufSkBaseWing.append(bufWing)

            lenLocs = len(lsLocTmp)
            # ADD SK TO LOFT BASE_______________________________________________________
            for i, current_tpl in enumerate(tpl_list[int(sbDvArm)+1:]):
                current_name = '{}AttachLoft{}'.format(
                    self.name, (lenLocs+i+1))
                nBufWing = gloss.name_format(prefix=prefix_dict['root'], name=current_name,
                                             nFunc='Layer%s' % (tpl_index + 1), nSide=self.side,
                                             incP=incPart)
                # CREATE_______________________________________________________
                bufWing = libRig.createObj(partial(
                    mc.group, **{'n': nBufWing, 'em': True}), match=[current_tpl], father=None)
                nSkLoftBase = gloss.name_format(prefix=prefix_dict['sk'], name=current_name,
                                                nFunc='Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
                skLoftBase = libRig.createObj(partial(mc.joint, **{'n': nSkLoftBase}), match=[current_tpl], father=bufWing,
                                              attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})
                lsSkBaseWing.append(skLoftBase)
                lsBufSkBaseWing.append(bufWing)

            # CVS WING BASE_______________________________________________________
            getCrvBaseWing = lib_curves.createDoubleCrv(
                objLst=lsSkBaseWing, axis='X', offset=0.2*sclWorld)
            lsCvBase = []
            numbSubDv = 1
            for i, current_crv in enumerate(getCrvBaseWing['crv']):
                createCrv = lib_curves.crvSubdivide(
                    crv=current_crv, subDiv=numbSubDv, subDivKnot=0, degree=3)
                nCv = mc.rename(current_crv, gloss.name_format(prefix=prefix_dict['cv'], name=self.name,
                                                               nFunc='base' +
                                                               str(i + 1) +
                                                               'Layer%s' % (
                                                                   tpl_index + 1),
                                                               nSide=self.side, incP=incPart))
                mc.setAttr(nCv + ".visibility", 0)
                lsCvBase.append(nCv)

            # LOFT____________________________________________
            nLoftBase = gloss.name_format(prefix=prefix_dict['loft'], name=self.name,
                                          nFunc='base' +
                                          'Layer%s' % (tpl_index + 1),
                                          nSide=self.side, incP=incPart)

            loftBase = libRig.createObj(partial(mc.loft, lsCvBase[0], lsCvBase[1:],
                                                **{'n': nLoftBase, 'ch': True,
                                                   'u': True, 'c': 0, 'ar': 1,
                                                   'd': 3, 'ss': 0, 'rn': 0,
                                                   'po': 0, 'rsn': True}),
                                        father=None, refObj=None, incPart=False,
                                        attributs={"visibility": 1})

            # Skin loft
            skinLoftBase = mc.skinCluster(lsSkBaseWing, nLoftBase, tsb=1, bm=1, nw=1, mi=3,
                                          omi=True, dr=4, rui=True)
            # Adjust loft weight
            lib_curves.weightLoft(nLoft=nLoftBase, lsSk=lsSkBaseWing, nbSubDv=numbSubDv,
                                  skinLoft=skinLoftBase)
            mc.delete(lsCvBase)
            mc.delete(lsLocTmp)
            mc.parent(loftBase, loftWing)

            lsBfSkbaseWing.append(lsBufSkBaseWing)
            lsLoftBase.append(loftBase)

        # CREATE BUF SK TO PARENT IN ARM RIG_______________________________________________________
        lsBufSkToArm = []
        for i, each in enumerate(lsBfSkbaseWing[1]):
            # CREATE GRP TO BUF SK BASE_______________________________________________________
            nBufWingSkToArm = gloss.name_format(
                prefix=prefix_dict['root'], name=self.name+'Sk', nFunc='toArm%s' % (i+1), nSide=self.side, incP=incPart)
            # CREATE_______________________________________________________
            bufWingSkToArm = libRig.createObj(partial(
                mc.group, **{'n': nBufWingSkToArm, 'em': True}), match=each, father=rigWing)
            lsBufSkToArm.append(bufWingSkToArm)
            #print 'bufWingSkToArm :', bufWingSkToArm

        for i, lsEach in enumerate(lsBfSkbaseWing):
            for j, each in enumerate(lsEach):
                mc.parent(each, lsBufSkToArm[j])

        # redo all for back lofts
        # CREATE LOFT BACK_______________________________________________________
        # CVS HAND_______________________________________________________
        getCrvBackHand = lib_curves.createDoubleCrv(
            objLst=[lsTplIkBackWg[-3], lsTplIkBackWg[-1]], axis='X', offset=0.2*sclWorld)
        lsCvHand = []
        numbSubDv = 0
        for i, each in enumerate(getCrvBackHand['crv']):
            createCrv = lib_curves.crvSubdivide(
                crv=each, subDiv=numbSubDv, subDivKnot=0, degree=1)
            nCvHand = mc.rename(each, gloss.name_format(prefix=prefix_dict['cv'], name=self.name,
                                                        nFunc='backHand' + str(i + 1), nSide=self.side, incP=incPart))
            mc.setAttr(nCvHand + ".visibility", 0)
            lsCvHand.append(nCvHand)

        # LOFT HAND BACK____________________________________________
        nLoftBackHand = gloss.name_format(
            prefix=prefix_dict['loft'], name=self.name, nFunc='backHand'+'Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
        loftBackHand = libRig.createObj(partial(mc.loft, lsCvHand[0], lsCvHand[1:], **{'n': nLoftBackHand, 'ch': True, 'u': True, 'c': 0, 'ar': 1,
                                                                                       'd': 1, 'ss': 0, 'rn': 0, 'po': 0, 'rsn': True}), father=None, refObj=None, incPart=False, attributs={"visibility": 0})
        # Skin loft
        skinLoftHand = mc.skinCluster(
            lsSkBackWingCtrHand, nLoftBackHand, tsb=1, bm=1, nw=1, mi=3, omi=True, dr=4, rui=True)
        # Adjust loft weight
        #weightCv =lib_curves.weightLoft(nLoft=nLoftBackHand,lsSk=lsSkBackWingCtrHand,nbSubDv=(numbSubDv*2)+1,skinLoft=skinLoftHand)
        mc.delete(lsCvHand)
        # Sa CTR HAND_______________________________________________________
        nLocHand = gloss.name_format(prefix='tmp', name=self.name, nFunc='Hand' +
                                     'Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
        locHand = libRig.createObj(partial(
            mc.spaceLocator, **{'n': nLocHand}), match=[lsRootFkBackWing[-2]], father=None)
        saHand = lib_connectNodes.nurbs_attach(
            lsObj=[nLoftBackHand, locHand], parentInSA=True, delLoc=True)

        # aimConstraint_______________________________________________________
        aimCnsHandCtr = mc.aimConstraint(
            saHand, lsAimHandCtr[0], aim=aim, u=upV, wut='object', wuo=lsUpVHandCtr[0])
        mc.parent(lsRootFkBackWing[-2], lsAimHandCtr[0])

        mc.parent(loftBackHand, loftWing)
        mc.parent(saHand, saWing)
        mc.delete(locHand)
        lsAttrRot = []
        for tpl_index, tpl_list in enumerate(all_tpl_dict['ls_lineCtrBackTpl']):
            # CREATE CTR BACK ADD_______________________________________________________
            lsFkBackAdd = []
            lsRootFkBackAdd = []
            lsBufWing = []
            lsRotWingBase = []
            lsSkBackWing = []
            #lsSkBackWingCtrHand = []
            # CREATE CTR BACK_____________________________________________________
            for i, each in enumerate(tpl_list):
                # NAME_______________________________________________________
                nFkWingBack = gloss.name_format(prefix=prefix_dict['c'], name=self.name+str(
                    i+1), nFunc='Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
                fkWingBack = libRig.createController(name=nFkWingBack, shape=libRig.Shp(
                    [self.selTypeFkWing], color=valColorCtr, size=(1, 1, 1)), match=[each], father=None)
                mc.setAttr(fkWingBack["c"] + ".segmentScaleCompensate", 0)
                shape = mc.listRelatives(fkWingBack["c"], s=True)[0]
                mc.setAttr(shape + ".overrideEnabled", True)
                mc.setAttr(shape + '.overrideRGBColors', 1)
                shapeRef = mc.listRelatives(each, s=True)[0]
                mc.setAttr(shape + '.overrideColorRGB', mc.getAttr(shapeRef + '.overrideColorRGB')[0][0],
                           mc.getAttr(shapeRef + '.overrideColorRGB')[0][1], mc.getAttr(shapeRef + '.overrideColorRGB')[0][2])
                if self.side == 'R':
                    mc.setAttr(fkWingBack["root"]+'.scaleX', -1)
                lib_shapes.snapShpCv(shpRef=each, shpTarget=[fkWingBack["c"]])
                lsFkBackAdd.append(fkWingBack["c"])
                lsRootFkBackAdd.append(fkWingBack["root"])
                mc.parent(fkWingBack["root"], lsFkBackWing[i])

                eachBase = all_tpl_dict['ls_lineCtrArmTpl'][tpl_index][i]
                # NAME_______________________________________________________
                nBufWing = gloss.name_format(prefix=prefix_dict['inf'], name=self.name+str(
                    i+1), nFunc='Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
                nTampWing = gloss.name_format(prefix='tamp', name=self.name+str(
                    i+1), nFunc='Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
                # CREATE_______________________________________________________
                bufWing = libRig.createObj(partial(
                    mc.group, **{'n': nBufWing, 'em': True}), match=[eachBase], father=rigWing)
                tampWing = libRig.createObj(partial(
                    mc.group, **{'n': nTampWing, 'em': True}), match=[eachBase], father=bufWing)
                lsRotWingBase.append(tampWing)
                # CREATE CONSTRAINT WING OR BODY TO FIRST CTR_______________________________________________________
                if i == 0:
                    nCnsWing = gloss.name_format(prefix=prefix_dict['cns'], name=self.name+'Rot'+str(
                        i+1), nFunc='Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
                    nCnsShoulder = gloss.name_format(prefix=prefix_dict['rig'], name=self.name+'Shoulder'+str(
                        i+1), nFunc='Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
                    cnsWing = libRig.createObj(partial(
                        mc.group, **{'n': nCnsWing, 'em': True}), match=[eachBase], father=bufWing)
                    cnsShoulder = libRig.createObj(partial(
                        mc.group, **{'n': nCnsShoulder, 'em': True}), match=[eachBase], father=bufWing)
                    mc.parentConstraint(cnsWing, tampWing)
                    mc.parentConstraint(cnsShoulder, tampWing)
                # CREATE AIM SYSTEM TO CTR_______________________________________________________
                nAimWing = gloss.name_format(prefix=prefix_dict['aim'], name=self.name+str(
                    i+1), nFunc='Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
                aimWing = libRig.createObj(partial(
                    mc.group, **{'n': nAimWing, 'em': True}), match=[eachBase], father=tampWing)
                nUpVWing = gloss.name_format(prefix=gloss.lexicon('upV'), name=self.name+str(
                    i+1), nFunc='Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
                upVWing = libRig.createObj(partial(
                    mc.group, **{'n': nUpVWing, 'em': True}), match=[eachBase], father=tampWing)
                nBufTargetWing = gloss.name_format(prefix=prefix_dict['inf'], name=self.name+'target'+str(
                    i+1), nFunc='Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
                bufTargetWing = libRig.createObj(partial(
                    mc.group, **{'n': nBufTargetWing, 'em': True}), match=[fkWingBack["c"]], father=tampWing)
                nTargetWing = gloss.name_format(prefix='rig', name=self.name+'target'+str(
                    i+1), nFunc='Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
                targetWing = libRig.createObj(partial(
                    mc.group, **{'n': nTargetWing, 'em': True}), match=[fkWingBack["c"]], father=bufTargetWing)

                nBufTargetCnsWing = gloss.name_format(prefix=prefix_dict['inf'], name=self.name+'targetCns'+str(
                    i+1), nFunc='Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
                bufTargetCnsWing = libRig.createObj(partial(
                    mc.group, **{'n': nBufTargetCnsWing, 'em': True}), match=[fkWingBack["c"]], father=fkWingBack["c"])
                nTargetCnsWing = gloss.name_format(prefix=prefix_dict['cns'], name=self.name+'targetCns'+str(
                    i+1), nFunc='Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
                TargetCnsWing = libRig.createObj(partial(
                    mc.group, **{'n': nTargetCnsWing, 'em': True}), match=[bufTargetCnsWing], father=bufTargetCnsWing)
                if self.side == 'L':
                    mc.move(1, 0, 0, upVWing, ls=True)
                    aim = (0.0, 1.0, 0.0)
                    upV = (0.0, 0.0, 1.0)
                else:
                    mc.move(-1, 0, 0, upVWing, ls=True)
                    aim = (0.0, 1.0, 0.0)
                    upV = (0.0, 0.0, -1.0)
                aimCns = mc.aimConstraint(
                    fkWingBack["c"], aimWing, aim=aim, u=upV, wut='object', wuo=upVWing)
                if self.side == 'R':
                    mc.setAttr(aimCns[0]+'.offsetY', 180)
                else:
                    pass
                #mc.parent(lsRootFkBackWing[i],tampWing)
                # CONSTRAINT PARENT SWITCH_______________________________________________________
                nMltDivFollow = gloss.name_format(prefix=gloss.lexicon(
                    'mltDiv'), name=self.name, nFunc='followIkHld'+'Div'+'Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
                nMltDblLinFollow = gloss.name_format(prefix=gloss.lexicon(
                    'mltDblLin'), name=self.name, nFunc='followIkHld'+'Neg'+'Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
                nAddDblLScl = gloss.name_format(prefix=gloss.lexicon(
                    'dblLin'), name=self.name, nFunc='followIkHld'+'Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
                mltDivFollow = mc.createNode("multiplyDivide", n=nMltDivFollow)
                mc.setAttr(mltDivFollow + ".operation", 2)
                mc.setAttr(mltDivFollow + ".input2X", 10)
                mc.connectAttr(nSwitchsCtrWing + ".stretchPart%s" %
                               (i), "%s.input1X" % (mltDivFollow), force=True)
                NodeMltDblLFollow = mc.createNode(
                    "multDoubleLinear", n=nMltDblLinFollow)
                mc.setAttr(NodeMltDblLFollow + ".input2", -1)
                mc.connectAttr(mltDivFollow + '.outputX', "%s.input1" %
                               (NodeMltDblLFollow), force=True)
                nodeAddDLFollow = mc.shadingNode(
                    "addDoubleLinear", n=nAddDblLScl, asUtility=True)
                mc.setAttr("%s.input2" % (nodeAddDLFollow), 1)
                mc.connectAttr(NodeMltDblLFollow + '.output',
                               "%s.input1" % (nodeAddDLFollow), force=True)

                getParentWeight = []
                getScaleWeight = []
                parentCnsFollow = mc.pointConstraint(
                    TargetCnsWing, targetWing, w=0)
                scaleCnsFollow = mc.scaleConstraint(
                    TargetCnsWing, targetWing, w=0)
                firstParentCnsFollow = mc.listConnections(mc.listRelatives(
                    targetWing, type="constraint")[0] + ".target", p=True)[-1]
                firstScaleCnsFollow = mc.listConnections(mc.listRelatives(
                    targetWing, type="constraint")[1] + ".target", p=True)[-1]
                getParentWeight.append(firstParentCnsFollow)
                getScaleWeight.append(firstScaleCnsFollow)
                parentCnsFollow2 = mc.pointConstraint(
                    bufTargetWing, targetWing, w=0)
                scaleCnsFollow2 = mc.scaleConstraint(
                    TargetCnsWing, targetWing, w=0)
                secondParentCnsFollow = mc.listConnections(mc.listRelatives(
                    targetWing, type="constraint")[0] + ".target", p=True)[-1]
                secondScaleCnsFollow = mc.listConnections(mc.listRelatives(
                    targetWing, type="constraint")[1] + ".target", p=True)[-1]
                getParentWeight.append(secondParentCnsFollow)
                getScaleWeight.append(firstScaleCnsFollow)
                #mc.setAttr(parentCnsFollow[0]+ ".interpType", 2)
                mc.connectAttr(nodeAddDLFollow + '.output',
                               getParentWeight[1], force=True)
                mc.connectAttr(mltDivFollow + '.outputX',
                               getParentWeight[0], force=True)
                mc.connectAttr(nodeAddDLFollow + '.output',
                               getScaleWeight[1], force=True)
                mc.connectAttr(mltDivFollow + '.outputX',
                               getScaleWeight[0], force=True)
                orientCnsFollow = mc.orientConstraint(
                    TargetCnsWing, targetWing, w=1)

                # ADJUST PARENT_______________________________________________________
                mc.parent(bufTargetWing, aimWing)
                # CREATE SK TO LOFT BACK_______________________________________________________
                nSkLoftBack = gloss.name_format(prefix=prefix_dict['sk'], name=self.name+'loftBack'+str(
                    i+1), nFunc='Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
                skLoftBack = libRig.createObj(partial(mc.joint, **{'n': nSkLoftBack}), match=[targetWing], father=targetWing,
                                              attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})
                lsSkBackWing.append(skLoftBack)
                mc.parent(bufWing, lsBufWingBase[i])

            # CVS WING BACK_______________________________________________________
            getCrvBackWing = lib_curves.createDoubleCrv(
                objLst=tpl_list, axis='X', offset=0.2*sclWorld)
            lsCvBack = []
            numbSubDv = 0
            for i, each in enumerate(getCrvBackWing['crv']):
                createCrv = lib_curves.crvSubdivide(
                    crv=each, subDiv=numbSubDv, subDivKnot=0, degree=3)
                nCv = mc.rename(each, gloss.name_format(prefix=prefix_dict['cv'], name=self.name,
                                                        nFunc='back' + str(i + 1)+'Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart))
                mc.setAttr(nCv + ".visibility", 0)
                lsCvBack.append(nCv)
            # LOFT____________________________________________
            nLoftBack = gloss.name_format(
                prefix=prefix_dict['loft'], name=self.name, nFunc='back'+'Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
            loftBack = libRig.createObj(partial(mc.loft, lsCvBack[0], lsCvBack[1:], **{'n': nLoftBack, 'ch': True, 'u': True, 'c': 0, 'ar': 1,
                                                                                       'd': 3, 'ss': 0, 'rn': 0, 'po': 0, 'rsn': True}), father=None, refObj=None, incPart=False, attributs={"visibility": 1})
            # Skin loft
            skinLoft = mc.skinCluster(
                lsSkBackWing, nLoftBack, tsb=1, bm=1, nw=1, mi=3, omi=True, dr=4, rui=True)
            # Adjust loft weight
            lib_curves.weightLoft(
                nLoft=nLoftBack, lsSk=lsSkBackWing, nbSubDv=numbSubDv, skinLoft=skinLoft)
            mc.delete(lsCvBack)
            #mc.parent(loftBackHand,loftWing)
            mc.parent(loftBack, loftWing)

            # CREATE SYSTEM ATTRIBUTS TO DRIVE ROTATION FEATHER_______________________________________________________
            nSystemRotElbow = gloss.name_format(
                prefix=prefix_dict['rig'], name=self.name, nFunc='elbow%s' % (tpl_index), nSide=self.side, incP=incPart)
            systemRotElbow = libRig.createObj(partial(
                mc.group, **{'n': nSystemRotElbow, 'em': True}), match=None, father=rigFeatherRot)
            nSystemRotHandle = gloss.name_format(
                prefix=prefix_dict['rig'], name=self.name, nFunc='handle%s' % (tpl_index), nSide=self.side, incP=incPart)
            systemRotHandle = libRig.createObj(partial(
                mc.group, **{'n': nSystemRotHandle, 'em': True}), match=None, father=rigFeatherRot)
            nSystemRotKnot = gloss.name_format(
                prefix=prefix_dict['rig'], name=self.name, nFunc='knot%s' % (tpl_index), nSide=self.side, incP=incPart)
            systemRotKnot = libRig.createObj(partial(
                mc.group, **{'n': nSystemRotKnot, 'em': True}), match=None, father=rigFeatherRot)
            # ADD ATTRIBUTES TO SWITCH____________________________________________
            for each in [nSystemRotElbow, nSystemRotHandle, nSystemRotKnot]:
                mc.addAttr(each, ln="rotFeathers_Option",
                           at="enum", en="_________")
                mc.setAttr(each + ".rotFeathers_Option", e=True, k=True)
                mc.addAttr(each, ln="valRot", at="double", dv=0)
                mc.setAttr(each + ".valRot", e=True, k=True)
                mc.addAttr(each, ln='invertValRot', at="long", dv=1)
                mc.setAttr(each + '.invertValRot', e=True, k=True)
                mc.addAttr(each, ln="fallOff", at="double", dv=0.01)
                mc.setAttr(each + ".fallOff", e=True, k=True)
                mc.addAttr(each, ln="eval_Values", at="enum", en="_________")
                mc.setAttr(each + ".eval_Values", e=True, k=True)

            # CREATE SA BASE WING_______________________________________________________
            lsRotBaseWing = []
            lenToCount = len(all_tpl_dict['ls_featherLinesBaseTpl'][tpl_index])
            for i, each in enumerate(all_tpl_dict['ls_featherLinesBaseTpl'][tpl_index]):
                #print("base tpl", each)
                nTmp = gloss.name_format(prefix='tmp', name=self.name+'Base'+str(i+1),
                                         nFunc='Layer%s' % (tpl_index + 1),
                                         nSide=self.side, incP=incPart)
                tmp = libRig.createObj(partial(mc.spaceLocator, **{'n': nTmp}),
                                       Match=[each], father=None)
                mc.parentConstraint(each, tmp)
                lSaSk = lib_connectNodes.nurbs_attach(lsObj=[lsLoftBase[tpl_index], tmp],
                                                      parentInSA=False, delLoc=True)
                mc.delete(tmp)
                mc.parent(lSaSk[0], saWing)
                lsAllSABaseWingStep.append(lSaSk[0])
                # CREATE GRP ROT_______________________________________________________
                nInfBase = gloss.name_format(prefix=prefix_dict['inf'], name=self.name+'Base'+str(
                    i+1), nFunc='Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
                infBase = libRig.createObj(
                    partial(mc.group, **{'n': nInfBase, 'em': True}), match=[each], father=lSaSk[0])
                nRotBase = gloss.name_format(prefix=prefix_dict['rot'], name=self.name+'Base'+str(
                    i+1), nFunc='Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
                rotBase = libRig.createObj(
                    partial(mc.group, **{'n': nRotBase, 'em': True}), match=[each], father=infBase)

                mc.addAttr(nSystemRotElbow, ln="listValues%s" %
                           (i), at="double", dv=lenToCount-i)
                mc.setAttr(nSystemRotElbow + ".listValues%s" %
                           (i), e=True, k=True)
                mc.addAttr(nSystemRotHandle, ln="listValues%s" %
                           (i), at="double", dv=lenToCount-i)
                mc.setAttr(nSystemRotHandle + ".listValues%s" %
                           (i), e=True, k=True)
                mc.addAttr(nSystemRotKnot, ln="listValues%s" %
                           (i), at="double", dv=i)
                mc.setAttr(nSystemRotKnot + ".listValues%s" %
                           (i), e=True, k=True)

                lsAttrs = []
                for u, eachAttr in enumerate([nSystemRotElbow, nSystemRotHandle, nSystemRotKnot]):
                    nameAttr = 'elbow'
                    nameSyst = nSystemRotElbow
                    if u == 1:
                        nameAttr = 'handle'
                        nameSyst = nSystemRotHandle
                    elif u == 2:
                        nameAttr = 'knot'
                        nameSyst = nSystemRotKnot
                    nMlDv1 = gloss.name_format(prefix=gloss.lexicon('mltDiv'), name=self.name+'1', nFunc='%s%s' % (
                        nameAttr, i)+'Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
                    mlDv1 = mc.createNode("multiplyDivide", n=nMlDv1)
                    mc.setAttr(mlDv1 + ".operation", 1)
                    mc.connectAttr(nameSyst + ".fallOff",
                                   "%s.input1X" % (mlDv1), force=True)
                    mc.connectAttr(nameSyst + ".listValues%s" %
                                   (i), "%s.input2X" % (mlDv1), force=True)
                    nMlDv2 = gloss.name_format(prefix=gloss.lexicon('mltDiv'), name=self.name+'2', nFunc='%s%s' % (
                        nameAttr, i)+'Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
                    mlDv2 = mc.createNode("multiplyDivide", n=nMlDv2)
                    mc.setAttr(mlDv2 + ".operation", 1)
                    nMlDbl2 = gloss.name_format(prefix=gloss.lexicon('mltDblLin'), name=self.name+'2', nFunc='%s%s' % (
                        nameAttr, i)+'Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
                    mlDbl2 = mc.createNode("multDoubleLinear", n=nMlDbl2)
                    mc.connectAttr(nameSyst + ".valRot",
                                   "%s.input1" % (mlDbl2), force=True)
                    mc.connectAttr(nameSyst + ".invertValRot",
                                   "%s.input2" % (mlDbl2), force=True)
                    mc.connectAttr(mlDbl2 + ".output", "%s.input1X" %
                                   (mlDv2), force=True)
                    mc.connectAttr(mlDv1 + '.outputX', "%s.input2X" %
                                   (mlDv2), force=True)
                    lsAttrs.append(mlDv2)

                mc.addAttr(nSystemRotElbow, ln="listValuesOut%s" %
                           (i), at="double", dv=i)
                mc.setAttr(nSystemRotElbow + ".listValuesOut%s" %
                           (i), e=True, k=True)
                mc.addAttr(nSystemRotHandle, ln="listValuesOut%s" %
                           (i), at="double", dv=i)
                mc.setAttr(nSystemRotHandle + ".listValuesOut%s" %
                           (i), e=True, k=True)
                mc.addAttr(nSystemRotKnot, ln="listValuesOut%s" %
                           (i), at="double", dv=i)
                mc.setAttr(nSystemRotKnot + ".listValuesOut%s" %
                           (i), e=True, k=True)

                mc.connectAttr(
                    lsAttrs[0] + '.outputX', nSystemRotElbow + ".listValuesOut%s" % (i), force=True)
                mc.connectAttr(
                    lsAttrs[1] + '.outputX', nSystemRotHandle + ".listValuesOut%s" % (i), force=True)
                mc.connectAttr(
                    lsAttrs[2] + '.outputX', nSystemRotKnot + ".listValuesOut%s" % (i), force=True)

                nAddDblRot = gloss.name_format(prefix=gloss.lexicon(
                    'plMA'), name=self.name+'1', nFunc='handle%s' % (i)+'Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
                addDblRot = mc.createNode("plusMinusAverage", n=nAddDblRot)

                mc.connectAttr(nSystemRotElbow + ".listValuesOut%s" %
                               (i), nAddDblRot + '.input1D[0]', force=True)
                mc.connectAttr(nSystemRotHandle + ".listValuesOut%s" %
                               (i), nAddDblRot + '.input1D[1]', force=True)
                mc.connectAttr(nSystemRotKnot + ".listValuesOut%s" %
                               (i), nAddDblRot + '.input1D[2]', force=True)

                lsAttrRot.append(addDblRot)
                lsRotBaseWing.append(rotBase)
                lsAllInfBaseWingStep.append(infBase)
                lsAllRotBaseWingStep.append(rotBase)
            # CREATE SA BACK WING_______________________________________________________
            lsSABackWing = []
            for i, each in enumerate(all_tpl_dict['ls_featherLinesBackTpl'][tpl_index]):
                nTmp = gloss.name_format(prefix='tmp', name=self.name+'Back'+str(
                    i+1), nFunc='Layer%s' % (tpl_index + 1), nSide=self.side, incP=incPart)
                tmp = libRig.createObj(
                    partial(mc.spaceLocator, **{'n': nTmp}), Match=[each], father=None)
                mc.parentConstraint(each, tmp)
                lSaSk = lib_connectNodes.nurbs_attach(
                    lsObj=[loftBack, tmp], parentInSA=False, delLoc=True)
                mc.delete(tmp)
                mc.parent(lSaSk[0], saWing)
                lsSABackWing.append(lSaSk[0])
                lsAllRotBackWingStep.append(lSaSk[0])

        lsAllAttrRot.append(lsAttrRot)
        lsAllInfBaseWing.append(lsAllInfBaseWingStep)
        lsAllSABaseWing.append(lsAllSABaseWingStep)
        lsAllRotBaseWing.append(lsAllRotBaseWingStep)
        lsAllRotBackWing.append(lsAllRotBackWingStep)

        ######################################################################################
        ######################################################################################
        ######################################################################################
        ############################## STEP FEATHERS PART ####################################
        for k, current_tpl in enumerate(lsInfoFeatherPart):
            lsRotBaseWing = lsAllRotBaseWing[k]
            lsRotBackWing = lsAllRotBackWing[k]
            lsAttrRot = lsAllAttrRot[k]
            lsAttrInf = lsAllInfBaseWing[k]
            lsAttrSaBase = lsAllSABaseWing[k]
            # GET INFO TO CREATE RIG ################################
            incPart = mc.getAttr(current_tpl+'.incInfo')
            side = (mc.attributeQuery(
                "update", node=current_tpl, listEnum=1)[0]).split(":")[1]
            if side == 'empty':
                side = ''
            color = lib_shapes.side_color(side=side)
            valColorCtr = color["colorCtr"]
            valColorCtrIK = color["colorIk"]
            valColorMstCtr = color["colorMaster"]
            # GET MASTER________________________________
            dicTplMstFeather = {}
            if mc.getAttr(current_tpl+'.masterTpl[0]') != "0":
                for i in range(mc.getAttr(current_tpl+'.masterTpl', mi=True, s=True)):
                    mstFeather = mc.getAttr(
                        current_tpl+'.masterTpl[%s]' % i).replace(" ", "")
                    dicTplMstFeather[(
                        i+1)] = [each for each in (mstFeather.split(","))]
            # GET IK________________________________
            dicTplIkFeather = {}
            if mc.getAttr(current_tpl+'.ik[0]') != "0":
                for i in range(mc.getAttr(current_tpl+'.ik', mi=True, s=True)):
                    ikFeather = mc.getAttr(
                        current_tpl+'.ik[%s]' % i).replace(" ", "")
                    dicTplIkFeather[(i+1)] = [each[1:-1]
                                              for each in (ikFeather[1:-1].split(","))]
            # GET CTR________________________________
            dicTplCtrFeather = {}
            if mc.getAttr(current_tpl+'.ctr[0]') != "0":
                for i in range(mc.getAttr(current_tpl+'.ctr', mi=True, s=True)):
                    ctrFeather = mc.getAttr(
                        current_tpl+'.ctr[%s]' % i).replace(" ", "")
                    dicTplCtrFeather[(i+1)] = [each[1:-1]
                                               for each in (ctrFeather[1:-1].split(","))]
            # GET SK________________________________
            dicTplSkFeather = {}
            if mc.getAttr(current_tpl+'.sk[0]') != "0":
                for i in range(mc.getAttr(current_tpl+'.sk', mi=True, s=True)):
                    skFeather = mc.getAttr(
                        current_tpl+'.sk[%s]' % i).replace(" ", "")
                    dicTplSkFeather[(i+1)] = [each[1:-1]
                                              for each in (skFeather[1:-1].split(","))]

            # CREATE RIG FEATHER ################################
            # CREATE GRP RIG FEATHER, SA FEATHER AND WORLDCENTER FEATHER___________
            nRigFeather = gloss.name_format(
                prefix=prefix_dict['rig'], name=self.nameFeatherPart, nSide=side, incP=incPart)
            nHookGrpFeather = gloss.name_format(prefix='hooks',
                                                name=self.nameFeatherPart, nSide=side,
                                                incP=incPart)

            rigFeather = libRig.createObj(partial(
                mc.group, **{'n': nRigFeather, 'em': True}), Match=None, father=lsRIGWing[k])
            hookGrpFeather = libRig.createObj(partial(mc.group, **{'n': nHookGrpFeather, 'em': True}),
                                              Match=None, father=rigFeather)

            # CREATE FEATHERS_____________________________________________________
            for key, tplMst in sorted(dicTplMstFeather.items()):
                # create master __________
                master = tplMst[0]
                lsTplIk = dicTplIkFeather.get(key)
                lsCtrFk = dicTplCtrFeather.get(key)
                lsTplSk = dicTplSkFeather.get(key)

                # NAME________________________________________________________________
                nNoTouch = gloss.name_format(prefix=gloss.lexicon(
                    'NoTouch'), name=self.nameFeatherPart+'Nb'+str(key), nSide=side, incP=incPart)
                nHook = gloss.name_format(prefix=prefix_dict['rig'],
                                          name=self.nameFeatherPart+'Nb'+str(key), nSide=side,
                                          incP=incPart)

                # FUSION TPL IK and CTR_______________________________________________
                concatIkFk = lsCtrFk
                concatIkFk.insert(0, lsTplIk[0])
                concatIkFk.insert(len(lsCtrFk) + 1, lsTplIk[-1])

                # # ADJUST DEGRE WITH SUBDIVISE_________________________________________
                # if len(concatIkFk) <= 2:
                #     degres = 1
                #     numbJtLen = len(concatIkFk) + 1
                # elif len(concatIkFk) == 3:
                #     degres = 2
                #     numbJtLen = len(concatIkFk)
                # else:
                #     degres = 3
                #     numbJtLen = len(concatIkFk) - 1

                # CREATE RIG CURVE____________________________________________________
                pos = [mc.xform(each2, q=True, ws=True, t=True)
                       for each2 in concatIkFk]

                # HOOK________________________________________________________________
                hookTail = libRig.createObj(partial(
                    mc.group, **{'n': nHook, 'em': True}), Match=self.nFly, father=rigFeather)

                # CREATE GRP NO TOUCH________________________________________________
                GrpNoTouch = libRig.createObj(partial(
                    mc.group, **{'n': nNoTouch, 'em': True}), typeFunction={"group": {"visibility": 0}})
                # parentage group NoTouch avec HookSpine

                mc.parent(GrpNoTouch, hookTail)

                # CREATE FK__________________________________________________________
                lsFkControl = []
                lsFkRoot = []
                lsFkControlAll = []

                if len(concatIkFk) < 2:
                    pass

                for i, elemFK in enumerate(concatIkFk[:-1]):
                    # NAME_______________________________________________________
                    nFk = gloss.name_format(prefix=prefix_dict['c'],
                                            name=self.nameFeatherPart +
                                            str(i+1)+'Nb'+str(key),
                                            nSide=side, incP=incPart)
                    # CREATE_____________________________________________________
                    createFk = libRig.createController(name=nFk, shape=libRig.Shp([self.typeCircle], color=valColorCtr,
                                                                                  size=(0.4 * worldScl, 0.4 * worldScl, 0.4 * worldScl)),
                                                       match=[elemFK])

                    mc.setAttr(createFk["c"] + ".segmentScaleCompensate", 0)
                    mc.setAttr(createFk["root"] + ".rotateOrder", libRgPreset.configAxis(
                        mb="rOrdSpine", side=side)["rOrdFk"], l=False, k=True)
                    mc.setAttr(createFk["c"] + ".rotateOrder", libRgPreset.configAxis(
                        mb="rOrdSpine", side=side)["rOrdFk"], l=False, k=True)

                    # skCtr = gloss.renameSplit(selObj=createFk["sk"], namePart=['sk'], newNamePart=['jnt'], reNme=True)

                    if side == 'R':
                        mc.setAttr(createFk["root"]+'.scaleX', -1)

                    shapeFk = mc.listRelatives(createFk["c"], s=True)[0]
                    mc.setAttr(shapeFk + ".overrideEnabled", True)
                    mc.setAttr(shapeFk + '.overrideRGBColors', 1)

                    shapeRefFk = mc.listRelatives(elemFK, s=True)[0]
                    mc.setAttr(shapeFk + '.overrideColorRGB', mc.getAttr(shapeRefFk + '.overrideColorRGB')[0][0],
                               mc.getAttr(shapeRefFk + '.overrideColorRGB')[0][1], mc.getAttr(shapeRefFk + '.overrideColorRGB')[0][2])

                    # parent to prev ctrl
                    current_parent = lsRotBaseWing[key - 1] if not lsFkControl else lsFkControl[-1]
                    mc.parent(createFk["root"], current_parent)
                    if mc.attributeQuery('segmentScaleCompensate', node=current_parent, ex=True):
                        mc.setAttr(current_parent +
                                   ".segmentScaleCompensate", 0)

                    lCtrl.append(createFk)
                    lsFkControl.append(createFk["c"])
                    lsFkRoot.append(createFk["root"])
                    lsFkControlAll.append(createFk["c"])

                # Connect Rot Root to attributes ____________________________________
                mc.connectAttr(
                    lsAttrRot[key-1] + ".output1D", lsFkRoot[0] + ".rotateX", force=True)

                valInfo = mc.getAttr(self.nWorld + '.scale')[0][0]
                # CREATE AIM CONSTRAINT BASE_______________________
                nAimFeatherBase = gloss.name_format(
                    prefix=prefix_dict['aim'], name=self.name, nFunc='BaseNb'+str(key), nSide=side, incP=incPart)
                aimFeatherBase = libRig.createObj(partial(
                    mc.group, **{'n': nAimFeatherBase, 'em': True}), match=[lsAttrInf[key-1]], father=lsAttrSaBase[key-1])
                nUpVFeatherBase = gloss.name_format(prefix=gloss.lexicon(
                    'upV'), name=self.name, nFunc='BaseNb'+str(key), nSide=side, incP=incPart)
                upVFeatherBase = libRig.createObj(partial(
                    mc.group, **{'n': nUpVFeatherBase, 'em': True}), match=[lsAttrSaBase[key-1]], father=lsAttrSaBase[key-1])

                if side == 'L':
                    mc.move((5*valInfo), 0, 0, upVFeatherBase, ls=True)
                else:
                    mc.move((5*valInfo), 0, 0,  upVFeatherBase, ls=True)
                aim = (0.0, 1.0, 0.0)

                upV = (1.0, 0.0, 0.0)
                ##########################################################
                getPOSI = mc.ls(mc.listHistory(lsRotBackWing[key-1]), type='pointOnSurfaceInfo')[0]
                getNbs = mc.listConnections(getPOSI+'.inputSurface')[0]
                self.aimOnNbs(aimFeatherBase, getNbs, getPOSI, 'Y')
                mc.delete(mc.parentConstraint(aimFeatherBase, upVFeatherBase, mo=False))
                mc.setAttr(upVFeatherBase+'.translateX', 5*valInfo+mc.getAttr(upVFeatherBase+'.translateX'))
                ##########################################################
                aimCnsBase = mc.aimConstraint(lsRotBackWing[key-1], aimFeatherBase, aim=aim, u=upV, wut='object', wuo=upVFeatherBase)

                mc.parent(lsAttrInf[key-1], aimFeatherBase)

                # PARENT HOOK WITH RIG MEMBER________________________________________________
                mc.parent(hookTail, self.hook)

        ######################################################################################
        ######################################################################################
        ######################################################################################
        # # hook feather surface to arm
        parent_module = mc.listConnections('{}.parent'.format(self.info))

        # parent new group under 'RIG' group
        all_parents = get_all_parents(self.hook)
        rig_grp = str()
        for parent in all_parents:
            if re.search('RIG', parent):
                rig_grp = parent
                break

        if rig_grp:
            mc.parent(rigWing, rig_grp)

        if not parent_module:
            return dicSk, lCtrl

        parent_module_anchors = [mc.getAttr('{}.listHooks[{}]'.format(parent_module[0],
                                                                      i)) for i in range(mc.getAttr('{}.listHooks'.format(parent_module[0]),
                                                                                                    mi=True, s=True))]
        parent_module_anchor_positions = [mc.xform(current_obj, q=True,
                                                   rp=True, ws=True) for current_obj in parent_module_anchors]
        arm_attach_hooks = dict()
        for root_obj in lsBufSkToArm:
            # find closest hook in parent, create hook if it doesn't exist, parent element underneath
            closest_anchor = getNearestTrans(root_obj, parent_module_anchors)
            if closest_anchor not in arm_attach_hooks.keys():
                hook_name = re.sub(r'[a-z]+_([a-zA-Z]+\d+)',
                                   r'\1SurfSk', closest_anchor)
                new_hook = crtHook([closest_anchor], [hook_name])
                arm_attach_hooks[closest_anchor] = new_hook
                mc.parent(new_hook, hookGrpFeather)
            mc.parent(root_obj, arm_attach_hooks[closest_anchor])

        # hook wing controls to arm
        ctrl_attach_hooks = dict()
        for ctrl_root in lsBufWingBase:
            closest_anchor = getNearestTrans(ctrl_root, parent_module_anchors)
            if closest_anchor not in ctrl_attach_hooks.keys():
                hook_name = re.sub(r'[a-z]+_([a-zA-Z]+\d+)',
                                   r'\1WingCtrl', closest_anchor)
                new_hook = crtHook([closest_anchor], [hook_name])
                ctrl_attach_hooks[closest_anchor] = new_hook
                mc.parent(new_hook, hooksWing)
            mc.parent(ctrl_root, ctrl_attach_hooks[closest_anchor])

        # addcg datas _____________________________________________
        cgWingAttr = gloss.name_format(prefix=gloss.lexiconAttr('cg'),name=self.name,nSide=side,incP=incPart)
        cgFeatherAttr = gloss.name_format(prefix=gloss.lexiconAttr('childCg'),name='feathers',nSide=side,incP=incPart)
        dicCgCtrl = {}
        lWingCtrl = lsFkBaseWing
        lWingCtrl.extend(lsFkBackWing)
        lWingCtrl.extend(lsFkBackAdd)
        dicCgCtrl[cgWingAttr] = lWingCtrl

        lFeathersCtrl = []
        for dic in lCtrl:
            lFeathersCtrl.append(dic['c'])
        dicCgCtrl[cgFeatherAttr] = lFeathersCtrl
        for cgAttr in [cgWingAttr, cgFeatherAttr]:
            if not mc.attributeQuery(cgAttr, n=self.info, ex=True):
                mc.addAttr(self.info, ln=cgAttr, dt='string', multi=True)
            [mc.setAttr(self.info+'.%s['%(cgAttr) +str(i)+']', attrVal, type='string') for i, attrVal in enumerate(dicCgCtrl[cgAttr])]



        return dicSk, lCtrl
