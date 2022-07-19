import maya.cmds as mc


def activeDef(shp, val):
    if mc.objectType(shp) == 'transform':
        shp = mc.listRelatives(shp, s=True, ni=True)[-1]
    lDef = mc.findDeformers(shp)
    if lDef:
        for node in lDef:
            mc.setAttr(node + '.envelope', val)



def compareSteps(srcStep, lDestSteps, onlyMsh):
    lMshShp = mc.listRelatives(srcStep + ':*', f=True, type='mesh') or []
    if lMshShp:
        lMsh = []
        dicCompare = {}
        dicCompare['unfound'] = {}
        dicCompare['unmatch'] = {}
        for shp in lMshShp:
            msh = mc.listRelatives(shp, p=True, f=True)[0]
            if onlyMsh == True:
                if msh.split('|')[-1].split(':')[-1].startswith('msh_'):
                    if not msh in lMsh:
                        lMsh.append(msh)
            else:
                if not msh in lMsh:
                    lMsh.append(msh)
        for msh in lMsh:
            for destStep in lDestSteps:
                chk = False
                mshDest = msh.replace(srcStep, destStep)
                if not mc.objExists(mshDest):
                    if not msh in dicCompare['unfound'].keys():
                        dicCompare['unfound'][msh] = []
                    dicCompare['unfound'][msh].append(destStep)
                else:
                    activeDef(mc.listRelatives(msh, s=True, ni=True)[-1], False)
                    activeDef(mc.listRelatives(mshDest, s=True, ni=True)[-1], False)
                    dupMsh = mshDest

                    if not mc.polyCompare(msh, dupMsh, v=True, fd=True) == 0:
                        if not msh in dicCompare['unmatch'].keys():
                            dicCompare['unmatch'][msh] = []
                        dicCompare['unmatch'][msh].append(destStep)
                    activeDef(mc.listRelatives(msh, s=True, ni=True)[-1], True)
                    activeDef(mc.listRelatives(mshDest, s=True, ni=True)[-1], True)

    return dicCompare


#compareSteps('SHD:', ['RIG:'], True)