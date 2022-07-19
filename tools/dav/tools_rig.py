
import maya.cmds as mc
from ellipse_rig import buildRig
from ellipse_rig.library import lib_pipe, lib_deformers
reload(buildRig)
reload(lib_pipe)
reload(lib_deformers)


def parentModule(lNodes):
    father = lNodes[-1]
    lNodes.remove(father)
    for child in lNodes:
        anchor = mc.listRelatives(child, p=True)[0]
        lCnst = mc.listConnections(anchor, type = 'parentConstraint', d=True) or []
        if lCnst:
            mc.delete(lCnst[0])
        cnst = mc.parentConstraint(father, anchor, mo=True)[0]
        if not mc.attributeQuery('driver', n=anchor, ex=True):
            mc.addAttr(cnst, ln='driver', dt="string")
        if not mc.attributeQuery('driven', n=cnst, ex=True):
            mc.addAttr(cnst, ln='driven', dt="string")
        mc.connectAttr(father + '.message', cnst + '.driver', f=True)
        mc.connectAttr(child + '.message', cnst + '.driven', f=True)
        dataNode = mc.getAttr(child+'.infPart')
        id = mc.getAttr(dataNode+'.masterTpl', s=True)
        mc.setAttr(dataNode+'.masterTpl['+str(id)+']', child, type='string')
        print 'SUCCES:', child, 'reparented to', father
#parentModule(mc.ls(sl=True))


def loadFacial(path = r'T:\03_FAB\00_ASSETS\STP\BNK\facialTpl\wip\MAYA\SMF_STP_LibFacial_tpl_v001_001.ma'):
    father = mc.ls(sl=True) or []
    if not len(father) == 1:
        mc.warning('select the father tpl')
        return
    if not mc.attributeQuery('infPart', n=father[0], ex=True):
        mc.warning('select a valide tpl to parent')
        return
    dtNode = mc.getAttr(father[0]+'.infPart')
    mc.file(path, r=True, ns='FACE')
    mc.connectAttr(dtNode+'.children', 'FACE:tplInfo_face_1.parent', f=True)
#loadFacial(path = r'T:\90_TEAM_SHARE\03_FAB\00_ASSETS\02_RIG\05_LIBS\01_CHARS\LIB_FACIAL\SMF_RIG_LibFacial_v001_001.ma')


def smfRigTool_ui():
    nWin = 'SMF_toolsRig'
    nPan = 'MASTER_panRig'
    version ='1.1'
    if mc.window(nWin, ex=True, q=True):
        mc.deleteUI(nWin, window=True)
    winSMF_toolsRig_UI = mc.window(nWin, t='rigging tools'+version, tlb=True)

    mBar = mc.menuBarLayout('mBar_toolsRig')
    mc.menu(l='Tools')
    mc.menuItem(l='tool', c='')
    mc.separator(h=2)
    ######
    pan = mc.paneLayout(nPan, cn='vertical3')
    ######
    mc.columnLayout(adj=True, w=225)
    mc.separator(h=7.5, st='in')
    mc.frameLayout(l='TEMPLATE', cll=True)
    mc.rowLayout(nc=2, adj=2)
    mc.frameLayout(l='Sep Tools', cll=True)
    mc.rowLayout(nc=2, adj=1)
    nTrgtType = mc.optionMenu('sepZone', label='face zone  :')
    dicTrgt = lib_names.trgtNames()
    mc.menuItem( label='None')
    for key in sorted(dicTrgt.keys()):
        mc.menuItem(label=key)

    mc.setParent('..')
    mc.rowLayout(nc=1, adj=1)
    mc.button(l='BUILD RIG', bgc=[.25,.2,.5], h=28, w=230, c='tools_characters.buildRig.doBuildRig(cleanScene = True, doCg = True, linkMirror=True, connMenuHideGrp=True, mathcIkFk=True, pipe=True)')
    mc.setParent('..')
    mc.separator(h=7.5, st='in')
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='GEN EXP', bgc=[.25,.2,.5], h=28, w=230, c='tools_characters.lib_pipe.genExp(nToKeep=[":RIG", ":MOD", ":FUR"], nToDel=[''])')
    mc.button(l='GEN ANI', bgc=[.25,.2,.5], h=28, w=230, c='tools_characters.lib_pipe.genVanim(nToKeep=[":RIG", ":MOD", ":FUR"], nToDel=[''])')
    mc.setParent('..')

    mc.columnLayout('zezettelol', adj=True, w=225)
    mc.separator(h=7.5, st='in')
    mc.frameLayout(l='FACIALE SEP', cll=True)
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='LOAD TRGT   ', bgc=[.25,.2,.5], h=28, w=230, c='tools_characters.loadTRGT()')
    mc.button(l='UPDATE TRGT   ', bgc=[.25,.2,.5], h=28, w=230, c='print "smab"')

    mc.setParent('..')
    mc.separator(h=7.5, st='in')
    mc.rowLayout(nc=2, adj=1)
    nTrgtType = mc.optionMenu('sepZone', label='face zone  :')
    mc.menuItem( label='None')
    mc.menuItem( label='Cheeks')
    mc.menuItem( label='Eyebrows')
    mc.menuItem( label='Eyelids')
    mc.menuItem( label='Jaw')
    mc.menuItem( label='Lips')
    mc.menuItem( label='Mouth')
    mc.menuItem( label='Nose')


    nTrgtType = mc.optionMenu('sepType', label='separation type  :')
    mc.menuItem( label='None')
    mc.menuItem( label='Left')
    mc.menuItem( label='Rigt')
    mc.menuItem( label='Middle')
    mc.menuItem( label='Up')
    mc.menuItem( label='Down')
    mc.menuItem( label='Ext')
    mc.menuItem( label='Int')
    mc.menuItem( label='Corner')

    mc.setParent('..')
    mc.rowLayout(nc=2, adj=1)
    mc.button(l='ADD SEP', bgc=[.25,.2,.5], h=28, w=230, c='tools_characters.buildSep(mc.ls(sl=True), [mc.optionMenu("sepZone", q=True, v=True)], [mc.optionMenu("sepType", q=True, v=True)])')


    mc.showWindow(winSMF_toolsRig_UI)
#smfCharactersTool_ui()
