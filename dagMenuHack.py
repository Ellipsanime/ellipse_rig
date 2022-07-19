import sys
import os
import os.path as osp
import maya.cmds as mc
import maya.mel as mel
from functools import partial


#customPath = 'T:\\90_TEAM_SHARE\\00_PROGRAMMATION\\maya\\tech_stp\\autoRigWip\\foundation_rig'
#customPath = 'C:\\STUFF'
srcDgMenuHackPath = os.path.realpath(__file__)
dgMenuHackPath = srcDgMenuHackPath.replace(srcDgMenuHackPath.split('ellipse_rig')[-1], '')
sys.path.append(dgMenuHackPath)
import dagMenuHack
reload(dagMenuHack)

# ==========================================================================
# show at top
# ==========================================================================

cb = mel.eval('global string $gChannelBoxName; $temp=$gChannelBoxName;')
if cb:
    mc.channelBox(cb, e=True, cat=False)

# ==========================================================================
# hack menu
# ==========================================================================

mel.eval('catchQuiet(dagMenuProc("",""))')

mayapath = osp.dirname(osp.dirname(sys.argv[0]))
path = osp.join(mayapath, 'scripts/others/dagMenuProc.mel')
if not os.path.isfile(path) and 'MAYA_LOCATION' in os.environ:
    mayapath = os.environ['MAYA_LOCATION']
    path = osp.join(mayapath, 'scripts/others/dagMenuProc.mel')

f = open(path)
lines = f.readlines()
f.close()

for line in lines:
    if 'global proc dagMenuProc' in line:
        i = lines.index(line)
        break


toolUser = 'ani'
#toolUser = 'rig'

if dgMenuHackPath in ['T:\\90_TEAM_SHARE\\00_PROGRAMMATION\\maya\\tech_stp\\autoRigWip\\foundation_rig', 'C:\\STUFF', 'R:\\PIPELINE\\ellipse_rig\\source\\ellipse_rig']:
    toolUser = 'rig'

cmd = """
string $selCtrl[] = `ls -selection`;
if (attributeExists("nodeType", $object) == 1 && getAttr($object + ".nodeType") == "control"){
    python("from dagMenuHack import rigMenu");
    python("rigMenu('" + $parent + "', '" + $object + "')");
} else if (attributeExists("rigMenu", $object) == 1 && getAttr($object + ".rigMenu") == 1){
    python("from dagMenuHack import rigMenu");
    python("rigMenu('" + $parent + "', '" + $object + "')");
}else if (size($selCtrl) > 0){
    if (attributeExists("nodeType", $selCtrl[0]) == 1 && getAttr($selCtrl[0] + ".nodeType") == "control"){
        python("from dagMenuHack import rigMenu");
        python("rigMenu('" + $parent + "', '" + $selCtrl[0] + "')");
        }

} else {
"""

if toolUser == 'rig':
    cmd = """
    if (attributeExists("nodeType", $object) == 1 && getAttr($object + ".nodeType") == "control"){
        python("from dagMenuHack import rigMenu");
        python("rigMenu('" + $parent + "', '" + $object + "')");
    } else if (attributeExists("rigMenu", $object) == 1 && getAttr($object + ".rigMenu") == 1){
        python("from dagMenuHack import rigMenu");
        python("rigMenu('" + $parent + "', '" + $object + "')");
    } else {
    """

lines.insert(i + 2, cmd)
lines.append('}\n')
dagMenuProc = ''.join(lines)

mel.eval(dagMenuProc)


def rigMenu(menu, node):
    # init
    sel = mc.ls(sl=True) or []
    #
    # get cgs and parent cgs
    cgs = getControlGroups(node)
    all_cgs = cgs
    for cg in cgs:
        parents = getControlGroupParents(cg)
        for p in parents:
            if p not in all_cgs:
                all_cgs.append(p)
    cg_all = all_cgs[-1]
    #
    # get master parent
    masterParent = None
    parents = mc.listRelatives(node, p=True, f=True) or []
    if parents and mc.objExists(parents[0].split('|')[1]):
            masterParent = parents[0].split('|')[1]
    #
    # get rig group

    rigGroup = None
    if mc.attributeQuery('rigGroup', n=cg_all, ex=True):
        rigs = mc.listConnections(cg_all + '.rigGroup', s=True, d=False) or []
        if rigs:
            rigGroup = rigs[0]
    #
    # object name
    mc.menuItem(label=node, boldFont=True, parent=menu)
    mc.menuItem(divider=True, parent=menu)
    #
    # show hide secondary controls
    if rigGroup:
        if mc.attributeQuery('controlsVisList', n=rigGroup, ex=True) and mc.attributeQuery('controlsVisState', n=rigGroup, ex=True):
            list = mc.listConnections(rigGroup + '.controlsVisList') or []
            if list:
                if mc.getAttr(rigGroup + '.controlsVisState') == 1:
                    pop = 'Hide'
                else:
                    pop = 'Show'
                mc.menuItem(label=pop + ' secondary controls', command=partial(showHideSecondaryControls, rigGroup), parent=menu)
    #
    # show hide ellipse_controls
    if mc.objExists(node + '.ellipse_controls'):
        if mc.getAttr(node + '.ellipse_controls') == 1:
            pop = 'Hide'
        else:
            pop = 'Show'
        mc.menuItem(label=pop + ' controls', command=partial(showHideControls, node), parent=menu)
    #
    # show hide viz controls attributes
    visAttrs = []
    if mc.objExists(node + '.menuShowHideAttrs'):
        visAttrs = mc.listConnections(node + '.menuShowHideAttrs', p=True) or []
    for attr in visAttrs:
        if mc.objExists(attr):
            if mc.getAttr(attr) == 1:
                pop = 'Hide'
            else:
                pop = 'Show'
        name = pop + ' ' + attr.split('.')[1]
        mc.menuItem(label=name, command=partial(showHideAttrs, attr), parent=menu)
    #
    # show hide cg
    visGroups = []
    if mc.objExists(node + '.menuHideGroups'):
        visGroups = mc.listConnections(node + '.menuHideGroups') or []
    for grp in visGroups:
        if mc.attributeQuery('membersVisibility', node=grp, ex=True):
            if mc.getAttr(grp + '.membersVisibility'):
                pop = 'Hide'
            else:
                pop = 'Show'
        else:
            pop = 'Hide'
            ctrls = getControlGroupMembers(grp)
            for ctrl in ctrls:
                if not mc.getAttr(ctrl + '.v'):
                    pop = 'Show'
        mc.menuItem(label=pop + ' ' + mc.getAttr(grp + '.name'), command=partial(showHideControlGroups, grp), parent=menu)
    mc.menuItem(divider=True, parent=menu)
    #
    # restore bindPose
    mc.menuItem(divider=True, parent=menu)
    mc.menuItem(label='Reset', subMenu=True, parent=menu)
    mc.menuItem(label=node, boldFont=True, command=partial(restoreBindPose, node))
    mc.menuItem(label='selection', command=partial(restoreBindPose, mc.ls(sl=True)))
    for cg in all_cgs:
        name = setName(cg)
        mc.menuItem(label=name, command=partial(restoreBindPose, cg))
    mc.setParent('..', menu=True)
    #
    # set bindPose
    if mc.attributeQuery('expertMode', n=masterParent, ex=True):
        if mc.getAttr(masterParent + '.expertMode'):
            mc.menuItem(label='Set BindPose', subMenu=True, parent=menu)
            mc.menuItem(label=node, boldFont=True, command=partial(setBindPose, node))
            mc.menuItem(label='selection', command=partial(setBindPose, mc.ls(sl=True)))
            for cg in all_cgs:
                name = setName(cg)
                mc.menuItem(label=name, command=partial(setBindPose, cg))
            mc.setParent('..', menu=True)
    #
    # selection
    mc.menuItem(label='Select', subMenu=True, parent=menu)
    mc.menuItem(label=node, boldFont=True, command=partial(selectNode, node))
    for cg in all_cgs:
        name = setName(cg)
        mc.menuItem(label=name, command=partial(selectControlGroupMembers, cg))
    #
    # keyframe
    mc.menuItem(label='Set key', subMenu=True, parent=menu)
    mc.menuItem(label=node, boldFont=True, command=partial(keyNode, node))
    mc.menuItem(label='selection', command=partial(keyNode, mc.ls(sl=True)))
    for cg in all_cgs:
        name = setName(cg)
        mc.menuItem(label=name, command=partial(keyControlGroupMembers, cg))
    #
    mc.setParent('..', menu=True)
    # snap to
    if sel:
        mc.menuItem(label='Snap to', subMenu=True, parent=menu)
        mc.menuItem(label=sel[0], boldFont=True, command=partial(snap, node, sel[0]))
        mc.menuItem(label='position', command=partial(snap, node, sel[0], rotation=False))
        mc.menuItem(label='orient', command=partial(snap, node, sel[0], position=False))
        mc.setParent('..', menu=True)
    else:
        mc.menuItem(label='Snap to', parent=menu, enable=False)
    #
    # pose flip mirror
    mc.menuItem(label='Pose', subMenu=True)
    mc.menuItem(label='Flip', subMenu=True)
    mc.menuItem(label=node, boldFont=True, command=partial(mirrorControl, node, 0))
    mc.menuItem(label='selection', command=partial(mirrorSelection, 0))
    for cg in all_cgs:
        name = setName(cg)
        mc.menuItem(label=name, command=partial(mirrorCtrlGroup, cg, 0))
    mc.setParent('..', menu=True)
    mc.menuItem(subMenu=True, label='<Mirror L to R')
    mc.menuItem(label=node, boldFont=True, command=partial(mirrorControl, node, 1))
    mc.menuItem(label='selection', command=partial(mirrorSelection, 1))
    for cg in all_cgs:
        name = setName(cg)
        mc.menuItem(label=name, command=partial(mirrorCtrlGroup, cg, 1))
    mc.setParent('..', menu=True)
    mc.menuItem(subMenu=True, label='Mirror> R to L')
    mc.menuItem(label=node, boldFont=True, command=partial(mirrorControl, node, -1))
    mc.menuItem(label='selection', command=partial(mirrorSelection, -1))
    for cg in all_cgs:
        name = setName(cg)
        mc.menuItem(label=name, command=partial(mirrorCtrlGroup, cg, -1))
    mc.setParent('..', menu=True)
    mc.setParent('..', menu=True)
    #
    # puppet mode
    puppetAttributes = [i for i in mc.listAttr(masterParent, ud=True) or [] if 'puppet' in i]
    if puppetAttributes:
        mc.menuItem(label='Puppet', subMenu=True)
        mc.menuItem(label='Activate All', bld=True, c=partial(showHidePuppet, masterParent, puppetAttributes, 'All'))
        mc.menuItem(label='Deactivate All', bld=True, c=partial(showHidePuppet, masterParent, puppetAttributes, 'None'))
        mc.menuItem(divider=True)
        for attr in puppetAttributes:
            name = attr.split('_', 1)[-1]
            value = mc.getAttr(masterParent + '.' + attr)
            mc.menuItem(label=name, cb=value, command=partial(showHidePuppet, masterParent, puppetAttributes, attr))
        mc.setParent('..', menu=True)
    else:
        mc.menuItem(label='Puppet', parent=menu, enable=False)
    #
    # ik fk
    if mc.objExists(node + '.menuMatchIKFK'):
        matchNode = mc.listConnections(node + '.menuMatchIKFK')
        if matchNode:
            switchCtrl = mc.listConnections(matchNode[0] + '.switch', shapes=True)
            switchVal = mc.getAttr(switchCtrl[0] + '.ikBlend')
            if switchVal > 0:
                mc.menuItem(label='Go to FK', rp='NW', command=partial(snapFK, matchNode[0]))
            if switchVal < 10:
                mc.menuItem(label='Go to IK', rp='NW', command=partial(snapIK, matchNode[0]))
        else:
            mc.warning('Problem on IKFK match, TOFIX')
    #
    # space switch
    if mc.objExists(node + '.menuSpaceSwitch') and mc.listConnections(node + '.menuSpaceSwitch'):
        matchNode = mc.listConnections(node + '.menuSpaceSwitch')[0]
        targets = mc.getAttr(matchNode + '.targets[*]')
        rps = ['NE', 'E', 'SE', 'S', 'N']
        for i, tgt in enumerate(targets):
            mc.menuItem(label='follow ' + tgt, radialPosition=rps[i],
                        echoCommand=1,
                        command=partial(spaceSwitch, matchNode, i),
                        parent=menu)
    #
    # dynamics
    dynNode = ''
    if mc.attributeQuery('dynamic', n=node, ex=True):
        lock = mc.getAttr(node + '.dynamic', l=True)
        if lock:
            shapes = mc.listRelatives(node, p=False, c=True, typ='shape', ni=True) or []
            for shape in shapes:
                if mc.attributeQuery('dynamic', n=shape, ex=True):
                    dynNode = shape
                    break
        else:
            dynNode = node
    if dynNode and mc.getAttr(node + '.dynamic', se=True):
        state = mc.getAttr(dynNode + '.dynamic')
        if state:
            mc.menuItem(label='Disable dynamic', rp='SW', command=partial(disableDynamic, dynNode) , parent=menu)
        else:
            mc.menuItem(label='Enable dynamic', rp='SW', command=partial(enableDynamic, dynNode) , parent=menu)
    #
    # functions
    mc.menuItem(divider=True)

    mc.menuItem(subMenu=True, label="functions")
    assetName = 'asset'
    if ':' in node:
        assetName = node.replace(node.split(':')[-1], '')[: -1]
    geo = node.replace(node.split(':')[-1], 'GEO')
    if not mc.objExists(geo):
        geo = node.replace('RIG:', 'MOD:')
    if mc.objExists(geo):
        geoSmooth = mc.displaySmoothness(geo, q=True, po=True) or []
        if geoSmooth:
            if geoSmooth[0] == 1:
                mc.menuItem(label="smooth "+assetName+" GEO", cb=0, command=partial(displayAssetSmooth ,geo, True))
            else:
                mc.menuItem(label="unsmooth "+assetName+" GEO", cb=1, command=partial(displayAssetSmooth, geo, False))

        valGeo = mc.getAttr(geo+'.v')
        if valGeo == True:
            mc.menuItem(label="hide "+assetName+" GEO", cb=0, command=partial(showHideGeo, geo, valGeo))
        if valGeo == False:
            mc.menuItem(label="show "+assetName+" GEO", cb=1, command=partial(showHideGeo, geo, valGeo))
    mc.menuItem(divider=True, dividerLabel='Patchs')

    #mc.menuItem(label="liberate the normals!", command=partial(flushVtxNormals))

    if mc.getAttr(node+'.useOutlinerColor') == False:
        mc.menuItem(label="tweak outliner ctrl color", cb=0, command=partial(displayColOutliner, node, True))
    else:
        mc.menuItem(label="reset outliner ctrl color", cb=1, command=partial(displayColOutliner, node, False))

    if mc.outlinerEditor("graphEditor1OutlineEd", q=True, hir=True):
        mc.menuItem(label="Hack graph editor", cb=1, command=lambda x: mc.outlinerEditor("graphEditor1OutlineEd", e=True, ignoreDagHierarchy=False))
    else:
        mc.menuItem(label="Hack graph editor", cb=0, command=lambda x: mc.outlinerEditor("graphEditor1OutlineEd", e=True, ignoreDagHierarchy=True))

    mc.setParent('..', menu=True)
    mc.menuItem(divider=True)
    mc.menuItem(subMenu=True, label="tools")
    mc.menuItem(label="Ctrl tools", command=partial(showAnimTools_UI))





# ==========================================================================
# common
# ==========================================================================


def getNamespace(node):
    namespace = ''
    tmp = node.split(':')
    if len(tmp) > 1:
        namespace = tmp[0]
    return namespace


def setName(cg):
    name = mc.getAttr(cg + '.name')
    namespace = getNamespace(cg)
    if namespace:
        if namespace != 'MOD' and namespace != 'RIG':
            name = namespace + ':' + mc.getAttr(cg + '.name')
    return name


# ==========================================================================
# show hide
# ==========================================================================


def showHideControlGroups(cg, *args):
    cgs = [cg] + getControlGroupChildrens(cg)
    value = True
    if mc.attributeQuery('membersVisibility', node=cg, ex=True):
        if mc.getAttr(cg + '.membersVisibility'):
            value = False
    for c in cgs:
        if mc.attributeQuery('membersVisibility', node=c, ex=True):
            mc.setAttr(c + '.membersVisibility', value)
        else:
            ctrls = getControlGroupMembers(c, recursive=False)
            visible = 0
            for ctrl in ctrls:
                visible += int(mc.getAttr(str(ctrl) + ".v"))
            if not visible:
                mc.showHidden(ctrls)
            else:
                mc.hide(ctrls)


def showHideControls(node, *args):
    if mc.attributeQuery('ellipse_controls', node=node, ex=True):
        if mc.getAttr(node + '.ellipse_controls') == 1:
            mc.setAttr(node + '.ellipse_controls', 0)
        else:
            mc.setAttr(node + '.ellipse_controls', 1)


def showHideSecondaryControls(node, *args):
    controls = [o for o in mc.listConnections(node + '.controlsVisList') or []] or []
    state = mc.getAttr(node + '.controlsVisState')
    if state:
        mc.hide(controls)
        mc.setAttr(node + '.controlsVisState', 0)
    else:
        mc.showHidden(controls)
        mc.setAttr(node + '.controlsVisState', 1)


def showHideAttrs(attr, *args):
    if mc.objExists(attr):
        if mc.getAttr(attr) == 1:
            mc.setAttr(attr, 0)
        else:
            mc.setAttr(attr, 1)


def showHidePuppet(node, attributes, attribute, state, *args):
    if attribute == 'All':
        for attr in attributes:
            mc.setAttr(node + '.' + attr, True)
    elif attribute == 'None':
        for attr in attributes:
            mc.setAttr(node + '.' + attr, False)
    else:
        mc.setAttr(node + '.' + attribute, state)

def showHideGeo(geo, valGeo, *args):
    val = False
    if valGeo == False:
        val = True
    mc.setAttr(geo+'.v', val)


# ==========================================================================
# controls
# ==========================================================================


def getAllControls():
    all_controls = []
    for o in mc.ls():
        if mc.attributeQuery('nodeType', node=o, ex=True) and mc.getAttr(o + '.nodeType') == 'control':
            all_controls.append(o)
    return all_controls


def getControlGroups(ctrl, recursive=False):
    cgs = []
    networks = mc.listConnections(ctrl + '.message', type='network') or []
    for n in networks:
        if mc.objExists(n + '.name'):
            cgs.append(str(n))
    if recursive:
        for cg in cgs:
            allChildrens = getControlGroupChildrens(cg)
            for c in allChildrens:
                if c not in cgs:
                    cgs.append(c)
    return cgs


def getControlGroupParents(cg, recursive=True):
    if mc.attributeQuery('parent', node=cg, ex=True):
        parents = mc.listConnections(cg + '.parent', type='network') or []
    elif mc.attributeQuery('parents', node=cg, ex=True):
        parents = mc.listConnections(cg + '.parents[0]', type='network') or []
    if recursive:
        for parent in parents:
            oldParents = getControlGroupParents(parent)
            for p in oldParents:
                if p not in parents:
                    parents.append(p)
    return parents


def getControlGroupChildrens(cg, recursive=True):
    if mc.attributeQuery('children', node=cg, ex=True):
        childrens = mc.listConnections(cg + '.children', type='network') or []
    if recursive:
        for children in childrens:
            allChildrens = getControlGroupChildrens(children)
            for c in allChildrens:
                if c not in childrens:
                    childrens.append(c)
    return childrens


def getControlGroupMembers(cg, recursive=True):
    members = mc.listConnections(cg + '.members', sh=1) or []
    if recursive:
        childs = mc.listConnections(cg + '.children') or []
        for c in childs:
            members.extend(getControlGroupMembers(c))
    return members


def selectNode(node, *args):
    """ select node """
    mc.select(node)


def selectControlGroupMembers(cg, *args):
    members = getControlGroupMembers(cg)
    if members:
        mc.select(members)


def keyNode(node, *args):
    """ key node """
    mc.setKeyframe(node)


def keyControlGroupMembers(cg, *args):
    members = getControlGroupMembers(cg)
    if members:
        for m in members:
            keyNode(m)


#==========================================================================
# bindPose
#==========================================================================


def restoreBindPose(nodes, *args):
    if isinstance(nodes, basestring):
        nodes = [nodes]
    # init
    ctrls = []
    # get controllers
    for node in nodes:
        if mc.objectType(node) == 'network':
            ctrls = getControlGroupMembers(node)
        else:
            ctrls.append(node)
    # reset controllers
    for ctrl in ctrls:
        if mc.attributeQuery('bindPoseAttrs', node=ctrl, exists=True) and mc.attributeQuery('bindPoseValues', node=ctrl, exists=True):
            attrs = mc.getAttr(ctrl + '.bindPoseAttrs', mi=True) or []
            for x in attrs:
                attr = mc.getAttr('{0}.bindPoseAttrs[{1}]'.format(ctrl, x))
                if not mc.getAttr('{0}.{1}'.format(ctrl, attr), settable=True):
                    continue
                value = mc.getAttr('{0}.bindPoseValues[{1}]'.format(ctrl, x))
                if not attr == 'ikBlend':
                    mc.setAttr('{0}.{1}'.format(ctrl, attr), value)


def setBindPose(nodes, *args):
    if isinstance(nodes, basestring):
        nodes = [nodes]
    # init
    ctrls = []
    # get controllers
    for node in nodes:
        if mc.objectType(node) == 'network':
            ctrls = getControlGroupMembers(node)
        else:
            ctrls.append(node)
    # set bindPose on controllers
    for ctrl in ctrls:
        # create attributes
        if mc.attributeQuery('bindPoseAttrs', n=ctrl, ex=True):
            indices = mc.getAttr(ctrl + '.bindPoseAttrs', multiIndices=True) or []
            if indices:
                for x in indices:
                    mc.removeMultiInstance('{0}.bindPoseAttrs[{1}]'.format(ctrl, x))
        else:
            mc.addAttr(ctrl, ln='bindPoseAttrs', multi=True, dt='string')
        if mc.attributeQuery('bindPoseValues', n=ctrl, ex=True):
            indices = mc.getAttr(ctrl + '.bindPoseValues', multiIndices=True) or []
            if indices:
                for x in indices:
                    mc.removeMultiInstance('{0}.bindPoseValues[{1}]'.format(ctrl, x))
        else:
            mc.addAttr(ctrl, ln='bindPoseValues', multi=True, at='float')
        # set bindPose
        keyableAttrs = mc.listAttr(ctrl, visible=True, keyable=True, scalar=True, leaf=True, shortNames=True) or []
        if keyableAttrs:
            bindPoseAttrs = []
            bindPoseValues = []
            idx = 0
            for x in xrange(len(keyableAttrs)):
                plug = '{0}.{1}'.format(ctrl, keyableAttrs[x])
                if mc.objExists(plug):
                    bpAttrsPlug = ctrl + '.bindPoseAttrs[{}]'.format(idx)
                    mc.setAttr(bpAttrsPlug, keyableAttrs[x], type='string')
                    bindPoseAttrs.append(keyableAttrs[x])
                    value = mc.getAttr(plug)
                    bpValuesPlug = ctrl + '.bindPoseValues[{}]'.format(idx)
                    mc.setAttr(bpValuesPlug, value)
                    bindPoseValues.append(value)
                    idx += 1


#==========================================================================
# snap
#==========================================================================


def snap(toSnap, dst, *args, **kwargs):
    """Snaps a transform on another.

    :param toSnap: Transform to snap
    :type toSnap: str
    :param dst: Destination transform
    :type dst: str
    :param position: Snap position
    :type position: bool
    :param rotation: Snap rotates
    :type rotation: bool
    :param scale: Snap scale
    :type scale: bool
    :param rotateOrder: Transferts rotate order
    :type rotateOrder: bool
    :param useDummy: Uses intermediate transform to prevent cycles during snap
    :type useDummy: bool
    """
    position = kwargs.get('position', kwargs.get('p', True))
    rotation = kwargs.get('rotation', kwargs.get('r', True))
    scale = kwargs.get('scale', kwargs.get('s', False))
    rotateOrder = kwargs.get('rotateOrder', kwargs.get('ro', True))
    useDummy = kwargs.get('useDummy', kwargs.get('d', True))

    if useDummy:
        dummy = mc.createNode('transform')
        snap(dummy, dst, position=position, rotation=rotation, scale=scale,
             rotateOrder=rotateOrder, useDummy=False)
        dst = dummy
    if rotateOrder:
        mc.setAttr(toSnap + '.rotateOrder', mc.getAttr(dst + '.rotateOrder'))
    if position and rotation:
        mc.delete(mc.parentConstraint(dst, toSnap))
    elif position:
        mc.delete(mc.pointConstraint(dst, toSnap))
    elif rotation:
        mc.delete(mc.orientConstraint(dst, toSnap))
    if scale:
        mc.delete(mc.scaleConstraint(dst, toSnap))
    if useDummy:
        mc.delete(dummy)
    if mc.nodeType(toSnap) == 'joint':
        mc.makeIdentity(toSnap, apply=True, rotate=True, translate=False, scale=False)


#==========================================================================
# mirror
#==========================================================================


def getMirrorControl(ctrl):
    if not mc.attributeQuery('nodesId', n=ctrl, ex=True):
        return
    ids = mc.getAttr(ctrl + '.nodesId', mi=True) or []
    mirror_index = [i for i in ids if mc.getAttr(ctrl + '.nodesId[{}]'.format(i)) == 'mirror'] or []
    if not mirror_index:
        return
    mctrl = mc.listConnections(ctrl + '.nodes[{}]'.format(mirror_index[0]), sh=1) or []
    if mctrl:
        return mctrl[0]


def getMirrorControls(ctrls):
    if isinstance(ctrls, basestring):
        ctrls = [ctrls]
    mctrls = []
    for ctrl in ctrls:
        mctrl = getMirrorControl(ctrl)
        if not mctrl in mctrls:
            mctrls.append(ctrl)
    return mctrls


def mirrorSelection(direction, *args):
    for x in mc.ls(sl=1):
        mirrorControl(x, direction)


def mirrorCtrlGroup(cg, dir_, *args):
    ctrls = getMirrorControls(getControlGroupMembers(cg))
    switch = [c for c in ctrls if 'Switch' in c] or []
    ik = [c for c in ctrls if ('Ik' in c or 'IK' in c or 'PV' in c) and c not in switch] or []
    fk = [c for c in ctrls if c not in switch and c not in ik] or []
    ctrls = ik + switch + fk
    # check if switch ikfk cg
    if dir_ == 0:
        ikfk = False
        iknode = []
        ikstate = []
        iknetwork = []
        for ctrl in ctrls:
            attrs = mc.listAttr(ctrl, ud=1) or []
            if 'ikBlend' in attrs and 'Switch' in ctrl:
                mctrl = getMirrorControl(ctrl)
                network = [m for m in mc.listConnections(ctrl + '.message', type='network') if 'menu_matchIKFK' in m] or []
                mnetwork = [m for m in mc.listConnections(mctrl + '.message', type='network') if 'menu_matchIKFK' in m] or []
                if not (ctrl, mctrl) or not (mctrl, ctrl) in iknode:
                    iknode.append((ctrl, mctrl))
                    ikstate.append((mc.getAttr(ctrl + '.ikBlend'), mc.getAttr(mctrl + '.ikBlend')))
                    iknetwork.append((network[0], mnetwork[0]))
                ikfk = True
        # snap all to fk
        if ikfk:
            for n1 in iknetwork:
                for n2 in n1:
                    if mc.getAttr(mc.listConnections(n2 + '.ik', s=True, d=False, p=False)[0] + '.ikBlend') == 0:
                        snapFK(n2)
    # mirror controls
    for c in ctrls:
        mirrorControl(c, dir_)
    # reset ikfk
    if dir_ == 0:
        if ikfk:
            for n1, s1 in zip(iknetwork, ikstate):
                for n2, s2 in zip(n1, reversed(s1)):
                    if s2 == 10:
                        snapIK(n2)


def mirrorControl(ctrl, direction, *args):
    # direction: 0: flip, mirror L: 1, mirror R (in) -1
    side = []
    if mc.objExists(ctrl + '.mirrorSide'):
        side = mc.getAttr(ctrl + '.mirrorSide') or []
    # side check
    if not side:
        return
    rvs = True
    if mc.nodeType(ctrl) == 'nurbsCurve':
        rvs = False  # reverse method

    r = [-1, 1, 1, 1, -1, -1]
    if mc.objExists(ctrl + '.mirrorType'):
        mtype = mc.getAttr(ctrl + '.mirrorType')
        if mtype == 1:
            r = [-1, -1, -1, 1, 1, 1]
        elif mtype == 3:
            r = [1, 1, -1, 1, 1, 1]
        elif mtype == 4:
            r = [1, 1, -1, 1, 1, 1]


    if side == 3:
        if not rvs:
            return
        # middle
        pos = mc.getAttr(ctrl + '.t')[0]
        rot = mc.getAttr(ctrl + '.r')[0]
        # sca = mc.getAttr(ctrl + '.s')
        if direction == 0:
            if mc.getAttr(ctrl + '.tx', se=True):
                mc.setAttr(ctrl + '.tx', pos[0] * r[0])
            if mc.getAttr(ctrl + '.ty', se=True):
                mc.setAttr(ctrl + '.ty', pos[1] * r[1])
            if mc.getAttr(ctrl + '.tz', se=True):
                mc.setAttr(ctrl + '.tz', pos[2] * r[2])
            if mc.getAttr(ctrl + '.rx', se=True):
                mc.setAttr(ctrl + '.rx', rot[0] * r[3])
            if mc.getAttr(ctrl + '.ry', se=True):
                mc.setAttr(ctrl + '.ry', rot[1] * r[4])
            if mc.getAttr(ctrl + '.rz', se=True):
                mc.setAttr(ctrl + '.rz', rot[2] * r[5])
        else:
            if mc.getAttr(ctrl + '.tx', se=True):
                mc.setAttr(ctrl + '.tx', 0)
            if mc.getAttr(ctrl + '.ry', se=True):
                mc.setAttr(ctrl + '.ry', 0)
            if mc.getAttr(ctrl + '.rz', se=True):
                mc.setAttr(ctrl + '.rz', 0)
    else:
        mctrl = getMirrorControl(ctrl)
        if not mctrl:
            return
        # left/right
        if direction == 0:
            if rvs:
                pos0 = mc.getAttr(ctrl + '.t')[0]
                rot0 = mc.getAttr(ctrl + '.r')[0]
                sca0 = mc.getAttr(ctrl + '.s')[0]
                pos1 = mc.getAttr(mctrl + '.t')[0]
                rot1 = mc.getAttr(mctrl + '.r')[0]
                sca1 = mc.getAttr(mctrl + '.s')[0]
                if mc.getAttr(ctrl + '.tx', se=True):
                    mc.setAttr(ctrl + '.tx', pos1[0] * r[0])
                if mc.getAttr(ctrl + '.ty', se=True):
                    mc.setAttr(ctrl + '.ty', pos1[1] * r[1])
                if mc.getAttr(ctrl + '.tz', se=True):
                    mc.setAttr(ctrl + '.tz', pos1[2] * r[2])
                if mc.getAttr(mctrl + '.tx', se=True):
                    mc.setAttr(mctrl + '.tx', pos0[0] * r[0])
                if mc.getAttr(mctrl + '.ty', se=True):
                    mc.setAttr(mctrl + '.ty', pos0[1] * r[1])
                if mc.getAttr(mctrl + '.tz', se=True):
                    mc.setAttr(mctrl + '.tz', pos0[2] * r[2])
                if mc.getAttr(ctrl + '.rx', se=True):
                    mc.setAttr(ctrl + '.rx', rot1[0] * r[3])
                if mc.getAttr(ctrl + '.ry', se=True):
                    mc.setAttr(ctrl + '.ry', rot1[1] * r[4])
                if mc.getAttr(ctrl + '.rz', se=True):
                    mc.setAttr(ctrl + '.rz', rot1[2] * r[5])
                if mc.getAttr(mctrl + '.rx', se=True):
                    mc.setAttr(mctrl + '.rx', rot0[0] * r[3])
                if mc.getAttr(mctrl + '.ry', se=True):
                    mc.setAttr(mctrl + '.ry', rot0[1] * r[4])
                if mc.getAttr(mctrl + '.rz', se=True):
                    mc.setAttr(mctrl + '.rz', rot0[2] * r[5])
                if mc.getAttr(ctrl + '.sx', se=True):
                    mc.setAttr(ctrl + '.sx', sca1[0])
                if mc.getAttr(ctrl + '.sy', se=True):
                    mc.setAttr(ctrl + '.sy', sca1[1])
                if mc.getAttr(ctrl + '.sz', se=True):
                    mc.setAttr(ctrl + '.sz', sca1[2])
                if mc.getAttr(mctrl + '.sx', se=True):
                    mc.setAttr(mctrl + '.sx', sca0[0])
                if mc.getAttr(mctrl + '.sy', se=True):
                    mc.setAttr(mctrl + '.sy', sca0[1])
                if mc.getAttr(mctrl + '.sz', se=True):
                    mc.setAttr(mctrl + '.sz', sca0[2])
            attrs = mc.listAttr(ctrl, ud=1, s=1, k=1) or []
            # custom attrs
            for attr0 in attrs:
                if not mc.objExists(mctrl + '.' + attr0):
                    continue
                vL = mc.getAttr(ctrl + '.' + attr0)
                vR = mc.getAttr(mctrl + '.' + attr0)
                if mc.getAttr(ctrl + '.' + attr0, se=True):
                    mc.setAttr(ctrl + '.' + attr0, vR)
                if mc.getAttr(mctrl + '.' + attr0, se=True):
                    mc.setAttr(mctrl + '.' + attr0, vL)
        else:
            if (side == 1 and direction < 0) or (side == 2 and direction > 0):
                tmp = mctrl
                mctrl = ctrl
                ctrl = tmp
            if rvs:
                pos0 = mc.getAttr(ctrl + '.t')[0]
                rot0 = mc.getAttr(ctrl + '.r')[0]
                sca0 = mc.getAttr(ctrl + '.s')[0]
                if mc.getAttr(mctrl + '.tx', se=True):
                    mc.setAttr(mctrl + '.tx', pos0[0] * r[0])
                if mc.getAttr(mctrl + '.ty', se=True):
                    mc.setAttr(mctrl + '.ty', pos0[1] * r[1])
                if mc.getAttr(mctrl + '.tz', se=True):
                    mc.setAttr(mctrl + '.tz', pos0[2] * r[2])
                if mc.getAttr(mctrl + '.rx', se=True):
                    mc.setAttr(mctrl + '.rx', rot0[0] * r[3])
                if mc.getAttr(mctrl + '.ry', se=True):
                    mc.setAttr(mctrl + '.ry', rot0[1] * r[4])
                if mc.getAttr(mctrl + '.rz', se=True):
                    mc.setAttr(mctrl + '.rz', rot0[2] * r[5])
                if mc.getAttr(mctrl + '.sx', se=True):
                    mc.setAttr(mctrl + '.sx', sca0[0])
                if mc.getAttr(mctrl + '.sy', se=True):
                    mc.setAttr(mctrl + '.sy', sca0[1])
                if mc.getAttr(mctrl + '.sz', se=True):
                    mc.setAttr(mctrl + '.sz', sca0[2])

            attrs = mc.listAttr(ctrl, ud=1, s=1, k=1) or []
            # custom attrs
            for attr0 in attrs:
                if not mc.objExists(mctrl + '.' + attr0):
                    continue
                v = mc.getAttr(ctrl + '.' + attr0)
                if mc.getAttr(mctrl + '.' + attr0, se=True):
                    mc.setAttr(mctrl + '.' + attr0, v)


#==========================================================================
# ik fk
#==========================================================================


def snapFK(matchNode, *args):
    sel = mc.ls(sl=1)
    sw = mc.listConnections(matchNode + '.switch', shapes=True)
    s = mc.getAttr(matchNode + '.fk', s=1)
    data = []
    for i in xrange(s):
        fk = mc.listConnections(matchNode + '.fk[%s]' % i)
        data.append((fk[0] + '.r', (mc.getAttr(fk[0] + '.rx'),
                                    mc.getAttr(fk[0] + '.ry'),
                                    mc.getAttr(fk[0] + '.rz'))))

    mc.setAttr(sw[0] + '.ikBlend', 0)
    for a, v in data:
        mc.setAttr(a, *v)
    if sel:
        mc.select(sel)


def snapIK(matchNode, *args):
    sel = mc.ls(sl=1)
    sw = mc.listConnections(matchNode + '.switch', shapes=True)
    s = mc.getAttr(matchNode + '.fk', s=1)
    ik = mc.listConnections(matchNode + '.ik')
    end = mc.listConnections(matchNode + '.fk[%s]' % (s - 1))
    papa = mc.listRelatives(ik[0], p=1, pa=1)
    dummyParent = mc.createNode('transform', p=papa[0])
    dummy = mc.createNode('transform', p=dummyParent)
    mc.setAttr(dummy + '.rotateOrder', mc.getAttr(ik[0] + '.rotateOrder'))
    offset = [0, 0, 0]
    if mc.objExists(ik[0] + '.orientOffset'):
        offset = mc.getAttr(ik[0] + '.orientOffset')[0]

    mc.pointConstraint(end[0], dummy)
    orientCon = mc.orientConstraint(end[0], dummy)
    mc.setAttr(orientCon[0] + '.offset', *offset)
    mc.setAttr(ik[0] + '.t', *mc.getAttr(dummy + '.t')[0])
    r = mc.getAttr(dummy + '.r')[0]
    mc.setAttr(ik[0] + '.r', r[0], r[1], r[2])

    mc.delete(dummyParent)

    # calcul du twist
    mc.setAttr(ik[0] + '.twist', 0)
    fk0 = mc.listConnections(matchNode + '.fk[0]')
    fk1 = mc.listConnections(matchNode + '.fk[1]')
    fkp = mc.listRelatives(fk0[0], p=1, pa=1)
    dummy = mc.createNode('transform', p=fkp[0])
    mc.pointConstraint(fk0[0], dummy)
    mc.aimConstraint(end[0], dummy, wut='none')
    angle1 = mc.createNode('transform', p=dummy)
    angle2 = mc.createNode('transform', p=dummy)
    mc.delete(mc.pointConstraint(fk1[0], angle1))
    mc.setAttr(sw[0] + '.ikBlend', 10)
    mc.delete(mc.pointConstraint(fk1[0], angle2))
    twprobe = mc.createNode('angleBetween')
    mc.connectAttr(angle2 + '.ty', twprobe + '.vector1Y')
    mc.connectAttr(angle2 + '.tz', twprobe + '.vector1Z')
    mc.connectAttr(angle1 + '.ty', twprobe + '.vector2Y')
    mc.connectAttr(angle1 + '.tz', twprobe + '.vector2Z')
    twist = mc.getAttr(twprobe + '.eulerX')
    if mc.getAttr(matchNode + '.reverseTwist'):
        twist *= float(-1)
    elif mc.getAttr(ik[0] + '.mirrorSide') == 2:
        twist *= float(-1)

    mc.setAttr(ik[0] + '.twist', twist)
    mc.delete(dummy)
    if sel:
        mc.select(sel)


#==========================================================================
# space switch
#==========================================================================


def spaceSwitch(menuSpaceSwitch, spaceIndex, *args):
    sel = mc.ls(sl=True)  # Keep selection

    constraint = mc.listConnections(menuSpaceSwitch + '.constraint')
    ctrl = mc.listConnections(menuSpaceSwitch + '.msg', type='transform')
    s = mc.getAttr(menuSpaceSwitch + '.targets', size=True)

    attrs = []
    for i in xrange(s):
        attrs.append(mc.getAttr(menuSpaceSwitch + '.attrs[%s]' % i))

    papa = mc.listRelatives(ctrl[0], parent=True, path=True)

    dummyParent = mc.createNode('transform', p=papa[0])
    dummy = mc.createNode('joint', p=dummyParent)
    mc.setAttr(dummy + '.rotateOrder', mc.getAttr(ctrl[0] + '.rotateOrder'))

    dummyLock = mc.createNode('transform')
    mc.delete(mc.parentConstraint(ctrl[0], dummyLock))
    mc.parentConstraint(dummyLock, dummy)

    for i in xrange(s):
        if attrs[i] != '':
            mc.setAttr(ctrl[0] + '.' + attrs[i], 0)

    if attrs[spaceIndex] != '':
        mc.setAttr(ctrl[0] + '.' + attrs[spaceIndex], 10)

    if mc.nodeType(ctrl[0]) == 'joint':
        jo = mc.getAttr(ctrl[0] + '.jo')[0]
        mc.setAttr(dummy + '.jo', *jo)

    type_ = mc.nodeType(constraint[0])
    t = mc.getAttr(dummy + '.t')[0]
    r = mc.getAttr(dummy + '.r')[0]
    if type_ == 'pointConstraint':
        mc.setAttr(ctrl[0] + '.t', *t)
    if type_ == 'orientConstraint':
        mc.setAttr(ctrl[0] + '.r', *r)
    if type_ == 'parentConstraint':
        if not mc.getAttr(ctrl[0] + '.tx', lock=True):
            mc.setAttr(ctrl[0] + '.tx', t[0])
        if not mc.getAttr(ctrl[0] + '.ty', lock=True):
            mc.setAttr(ctrl[0] + '.ty', t[1])
        if not mc.getAttr(ctrl[0] + '.tz', lock=True):
            mc.setAttr(ctrl[0] + '.tz', t[2])
        if mc.nodeType(ctrl[0]) == 'joint':
            jo = mc.getAttr(ctrl[0] + '.jo')[0]
            mc.setAttr(dummy + '.jo', *jo)
            r = mc.getAttr(dummy + '.r')[0]

        if not mc.getAttr(ctrl[0] + '.rx', lock=True):
            mc.setAttr(ctrl[0] + '.rx', r[0])
        if not mc.getAttr(ctrl[0] + '.ry', lock=True):
            mc.setAttr(ctrl[0] + '.ry', r[1])
        if not mc.getAttr(ctrl[0] + '.rz', lock=True):
            mc.setAttr(ctrl[0] + '.rz', r[2])

    mc.delete(dummyParent, dummyLock)
    if sel:
        mc.select(sel)  # Restore selection


#==========================================================================
# dynamic
#==========================================================================


def enableDynamic(node, *args):
    mc.setAttr(node + '.dynamic', 1)


def disableDynamic(node, *args):
    mc.setAttr(node + '.dynamic', 0)



#==========================================================================
# display
#==========================================================================
def displayAssetSmooth(geo, smoothVal, *args):
    if smoothVal == True:
        mc.displaySmoothness(geo, du=3, dv=3, pw=16, ps=4, po=3)
    else:
        mc.displaySmoothness(geo, du=0, dv=0, pw=4, ps=1, po=1)


def displayColOutliner(node, val, *args):
    cg = getControlGroups(node, recursive=False)[0]
    masterCg = cg
    chkMaster = getControlGroupParents(cg, recursive=True) or []
    if chkMaster:
        masterCg = chkMaster[-1]
    lCtrl = getControlGroupMembers(masterCg, recursive=True)
    for ctrl in lCtrl:
        print ctrl
        mc.setAttr(ctrl+'.useOutlinerColor', val)
        if val == True:
            mc.setAttr(ctrl+'.outlinerColor', 0, 1, 0)
    mel.eval("AEdagNodeCommonRefreshOutliners();")

def flushVtxNormals(*args):
    lMsh = mc.ls(type='mesh')
    for msh in lMsh:
        mc.polySetToFaceNormal(msh)
        mc.polySoftEdge(msh,  a=180, ch=1)
        mc.select(cl=True)


#==========================================================================
# tools
#==========================================================================
def showAnimTools_UI(*args):
    import tools_dagMenu
    reload(tools_dagMenu)
    tools_dagMenu.SMAB_animTools_UI()