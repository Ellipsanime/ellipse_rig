import maya.cmds as mc
from prod_presets import global_presets


class fileDatas(global_presets.fileDatas):
    def __init__(self):
        # globals
        self.dirTrunk = '\\'
        self.filePath = mc.file(q=True, sn=True) or 'unamed file'
        self.project = 'MRS'
        self.fileType = '.ma'
        self.lDir = ['work', 'snap', 'pub']
        self.tasks = {'STP':['tpl', 'rig', 'build']}
        self.steps = self.tasks.keys()
        self.fileName = 'unamed file'
        if self.filePath != 'unamed file':
            self.fileName = self.filePath.split(self.dirTrunk)[-1]


        self.test = 'LA PARTOUZE DES RENARDS'
        # prod
        self.sncTrunk = '__'
        self.sncIncTrunk = '__v'
        self.dirEnd = 1

        self.dirTypeId = 4
        self.dirStepId = 6
        self.dirTaskId = 7
        self.dirAssetId = 5
        self.dirIncId = ''
        self.dirAddId = ''

        self.scnTypeId = 1
        self.scnStepId = 3
        self.scnTaskId = 3
        self.scnAssetId = 2
        self.scnIncId = ''
        self.scnAddId = -2



        #Rig tasks
        self.tpl = 'tpl'
        self.build = 'build'
        self.rig = 'rig'
        #Assets type
        self.chr = 'Character'
        self.prp = 'Prop'
        self.bg = ''

