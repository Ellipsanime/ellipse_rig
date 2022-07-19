import maya.cmds as cmds
import maya.api.OpenMaya as aom

def distLength(itemA, itemB):
	vA = aom.MVector(cmds.xform(itemA, q = True, ws = True, t = True))
	vB = aom.MVector(cmds.xform(itemB, q = True, ws = True, t = True))
	dist = aom.MVector(vB-vA).length()

	return dist

def getBarycenter(items = []):
	posX, posY, posZ = [], [], []
	for item in items:
		pos = cmds.xform(item, q = True, ws = True, t = True)
		posX.append(pos[0]), posY.append(pos[1]), posZ.append(pos[2])

	avrX, avrY, avrZ =  sum(posX)/len(posX), sum(posY)/len(posY), sum(posZ)/len(posZ)

	return avrX, avrY, avrZ

def bsFromMsh(msh):
	mshBaseName = msh.split(':')[-1]

	blsNode = cmds.listConnections('%s.inMesh'%msh, s = True, type = 'blendShape') or []
	if blsNode:
		tgts = cmds.listAttr('%s.weight'%blsNode[0], m = True) or []
		for tgt in tgts:
			if tgt == mshBaseName:
				return blsNode[0], tgt

def updateTplPosition(msh, tpl):

	closestVtx = []
	bsTgt, bsAttr = bsFromMsh(msh)

	cmds.setAttr('%s.%s'%(bsTgt, bsAttr), 0)

	nbrVtx = cmds.polyEvaluate(msh, v = True)

	#Get Closest Vtx
	distVtxFromTpl = {}
	for i in range(nbrVtx):
		vtx = '%s.vtx[%s]'%(msh, i)
		dist = distLength(tpl, vtx)
		distVtxFromTpl[dist] = vtx


	#Get Bar From 100 ClosestVtx
	distVtxFromTplSorted = sorted(distVtxFromTpl.keys())[:100]

	barX, barY, barZ = [], [], []
	for i in range(100):
		vtx =  distVtxFromTpl[distVtxFromTplSorted[i]]

		closestVtx.append(vtx)


	posBarInit = getBarycenter(closestVtx)
	#loc = cmds.spaceLocator(n = 'bar_loc')[0]
	#cmds.xform(loc, ws = True, t = posBarInit)

	#Get Offset between currTpl and barInit
	vTpl = aom.MVector(cmds.xform(tpl, q = True, ws = True, t = True))
	vBar = aom.MVector(posBarInit)
	vOffset = aom.MVector(vTpl-vBar)

	#Get New Bar From BS
	cmds.setAttr('%s.%s'%(bsTgt, bsAttr), 1)

	currBar = getBarycenter(closestVtx)

	currBarLoc = cmds.spaceLocator(n = 'new%sPos_loc'%tpl)[0]
	#cmds.xform(currBarLoc, ws = True, t = currBar)


	#locOffset = cmds.duplicate(currBarLoc, n = 'new%sPos_loc'%tpl)[0]
	cmds.xform(currBarLoc, ws = True, t = [currBar[0]+vOffset[0], currBar[1]+vOffset[1], currBar[2]+vOffset[2]])

	return currBarLoc

#updateTplPosition('ROOT:MOD:msh_body', 'ROOT:tpl_armMtr_1_L')


def ctrlFromTplMaster(tpl):
    #tpl = 'ROOT:tplRig_spine_1'
    toUpdate = []
    allFromTpl = cmds.listRelatives(tpl, ad = True)
    for item in allFromTpl:
        if item.startswith('ROOT:tpl_') or item.startswith('ROOT:FACE:tpl_') and cmds.nodeType(item) == 'joint':
            toUpdate.append(item)


	return toUpdate


def test(msh, lTpl):
    dicSuce = {}
    i = 1
    ctrls = lTpl #ctrlFromTplMaster(tpl)
    for ctrl in ctrls:
        if mc.listRelatives(ctrl, s=True, ni=True):
            if mc.objectType(mc.listRelatives(ctrl, s=True, ni=True)[0]) == 'nurbsCurve':
                print 'Step 1: %s/%s'%(i, len(ctrls))
                loc = updateTplPosition(msh, ctrl)
                dicSuce[ctrl] = loc
                i += 1

    i = 1
    for ctrl in dicSuce.keys():
        print 'Step 2:%s/%s'%(i, len(ctrls)+1)
        lLocked = []
        for attr in ['X', 'Y', 'Z']:
            if cmds.getAttr(ctrl+'.translate'+attr, lock=True):
                lLocked.append(attr.lower())
        if lLocked:
            cmds.pointConstraint(dicSuce[ctrl], ctrl, mo=False, skip=lLocked)
        else:
            cmds.pointConstraint(dicSuce[ctrl], ctrl, mo=False)
        i+=1

lTpl = mc.ls('*.infPart', r=True, o=True)
test('ROOT:MOD:msh_body', lTpl)




