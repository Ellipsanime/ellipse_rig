import maya.cmds as mc
import os , sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
#import Smurf04_pressets
#reload(Smurf04_pressets)
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

        self.test = 'BELFOUTRE ET LUPINE'

        self.plugins = ['Turtle', 'stereoCamera']

        self.stepMod = '_mdl'
        self.stepStp = '_stp'
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
        print 'HERE :', fileInc.split('.')[0][1:]
        return fileInc.split('.')[0][1:]

    def updateFileInc(self):
        newInc = self.updateInc()
        nackedName = self.fileName[: len(self.fileName)-(len(self.fileName.split(self.scnTrunk)[-1].split(self.scnTrunk)[-1])-1)]
        newFileName = nackedName+newInc+'.ma'
        return newFileName

    def getScnTask(self):
        assetTask = self.fileName.split(self.stp)[-1].split(self.scnTrunk)[0]
        return assetTask




class faceDatas(global_presets.faceDatas):
    def __init__(self, *args):
        super(faceDatas, self).__init__(*args)
        self.lZones = ['eyebrows', 'eyelids', 'mouth', 'lips']


    def listOfShapes(self):
        #EYEBROWS##################################################
        dicEyebrows = {}
        dicEyebrows['ebSlide'] = ['eb_slide_up', 'eb_slide_dn']
        dicEyebrows['squeeze'] = ['eb_squeeze']
        #EYELIDS###################################################
        dicEyelids = {}
        dicEyelids['elBlink'] = ['el_Blink']
        #MOUTH#####################################################
        dicMouth = {}
        dicMouth['mEmote'] = ['mo_smile', 'mo_frown']
        #dicMouth['mSlide'] = ['mo_raiser', 'mo_lower']
        dicMouth['mStrech'] = ['mo_wide', 'mo_narrow']
        # LIPS######################################################
        dicLips = {}
        dicLips['lU'] = ['li_uRaiser', 'li_uLower']
        #######################################################################
        dicShapes = {'dicMouth':dicMouth, 'dicLips':dicLips, 'dicEyebrows':dicEyebrows, 'dicEyelids':dicEyelids}
        return dicShapes



    def trgtToCtrlChan(self):
        dicChans = {}
        dicChansPositive = {}
        dicChansNegative = {}

        #_EYEBROWS_##################################################
        dicChansPositive['eb_slide_up'] = 'translateY'   #+
        dicChansNegative['eb_slide_dn'] = 'translateY'   #-
        dicChansNegative['eb_squeeze'] = 'translateX'    #-
        #_EYELIDS_###################################################
        dicChansNegative['el_blink'] = 'scaleY' #-
        #_MOUTH_#####################################################
        dicChansPositive['mo_smile'] = 'translateY'    #+
        dicChansNegative['mo_frown'] = 'translateY'    #-
        dicChansPositive['mo_wide'] = 'translateX'     #+
        dicChansNegative['mo_narrow'] = 'translateX'   #-
        #dicChansPositive['mo_raiser'] = 'translateY' #+
        #dicChansNegative['mo_lower'] = 'translateY'  #-
        # LIPS######################################################
        dicChansPositive['li_uRaiser'] = 'translateY'  # +
        dicChansNegative['li_uLower'] = 'translateY'  # -
        ################################################################################
        dicChans = {'positive':dicChansPositive, 'negative':dicChansNegative}
        return dicChans