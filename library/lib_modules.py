import sys
import maya.cmds as mc
import maya.mel as mel
from functools import partial

def modulesBtnSwitcher_UI(btnTrigger):
    lBtnModules = ['btnSpineModule', 'btnArmModule', 'btnLegModule', 'btnNeckModule', 'btnEyeModule', 'btnTailModule', 'btnSnakeModule', 'btnWingModule']
    if mc.frameLayout('moduleFrameOptions_UI', ex=True):
        mc.deleteUI('moduleFrameOptions_UI', lay=True)
    for btn in lBtnModules:
        if btnTrigger != btn:
            mc.button(btn, e=True, bgc=[.4, .4, .4])
        mc.button(btnTrigger, e=True, bgc=[.3, .5, .5])
    if btnTrigger == 'btnSpineModule':
        mc.frameLayout('moduleFrameOptions_UI', label='Spine options:', bv=True, p='module_options')
        tplSpine_UI('moduleFrameOptions_UI', 'moduleSide_UI', 'moduleCtrlFk_UI', 'moduleSk_UI')
    elif btnTrigger == 'btnArmModule':
        mc.frameLayout('moduleFrameOptions_UI', label='Arm options:', bv=True, p='module_options')
        tplArm_UI('moduleFrameOptions_UI', 'moduleSide_UI', 'moduleCtrlFk_UI', 'moduleSk_UI')
    elif btnTrigger == 'btnLegModule':
        mc.frameLayout('moduleFrameOptions_UI', label='Leg options:', bv=True, p='module_options')
        tplLeg_UI('moduleFrameOptions_UI', 'moduleSide_UI', 'moduleCtrlFk_UI', 'moduleSk_UI')
    elif btnTrigger == 'btnNeckModule':
        mc.frameLayout('moduleFrameOptions_UI', label='Neck options:', bv=True, p='module_options')
        tplNeck_UI('moduleFrameOptions_UI', 'moduleSide_UI', 'moduleCtrlFk_UI', 'moduleSk_UI')
    elif btnTrigger == 'btnEyeModule':
        mc.frameLayout('moduleFrameOptions_UI', label='Eye options:', bv=True, p='module_options')
        tplEye_UI('moduleFrameOptions_UI','moduleSide_UI', 'moduleCtrlFk_UI')
    elif btnTrigger == 'btnTailModule':
        mc.frameLayout('moduleFrameOptions_UI', label='Eye options:', bv=True, p='module_options')
        tplTail_UI('moduleFrameOptions_UI', 'moduleSide_UI', 'moduleCtrlFk_UI', 'moduleSk_UI')
    elif btnTrigger == 'btnWingModule':
        mc.frameLayout('moduleFrameOptions_UI', label='Wing options:', bv=True, p='module_options')
        tplWing_UI('moduleFrameOptions_UI', 'moduleAddFrameOptions_UI', 'moduleSide_UI', 'moduleRows_UI', 'moduleFeathers_UI', 'moduleCtrlFk_UI')

def tplSpine(side, nbrFkCtrl, nbrSk):
    from ellipse_rig.assets.characters import guide_spine
    reload(guide_spine)
    guide = guide_spine.Spine(name='spine',side=side,selObj=mc.ls(sl=True),numb=nbrFkCtrl,numbSk=nbrSk) # instance class charGuide
    guide.createSpine()


def tplSpine_UI(uiFram, uiSide, uiFk, uiSk):

    mc.separator(h=5, st="in")
    mc.radioButtonGrp(uiSide, nrb=3, l='Side : ', la3=['None', 'Left', 'Right'], ct4=('left', 'left', 'left', 'left'), co4=(0, -100, -150, -205), on1="mc.radioButtonGrp('"+uiSide+"', e=True, bgc=[.7, .6, .1])", on2="mc.radioButtonGrp('"+uiSide+"', e=True, bgc=[.5, .2, .2])", on3="mc.radioButtonGrp('"+uiSide+"', e=True, bgc=[.2, .3, .5])", sl=1, bgc=[.7, .6, .1])
    mc.separator(h=5, st="in")
    mc.intFieldGrp(uiFk, numberOfFields=1, label='FK ctrl :', cal=(1, 'left'), cat=(2, 'left', -80), value1=3, p=uiFram)
    mc.separator(h=5, st="in")
    mc.intFieldGrp(uiSk, numberOfFields=1, label='SK joints :', cal=(1, 'left'), cat=(2, 'left', -80), value1=5, p=uiFram)
    mc.separator(h=5, st="in")


########################################################################################################################
def tplArm(side, nbrFkClav, nbrSkClav, nbrFkCtrl, nbrSk, nbrPVCtrl, nbrHandFkCtrl, nbrFingers, nbrFingerFkCtrl):
    from ellipse_rig.assets.characters import guide_arm
    reload(guide_arm)
    guide = guide_arm.Arm(name='arm', side=side, selObj=mc.ls(sl=True), numbStartSk=nbrSkClav, numbStartMb=nbrFkClav, numb=nbrFkCtrl, numbSk=nbrSk, numbPlV=nbrPVCtrl, numbMidMb=nbrHandFkCtrl, numbEndMb=nbrFingers, subDvEndMb=nbrFingerFkCtrl)
    guide.createArm()


def tplArm_UI(uiFram, uiSide, uiFk, uiSk):
    mc.separator(h=5, st="in")
    mc.radioButtonGrp(uiSide, nrb=3, l='Side : ', la3=['None', 'Left', 'Right'], ct4=('left', 'left', 'left', 'left'), co4=(0, -100, -150, -205), on1="mc.radioButtonGrp('"+uiSide+"', e=True, bgc=[.7, .6, .1])", on2="mc.radioButtonGrp('"+uiSide+"', e=True, bgc=[.5, .2, .2])", on3="mc.radioButtonGrp('"+uiSide+"', e=True, bgc=[.2, .3, .5])", sl=2, bgc=[.5, .2, .2])
    mc.separator(h=5, st="in")
    mc.intFieldGrp('moduleCtrlClav_UI', numberOfFields=1, label='Clav FK ctrl :', cal=(1, 'left'), cat=(2, 'left', -40), value1=1, p=uiFram)
    mc.separator(h=5, st="in")
    mc.intFieldGrp('moduleSkClav_UI', numberOfFields=1, label='Clav SK ctrl :', cal=(1, 'left'), cat=(2, 'left', -40), value1=1, p=uiFram)
    mc.separator(h=5, st="in")
    mc.intFieldGrp(uiFk, numberOfFields=1, label='Arm FK ctrl :', cal=(1, 'left'), cat=(2, 'left', -40), value1=1, p=uiFram)
    mc.separator(h=5, st="in")
    mc.intFieldGrp(uiSk, numberOfFields=1, label='Arm SK joints :', cal=(1, 'left'), cat=(2, 'left', -40), value1=7, p=uiFram)
    mc.separator(h=5, st="in")
    mc.intFieldGrp('moduleCtrlPv_UI', numberOfFields=1, label='PVector :', cal=(1, 'left'), cat=(2, 'left', -40), value1=1, p=uiFram)
    mc.separator(h=5, st="in")
    mc.intFieldGrp('moduleCtrlHand_UI', numberOfFields=1, label='Hand FK ctrl :', cal=(1, 'left'), cat=(2, 'left', -40), value1=1, p=uiFram)
    mc.separator(h=5, st="in")
    mc.intFieldGrp('moduleCtrlFingers_UI', numberOfFields=1, label='Nbr Fingers :', cal=(1, 'left'), cat=(2, 'left', -40), value1=5, p=uiFram)
    mc.separator(h=5, st="in")
    mc.intFieldGrp('moduleCtrlPhalanges_UI', numberOfFields=1, label='Finger FK ctrl :', cal=(1, 'left'), cat=(2, 'left', -40), value1=3, p=uiFram)
    mc.separator(h=5, st="in")

########################################################################################################################
def tplLeg(side, nbrFkClav, nbrSkClav, nbrFkCtrl, nbrSk, nbrPVCtrl, nbrHandFkCtrl, nbrFingers, nbrFingerFkCtrl):
    from ellipse_rig.assets.characters import guide_leg
    reload(guide_leg)
    #guide = guide_leg.Leg(name='leg',side='L',selObj=mc.ls(sl=True),numb=1,numbSk=7,numbMidMb=1,numbEndMb=5) # old
    guide = guide_leg.Leg(name='leg', side=side, selObj=mc.ls(sl=True), numbStartSk=nbrSkClav, numbStartMb=nbrFkClav, numb=nbrFkCtrl, numbSk=nbrSk, numbPlV=nbrPVCtrl, numbMidMb=nbrHandFkCtrl, numbEndMb=nbrFingers, subDvEndMb=nbrFingerFkCtrl)
    guide.createLeg()

def tplLeg_UI(uiFram, uiSide, uiFk, uiSk):
    mc.separator(h=5, st="in")
    mc.radioButtonGrp(uiSide, nrb=3, l='Side : ', la3=['None', 'Left', 'Right'], ct4=('left', 'left', 'left', 'left'), co4=(0, -100, -150, -205), on1="mc.radioButtonGrp('"+uiSide+"', e=True, bgc=[.7, .6, .1])", on2="mc.radioButtonGrp('"+uiSide+"', e=True, bgc=[.5, .2, .2])", on3="mc.radioButtonGrp('"+uiSide+"', e=True, bgc=[.2, .3, .5])", sl=2, bgc=[.5, .2, .2])
    mc.separator(h=5, st="in")
    mc.intFieldGrp('moduleCtrlClav_UI', numberOfFields=1, label='Pelv FK ctrl :', cal=(1, 'left'), cat=(2, 'left', -40), value1=1, p=uiFram)
    mc.separator(h=5, st="in")
    mc.intFieldGrp('moduleSkClav_UI', numberOfFields=1, label='Pelv SK ctrl :', cal=(1, 'left'), cat=(2, 'left', -40), value1=1, p=uiFram)
    mc.separator(h=5, st="in")
    mc.intFieldGrp(uiFk, numberOfFields=1, label='Leg FK ctrl :', cal=(1, 'left'), cat=(2, 'left', -40), value1=1, p=uiFram)
    mc.separator(h=5, st="in")
    mc.intFieldGrp(uiSk, numberOfFields=1, label='Leg SK joints :', cal=(1, 'left'), cat=(2, 'left', -40), value1=7, p=uiFram)
    mc.separator(h=5, st="in")
    mc.intFieldGrp('moduleCtrlPv_UI', numberOfFields=1, label='PVector :', cal=(1, 'left'), cat=(2, 'left', -40), value1=1, p=uiFram)
    mc.separator(h=5, st="in")
    mc.intFieldGrp('moduleCtrlHand_UI', numberOfFields=1, label='Foot FK ctrl :', cal=(1, 'left'), cat=(2, 'left', -40), value1=1, p=uiFram)
    mc.separator(h=5, st="in")
    mc.intFieldGrp('moduleCtrlFingers_UI', numberOfFields=1, label='Nbr Toes :', cal=(1, 'left'), cat=(2, 'left', -40), value1=5, p=uiFram)
    mc.separator(h=5, st="in")
    mc.intFieldGrp('moduleCtrlPhalanges_UI', numberOfFields=1, label='Toe FK ctrl :', cal=(1, 'left'), cat=(2, 'left', -40), value1=3, p=uiFram)
    mc.separator(h=5, st="in")


########################################################################################################################
def tplHead(side, nbrFkCtrl, nbrSk):
    from ellipse_rig.assets.characters import guide_head
    reload(guide_head)
    guide = guide_head.Head(name='head',side=side,selObj=mc.ls(sl=True),numbNeck=nbrFkCtrl,numbSk=nbrSk) # instance class charGuide
    guide.createHead()

def tplNeck_UI(uiFram, uiSide, uiFk, uiSk):
    mc.separator(h=5, st="in")
    mc.radioButtonGrp(uiSide, nrb=3, l='Side : ', la3=['None', 'Left', 'Right'], ct4=('left', 'left', 'left', 'left'), co4=(0, -100, -150, -205), on1="mc.radioButtonGrp('"+uiSide+"', e=True, bgc=[.7, .6, .1])", on2="mc.radioButtonGrp('"+uiSide+"', e=True, bgc=[.5, .2, .2])", on3="mc.radioButtonGrp('"+uiSide+"', e=True, bgc=[.2, .3, .5])", sl=1, bgc=[.7, .6, .1])
    mc.separator(h=5, st="in")
    mc.intFieldGrp(uiFk, numberOfFields=1, label='FK ctrl :', cal=(1, 'left'), cat=(2, 'left', -80), value1=1, p=uiFram)
    mc.separator(h=5, st="in")
    mc.intFieldGrp(uiSk, numberOfFields=1, label='SK joints :', cal=(1, 'left'), cat=(2, 'left', -80), value1=1, p=uiFram)
    mc.separator(h=5, st="in")
########################################################################################################################

def tplEye(side, nbrFkCtrl, nbrFk):
    from ellipse_rig.assets.characters import guide_eyes
    reload(guide_eyes)
    guide = guide_eyes.Eyes(name='eye',side=side,selObj=mc.ls(sl=True),numb=nbrFkCtrl,numbSk=nbrFk) # instance class charGuide
    guide.createEyes()

def tplEye_UI(uiFram, uiSide, uiFk):
    mc.separator(h=5, st="in")
    mc.radioButtonGrp(uiSide, nrb=3, l='Side : ', la3=['None', 'Left', 'Right'], ct4=('left', 'left', 'left', 'left'), co4=(0, -100, -150, -205), on1="mc.radioButtonGrp('"+uiSide+"', e=True, bgc=[.7, .6, .1])", on2="mc.radioButtonGrp('"+uiSide+"', e=True, bgc=[.5, .2, .2])", on3="mc.radioButtonGrp('"+uiSide+"', e=True, bgc=[.2, .3, .5])", sl=2, bgc=[.5, .2, .2])
    mc.separator(h=5, st="in")
    mc.intFieldGrp(uiFk, numberOfFields=1, label='Nbr Eye :', cal=(1, 'left'), cat=(2, 'left', -80), value1=3, p=uiFram)
    mc.separator(h=5, st="in")
########################################################################################################################


def tplTail(side, nbrFkCtrl, nbrSk):
    from ellipse_rig.assets.characters import guide_tail
    reload(guide_tail)
    guide = guide_tail.Tail(name='tail',side=side,selObj=mc.ls(sl=True),numb=nbrFkCtrl,numbSk=nbrSk) # instance class charGuide
    guide.createTail()

def tplTail_UI(uiFram, uiSide, uiFk, uiSk):
    mc.separator(h=5, st="in")
    mc.radioButtonGrp(uiSide, nrb=3, l='Side : ', la3=['None', 'Left', 'Right'], ct4=('left', 'left', 'left', 'left'), co4=(0, -100, -150, -205), on1="mc.radioButtonGrp('"+uiSide+"', e=True, bgc=[.7, .6, .1])", on2="mc.radioButtonGrp('"+uiSide+"', e=True, bgc=[.5, .2, .2])", on3="mc.radioButtonGrp('"+uiSide+"', e=True, bgc=[.2, .3, .5])", sl=1, bgc=[.7, .6, .1])
    mc.separator(h=5, st="in")
    mc.intFieldGrp(uiFk, numberOfFields=1, label='FK/IK ctrl :', cal=(1, 'left'), cat=(2, 'left', -80), value1=3, p=uiFram)
    mc.separator(h=5, st="in")
    mc.intFieldGrp(uiSk, numberOfFields=1, label='SK joints :', cal=(1, 'left'), cat=(2, 'left', -80), value1=5, p=uiFram)
    mc.separator(h=5, st="in")

########################################################################################################################

def tplWing(side, nbrFeatherRow, nbrFeather, nbrFeatherFkCtrl):
    from ellipse_rig.assets.characters import guide_wing
    reload(guide_wing)
    guideW = guide_wing.Wing(name='wing',side=side,selObj=mc.ls(sl=True),numb=1,numbSk=1,nbFeathersbyLine=nbrFeather,offsetIk=(0,4,0),offsetT=(0,6.5,0),offsetR=(0,0,0), incVal=None)
    toto = guideW.createWing()
    mc.select(cl=True)
    mc.select(toto['lsIk'][0])

    if nbrFeatherRow > 0:
        from ellipse_rig.assets.characters import guide_featherPart
        reload(guide_featherPart)
        guideF = guide_featherPart.Feather(name='feather',side=side,selObj=mc.ls(sl=True),lsNbfk =nbrFeatherFkCtrl,numb=1,numbSk=1,offsetIk=(0,3,0),offsetT=(0,6.5,0),offsetR=(-90,0,0),countLines=None,countFeathers=None)
        guideF.createFeather()

def tplWing_UI(uiFram, uiFramAdd, uiSide, uiFeatherRows, uiFeathers, uiFeatherSk):
    mc.separator(h=5, st="in")
    mc.radioButtonGrp(uiSide, nrb=3, l='Side : ', la3=['None', 'Left', 'Right'], ct4=('left', 'left', 'left', 'left'), co4=(0, -100, -150, -205), on1="mc.radioButtonGrp('"+uiSide+"', e=True, bgc=[.7, .6, .1])", on2="mc.radioButtonGrp('"+uiSide+"', e=True, bgc=[.5, .2, .2])", on3="mc.radioButtonGrp('"+uiSide+"', e=True, bgc=[.2, .3, .5])", sl=2, bgc=[.5, .2, .2])
    mc.separator(h=5, st="in")
    #mc.intSlider(uiFeatherRows, min=0, max=10, value=0, step=1, cc=partial(tplFeathers_UI, uiFram, uiFramAdd, uiFeatherRows, uiFeathers, uiFeatherSk), p=uiFram)
    mc.intSliderGrp(uiFeatherRows, label='Feathers row', min=0, max=10, value=0, step=1, field=True, cc=partial(tplFeathers_UI, uiFram, uiFramAdd, uiFeatherRows, uiFeathers, uiFeatherSk), cl3=['left', 'left', 'left'], p=uiFram)
    mc.separator(h=5, st="in")
    mc.frameLayout(uiFramAdd, label='Feathers options:', bv=True, p=uiFram)
    mc.separator(h=5, st="in")
    mc.text(label='Feathers options row 1 :', align='left', fn='fixedWidthFont', bgc=[.4, .4, .4], en=False)
    mc.intFieldGrp(uiFeathers+'_1', numberOfFields=1, en=False, label='Nbr feathers:', cal=(1, 'left'), cat=(2, 'left', -60), value1=8, p=uiFramAdd)
    mc.intFieldGrp(uiFeatherSk+'_1', numberOfFields=1, en=False, label='Feather FK ctrl:', cal=(1, 'left'), cat=(2, 'left', -60), value1=3, p=uiFramAdd)



def tplFeathers_UI(uiFram, uiFramAdd, uiFeatherRows, uiFeathers, uiFeatherSk, *args):
    #nbrRows = mc.intSlider(uiFeatherRows, q=True, value=True)
    nbrRows = mc.intSliderGrp(uiFeatherRows, q=True, value=True)
    lChild = mc.frameLayout(uiFramAdd, q=True, ca=True) or []
    dicVal = {}
    if lChild:
        if not len(lChild)/2 == nbrRows:
            for child in lChild:
                type = mc.objectTypeUI(child)
                if type == 'rowGroupLayout':
                    dicVal[child] = mc.intFieldGrp(child, q=True, v1=True)
    mc.deleteUI(uiFramAdd)
    mc.frameLayout(uiFramAdd, label='Feathers options:', bv=True, p=uiFram)
    for row in range(1, nbrRows+1):
        mc.separator(h=5, st="in", ann='Row '+str(row)+' feathers:', p=uiFramAdd)
        mc.text(label='Feathers options row '+str(row)+' :', align='left', fn='fixedWidthFont', bgc=[.4, .4, .4])
        mc.intFieldGrp(uiFeathers+'_'+str(row), numberOfFields=1, en=True, label='Nbr feathers:', cal=(1, 'left'), cat=(2, 'left', -60), value1=8, p=uiFramAdd)
        mc.intFieldGrp(uiFeatherSk+'_'+str(row), numberOfFields=1, en=True, label='Feather FK ctrl:', cal=(1, 'left'), cat=(2, 'left', -60), value1=3, p=uiFramAdd)
    if dicVal:
        for field in dicVal.keys():
            if mc.intFieldGrp(field, ex=True):
                mc.intFieldGrp(field, e=True, value1=dicVal[field])
########################################################################################################################

def buildModuleTpl():
    btnTrigger = ''
    lBtnModules = ['btnSpineModule', 'btnArmModule', 'btnLegModule', 'btnNeckModule', 'btnEyeModule', 'btnTailModule', 'btnSnakeModule', 'btnWingModule']
    dicSide = {1:'', 2:'L', 3:'R'}
    side = dicSide[mc.radioButtonGrp('moduleSide_UI', q=True, sl=True)]
    for btn in lBtnModules:
        if round(mc.button(btn, q=True, bgc=True)[0], 1) == 0.3:
            btnTrigger = btn
    if btnTrigger:
        if btnTrigger == 'btnSpineModule':
            nbrFkCtrl = mc.intFieldGrp('moduleCtrlFk_UI', q=True, v1=True)
            nbrSk = mc.intFieldGrp('moduleSk_UI', q=True, v1=True)
            tplSpine(side, nbrFkCtrl, nbrSk)
            print 'spine generated',
        elif btnTrigger == 'btnArmModule':
            nbrFkClav = mc.intFieldGrp('moduleCtrlClav_UI', q=True, v1=True)
            nbrSkClav = mc.intFieldGrp('moduleSkClav_UI', q=True, v1=True)
            nbrFkCtrl = mc.intFieldGrp('moduleCtrlFk_UI', q=True, v1=True)
            nbrSk = mc.intFieldGrp('moduleSk_UI', q=True, v1=True)
            nbrPVCtrl = mc.intFieldGrp('moduleCtrlPv_UI', q=True, v1=True)
            nbrHandFkCtrl = mc.intFieldGrp('moduleCtrlHand_UI', q=True, v1=True)
            nbrFingers = mc.intFieldGrp('moduleCtrlFingers_UI', q=True, v1=True)
            nbrFingerFkCtrl = mc.intFieldGrp('moduleCtrlPhalanges_UI', q=True, v1=True)
            tplArm(side, nbrFkClav, nbrSkClav, nbrFkCtrl, nbrSk, nbrPVCtrl, nbrHandFkCtrl, nbrFingers, nbrFingerFkCtrl)
            print 'Arm generated'
        elif btnTrigger == 'btnLegModule':
            nbrFkClav = mc.intFieldGrp('moduleCtrlClav_UI', q=True, v1=True)
            nbrSkClav = mc.intFieldGrp('moduleSkClav_UI', q=True, v1=True)
            nbrFkCtrl = mc.intFieldGrp('moduleCtrlFk_UI', q=True, v1=True)
            nbrSk = mc.intFieldGrp('moduleSk_UI', q=True, v1=True)
            nbrPVCtrl = mc.intFieldGrp('moduleCtrlPv_UI', q=True, v1=True)
            nbrHandFkCtrl = mc.intFieldGrp('moduleCtrlHand_UI', q=True, v1=True)
            nbrFingers = mc.intFieldGrp('moduleCtrlFingers_UI', q=True, v1=True)
            nbrFingerFkCtrl = mc.intFieldGrp('moduleCtrlPhalanges_UI', q=True, v1=True)
            tplLeg(side, nbrFkClav, nbrSkClav, nbrFkCtrl, nbrSk, nbrPVCtrl, nbrHandFkCtrl, nbrFingers, nbrFingerFkCtrl)
            print 'Leg generated'
        elif btnTrigger == 'btnNeckModule':
            nbrFkCtrl = mc.intFieldGrp('moduleCtrlFk_UI', q=True, v1=True)
            nbrSk = mc.intFieldGrp('moduleSk_UI', q=True, v1=True)
            tplHead(side, nbrFkCtrl, nbrSk)
            print 'Neck generated'
        elif btnTrigger == 'btnEyeModule':
            nbrFkCtrl = mc.intFieldGrp('moduleCtrlFk_UI', q=True, v1=True)
            tplEye(side, nbrFkCtrl, 55)
            print 'Eye generated'
        elif btnTrigger == 'btnTailModule':
            nbrFkCtrl = mc.intFieldGrp('moduleCtrlFk_UI', q=True, v1=True)
            nbrSk = mc.intFieldGrp('moduleSk_UI', q=True, v1=True)
            tplTail(side, nbrFkCtrl, nbrSk)
            print 'tail generated'
        elif btnTrigger == 'btnWingModule':

            lOptionsAdd = mc.frameLayout('moduleFrameOptions_UI', q=True, ca=True) or []
            nbrFeather = []
            nbrFeatherFkCtrl = []
            if lOptionsAdd:
                dicAdds = {}
                for add in lOptionsAdd:
                    if mc.objectTypeUI(add) == 'frameLayout':
                        lItems = mc.frameLayout(add, q=True, ca=True) or []
                        if lItems:
                            lFields = []
                            for item in lItems:
                                if mc.objectTypeUI(item) == 'rowGroupLayout':
                                    lFields.append(item)
                            i = 0
                            for field in range(0, len(lFields)/2):
                                print lFields[i], lFields[i+1], i
                                dicAdds[field] = {mc.intFieldGrp(lFields[i], q=True, v1=True): mc.intFieldGrp(lFields[i+1], q=True, v1=True)}
                                nbrFeather.append(mc.intFieldGrp(lFields[i], q=True, v1=True))
                                nbrFeatherFkCtrl.append(mc.intFieldGrp(lFields[i+1], q=True, v1=True))
                                i += 2
            nbrFeatherRow = len(nbrFeather)
            tplWing(side, nbrFeatherRow, nbrFeather, nbrFeatherFkCtrl)
            print 'wing generated'
    else:
        print 'no module type seted',





########################################################################################################################
def tplSym():
    from ellipse_rig.library import lib_dataNodes
    reload(lib_dataNodes)
    tpl = mc.ls(sl=True)[0]
    dataNode = lib_dataNodes.getTplDataNodeFromTpl(tpl)
    side = mc.getAttr(dataNode+'.side')
    from ellipse_rig.assets.characters import guide_tool
    reload(guide_tool)

    sym = guide_tool.symCtr(side=side) #instance class charGuide

########################################################################################################################
def tplReparent(lNodes=mc.ls(sl=True)):
    from ellipse_rig.assets.characters import guide_tool
    reload(guide_tool)
    guide_tool.parentModuleTo(lNodes)




