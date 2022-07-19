# coding: utf-8

import maya.cmds as mc
import re
from functools import partial
from itertools import takewhile

def type_color(key):
    nTypesColor = {}

    nTypesColor['red'] = 'red'
    nTypesColor['green'] = 'green'
    nTypesColor['yellow'] = 'yellow'
    return nTypesColor[key]


def type_name(key):
    ############################## TYPE ######################################
    nTypes = {}
    #TEMPLATE_________________________________________________________________
    nTypes['tpl'] = 'tpl' # template
    nTypes['tplRig'] = 'tplRIG' # template
    nTypes['tplSurfAttach'] = 'tplSurfAttach' # template
    nTypes['mtrTpl'] = 'mtrTpl' # template
    #RIGGING_BASE_____________________________________________________________
    nTypes['all'] = 'ALL' # top Node
    nTypes['world'] = 'WORLD' # world
    nTypes['walk'] = 'WALK' # world
    nTypes['fly'] = 'FLY' # fly
    nTypes['rig'] = 'RIG' # rig
    nTypes['geo'] = 'GEO' # geo
    nTypes['switch'] = 'SWITCH' # switch
    nTypes['all_switch'] = 'ALL_SWITCH' # all switch

    #RIGGING__________________________________________________________________
    nTypes['hook'] = 'hook' # hook
    nTypes['inf'] = 'inf' # info
    nTypes['offSet'] = 'offSet' # offSet
    nTypes['root'] = 'root' # root
    nTypes['c'] = 'c' # controller
    nTypes['sk'] = 'sk' # skin joint
    nTypes['jt'] = 'jt' # joint
    nTypes['upV'] = 'upV' # up vector
    nTypes['eff'] = 'eff' # effector
    nTypes['aim'] = 'aim' # aim
    nTypes['lookAt'] = 'lookAt' # lookAt
    nTypes['o'] = 'o' # o
    nTypes['ao'] = 'ao' # ao
    nTypes['ik'] = 'ik' # ik
    nTypes['trf'] = 'trf' # transform
    nTypes['trans'] = 'trans' # translate
    nTypes['rot'] = 'rot' # rotate
    nTypes['scl'] = 'scl' # scale
    nTypes['check'] = 'check' # checker
    nTypes['chain'] = 'chain' # chain
    nTypes['roll'] = 'roll' # roll
    nTypes['end'] = 'end' # end
    nTypes['target'] = 'target' # target
    nTypes['mtr'] = 'mtr' # master
    nTypes['hdl'] = 'hdl' # Handle
    nTypes['add'] = 'add' # Add


    nTypes['world'] = 'WORLD' # world
    nTypes['walk'] = 'WALK' # walk
    nTypes['fly'] = 'FLY' # fly

    # CONSTRAINT________________________________________________________________
    nTypes['cns'] = 'cns' # constraint
    nTypes['lnk'] = 'lnk' # link
    nTypes['cnsO'] = 'cnsO' # constraintO
    nTypes['inst'] = 'inst' # instance

    # NODE______________________________________________________________________
    nTypes['mtxDcp'] = 'mtxDcp' # matrixDecomposition
    nTypes['mtxMlt'] = 'mtxMlt' # matrixMultiply
    nTypes['mtxFour'] = 'mtxFour' # matrixFourByFour
    nTypes['mtxInv'] = 'mtxInv' # matrixInverse
    nTypes['mltDiv'] = 'mltDiv' # multiplyDivide
    nTypes['mltDblLin'] = 'mltDblLin' # mltDoubleLinear
    nTypes['addDblLin'] = 'addDblLin' # addDoubleLinear
    nTypes['distDim'] = 'distDim' # distanceDimension
    nTypes['ptOnSurf'] = 'pOSf' # pointOnSurface
    nTypes['ptOnSurfI'] = 'pOSfI' # pointOnSurfaceInfo
    nTypes['clsSurf'] = 'clsSurf' # closeSurface
    nTypes['trfNod'] = 'trfNod' # transformNode

    nTypes['cnd'] = 'cnd'  # conditionNode
    nTypes['mD'] = 'mD'  # multiplyDivide
    nTypes['dM'] = 'dM'  # decomposeMatrix
    nTypes['mltM'] = 'mltM'  # multiMatrix

    nTypes['sa'] = 'sa'  # surfAttach
    nTypes['ca'] = 'ca'  # curveAttach

    nTypes['UV'] = 'UV'  # UV nurbs

    # DEFORMS____________________________________________________________________
    nTypes['DEFORMER'] = 'DEFORMER' # template
    nTypes['bend'] = 'bend' # bend
    nTypes['squash'] = 'squash' # bend
    nTypes['ltc'] = 'ltc' # lattice
    nTypes['hdl'] = 'hdl' # handle

    # SHAPE______________________________________________________________________
    nTypes['geo'] = 'geo' # geometry
    nTypes['cv'] = 'cv' # curve
    nTypes['loft'] = 'loft' # loft
    nTypes['surf'] = 'surf' # surface
    nTypes['shp'] = 'shp' # shape

    # EXPRESSION CONNECTION_______________________________________________________
    nTypes['exp'] = 'exp' # expression
    nTypes['attr'] ='attr' # attributes

    # SET_________________________________________________________________________
    nTypes['set'] = 'set' # set

    # RIGGING CHARACTER___________________________________________________________
    nTypes['clav'] = 'clav' # clavicule
    nTypes['eyeTarget'] = 'eyeTarget' # eyeTarget
    nTypes['footRoll'] = 'footRoll' # footRoll
    nTypes['ballRoll'] = 'ballRoll' # ballRoll

    return nTypes[key]
# type_name(nTypes['set'])
##NAMESPACES FOR PUBLISH################################################################################################
def refNspaceMOD():
    dicNspace = {}
    dicNspace['importe'] = ['HUMANEYES', 'BUCCALKIT', 'MOD']
    dicNspace['remove'] = ['RIG', 'FUR', 'UV', 'SHD', 'TURN']
    return dicNspace

def refNspaceUV():
    dicNspace = {}
    dicNspace['importe'] = ['HUMANEYES', 'BUCCALKIT']
    dicNspace['remove'] = ['MOD', 'RIG', 'FUR', 'UV', 'SHD', 'TURN']
    return dicNspace

def refNspaceRIG():
    dicNspace = {}
    dicNspace['importe'] = ['MOD', 'RIG', 'HUMANEYES', 'BUCCALKIT', 'SHP']
    dicNspace['remove'] = ['FUR', 'UV', 'SHD', 'TURN']
    return dicNspace

def refNspaceFUR():
    dicNspace = {}
    dicNspace['importe'] = ['']
    dicNspace['remove'] = ['RIG', 'HUMANEYES', 'BUCCALKIT', 'FUR', 'SHD', 'UV','MOD', 'TURN']
    return dicNspace
##TRGT ZONE######################################################################################################################
def trgtNames():
    dicTrgt = {}
    #dicTrgt['none'] = ''
    dicTrgt['cheeks'] = 'ch'
    dicTrgt['eyebrows'] = 'eb'
    dicTrgt['eyelids'] = 'el'
    dicTrgt['ears'] = 'er'
    dicTrgt['jaw'] = 'jw'
    dicTrgt['lips'] = 'li'
    dicTrgt['mouth'] = 'mo'
    dicTrgt['nose'] = 'no'
    return dicTrgt

def sepSlices():
    dicSlices = {}
    #dicSlices['none'] = ''
    #dicTrgt['Left'] = 'Lt'
    #dicTrgt['Right'] = 'Rt'
    dicSlices['Middle'] = 'Mid'
    dicSlices['Up'] = 'Up'
    dicSlices['Down'] = 'Dn'
    dicSlices['Ext'] = 'Ext'
    dicSlices['Int'] = 'Int'
    dicSlices['Corner'] = 'Corn'
    return dicSlices



def name_format(prefix=None, name=None, nFunc=None,incPart=None,inc=None, nSide=None, order=(0,1,2,3,4,5), **kwargs):
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
        ("_" + prefix) if prefix else "",
        ("_" + name) if name else "", ("" + nFunc) if nFunc else "", ("" + inc) if inc else "",
        ("_" + incPart) if incPart else "", ("_" + nSide) if nSide else "")
    nameFormat = nameFormat[1:]
    splitObj = nameFormat.split("_")
    '''
    if mc.objExists(nameFormat)== True:
        if name == None:
            inc = str(getMaxIncObj(name=[splitObj[0]], side='', slideSplit=0))
        else:
            inc= str(getMaxIncObj(name=[splitObj[0],splitObj[1]], side='', slideSplit=1))
    else:
        pass

    nameFormat = ('{%s}{%s}{%s}{%s}{%s}{%s}' % (order[0], order[1], order[2], order[3], order[4], order[5])).format(
        ("_" + prefix) if prefix else "",
        ("_" + name) if name else "", ("" + nFunc) if nFunc else "", ("" + inc) if inc else "",
        ("_" + incPart) if incPart else "", ("_" + nSide) if nSide else "")
    nameFormat = nameFormat[1:]
    '''
    return nameFormat
#name_format(prefix='tpl', name='toto', func=None, inc='1', nSide='L', order=[0,1,2,3,4,5])


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


def InspectE(lFilter=None, lDel=None, side=None, incPart='incPart', *args):
    # inspecter la scene
    Obj = mc.ls(tr=True)
    # filter by namePart
    getNObj = []
    for i, eachE in enumerate(Obj):
        if set(re.findall('|'.join(lFilter), eachE)) == set(lFilter):
            getNObj.append(eachE)
    # filter by incPart
    DicAll = {}; DicObj = {}; lIncPart = []
    if getNObj == []:
        pass
    else:
        for j, each in enumerate(getNObj):
            if mc.objExists(each + ".%s" % incPart) is True:
                lIncPart.append(int(mc.getAttr(each + ".%s" % incPart)))
        lIncPart.sort()
        lIncPart = (set(lIncPart))  # set incrementation

        for inc in lIncPart:
            DicAll[str(inc)] = []

        for each in getNObj:
            if mc.objExists(each + ".%s" % incPart) is True:
                DicAll[str(mc.getAttr(each + ".%s" % incPart))].append(each)
        # filter tpl
        if lDel==None:
            DicObj = DicAll
        else:
            for k, v in DicAll.items():
                DicObj[k] = [s for s in v if not re.match("^.*({}).*$".format('|'.join(lDel)), s)]
    return DicObj

#InspectE(lFilter=['tpl', 'rope'], lDel=['Knot', 'Mtr'])


def incPart(name=None, **kwargs):
    '''
    :return: name_format
    '''
    #nameFormat = nameFormat[1:]
    splitObj = name.split("_")
    incPart = 1
    if mc.objExists(name)== True:
        if len(splitObj) == 1:
            incPart = str(getMaxIncObj(name=[splitObj[0]], side='', slideSplit=1))
        else:
            incPart= str(getMaxIncObj(name=[splitObj[0],splitObj[1]], side='', slideSplit=2))
    incPart = str(int(incPart))
    return incPart


def rig_exist(name):
    '''
    Inspect if rig already exist
    :return: a dictionnary the name of the controllers if they exist, otherwise {}
    '''
    return mc.objExists(name)


def inspectPartNameExist(partName=None, selObj=None, sliddeSplit=None, exist=None):
    '''
    Inspect if part of selObj exist
    :return: True or False
    '''
    splitObj = selObj.split("_")
    works = partName
    # inspect part name or full name
    if sliddeSplit == None:
        name = re.findall('|'.join(works), selObj)
    else:
        name = re.findall('|'.join(works), splitObj[sliddeSplit])
    # get if all string of partName exist
    for i, each in enumerate(partName):
        try:
            if each == name[i]:
                exist = True
        except:
            exist = False
    return exist
# inspect = inspectPartNameExist(self,partName=['tpl', 'ball'], selObj=mc.ls(sl=True)[0], sliddeSplit=None)


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


def incrementationABC(value=''):
    for i, each in enumerate(value):
        countLetter = chr(ord('a') + i)
        if i > 25:
            countLetter = 'a' + chr(ord('a') + i - 26)
        print countLetter
#incrementationABC(value="totofffffffffffffffffhhfffhfffffffffffff")


def renameSplit(selObj=None, namePart=None, newNamePart=None, reNme=False):
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


def get_increment(strNum):
    ## Gugu
    r = strNum[-1::-1]
    d = [c.isdigit() for c in r]
    ## retourne le nombre de fin de la string
    num = ''.join((i[0] for i in takewhile(lambda (x, y): y, zip(r, d))))[-1::-1] or None
    if num:
        strCutNum = strNum.split(num)[0]
        return strCutNum, num
    else:
        #print '##   no incrementation exist on ', strNum
        return strNum, None


def set_increment(name):
    ## Gugu
    strCutNum, num = get_increment(name)
    lAllTrsf = mc.ls(sl=False, type='transform')
    lNamed = []
    ## checker ds tous les trsfm s'il n'existe pas d'autre obj incremente
    for transform in lAllTrsf:
        if strCutNum in transform:
            ## checker que les caracteres suivant le nom coupe soit bien un digit
            if len(transform) > len(strCutNum):
                if transform[len(strCutNum)].isdigit():
                    lNamed.append(transform)
    lNum = []
    for named in lNamed:
        strCutNum2, num2 = get_increment(named)
        if num2:
            lNum.append(num2)
    if lNum:
        numMax = max(lNum)
    else :
        numMax = 0
    newName = strCutNum + str(int(numMax) + 1)
    return newName