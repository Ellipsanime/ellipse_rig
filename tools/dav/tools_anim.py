import maya .cmds as mc


#CORRECTIVES SHAPES (chara in pose)#GEN TARGETS###############################################################################################################################################
def exctractPose(lMsh):
    lCtrl = []
    if not mc.objExists('SHP'):
        mc.createNode('transform', n='SHP')
    dicCtrlPos = {}
    lObj = mc.ls('*.nodeType', r=True)
    for obj in lObj:
        if mc.getAttr(obj) == 'control':
            lCtrl.append(obj.split('.')[0])
        if lCtrl:
            for ctrl in lCtrl:
                if not ctrl in dicCtrlPos.keys():
                    dicCtrlPos[ctrl] = {}
                lAttrs = mc.listAttr(ctrl, k=True)
                for attr in lAttrs:
                    if not '.' in attr:
                        if  not mc.attributeQuery(attr, n=ctrl, ch=True):
                            val = mc.getAttr(ctrl+'.'+attr)
                            dicCtrlPos[ctrl][attr] = val
    for msh in lMsh:
        clearName = msh
        if ':' in msh:
            clearName = msh.split(':')[-1]
        dupName = 'shp'+clearName[len(clearName.split('_')[0]):]
        dupMsh = mc.duplicate(msh, n=dupName)[0]
        mc.parent(dupMsh, 'SHP')
        mc.addAttr(dupMsh, ln='notes', dt='string')
        mc.setAttr(dupMsh+'.notes', dicCtrlPos, type='string')
        mc.setAttr(dupMsh+'.notes', dicCtrlPos, type='string', lock=True)
# exctractPose(mc.ls(sl=True))
########################################################################


def smfAnimTool_ui():
    nWin = 'SMF_aniTool'
    nPan = 'MASTER_panAni'
    version ='  1.1'
    if mc.window(nWin, ex=True, q=True):
        mc.deleteUI(nWin, window=True)
    winSMF_animTool_UI = mc.window(nWin, t='Larsouille   '+version, tlb=True)


    mBar = mc.menuBarLayout('mBar')
    mc.menu(l='Tools')
    mc.menuItem(l='tools_Fur', c='tools_publish.loadFurTools()')
    mc.menuItem(divider=True)
    mc.menuItem(l='tools_Facial', c='tools_publish.tools_facialShapes.smfBlendShapesTool_ui()')
    mc.menuItem(divider=True)
    mc.menuItem(l='tools_Rig', c='tools_publish.tools_characters.smfCharactersTool_ui()')
    mc.menuItem(divider=True)
    mc.menuItem(l='tools_Uv', c='print "to do"')
    mc.menuItem(divider=True)
    mc.menuItem(l='tools_Ani', c='print "tools_publish.tools_anim.smfAnimTool_ui()"')
    mc.separator(h=2)

    ######
    pan = mc.paneLayout(nPan, cn='vertical3')
    ######
    mc.columnLayout(adj=True, w=225)

    mc.rowLayout(nc=1, adj=1)
    mc.button(l='extract shape', h=28, w=130, c='tools_anim.exctractPose(mc.ls(sl=True))')


    mc.showWindow(winSMF_animTool_UI)
#smfAnimTool_ui()
###################################################################


#dkAnim######################################

def getAnimCrv():
    lAniCrv = mc.ls(type='animCurve')
    lAniKey = []
    for crv in lAniCrv:
        lConn = mc.listConnections(crv, s=True, d=False) or []
        if not lConn:
            lAniKey.append(crv)
    return lAniKey

#getAnimCrv()