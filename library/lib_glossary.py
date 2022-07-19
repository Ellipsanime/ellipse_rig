# coding: utf-8

import maya.cmds as mc
import re
from functools import partial
from itertools import takewhile
from ellipse_rig.library import lib_namespace
reload(lib_namespace)

class nomenclature():

    orderFormat = (0, 1, 2, 3, 4, 5)

    @classmethod
    def changeOrderFormat(cls, newOrder):
        nomenclature.orderFormat = newOrder


def lexicon(key):
    ############################## TYPE ######################################
    nTypes ={}
    try:
        #TEMPLATE_________________________________________________________________
        nTypes['tpl'] = 'tpl' # template
        nTypes['tplCtr'] = 'tplCtr' # template control
        nTypes['tplHook'] = 'tplHook' # template hook
        nTypes['tplRig'] = 'tplRIG' # template rig
        nTypes['tplSurfAttach'] = 'tplSrfAttach' # template
        nTypes['tplMtr'] = 'tplMtr' # template
        nTypes['tplSA'] = 'tplSA' # template
        nTypes['tplCv'] = 'tplCv' # template
        nTypes['tplUpV'] = 'tplUpV' # template
        nTypes['tplPlV'] = 'tplPlV' # template
        nTypes['tplLookAt'] = 'tplLookAt' # template
        nTypes['tplRoot'] = 'tplRoot' # template
        nTypes['tplSk'] = 'tplSk' # template
        nTypes['tplLoft'] = 'tplLoft' # template
        nTypes['tplIk'] = 'tplIk' # template
        nTypes['tplInfo'] = 'tplInfo' # template
        nTypes['tplSa'] = 'tplSa' # template
        nTypes['tplUv'] = 'tplUv' # template
        nTypes['tplInf'] = 'tplInf' # template
        nTypes['tplBuf'] = 'tplBuf' # template
        nTypes['tplMtxMlt'] = 'tplMtxMlt' # template
        nTypes['tplMtxDcp'] = 'tplMtxDcp' # template
        nTypes['tplMtxFour'] = 'tplMtxFour' # template
        nTypes['tplPtOnSurfI'] = 'tplPtOnSurfI' # template
        nTypes['tplClsSurf'] = 'tplClsSurf' # template
        nTypes['tplBank'] = 'tplBank' # template
        nTypes['tplCnsPt'] = 'tplCnsPt' # template
        nTypes['tplRig'] = 'tplRig' # template

        #RIGGING_BASE_____________________________________________________________
        nTypes['all'] = 'ALL' # top Node
        nTypes['world'] = 'WORLD' # world
        nTypes['walk'] = 'WALK' # walk
        nTypes['fly'] = 'FLY' # fly
        nTypes['RIG'] = 'RIG' # rig
        nTypes['geo'] = 'GEO' # geo
        nTypes['switch'] = 'switch' # switch
        nTypes['all_switch'] = 'ALL_SWITCH' # all switch
        nTypes['switchs'] = 'SWITCHS' # all switch
        nTypes['rig'] = 'rig' # rig
        #RIGGING__________________________________________________________________
        nTypes['hook'] = 'hook' # hook
        nTypes['inf'] = 'inf' # info
        nTypes['offSet'] = 'offSet' # offSet
        nTypes['root'] = 'root' # root
        nTypes['c'] = 'c' # controller
        nTypes['sk'] = 'sk' # skin joint
        nTypes['jt'] = 'jt' # joint
        nTypes['upV'] = 'upV' # up vector
        nTypes['plV'] = 'plV' # pole vector
        nTypes['eff'] = 'eff' # effector
        nTypes['aim'] = 'aim' # aim
        nTypes['lookAt'] = 'lookAt' # lookAt
        nTypes['o'] = 'o' # o
        nTypes['ao'] = 'ao' # ao
        nTypes['ik'] = 'ik' # ik
        nTypes['fk'] = 'fk' # ik
        nTypes['info'] = 'info' # info
        nTypes['trf'] = 'trf' # transform
        nTypes['trans'] = 'trans' # translate
        nTypes['rot'] = 'rot' # rotate
        nTypes['scl'] = 'scl' # scale
        nTypes['s'] = 's' # scale variante
        nTypes['scale'] = 'scale' # scale variante
        nTypes['check'] = 'check' # checker
        nTypes['chain'] = 'chain' # chain
        nTypes['roll'] = 'roll' # roll
        nTypes['end'] = 'end' # end
        nTypes['target'] = 'target' # target
        nTypes['mtr'] = 'mtr' # master
        nTypes['hdl'] = 'hdl' # Handle
        nTypes['ikHdl'] = 'ikHdl' # IK Handle
        nTypes['add'] = 'add' # Add
        nTypes['world'] = 'WORLD' # world
        nTypes['walk'] = 'WALK' # walk
        nTypes['fly'] = 'FLY' # fly
        nTypes['buf'] = 'buf' # buf
        nTypes['front'] = 'front' # front
        nTypes['back'] = 'back' # back
        nTypes['left'] = 'left' # left
        nTypes['right'] = 'right' # right
        nTypes['ikHandle'] = 'ikHandle' # ikHandle
        nTypes['rootIkHandle'] = 'rootIkHandle' # RootIkHandleRoot
        nTypes['rootJt'] = 'rootJt' # rootJoint
        nTypes['start'] = 'start' # start
        nTypes['end'] = 'end' # end
        nTypes['bpm'] = 'bpm' # bpm
        nTypes['twist'] = 'twist' # twist
        nTypes['wrist'] = 'wrist' # wrist
        nTypes['dn'] = 'dn' # down
        nTypes['rev'] = 'rev' # reverse
        nTypes['loc'] = 'loc' # locator
        nTypes['jnt'] = 'jnt' # joint
        nTypes['ikBlend'] = 'ikBlend' # ikBlend
        nTypes['orient'] = 'orient' # orient
        nTypes['add'] = 'add' # add
        nTypes['arc'] = 'arc' # arc
        nTypes['bindP'] = 'bindP' # bind pre matrix
        nTypes['mid'] = 'mid' # middle
        nTypes['GRP'] = 'GRP' # GRP
        nTypes['anchor'] = 'anchor' # anchor
        nTypes['cg'] = 'cg' # cg
        nTypes['off'] = 'off' # off
        # CONSTRAINT________________________________________________________________
        nTypes['cns'] = 'cns' # constraint
        nTypes['lnk'] = 'lnk' # link
        nTypes['cnsO'] = 'cnsO' # constraintO
        nTypes['inst'] = 'inst' # instance

        # NODE______________________________________________________________________
        nTypes['mtxDcp'] = 'dM' # matrixDecomposition
        nTypes['mtxMlt'] = 'mltM' # matrixMultiply
        nTypes['mtxFour'] = 'mtxFour' # matrixFourByFour
        nTypes['mtxInv'] = 'mtxInv' # matrixInverse
        nTypes['mltDiv'] = 'mltDiv' # multiplyDivide
        nTypes['dblLin'] = 'dblLin' # doubleLinear
        nTypes['mltDblLin'] = 'mlt' # mltDoubleLinear
        nTypes['addDblLin'] = 'addDblLin' # addDoubleLinear
        nTypes['distDim'] = 'distDim' # distanceDimension
        nTypes['pBlend'] = 'pBl' # pair blend
        nTypes['blendCol'] = 'bldCol' # blendColor
        nTypes['ptOnSurf'] = 'pOSf' # pointOnSurface
        nTypes['ptOnSurfI'] = 'pOSfI' # pointOnSurfaceInfo
        nTypes['clsSurf'] = 'clsSurf' # closeSurface
        nTypes['trfNod'] = 'trfNod' # transformNode
        nTypes['mPath'] = 'mPath' # motionPath
        nTypes['cnd'] = 'cnd'  # conditionNode
        nTypes['mD'] = 'mD'  # multiplyDivide
        nTypes['dM'] = 'dM'  # decomposeMatrix
        nTypes['mltM'] = 'mltM'  # multiMatrix
        nTypes['sa'] = 'sa'  # surfAttach
        nTypes['SA'] = 'SA'  # surfAttach
        nTypes['ca'] = 'ca'  # curveAttach
        nTypes['UV'] = 'UV'  # UV nurbs
        nTypes['dstD'] = 'dstD'  # Distance dimension
        nTypes['clmp'] = 'clmp'  # Clamp
        nTypes['plMA'] = 'plMA'  # plusMinusAverage
        nTypes['quatToEuler'] = 'qTE'  # quatToEuler
        nTypes['blendColors'] = 'bld'  # blendColors

        # DEFORMS____________________________________________________________________
        nTypes['DEFORMER'] = 'DEFORMER' # template
        nTypes['bend'] = 'bend' # bend
        nTypes['squash'] = 'squash' # bend
        nTypes['ltc'] = 'ltc' # lattice
        nTypes['hdl'] = 'hdl' # handle
        nTypes['skin'] = 'skin' # skin
        nTypes['cls'] = 'cls' # cluster
        # SHAPE______________________________________________________________________
        nTypes['geo'] = 'geo' # geometry
        nTypes['cv'] = 'crv' # curve
        nTypes['arcLen'] = 'arcLen' # curve
        nTypes['loft'] = 'loft' # loft
        nTypes['surf'] = 'surf' # surface
        nTypes['shp'] = 'shp' # shape

        # EXPRESSION CONNECTION_______________________________________________________
        nTypes['exp'] = 'exp' # expression
        nTypes['attr'] ='attr' # attributes

        # SET_________________________________________________________________________
        nTypes['set'] = 'set' # set

        # RIGGING CHARACTER___________________________________________________________
        nTypes['NoTouch'] = 'NoTouch' # place on World
        nTypes['cog'] = 'cog' # cog
        nTypes['clav'] = 'clav' # clavicule
        nTypes['eyeTarget'] = 'eyeTarget' # eyeTarget
        nTypes['footRoll'] = 'footRoll' # footRoll
        nTypes['ballRoll'] = 'ballRoll' # ballRoll
        nTypes['pelvis'] = 'pelvis' # ballRoll
        nTypes['spine'] = 'spine' # ballRoll
        nTypes['leg'] = 'leg' # ballRoll
        nTypes['bank'] = 'bank' # bank
        nTypes['rootBank'] = 'rootBank' # bank
        nTypes['sclBank'] = 'sclBank' # bank
        nTypes['ballRoll'] = 'ballRoll' # bank
        nTypes['ballPiv'] = 'ballPiv' # bank
        nTypes['chain'] = 'chain' # chain
        nTypes['stomp'] = 'stomp' # stomp
        nTypes['roll'] = 'roll' # roll
        nTypes['piv'] = 'piv' # piv
        nTypes['heel'] = 'heel' # heel
        nTypes['roll'] = 'roll' # roll
        nTypes['part'] = 'part' # part
        nTypes['base'] = 'base' # roll
        nTypes['shoulder'] = 'shoulder' # roll
        nTypes['hip'] = 'hip' # hip
        nTypes['ankle'] = 'ankle'
        nTypes['skull'] = 'skull' # skull
        nTypes['metacarpe'] = 'metacarpe' # metacarpe
        nTypes['metatarse'] = 'metatarse' # metatarse
        nTypes['stretch'] = 'stretch' # stretch
        nTypes['pinch'] = 'pinch' # pinch
        nTypes['min'] = 'min' # min
        nTypes['max'] = 'max' # max

        return nTypes[key]
    except:
        mc.warning( "{} n'existe pas !!!!".format(key))
# lexicon('set')



def lexiconAttr(key):
    ############################## TYPE ######################################
    nTypes ={}
    try:
        # ATTRIBUTS NAME___________________________________________________________
        nTypes['attrChild'] = 'children' # attributs child
        nTypes['attrParent'] = 'parent' # attributs parent
        nTypes['moduleDataTpl'] = 'moduleDataTpl' # module Data Tpl
        nTypes['moduleType'] = 'moduleType' # module Type
        nTypes['moduleMirror'] = 'moduleMirror' # module Mirror
        nTypes['listHooks'] = 'listHooks' # list Hooks
        nTypes['masterTpl'] = 'masterTpl' # master Tpl
        nTypes['rigAddTpl'] = 'rigAddTpl' # rigAdd Tpl

        nTypes['cgAll'] = 'all' # cg all
        nTypes['cgMaster'] = 'master' # cg master
        nTypes['cgSwitch'] = 'switch' # cg switch
        nTypes['cgIk'] = 'ik' # cg ik
        nTypes['fkRig'] = 'fk' # cg fk
        nTypes['cgClav'] = 'fkClav' # cg fk Clav
        nTypes['cgFkMb'] = 'fkMb' # cg fk Member
        nTypes['cgFkMidMb'] = 'fkMidMb' # cg fk Middle Member
        nTypes['cgFkArc'] = 'fkArc' # cg fk Arc
        nTypes['cgFkShp'] = 'fkShp' # cg Shp


        nTypes['cg'] = 'cg' # CG
        nTypes['buildCg'] = 'buildCg' # is CG build ?
        nTypes['childCg'] = 'childCg' # childCg
        nTypes['parentCg'] = 'parentCg' # parentCg
        nTypes['builtCg'] = 'controlGroupBuilt'
        nTypes['matchIKFK'] = 'matchIKFK'


        nTypes['metacarpAim'] = 'metacarpAim'
        nTypes['metacarpTwist'] = 'metacarpTwist'


        return nTypes[key]
    except:
        mc.warning("{} n'existe pas !!!!".format(key))




def name_format(prefix=None,name=None,nFunc=None,inc=None,incP='1',nSide=None,order=nomenclature.orderFormat,incInfo=None, **kwargs):
    '''
    concatenate and define order to create name
    upper first character to flag func
    :return: name_format
    '''

    if nFunc != None:
        nFunc = nFunc[0].upper()+ nFunc[1:]
    else:
        pass
    order = list(order)
    nameFormat = ('{%s}{%s}{%s}{%s}{%s}{%s}' % (order[0], order[1], order[2], order[3], order[4], order[5])).format(
        ("" + prefix) if prefix else "",
        ("_" + name) if name else "", ("" + nFunc) if nFunc else "", ("" + inc) if inc else "",
        ("_" + incP) if incP else "", ("_" + nSide) if nSide else "")
    if incInfo != None:
        nameFormat= inspect_inc(selObj=nameFormat, slideSplit=2)
    return nameFormat
#name_format(prefix='tpl',name='toto',nFunc=None,inc='1',incP='1',nSide='L',order=[0,1,2,3,4,5])


def Inspect_tplInfo(lFilter=None,*args):
    # inspecter la scene
    Obj = mc.ls(tr=True)
    # filter by namePart
    lsTplInfo = []
    for i, eachE in enumerate(Obj):
        if set(re.findall('|'.join(lFilter), eachE)) == set(lFilter):
            lsTplInfo.append(eachE)
    return lsTplInfo
#test=Inspect_tplInfo(lFilter=['tplInfo','spine'])


def inspect_inc(selObj=None, slideSplit=None):

    while True:
        getNamespace = lib_namespace.lsAllNspace(toExclude = ['UI', 'shared'])
        objExist = selObj
        for eachNamespace in getNamespace:
            if mc.objExists(eachNamespace+':'+selObj) is True:
                objExist = eachNamespace+':'+ selObj

        if mc.objExists(objExist) is True :
            splitObj = selObj.split("_")
            namePart = [n.strip("0123456789") for n in splitObj]
            numb = re.findall('\d+', splitObj[slideSplit])[0]
            count = int(numb) + 1
            splitObj[slideSplit] = namePart[slideSplit]+str(count)
            selObj = "_".join(splitObj)
        else:
            break
    '''
    while True:
        if mc.objExists(selObj) is True or mc.objExists('ROOT:'+ selObj) is True:
            print selObj
            splitObj = selObj.split("_")
            namePart = [n.strip("0123456789") for n in splitObj]
            numb = re.findall('\d+', splitObj[slideSplit])[0]
            count = int(numb) + 1
            splitObj[slideSplit] = namePart[slideSplit]+str(count)
            selObj = "_".join(splitObj)
        else:
            break
    '''
    return selObj
#inspect_inc(selObj="root_ballTpl1_1_R", slideSplit=2)


def get_inc(selObj=None, slideSplit=None):

    splitObj = selObj.split("_")
    namePart = [n.strip("0123456789") for n in splitObj]
    numb = re.findall('\d+', splitObj[slideSplit])[0]
    count = numb
    return count
#get_inc(selObj="tpl_spine0_10", slideSplit=2)


def renameSplit(selObj=None, namePart=None, newNamePart=None, reNme=False):
    '''
    Split selObj by part and get incrementation of this part
    :return: incrementation
    '''
    namePart = [n.strip("0123456789") for n in namePart]
    if selObj == []:
        print 'ls empty'
    else:
        oldSelObj = selObj
        for j, eachNamePart in enumerate(namePart):
            splitObj = selObj.split("_")
            selObj = selObj.replace(namePart[j], newNamePart[j])
        if reNme != False:
            mc.rename(oldSelObj, selObj)
        return selObj
#renameSplit(selObj=mc.ls(sl=True)[0], namePart=['tpl', 'ropeTpl1'], newNamePart=['cv', 'ropeTpl45'], reNme=False)



def inspectIncObj(selObj=None, slideSplit=None):
    '''
    Split selObj by part and get incrementation of this part
    :return: incrementation
    '''
    splitObj = selObj.split("_")
    try:
        numb = re.findall('\d+', splitObj[slideSplit])[0]
    except:
        numb = "empty"
    return numb


def getMaxIncObj(name=None, side='', slideSplit=None,inc=None, *args):
    '''
    Get maxi incrementation of object in scene with a similar name
    :return: maxi incrementation
    '''
    # inspecter la scene
    Obj = mc.ls(tr=True)
    getE = []
    for i, eachE in enumerate(Obj):
        les_mots = name
        if set(re.findall('|'.join(les_mots), eachE)) == set(les_mots):
            getE.append(str(eachE))
    getLstNumb = []
    if getE == []:
        print "no object name match in viewport"
    else:
        for each in getE:
            getNumb = inspectIncObj(each, slideSplit)
            if getNumb is "empty":
                getLstNumb.append(1)
            else:
                getLstNumb.append(int(getNumb)+ 1)
    maxVal = max(getLstNumb)
    return maxVal
# getMaxIncObj("Sphere", "", sliddeSplit=1)