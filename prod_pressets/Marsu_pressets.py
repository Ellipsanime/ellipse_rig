import maya.cmds as mc
import os , sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
import global_presets
reload(global_presets)


class fileDatas(global_presets.fileDatas):
    def __init__(self, currentFile=mc.file(q=True, sn=True) or 'unamed file', *args):
        super(fileDatas, self).__init__(*args)
        self.test = 'long LONG tail'
        # globals
        self.project = 'MSR'
        self.prod = 'msr'
        self.fileType = '.ma'
        self.lDir = ['wip', 'toCheck', 'exp']

        self.plugins = ['Turtle', 'mtoa', 'stereoCamera']

        self.fileName = 'unknown'
        self.ref = None
        if self.filePath != 'unknown':
            self.fileName = self.filePath.split(self.dirTrunk)[-1]
            self.ref = mc.file(self.filePath, q=True, reference=True) or []
        # prod
        #C:\Users\feine\Documents\ellipse\MARSU\02_DEV\ASSETS\CHR\Marsu\mod\modeling\work\MAYA\MRSDEV_CHR_Marsu_Modeling_v107.ma
        self.scnTrunk = '_'
        self.scnIncTrunk = '_v'
        self.dirEnd = 2

        self.dirTypeId = -7
        self.dirStepId = -5
        self.dirTaskId = -4
        self.dirAssetId = -6
        self.dirIncId = ''
        self.dirAddId = ''

        self.scnTypeId = -4
        #self.scnStepId = ''
        self.scnTaskId = -2
        self.scnAssetId = -3
        self.scnIncId = ''
        self.scnAddId = ''

        # Task dir
        self.dirWip = 'work'
        self.dirPub = 'OUT'
        # Steps
        self.mod = 'mod'
        self.shp = 'SHP'
        self.stp = 'stp'
        self.shd = 'shd'
        self.fur = 'FUR'
        self.dirSteps = {self.mod: 'MOD', self.shd: 'SHD', self.stp: 'RIG', self.fur: 'FUR'}

        # Rig tasks
        self.tpl = 'rigtemplate'
        self.build = 'rigbuild'
        self.rig = 'rig'
        self.exp = 'exp'
        self.rnd = 'vrender'
        self.toChk = 'vanim'
        self.ani = 'vanim'
        self.lay = 'vlay'
        self.trgt = 'shapefacial'

        # steps
        self.stepMod = 'mod'
        self.stepStp = 'stp'
        # namespaces
        self.nSpaces = {self.mod: 'MOD', self.shp: 'SHP', self.shd: 'SHD', self.stp: 'RIG', self.fur: 'FUR',
                        self.exp: 'EXP'}
        # Assets type
        self.chr = 'CHR'
        self.prp = 'PRP'
        self.bg = 'BG'
        # toto
        self.tasks = {self.mod: ['high'], self.shd: ['base'],
                      self.stp: [self.tpl, self.rig, self.ani, self.trgt, self.exp], self.fur: ['art']}
        self.steps = self.tasks.keys()
        self.vAniStepToDel = [self.shd, self.fur]
        self.refToKeep = [self.nSpaces[self.mod], self.nSpaces[self.shp], self.nSpaces[self.stp], self.nSpaces[self.exp], 'TAIL', 'BOING']
        self.refToRemove = [self.nSpaces[self.shd], self.nSpaces[self.fur]]

        #published scene
        self.doExp = True
        self.doChk = True
        self.doAni = True
        self.doRnd = True
    ####### SCENE GENERATORS #####################################################

    def refNspaceRIG(self):
        dicNspace = {}
        dicNspace['importe'] = ['MOD', 'RIG', 'EYES', 'BUCCALKIT', 'FACESHAPE', 'TAIL']
        dicNspace['remove'] = ['FUR', 'UV', 'SHD', 'TURN']
        return dicNspace



    def genMod(self):
        newDir = self.filePath.replace(self.fileName, self.dirPub)
        self.genFolder(newDir)
        modScn = self.switchScnTask('_w', '_r')
        newPath = newDir + self.dirTrunk + self.fileName
        self.saveScene(self.filePath, newPath)


    def genRig(self):
        newDir = self.filePath.replace(self.fileName, self.dirPub)
        self.genFolder(newDir)
        rigScn = self.fileName.replace(self.scnTrunk+self.tpl+self.scnTrunk, self.scnTrunk+self.rig+self.scnTrunk)
        newPath = newDir + self.dirTrunk + rigScn
        self.saveScene(self.filePath, newPath)



    def genExp(self):
        newDir = self.filePath.replace(self.fileName, self.dirPub)
        self.genFolder(newDir)
        rigScn = self.switchScnTask(self.getScnTask(), self.exp).split(self.dirTrunk)[-1]
        newPath = newDir+self.dirTrunk+rigScn
        self.saveScene(self.filePath, newPath)
        print
        'exp generated'



    def genVRnd(self, push=False):
        # crvGuidesRestPosition()
        rndScn = self.switchScnTask(self.getScnTask(), self.rnd)
        self.saveScene(self.filePath, rndScn)
        print 'vRender generated'


    def genVChk(self):
        rndScn = self.switchScnTask(self.getScnTask(), self.toChk)
        self.saveScene(self.filePath, rndScn)
        print 'toChk generated'

    def genVAni(self):
        print('open pipe do that')
        # removeGroom()
        # clean.rootUnkeyable()

    def genVLay(self):
        newDir = self.filePath.split(self.dirTrunk + self.dirWip + self.dirTrunk)[0] + self.dirTrunk + self.dirPub
        self.genFolder(newDir)
        pubPath = self.switchDirTask(self.dirWip, self.dirPub)
        pubScn = self.switchScnTask(self.lay + '_w', self.lay + '_' + self.toChk + '_r')
        newPath = pubPath.replace(self.fileName, pubScn.split(self.dirTrunk)[-1])
        self.saveScene(self.filePath, newPath)
        print 'vLay generated for', self.getScnAsset()

class faceDatas(global_presets.faceDatas):
    def __init__(self, *args):
        super(faceDatas, self).__init__(*args)
        self.lZones = ['eyebrows', 'eyelids', 'mouth', 'lips']

    def trgtNames(self):
        dicTrgt = {}
        # dicTrgt['none'] = ''
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
        # dicSlices['none'] = ''
        # dicTrgt['Left'] = 'Lt'
        # dicTrgt['Right'] = 'Rt'
        dicSlices['Middle'] = 'Mid'
        dicSlices['Up'] = 'Up'
        dicSlices['Down'] = 'Dn'
        dicSlices['Ext'] = 'Ext'
        dicSlices['Int'] = 'Int'
        dicSlices['Corner'] = 'Corn'
        return dicSlices

    def listOfShapes(self):
        # EYEBROWS##################################################
        dicEyebrows = {}
        dicEyebrows['ebSlide'] = ['eb_raiser', 'eb_lower']
        dicEyebrows['ebSqueeze'] = ['eb_squeeze']
        # EYELIDS###################################################
        dicEyelids = {}
        dicEyelids['elSlide'] = ['el_raiser', 'el_lower']
        # MOUTH#####################################################
        dicMouth = {}
        dicMouth['moEmote'] = ['mo_smile', 'mo_frown']
        dicMouth['moStrech'] = ['mo_wide', 'mo_narrow']
        dicMouth['moCornerStrech'] = ['mo_cornerPinch', 'mo_cornerSpacing']

        # LIPS######################################################
        dicLips = {}
        dicLips['liRoll'] = ['li_rollIn', 'li_rollOut']
        dicLips['liPush'] = ['li_pushOut']
        dicLips['liU'] = ['li_uRaiser', 'li_uLower']
        ###########################################################
        dicShapes = {'dicMouth': dicMouth, 'dicEyebrows': dicEyebrows, 'dicLips': dicLips, 'dicEyelids': dicEyelids}

        return dicShapes

    def trgtToCtrlChan(self):
        dicChans = {}
        dicChansPositive = {}
        dicChansNegative = {}

        # EYEBROWS##################################################
        dicChansPositive['eb_raiser'] = 'translateY'  # +
        dicChansNegative['eb_lower'] = 'translateY'  # -
        dicChansNegative['eb_squeeze'] = 'translateX'  # -


        # EYELIDS###################################################
        dicChansPositive['el_raiser'] = 'translateY'  # +
        dicChansNegative['el_lower'] = 'translateY'  # -

        # NOSE######################################################
        dicChansPositive['no_snear'] = 'translateY'  # +
        # MOUTH#####################################################
        dicChansPositive['mo_smile'] = 'translateY'  # +
        dicChansNegative['mo_frown'] = 'translateY'  # -
        dicChansPositive['mo_wide'] = 'translateX'  # +
        dicChansNegative['mo_narrow'] = 'translateX'  # -

        dicChansNegative['mo_cornerPinch'] = 'scaleY'  # +
        dicChansPositive['mo_cornerSpacing'] = 'scaleY'  # -

        # LIPS######################################################
        dicChansPositive['li_rollIn'] = 'rotateX'  # +
        dicChansNegative['li_rollOut'] = 'rotateX'  # -
        dicChansPositive['li_pushOut'] = 'translateZ'  # +
        dicChansPositive['li_uRaiser'] = 'translateY'  # +
        dicChansNegative['li_uLower'] = 'translateY'  # -


        dicChans = {'positive': dicChansPositive, 'negative': dicChansNegative}
        return dicChans