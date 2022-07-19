import maya.cmds as mc
import os
from functools import partial
from ellipse_rig.icons import ic_datas
reload(ic_datas)


def getIconsPath():
    pathDir = ic_datas.getIconsPath()
    pathIcon = os.path.join(pathDir, 'ic_facialTool')
    return pathIcon

def crtButton_UI(name='', label='empty', colors=[0.35, 0.35, 0.35], cmmd='print "to do"', h=25, w=200, tip='', ic=''):
    if name:
        btn = mc.button(name, l=label, h=h, w=w, bgc=colors, c=cmmd, ann=tip)
        return btn
    else:
        btn = mc.button(l=label, h=h, w=w, bgc=colors, c=cmmd, ann=tip)
        return btn

# TO DO  custom attrs loader########################################################################################

def getCrtlAttr(framLay):
    lCtrl = mc.ls(sl=True)
    lAttrs = []
    for ctrl in lCtrl:
        getAttrs = mc.listAttr(ctrl, k=True)
        for attr in getAttrs:
            if not attr in lAttrs:
                lAttrs.append(attr)
    lAttrsUI(lAttrs, framLay)


def lAttrsUI(lItems, framLay):
    nWin = 'lAttrsWin_UI'
    nPan = 'lAttrsWin_UImasterPan'
    if mc.window(nWin, ex=True, q=True):
        mc.deleteUI(nWin, window=True)
    win_lAttrs_UI = mc.window(nWin, t=nWin, tlb=True)
    rowA = mc.columnLayout(adj=True)
    itemsList = mc.textScrollList('suce28', ams=True)
    mc.button(l='load attrs', c='loadCrtlAttr(' + str(itemsList) + ', ' + str(framLay) + ', ' + str(lItems) + ')')
    # mc.button(l='load attrs', c='loadCrtlAttr(itemsList, framLay, lItems)')
    mc.showWindow(win_lAttrs_UI)
    mc.textScrollList(itemsList, e=True, a=lItems)

def loadCrtlAttr(listCtrl='', framLay='', lCtrl=[]):
    lAttrs = mc.textScrollList(listCtrl, q=True, si=True)
    for ctrl in lCtrl:
        for attr in lAttrs:
            print ctrl + '.' + attr
# END  TO DO###################################################################################



# CLAMP#########################################################################################
def toogleClampSlider(slider, chkBox, *args, **kwargs):
    val = mc.checkBox(chkBox, q=True, v=True)
    min = mc.attrFieldSliderGrp(slider, q=True, min=True)
    max = mc.attrFieldSliderGrp(slider, q=True, max=True)
    if val == False:
        mc.attrFieldSliderGrp(slider, e=True, min=min * 2, max=max * 2)
    elif val == True:
        mc.attrFieldSliderGrp(slider, e=True, min=min / 2, max=max / 2)


def toogleClampSliders(uiFather, chkBoxAll, *args, **kwargs):
    val = mc.checkBox(chkBoxAll, q=True, v=True)
    lChild_UI = mc.columnLayout(uiFather, q=True, ca=True) or []
    if lChild_UI:
        lRowLay = mc.lsUI(lChild_UI, type='rowLayout') or []
        if lRowLay:
            for rowLay in lRowLay:
                lCtrl_UI = mc.rowLayout(rowLay, q=True, ca=True) or []
                if lCtrl_UI:
                    slider = ''
                    chkBox = ''
                    for ctrl_UI in lCtrl_UI:
                        if mc.objectTypeUI(ctrl_UI, i='checkBox'):
                            if mc.checkBox(ctrl_UI, q=True, l=True) == 'Clamp':
                                chkBox = ctrl_UI
                                mc.checkBox(chkBox, e=True, v=val)
                        elif mc.objectTypeUI(ctrl_UI, i='rowGroupLayout'):
                            slider = ctrl_UI
                    if slider and chkBox:
                        toogleClampSlider(slider, chkBox)


##################################################################################################
# RESET############################################################################################
def resetSlider(slider, *args, **kwargs):
    if mc.objectTypeUI(slider, i='rowGroupLayout'):
        attr = mc.attrFieldSliderGrp(slider, q=True, at=True)
        mc.setAttr(attr, 0.0)


def resetSliders(uiFather, *args, **kwargs):
    lRowLay = mc.columnLayout(uiFather, q=True, ca=True) or []
    if lRowLay:
        for rowLay in lRowLay:
            lChilds = mc.rowLayout(rowLay, q=True, ca=True) or []
            if lChilds:
                for child in lChilds:
                    if mc.objectTypeUI(child, i='rowGroupLayout'):
                        attr = mc.attrFieldSliderGrp(child, q=True, at=True)
                        mc.setAttr(attr, 0.0)


##################################################################################################
# LOAD SLIDERS#####################################################################################
def loadChanDrivers(node, uiFather, suff='_chanDriver_UI', lAttr=[], *args, **kwargs):
    lSliders = mc.lsUI(type='attrFieldSliderGrp') or []
    if mc.objExists(node):
        if not lAttr:
            lAttr = mc.listAttr(node, ud=True, k=True) or []
        if lAttr:
            for attr in lAttr:
                if attr + suff in lSliders:
                    rowLay = mc.attrFieldSliderGrp(attr + suff, q=True, parent=True)
                    lCtrl_UI = mc.rowLayout(rowLay, q=True, ca=True) or []
                    if lCtrl_UI:
                        mc.deleteUI(lCtrl_UI)
                    mc.deleteUI(rowLay)
                min = mc.attributeQuery(attr, n=node, min=True)[0]
                max = mc.attributeQuery(attr, n=node, max=True)[0]
                rowLay = mc.rowLayout(nc=4, adj=2, p=uiFather)
                sliderIsolateChkBox = mc.checkBox('isolate_'+node+'_'+attr + suff, l='', v=False)
                slideCtrl = mc.attrFieldSliderGrp(attr + suff, min=min / 2, max=max / 2, at=node + '.' + attr)
                sliderResetBtn = crtButton_UI(label='reset', colors=[0.35, 0.35, 0.35], w=40, h=15,
                                              cmmd=partial(resetSlider, slideCtrl))
                sliderClampChkBox = mc.checkBox(label='Clamp', v=True)
                mc.checkBox(sliderClampChkBox, e=True, cc=partial(toogleClampSlider, slideCtrl, sliderClampChkBox))

#################################################################################################
#ISOLATE SLIDERS#################################################################################
def isolateChanDriver(uiFather, *args, **kwargs):
    lChild_UI = mc.columnLayout(uiFather, q=True, ca=True) or []
    if lChild_UI:
        lRowLay = mc.lsUI(lChild_UI, type='rowLayout') or []
        if lRowLay:
            for rowLay in lRowLay:
                lCtrl_UI = mc.rowLayout(rowLay, q=True, ca=True) or []
                if lCtrl_UI:
                    for ctrl_UI in lCtrl_UI:
                        try:
                            if mc.objectTypeUI(ctrl_UI, i='checkBox'):
                                if ctrl_UI.startswith('isolate_'):
                                    val = mc.checkBox(ctrl_UI, q=True, v=True)
                                    if val == False:
                                        rowLay = mc.checkBox(ctrl_UI, q=True, parent=True)
                                        lChild_UI = mc.rowLayout(rowLay, q=True, ca=True) or []
                                        if lChild_UI:
                                            mc.deleteUI(lChild_UI)
                                        mc.deleteUI(rowLay)
                        except:
                            pass


#################################################################################################
def chanSliders_UI(father, *args, **kwargs):
    iconsPath = getIconsPath()
    nSlidersLay = 'tufistule'
    nUIFather = 'sucee'
    mc.scrollLayout(nSlidersLay, horizontalScrollBarThickness=1, verticalScrollBarThickness=1, cr=True, p=father)
    mc.frameLayout('titi', l='Sculpts sliders', cll=True)
    mc.columnLayout(adj=True)
    mc.rowLayout(nc=4, adj=2)
    #slidersIsolateBtn = crtButton_UI(label='Isolate', colors=[0.35, 0.35, 0.35], w=20, h=23)
    slidersIsolateBtn = mc.iconTextButton(label='Isolate', style='iconOnly', image1=os.path.join(iconsPath, 'ic_isolate.jpg'))


    mc.button(l='Load Sliders', c=partial(loadChanDrivers, 'c_targets', nUIFather, '_chanDriver_UI'))
    slidersResetBtn = crtButton_UI(label='Reset', colors=[0.35, 0.35, 0.35], w=40, h=23)
    clampAllChkBox = mc.checkBox(label='Clamp', v=True)
    mc.setParent('..')
    mc.setParent('..')
    mc.separator(h=7.5, st='in')
    uiFather = mc.columnLayout(nUIFather, adj=True)
    ###################################
    popTrgtSliders = mc.popupMenu()
    mc.menuItem(l='trgt', cb=True)
    mc.menuItem(l='cor', cb=True)
    mc.menuItem(l='mix', cb=True)
    mc.menuItem(l='comb', cb=True)
    ##################################
    #mc.button(slidersIsolateBtn, e=True, c=partial(isolateChanDriver, uiFather))
    mc.iconTextButton(slidersIsolateBtn, e=True, c=partial(isolateChanDriver, uiFather))
    mc.checkBox(clampAllChkBox, e=True, cc=partial(toogleClampSliders, uiFather, clampAllChkBox))
    mc.button(slidersResetBtn, e=True, c=partial(resetSliders, uiFather))


def SMAB_facialSlidersTool_ui(*args, **kwargs):
    nWin = 'UI_facialSlidersTool'
    nPan = 'MASTER_facialSlidersTool'
    version = '2.0'

    if mc.window(nWin, ex=True, q=True):
        mc.deleteUI(nWin, window=True)
    win_facialSlidersTool_UI = mc.window(nWin, t='facial sliders ' + version)

    panMaster = mc.paneLayout(nWin + 'MasterPan', cn='vertical2')
    chanSliders_UI(panMaster)
    mc.showWindow(win_facialSlidersTool_UI)


#SMAB_facialSlidersTool_ui()