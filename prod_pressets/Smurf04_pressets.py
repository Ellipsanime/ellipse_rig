import maya.cmds as mc
import os , sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
import global_presets
reload(global_presets)



class fileDatas(global_presets.fileDatas):
    #T:\04_FAB\ASSETS\prp\BarrelC\_stp\WIP\prp_BarrelC__stp__sous_description_w001.ma
    #T:\04_FAB\ASSETS\prp\BarrelC\_mdl\PUB\prp_BarrelC__mdl__r001.ma
    def __init__(self, currentFile = mc.file(q=True, sn=True) or 'unamed file', *args):
        super(fileDatas, self).__init__(*args)
        # globals
        self.lDir = ['WIP', 'PUB']
        self.tasks = {'mdl':['high'], 'shd':['base'], 'stp':['tpl', 'rig', 'build', 'trgt', 'exp']}
        self.steps = self.tasks.keys()
        if self.filePath != 'unknown':
            self.fileName = self.filePath.split(self.dirTrunk)[-1]

        self.test = 'SUUUUCEFETTE'

        self.plugins = ['Turtle', 'mtoa', 'stereoCamera']

        # prod
        self.scnTrunk = '_'
        self.dirEnd = 2

        self.dirTypeId = -5
        self.dirStepId = -3
        self.dirTaskId = -2
        self.dirAssetId = 4
        self.dirIncId = ''
        self.dirAddId = ''


        self.scnTypeId = 0
        self.scnStepId = 1
        self.scnTaskId = -3
        self.scnAssetId = 2
        self.scnIncId = ''
        self.scnAddId = ''


        #Task dir
        self.dirWip = 'WIP'
        self.dirPub = 'PUB'
        #Steps
        self.mod = self.scnTrunk+self.scnTrunk+'mdl'+self.scnTrunk+self.scnTrunk
        self.stp = self.scnTrunk+self.scnTrunk+'stp'+self.scnTrunk+self.scnTrunk
        self.shd = self.scnTrunk+self.scnTrunk+'shd'+self.scnTrunk+self.scnTrunk
        self.dirSteps = {self.mod: self.scnTrunk+'mdl', self.shd: self.scnTrunk+'shd', self.stp: self.scnTrunk+'stp'}
        self.sncSteps = {self.scnTrunk + 'mdl': self.mod,self.scnTrunk + 'shd':  self.shd,
                         self.scnTrunk + 'stp': self.stp}
        #Rig tasks
        self.tpl = 'tpl'
        self.build = 'build'
        self.rig = 'rig'
        #Assets type
        self.chr = 'chr'
        self.prp = 'prp'
        # namespaces
        self.nSpaces = {self.mod:'MOD', self.shd:'SHD', self.stp:'RIG', self.fur:'FUR'}
        #toto
        self.tasks = {self.mod: ['high'], self.shd: ['base'], self.stp: [self.tpl, self.rig, 'vanim', 'trgt', 'exp'], self.fur: ['art']}
        self.steps = self.tasks.keys()

        self.scnIncTrunk = self.scnTrunk+self.stp+self.scnTrunk


    def getInc(self):
        fileInc = self.fileName.split(self.scnTrunk)[-1]
        #print 'HERE :', fileInc.split('.')[0][1:]
        return fileInc.split('.')[0][1:]

    def updateFileInc(self):
        newInc = self.updateInc()
        nackedName = self.fileName[: len(self.fileName)-(len(self.fileName.split(self.scnTrunk)[-1].split(self.scnTrunk)[-1])-1)]
        newFileName = nackedName+newInc+'.ma'
        return newFileName

    def getScnTask(self):
        assetTask = self.fileName.split(self.stp)[-1].split(self.scnTrunk)[0]
        return assetTask

    def genVAni(self):
        newPath = self.filePath.replace(self.toChk+'_', '')
        self.saveScene(self.filePath, newPath)
        print 'vAnim generated for', self.getScnAsset()

class faceDatas(global_presets.faceDatas):
    def __init__(self, *args):
        super(faceDatas, self).__init__(*args)



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
        dicNose['nSnear'] = ['no_snear']
        #MOUTH#####################################################
        dicMouth = {}
        dicMouth['mEmote'] = ['mo_smile', 'mo_frown']
        dicMouth['mStrech'] = ['mo_wide', 'mo_narrow']
        dicMouth['mDepth'] = ['mo_depthOut', 'mo_depthIn']
        dicMouth['mPuffCorner'] = ['mo_puffCorner']
        dicMouth['mOpen'] = ['mo_open']
        dicMouth['mCornerTwist'] = ['mo_cornerTwistDn', 'mo_cornerTwistUp']
        dicMouth['mCornerStrech'] = ['mo_cornerPinch', 'mo_cornerSpacing']


        #LIPS######################################################
        dicLips = {}
        dicLips['lRoll'] = ['li_rollIn', 'li_rollOut']
        dicLips['lPush'] = ['li_pushIn', 'li_pushOut']
        dicLips['lPinch'] = ['li_pinch']
        dicLips['lSlide'] = ['li_raiser', 'li_lower']
        dicLips['lPuff'] = ['li_puffIn', 'li_puffOut']
        dicLips['lU'] = ['li_uRaiser', 'li_uLower']
        dicLips['lSlipe'] = ['li_slipeLt', 'li_slipeRt']
        dicLips['lTwist'] = ['li_twistUp', 'li_twistDn']
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