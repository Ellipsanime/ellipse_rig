import maya.cmds as mc
import os, glob, re
from functools import partial
from itertools import takewhile

class fileDatas(object):

    FILEPATH = mc.file(q=True, sn=True)


    def __init__(self):
        # globals
        FILEPATH = mc.file(q=True, sn=True) or 'unamed file'
        if FILEPATH == 'unamed file':
            FILEPATH = mc.file(q=True, loc=True)

        self.dirTrunk = r'/'
        self.filePath = FILEPATH
        self.project = 'SMF'
        self.prod = 'smf'
        self.fileType = '.ma'
        self.lDir = ['wip', 'toCheck', 'exp']

        self.plugins = ['Turtle', 'mtoa', 'stereoCamera']

        self.test = 'global'

        self.fileName = 'unknown'
        self.ref = None
        if self.filePath != 'unknown':
            self.fileName = self.filePath.split(self.dirTrunk)[-1]
            self.ref = mc.file(self.filePath, q=True, reference=True) or []
        # prod
        self.scnTrunk = '_'
        self.scnIncTrunk = '_v'
        self.dirEnd = 2

        self.dirTypeId = 4
        self.dirStepId = 3
        self.dirTaskId = 6
        self.dirAssetId = 5
        self.dirIncId = ''
        self.dirAddId = ''



        self.scnTypeId = 1
        self.scnStepId = 1
        self.scnTaskId = -3
        self.scnAssetId = 2
        self.scnIncId = ''
        self.scnAddId = 3


        #Task dir
        self.dirWip = 'wip'
        self.dirPub = ''
        #Steps
        self.mod = 'MOD'
        self.shp = 'SHP'
        self.stp = 'STP'
        self.shd = 'SHD'
        self.fur = 'FUR'
        self.dirSteps = {self.mod:'MOD', self.shd:'SHD', self.stp:'RIG', self.fur:'FUR'}

        #Rig tasks
        self.tpl = 'tpl'
        self.build = 'wip'
        self.rig = 'rig'
        self.exp = 'exp'
        self.rnd = 'vrender'
        self.toChk = 'toCheck'
        self.ani = 'vanim'
        self.lay = 'vlay'
        self.trgt = 'trgt'

        #steps
        self.stepMod = '_mdl'
        self.stepStp = '_stp'
        # namespaces
        self.nSpaces = {self.mod: 'MOD', self.shp: 'SHP', self.shd: 'SHD', self.stp: 'RIG', self.fur: 'FUR', self.exp: 'EXP'}
        #Assets type
        self.chr = 'CHR'
        self.prp = 'PRP'
        self.bg = 'BG'
        #toto
        self.tasks = {self.mod: ['high'], self.shd : ['base'], self.stp : [self.tpl, self.rig, self.ani, self.trgt, self.exp], self.fur: ['art']}
        self.steps = self.tasks.keys()
        self.vAniStepToDel = [self.shd, self.fur]
        self.refToKeep = [self.nSpaces[self.mod], self.nSpaces[self.shp], self.nSpaces[self.stp], self.nSpaces[self.exp]]
        self.refToRemove = [self.nSpaces[self.shd], self.nSpaces[self.fur]]


        #published scene
        self.doExp = True
        self.doChk = True
        self.doAni = True
        self.doRnd = False



    def getDir(self):
        dirFolder = ''
        trunk = self.filePath.split(self.dirTrunk)
        for i in range(0, self.dirEnd):
            dirFolder += trunk[i]+self.dirTrunk
        return dirFolder

    def getFileName(self):
        self.fileName = self.filePath.split(self.dirTrunk)[-1]
        return self.fileName

    def getDirType(self):
        assetType = self.filePath.split(self.dirTrunk)[self.dirTypeId]
        return assetType

    def getScnType(self):
        assetType = self.fileName.split(self.scnTrunk)[self.scnTypeId]
        return assetType

    def getDirStep(self):
        assetTask = self.filePath.split(self.dirTrunk)[self.dirStepId]
        return assetTask

    def getScnStep(self):
        assetTask = self.fileName.split(self.scnTrunk)[self.scnStepId]
        return assetTask

    def getRefDirStep(self, ref):
        assetTask = ref.split(self.dirTrunk)[self.dirStepId]
        return assetTask

    def getDirTask(self):
        assetTask = self.filePath.split(self.dirTrunk)[self.dirTaskId]
        return assetTask

    def getScnTask(self):
        assetTask = self.fileName.split(self.scnTrunk)[self.scnTaskId]
        return assetTask

    def getDirAsset(self):
        asset = self.filePath.split(self.dirTrunk)[self.dirAssetId]
        return asset

    def getScnAsset(self):
        asset = self.fileName.split(self.scnTrunk)[self.scnAssetId]
        return asset

    def getInc(self):
        fileInc = self.fileName.split(self.scnIncTrunk)[-1]
        return fileInc.split('.')[0]

    def getScnRefs(self):
        lRef = mc.file(self.filePath, q=True, reference=True) or []
        return lRef

    def updateInc(self):
        fileInc = self.getInc().split('_')[-1]
        #print 'HERE inc:', fileInc
        updateInc = str(int(fileInc)+1)
        newInc = fileInc[: len(fileInc)-len(updateInc)]+updateInc
        return newInc

    def updateFileInc(self):
        inc = self.getInc()
        newInc = self.updateInc()
        nackedName = self.fileName.split(self.scnIncTrunk)[0]
        newFileName = nackedName+self.scnIncTrunk+newInc
        return newFileName


    def getAdd(self):
        print 'toto'

    def getLastFile(self, dir, fileName, fileType):
        if not os.path.exists(dir):
            mc.warning(dir, 'does not exist')
        else:
            lFiles = glob.glob(dir+self.dirTrunk+fileName.split(self.scnIncTrunk)[0]+self.scnIncTrunk+'*'+fileType)
            if lFiles:
                latest_file = max(lFiles, key=os.path.getmtime)
                return latest_file
            else:
                mc.warning('no file found for', fileName)

    def getfilesFromDir(self):
        print 'toDo'


    def getOtherStepDir(self, stepSrc, stepDest):
        assetDir = self.filePath.split(self.dirWip)[0]
        newDir = assetDir.replace(self.dirTrunk+stepSrc+self.dirTrunk, self.dirTrunk+stepDest+self.dirTrunk)+self.dirTrunk+self.dirPub
        return newDir

    def getOtherStep(self):
        print 'toto'

    def getRefDatas(self):
        dicRef = {}
        dicRef['steps'] = {}
        dicRef['steps'][self.exp] = []
        for ref in self.ref:
            refStep = mc.referenceQuery(ref, ns=True)[1 :]
            if not refStep in dicRef['steps'].keys():
                dicRef['steps'][refStep] = []
            dicRef['steps'][refStep].append(ref)
            if not ref in dicRef.keys():
                dicRef[ref] = {}
                dicRef[ref]['refNode'] = mc.referenceQuery(ref, rfn=True)
                dicRef[ref]['nspace'] = refStep
                dicRef[ref]['edits'] = mc.reference(referenceNode=dicRef[ref]['refNode'], query=True, editCommand=True)
        return dicRef


    def genFolder(self, dir):
        try:
            if not os.path.exists(dir):
                os.makedirs(dir)
        except OSError:
            print ('Error: Creating directory. '+dir)

    def buildSceneName(self):
        print 'toto'

    def switchScnTask(self, taskSrc, taskDest):
        newScnName = self.fileName.replace(taskSrc, taskDest)
        newPath = self.filePath.replace(self.fileName, newScnName)
        return newPath

    def switchDirTask(self, taskSrc, taskDest):
        newPath = self.filePath.replace(taskSrc, taskDest)
        return newPath


    def saveScene(self, oldPath, newPath):
        mc.file(oldPath, rn=newPath)
        mc.file(save=True)
        self.filePath = newPath
        self.fileName = self.filePath.split(self.dirTrunk)[-1]

####### SCENE GENERATORS #####################################################
    def genMod(self):
        newDir = self.filePath.split(self.dirTrunk + self.dirWip + self.dirTrunk)[0] + self.dirTrunk + self.dirPub
        self.genFolder(newDir)
        modScn = self.switchScnTask('_w', '_r')
        newPath = newDir+self.dirTrunk+modScn.split(self.dirTrunk)[-1]
        self.saveScene(self.filePath, newPath)

    def genRig(self):
        newPath = self.switchScnTask(self.tpl, self.rig)
        self.saveScene(self.filePath, newPath)


    def genExp(self):
        if self.getScnType() == self.chr:
            #newPath = self.switchScnTask(self.getScnTask()+'_w', self.exp+'_r')
            newPath = self.switchScnTask(self.getScnTask(), self.exp)
            self.saveScene(self.filePath, newPath)
        if self.getScnType() == self.prp:
            print 'PROOOOPS'


    def genVChk(self):
        chkScn = ''
        newDir = self.filePath.split(self.dirTrunk + self.dirWip + self.dirTrunk)[0] + self.dirTrunk + self.dirPub
        self.genFolder(newDir)
        if self.getScnTask() in [self.build, self.exp]:
            chkScn = self.switchScnTask(self.getScnTask()+'_w', self.toChk+'_r')
        else:
            chkScn = self.switchScnTask(self.getScnTask(), self.toChk)
        chkPath = self.switchDirTask(self.dirWip, self.dirPub)
        newPath = chkPath.replace(self.fileName, chkScn.split(self.dirTrunk)[-1])
        self.saveScene(self.filePath, newPath)

    def genVRnd(self, push=False):
        #crvGuidesRestPosition()
        newPath = self.switchScnTask(self.getScnTask(), self.rnd)
        self.saveScene(self.filePath, newPath)
        print 'vanimRnd generated for', self.getScnAsset()
        #if push == True:
            #quickPushInSG(newPath, assetType, step, task, asset)
        #print 'vanimFull pushed for', self.getScnAsset()

    def genVAni(self):
        print 'toto'
        #removeGroom()
        #clean.rootUnkeyable()

    def genVLay(self):
        newDir = self.filePath.split(self.dirTrunk + self.dirWip + self.dirTrunk)[0] + self.dirTrunk + self.dirPub
        self.genFolder(newDir)
        pubPath = self.switchDirTask(self.dirWip, self.dirPub)
        pubScn = self.switchScnTask(self.lay+'_w', self.lay+'_'+self.toChk+'_r')
        newPath = pubPath.replace(self.fileName, pubScn.split(self.dirTrunk)[-1])
        self.saveScene(self.filePath, newPath)
        print 'vLay generated for', self.getScnAsset()






class lexic(object):
    #def __init__(self):
    def type_color(self, key):
        nTypesColor = {}

        nTypesColor['red'] = 'red'
        nTypesColor['green'] = 'green'
        nTypesColor['yellow'] = 'yellow'
        return nTypesColor[key]

    def type_name(self, key):
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
    def refNspaceMOD(self):
        dicNspace = {}
        dicNspace['importe'] = ['HUMANEYES', 'BUCCALKIT', 'MOD']
        dicNspace['remove'] = ['RIG', 'FUR', 'UV', 'SHD', 'TURN']
        return dicNspace

    def refNspaceUV(self):
        dicNspace = {}
        dicNspace['importe'] = ['HUMANEYES', 'BUCCALKIT']
        dicNspace['remove'] = ['MOD', 'RIG', 'FUR', 'UV', 'SHD', 'TURN']
        return dicNspace

    def refNspaceRIG(self):
        dicNspace = {}
        dicNspace['importe'] = ['MOD', 'RIG', 'HUMANEYES', 'BUCCALKIT', 'SHP']
        dicNspace['remove'] = ['FUR', 'UV', 'SHD', 'TURN']
        return dicNspace

    def refNspaceFUR(self):
        dicNspace = {}
        dicNspace['importe'] = ['']
        dicNspace['remove'] = ['RIG', 'HUMANEYES', 'BUCCALKIT', 'FUR', 'SHD', 'UV','MOD', 'TURN']
        return dicNspace
    ##TRGT ZONE######################################################################################################################
    def trgtNames(self):
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

    def sepSlices(self):
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



class faceDatas(object):
    def __init__(self):
        self.lZones = ['eyebrows', 'eyelids', 'nose', 'cheeks', 'ears', 'mouth', 'lipse', 'jaw']
        self.lSlices = ['Int', 'Middle', 'Ext', 'Up', 'Down', 'Corner']



    def trgtNames(self):
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

    def sepSlices(self):
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


    def listOfShapes(self):
        #EYEBROWS##################################################
        dicEyebrows = {}
        dicEyebrows['ebSlide'] = ['eb_slide_up', 'eb_slide_dn']
        dicEyebrows['ebTwistInt'] = ['eb_intTwist_up', 'eb_intTwist_dn']
        dicEyebrows['ebTwistExt'] = ['eb_extTwist_up', 'eb_extTwist_dn']
        dicEyebrows['ebSqueeze'] = ['eb_squeeze']
        dicEyebrows['ebWrinkle'] = ['eb_wrinkle']
        #EYELIDS###################################################
        dicEyelids = {}
        dicEyelids['elSlide'] = ['el_slide_up', 'el_slide_dn']
        dicEyelids['elTwist'] = ['el_twist_in', 'el_twist_out']
        dicEyelids['elConcealar'] = ['el_Concealar']
        dicEyelids['elOpen'] = ['el_open']
        #CHEEKS####################################################
        dicCheeks = {}
        dicCheeks['chPuff'] = ['ch_puffOut', 'ch_puffIn']
        dicCheeks['chCheeks'] = ['ch_cheeks']
        #NOSE######################################################
        dicNose = {}
        dicNose['noSnear'] = ['no_snear']
        #MOUTH#####################################################
        dicMouth = {}
        dicMouth['moEmote'] = ['mo_smile', 'mo_frown']
        dicMouth['moStrech'] = ['mo_wide', 'mo_narrow']
        dicMouth['moDepth'] = ['mo_depthOut', 'mo_depthIn']
        dicMouth['moPuffCorner'] = ['mo_puffCorner']
        dicMouth['moOpen'] = ['mo_open']
        dicMouth['moCornerTwist'] = ['mo_cornerTwistDn', 'mo_cornerTwistUp']
        dicMouth['moCornerStrech'] = ['mo_cornerPinch', 'mo_cornerSpacing']


        #LIPS######################################################
        dicLips = {}
        dicLips['liRoll'] = ['li_rollIn', 'li_rollOut']
        dicLips['liPush'] = ['li_pushIn', 'li_pushOut']
        dicLips['liPinch'] = ['li_pinch']
        dicLips['liSlide'] = ['li_raiser', 'li_lower']
        dicLips['liPuff'] = ['li_puffIn', 'li_puffOut']
        dicLips['liU'] = ['li_uRaiser', 'li_uLower']
        dicLips['liSlipe'] = ['li_slipeLt', 'li_slipeRt']
        dicLips['liTwist'] = ['li_twistUp', 'li_twistDn']
        ###########################################################
        dicShapes = {'dicMouth':dicMouth, 'dicEyebrows':dicEyebrows, 'dicLips':dicLips, 'dicCheeks':dicCheeks, 'dicNose':dicNose, 'dicEyelids':dicEyelids}

        return dicShapes



    def trgtToCtrlChan(self):
        dicChans = {}
        dicChansPositive = {}
        dicChansNegative = {}

        #EYEBROWS##################################################
        dicChansPositive['eb_slide_up'] = 'translateY'   #+
        dicChansNegative['eb_slide_dn'] = 'translateY'   #-
        dicChansNegative['eb_squeeze'] = 'translateX'    #-
        dicChansPositive['eb_wrinkle'] = 'scaleZ'        #+

        dicChansPositive['eb_intTwist_dn'] = 'rotateZ'   #+
        dicChansNegative['eb_intTwist_up'] = 'rotateZ'   #-
        dicChansNegative['eb_extTwist_dn'] = 'rotateZ'   #-
        dicChansPositive['eb_extTwist_up'] = 'rotateZ'   #+
        #EYELIDS###################################################
        dicChansPositive['el_slide_up'] = 'translateY' #+
        dicChansNegative['el_slide_dn'] = 'translateY' #-

        dicChansPositive['el_twist_in'] = 'rotateZ'    #+
        dicChansNegative['el_twist_out'] = 'rotateZ'   #-
        dicChansPositive['el_Concealar'] = 'scaleZ'    #+

        dicChans['el_open'] = ''
        #CHEEKS####################################################
        dicChansPositive['ch_puffOut'] = 'scaleZ'      #+
        dicChansNegative['ch_puffIn'] = 'scaleZ'       #-
        dicChansPositive['ch_cheeks'] = 'translateY'   #+
        #NOSE######################################################
        dicChansPositive['no_snear'] = 'translateY'    #+
        #MOUTH#####################################################
        dicChansPositive['mo_smile'] = 'translateY'    #+
        dicChansNegative['mo_frown'] = 'translateY'    #-
        dicChansPositive['mo_wide'] = 'translateX'     #+
        dicChansNegative['mo_narrow'] = 'translateX'   #-
        dicChansPositive['mo_depthOut'] = 'translateZ' #+
        dicChansNegative['mo_depthIn'] = 'translateZ'  #-
        dicChansPositive['mo_puffCorner'] = 'scaleZ'   #+
        dicChansNegative['mo_cornerPinch'] = 'scaleY'  #+
        dicChansPositive['mo_cornerSpacing'] = 'scaleY'  #-

        dicChansPositive['mo_cornerTwistUp'] = 'rotateZ'#+
        dicChansNegative['mo_cornerTwistDn'] = 'rotateZ'#-
        dicChans['mo_open'] = ''
        #LIPS######################################################
        dicChansPositive['li_rollIn'] = 'rotateX'     #+
        dicChansNegative['li_rollOut'] = 'rotateX'    #-
        dicChansNegative['li_pushIn'] = 'translateZ'  #-
        dicChansPositive['li_pushOut'] = 'translateZ' #+
        dicChansNegative['li_pinch'] = 'scaleY'       #-
        dicChansPositive['li_raiser'] = ''  #
        dicChansNegative['li_lower'] = ''   #
        dicChansPositive['li_puffOut'] = 'scaleZ'     #+
        dicChansNegative['li_puffIn'] = 'scaleZ'      #-
        dicChansPositive['li_uRaiser'] = 'translateY'    #+
        dicChansNegative['li_uLower'] = 'translateY'     #-
        dicChansPositive['li_slipeLt'] = 'translateX' #+
        dicChansNegative['li_slipeRt'] = 'translateX' #-
        dicChansPositive['li_twistUp'] = 'rotateZ'        #+
        dicChansNegative['li_twistDn'] = 'rotateZ'      #-

        dicChans = {'positive':dicChansPositive, 'negative':dicChansNegative}
        return dicChans


class sceneCleans(object):
    def __init__(self):
        print 'to do'