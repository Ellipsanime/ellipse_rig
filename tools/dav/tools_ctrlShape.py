import maya.cmds as mc
import os
from functools import partial
from ellipse_rig.library import lib_shapes
reload(lib_shapes)


def listSel():
    return mc.ls(sl=True, fl=True)

def genShp(type, aim):
    crv = lib_shapes.shp_form(type,"Index","red",name=None)
    return crv

def posShp(getSel, type, aim, *args):
    lObj = []
    if isinstance(getSel, list):
        lObj = getSel
    else:
        lObj = getSel()
    if lObj:
        for obj in lObj:
            shp = genShp(type, aim)
            mc.delete(mc.parentConstraint(obj, shp, mo=False))
    else:
        shp = genShp(type, aim)



    #bBox = lib_shapes.bounding_box_utils(lObj,size=None,delete=True)
    #lib_shapes.parent_shp(lsObj=lObj, lsShp=[type], delBaseShp=None, colorType="Index", color="red",rotShp=(0, 0, 0),bound=bBox)
    #lib_shapes.shape_size(shp,rotShp=(0, 0, 0),bound=bBox)


def parentShpToCtrl(getSel, chkCtrl, add, inPlace):
    lNodes = []
    if isinstance(getSel, list):
        lNodes = getSel
    else:
        lNodes = getSel()
    lCtrl = []
    lShp = lNodes
    for node in lNodes:
        if mc.attributeQuery('nodeType', n=node, ex=True):
            if mc.getAttr(node+'.nodeType') == 'control':
                lCtrl.append(node)
    for ctrl in lCtrl:
        lShp.remove(ctrl)

    if not lCtrl:
        mc.warning('you need to select at least one ctrl : does your selected ctrl is/are in a CG?')
    else:
        if not lShp:
            mc.warning('no shape to copy was found in your selection')
        else:
            for ctrl in lCtrl:
                chkShp = mc.listRelatives(ctrl, s=True) or []
                if chkShp:
                    for oldShp in chkShp:
                        if not mc.attributeQuery('nodeType', n=oldShp, ex=True):
                            try:
                                mc.delete(oldShp)
                            except:
                                mc.setAttr(oldShp+'.v', False)
                                mc.select(oldShp)
                                lib_pipe.addFlagAttr("deleteMe", 1)
                i = 1
                for shp in lShp:
                    lCrv = mc.listRelatives(shp, s=True) or []
                    if lCrv:
                        if mc.attributeQuery('nodeType', n=lCrv[0], ex=True):
                            if mc.getAttr(node+'.nodeType') == 'control':
                                mc.parent(lCrv[0], ctrl, add=True, s=True)

                        else:
                            tmp = mc.duplicate(shp, n=shp+'Tmp')[0]
                            mc.parent(tmp, ctrl)
                            mc.makeIdentity(tmp, a=True)
                            mc.delete(mc.parentConstraint(ctrl, tmp, mo=False))
                            mc.makeIdentity(tmp, a=True)
                            mc.parent(tmp, world=True)
                            lCrv = mc.listRelatives(tmp, s=True)
                            for crv in lCrv:
                                mc.parent(crv, ctrl, r=True, s=True)
                                mc.rename(crv, ctrl+'Shape'+str(i))
                                i += 1
                            mc.delete(tmp)
                            i += 1

#parentShpToCtrl(mc.ls(sl=True))

def crtShapes_UI():
    pathDir = os.path.dirname(__file__)
    pathParent = os.path.split(os.path.split(pathDir)[0])[0]
    pathIcon = os.path.join(pathParent, 'icons', 'ic_ctrlShapes')
    nWin = 'SMF_crtShapesTools'
    nPan = 'CTRLSHAPES_MASTER_pan'
    version ='1.1'
    if mc.window(nWin, ex=True, q=True):
        mc.deleteUI(nWin, window=True)
    winSMF_publishTool_UI = mc.window(nWin, t='shapes tool'+version, tlb=True)

    ######
    pan = mc.paneLayout(nPan, cn='top3', w=300)
    ######

    mc.frameLayout(l='Utils')
    mc.columnLayout()
    mc.rowLayout(nc=2, adj=2)
    mc.radioButtonGrp('rButtonAxe', nrb=3, l='type : ', la3=['X', 'Y', 'Z'],
                      ct4=('left', 'left', 'left', 'left'), co4=(5, -100, -150, -205))
    mc.radioButtonGrp('rButtonAxe', e=True, select=1)
    mc.button(l='Reorient')
    mc.setParent('..')
    mc.rowLayout(nc=2, adj=2)
    mc.button(l='Add to')
    mc.button(l='Replace')

    mc.setParent('..')
    mc.rowLayout(nc=2)
    mc.button(l='Delete')
    mc.button(l='Store')

    mc.setParent('..')
    mc.setParent('..')
    mc.setParent('..')

    mc.columnLayout(adj=True, w=225)
    mc.rowLayout(nc=4)

    mc.button(l='IK', h=75, w=75, c=partial(posShp, listSel, "square", "Y"))
    mc.button(l='rigAdd', h=75, w=75, c=partial(posShp, listSel, "rigAdd", "Y"))
    mc.button(l='IK 3D', h=75, w=75, c=partial(posShp, listSel, "cube", "Y"))
    mc.button(l='FK', h=75, w=75, c=partial(posShp, listSel, "circle", "Y"))

    mc.setParent('..')
    mc.rowLayout(nc=4)
    mc.button(l='pinSimple', h=75, w=75, c=partial(posShp, listSel, "pinSimple", "Y"))
    mc.button(l='fly', h=75, w=75, c=partial(posShp, listSel, "fly", "Y"))
    mc.button(l='pinQuadro', h=75, w=75, c=partial(posShp, listSel, "pinQuadro", "Y"))
    mc.button(l='Boulette', h=75, w=75, c=partial(posShp, listSel, "sphere", "Y"))

    mc.setParent('..')
    mc.setParent('..')
    mc.frameLayout(l='ALL', cll=True)
    mc.rowLayout(nc=4)
    mc.button(l='arrowQuadro2', h=75, w=75, c=partial(posShp, listSel, "arrowQuadro2", "Y"))
    mc.button(l='arrowSingle', h=75, w=75, c=partial(posShp, listSel, "arrowSingle", "Y"))
    mc.button(l='arrowOctogone', h=75, w=75, c=partial(posShp, listSel, "arrowOctogone", "Y"))
    mc.button(l='boomrang', h=75, w=75, c=partial(posShp, listSel, "boomrang", "Y"))

    mc.setParent('..')
    mc.rowLayout(nc=4)
    mc.button(l='star', h=75, w=75, c=partial(posShp, listSel, "star", "Y"))
    mc.button(l='pinDouble', h=75, w=75, c=partial(posShp, listSel, "pinDouble", "Y"))
    #mc.button(l='arrowQuadroBump', h=75, w=75, c=partial(posShp, listSel, "arrowQuadroBump", "Y"))
    mc.iconTextButton(style='iconOnly', image1=pathIcon+r'\toto.jpg', label='arrowQuadroBump', w=80, h=80, c=partial(posShp, listSel, "arrowQuadroBump", "Y"))
    mc.button(l='arrowSingle2', h=75, w=75, c=partial(posShp, listSel, "arrowSingle2", "Y"))
    mc.setParent ('..')
    mc.rowLayout(nc=4)
    mc.button(l='Global', h=75, w=75, c=partial(posShp, listSel, "squareRounded", 'Y'))
    mc.button(l='arrowLine', h=75, w=75, c=partial(posShp, listSel, "arrowLine", 'Y'))
    mc.button(l='circleArrow', h=75, w=75, c=partial(posShp, listSel, "circleArrow", 'Y'))
    mc.button(l='cross', h=75, w=75, c=partial(posShp, listSel, "cross", 'Y'))

    mc.setParent ('..')
    mc.rowLayout(nc=4)
    mc.button(l='arrowDouble', h=75, w=75, c=partial(posShp, listSel, "arrowDouble", 'Y'))
    mc.button(l='arrowSingleCrv', h=75, w=75)

    mc.button(l='arrowDouble2', h=75, w=75, c=partial(posShp, listSel, "arrowDouble2", 'Y'))
    mc.button(l='Switch', h=75, w=75, c=partial(posShp, listSel, "empty", 'Y'))
    mc.setParent ('..')
    mc.rowLayout(nc=4)

    mc.button(l='arrowDoubleCrv', h=75, w=75, c=partial(posShp, listSel, "arrowDoubleCrv", 'Y'))
    mc.button(l='triangle', h=75, w=75, c=partial(posShp, listSel, "triangle", 'Y'))
    mc.button(l='arrowSingleCrv2', h=75, w=75, c=partial(posShp, listSel, "arrowSingleCrv2", 'Y'))
    mc.button(l='line', h=75, w=75, c=partial(posShp, listSel, "line", 'Y'))
    mc.setParent ('..')
    mc.rowLayout(nc=4)

    mc.button(l='circleArrow4', h=75, w=75, c=partial(posShp, listSel, "circleArrow4", 'Y'))
    mc.button(l='pyramide', h=75, w=75, c=partial(posShp, listSel, "pyramide", 'Y'))
    mc.button(l='arrowDoubleCrv2', h=75, w=75, c=partial(posShp, listSel, "arrowDoubleCrv2", 'Y'))

    mc.button(l='roll', h=75, w=75, c=partial(posShp, listSel, "roll", 'Y'))
    mc.setParent ('..')
    mc.rowLayout(nc=4)
    mc.button(l='arrowQuadro', h=75, w=75, c=partial(posShp, listSel, "arrowQuadro", 'Y'))
    mc.button(l='circleDemi', h=75, w=75, c=partial(posShp, listSel, "circleDemi", 'Y'))
    mc.button(l='crossLine', h=75, w=75, c=partial(posShp, listSel, "crossLine", 'Y'))
    mc.button(l='arrowDouble3', h=75, w=75, c=partial(posShp, listSel, "arrowDouble3", 'Y'))
    mc.setParent('..')
    mc.rowLayout(nc=3)
    mc.button(l='pyramide2', h=75, w=75, c=partial(posShp, listSel, "pyramide2", 'Y'))
    mc.button(l='arrowSingleCrv', h=75, w=75, c=partial(posShp, listSel, "arrowSingleCrv", 'Y'))
    mc.button(l='crossArrow', h=75, w=75, c=partial(posShp, listSel, "crossArrow", 'Y'))






    mc.showWindow(winSMF_publishTool_UI)
#crtShapes_UI()
