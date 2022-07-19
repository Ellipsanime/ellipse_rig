import maya.cmds as mc



###########################
#           SET           #
###########################

def setNspace(nspace):
    mc.namespace(set=':' + nspace)
# setNspace(':')



###########################
#         RECURS          #
###########################

def recursListNamespace(lNspace, nspace):
    setNspace(':' + nspace)
    findNspace = mc.namespaceInfo(nspace, lon=True) or []
    if findNspace:
        for find in findNspace:
            lNspace.append(find)
    setNspace('')
    return lNspace
# recursListNamespace(lNspace, nspace)


def recursInc(lInc):
    lInc.sort()
    if not lInc[0] == 1:
        lInc[0] = 1
    for i in range(0, len(lInc)):
        if i < len(lInc) - 1:
            if not lInc[i] + 1 == lInc[i + 1]:
                lInc[i + 1] = lInc[i] + 1
                recursInc(lInc)
    return lInc


# recursInc([8, 2, 3, 12, 5, 6, 9, 22, 10, 13, 78])


###########################
#          LIST           #
###########################
def lsChildNspaceOf(nspace):
    """return only children namespace of the given namespace"""
    lNspace = mc.namespaceInfo(nspace, lon=True) or []
    for i in ['UI', 'shared']:
        if i in lNspace:
            lNspace.remove(i)
    return lNspace


def lsAllNspaceOf(nspace):
    """return all namespace of the given namespace"""
    lNspace = mc.namespaceInfo(nspace, lon=True) or []
    for i in ['UI', 'shared']:
        if i in lNspace:
            lNspace.remove(i)
    for nspace in lNspace:
        recursListNamespace(lNspace, nspace)
    return lNspace


#lsAllNspaceOf(getNspaceFromObj(mc.ls(sl=True)[0]))


def lsAllNspace(toExclude = ['UI', 'shared']):
    """return all namespace in the scene (except UI and shared and MOD)"""
    setNspace(':')
    lNspace = []
    try:
        lNspace = mc.namespaceInfo(lon=True) or []
        for i in toExclude:
            if i in lNspace:
                lNspace.remove(i)
        for nspace in lNspace:
            recursListNamespace(lNspace, nspace)
    except:
        pass
    finally:
        return lNspace

# lsAllNspace()

def lsSameModuleType(nspace):
    """return all modules wich are the same type of the given namespace"""
    lBroModules = []
    module = getModuleFromeNspace(nspace)
    nspaceFather = getNspaceFather(nspace)
    lBro = lsAllNspaceOf(nspaceFather)
    for bro in lBro:
        if module in bro:
            lBroModules.append(bro)
    return lBroModules
#lsSameModuleType(':WORLD:EYE_L_1')



###########################
#          CHECK          #
###########################
def chkLInc(lInc):
    if not len(lInc) == lInc[-1]:
        print 'AIE'


# chkLInc(lInc)


def chkTwins(lObj):
    lNspace = []
    lBro = []
    for obj in lObj:
        lNspace.append(getNspaceFromObj(obj))
    for nspace in lNspace:
        lBro.append(nspace[:-len(nspace.split("_")[-1])])
    lLastName = list(set(lBro))
    if len(lLastName) == 1:
        return lNspace[0]


# chkTwins(mc.ls(sl=True))




def removeNsRefs():
    scenePath=mc.file(q=True, sceneName=True)
    lRef=mc.file(scenePath, q=True, reference=True)
    lToExclude = ['UI', 'shared']
    for ref in lRef:
        nSpace=mc.referenceQuery(ref, ns=True)
        nsRef=nSpace.split(':')[-1]
        lToExclude.append(nsRef)
    lNspace = mc.namespaceInfo(lon=True) or []
    for nsRef in lToExclude:
        lNspace.remove(nsRef)

#removeNsRefs()



###########################
#           GET           #
###########################

def getNodeName(obj):
    nNode = obj.split(':')[-1]
    return nNode

# getNodeName(obj)


def getNspaceFromObj(obj):
    nspace = ''
    if ':' in obj:
        nNode = obj.split(':')[-1]
        nspace = obj.replace(':' + nNode, '')
    return nspace


# getNspaceFromObj(mc.ls(sl=True)[0])


def getNspaceFather(nspace):
    nspaceFather = nspace[:-len(nspace.split(":")[-1]) - 1]
    # nspaceFather = nspace.replace(nspace.split(':')[-1], '')
    return nspaceFather


# getNspaceFather(getNspaceFromObj(mc.ls(sl=True)[0]))


def getInc(nspace):
    inc = nspace.split('_')[-1]
    return inc


# getInc(getNspaceFromObj(mc.ls(sl=True)[0]))

def getSide(nspace):
    side = ''
    trunk = nspace.split('_')
    if len(trunk) == 3:
        side = trunk[1]
    return side


def getTwins(nspace):
    """return all namespace who are the same of the given except the final incrementation"""
    lTwins = []
    chkChil = nspace[:-len(nspace.split("_")[-1])]
    nspaceFather = getNspaceFather(nspace)
    lBro = lsAllNspaceOf(nspaceFather)
    for bro in lBro:
        inc = getInc(bro)
        if bro == chkChil + str(inc):
            lTwins.append(bro)
    return lTwins


# getTwins(getNspaceFromObj(mc.ls(sl=True)[0]))

def getClones(nspace):
    """return all namespace who are the same of the given """
    lClones = []
    nspaceFather = getNspaceFather(nspace)
    lBro = lsAllNspaceOf(nspaceFather)
    for bro in lBro:
        if bro == nspace:
            lClones.append(bro)
    return lClones


def getNspaceHI():
    """return the hi off all the nspace in the scene in a dictionary [father1] -> [namespace1]; [father2] -> [nsamespace2]..."""
    lNspace = lsAllNspace()
    dicLNspace = {}
    inc = 1
    for nspaceLong in lNspace:
        nspace = nspaceLong.split(':')[-1]
        father = getNspaceFather(nspaceLong)
        dicLNspace['namespace' + str(inc)] = nspace
        dicLNspace['father' + str(inc)] = father
        inc += 1
    return dicLNspace


# getNspaceHI()


def getModuleFromeNspace(nspace):
    module = nspace.split(':')[-1]
    moduleType = module
    if '_' in module:
        moduleType = module.split('_')[0]
    return moduleType


def getNsapceRIG(nspaceTPL):
    nspaceRIG = nspaceTPL.replace(nspaceTPL.split(':')[0] + ':', '')
    return nspaceRIG

def getModuleSide(module):
    side = ''
    if len(module.split('_')) >= 3:
        side = module.split('_')[1]
    return side

def getSymModuleHi(module):
    side = getSide(module)
    symModule = ''
    if side in ['Left', 'L', '_L']:
        symModule = module.split('_')[0] + '_' + 'R' + '_' + module.split('_')[-1]
    elif side in ['Right', 'R', '_R']:
        symModule = module.split('_')[0] + '_' + 'L' + '_' + module.split('_')[-1]
    return symModule


def getNspaceTrunk(nspace):
    lModules = nspace.split(':')
    branch = []
    trunk = ''
    for module in lModules:
        if '_L_' in module or '_R_' in module:
            break
        branch.append(module)
        trunk = trunk + module + ':'
    return trunk


# getNspaceTrunk('TPL:WORLD:SPINE_1:CLAV_L_1:ARM_L_1:SPINE_1:')


def getNspaceSym(nspace):
    trunk = getNspaceTrunk(nspace)
    branchs = nspace.replace(trunk, '')
    lBranchs = branchs.split(':')
    nspaceSym = trunk
    for leaf in lBranchs:
        moduleSym = leaf
        if not getSide(leaf) == '':
            moduleSym = getSymModuleHi(leaf)
        nspaceSym = nspaceSym + moduleSym +':'
    return nspaceSym [: -1]
#getNspaceSym(namespace.getNspaceFromObj(mc.ls(sl=True)[0]))


###########################
#           DELETE        #
###########################

def removeNspace(nspace, keep=True):
    if mc.namespace(ex=':'+nspace):
        mc.namespace(rm=':'+nspace, mnr=keep)
#remNspace(nspace, keep=True)



###########################
#           EXE           #
###########################


def crtNspace(nspace, makeInc):
    if not mc.namespace(ex=':' + naming.nsTpl):
        mc.namespace(add=naming.nsTpl, parent=':')
    nspaceFather = ':' + naming.nsTpl
    newNspace = ''
    lInc = []
    inc = 1
    lFathers = mc.ls(sl=True) or []
    if lFathers:
        father = lFathers[0]
        fullNspace = getNspaceFromObj(father)
        if fullNspace == '':
            nspaceFather = ':' + naming.nsTpl
        else:
            node = father.split(':')[-1]
            nspaceFather = father.replace(':' + node, '')
        if mc.namespace(ex=':' + nspaceFather + ':' + nspace + '_' + str(inc)):
            lNspace = lsAllNspaceOf(nspaceFather)
            lNspace = getTwins(nspaceFather +':' + nspace+'_'+str(inc))
            for id in lNspace:
                lInc.append(int(id.split('_')[-1]))
            lInc.sort()
            inc = int(lInc[-1]) + inc
    # newNspace=mc.namespace(add=nspace+'_'+str(inc), parent=':'+nspaceFather)
    if makeInc != 0:
        newNspace = mc.namespace(add=nspace + '_' + str(inc), parent=':' + nspaceFather)
    elif makeInc == 0:
        newNspace = mc.namespace(add=nspace, parent=':' + nspaceFather)
    setNspace(newNspace)
    return newNspace
# crtNspace('FINGER_L')



def transNspace(nsapceSource, nspaceDest):
    # transfer tout le contenue du namespaceSource (nspace et nodes)
    # dans un nspaceDestination qui est frere du nspaceSource (sous le meme parent)
    lNspace = lsChildNspaceOf(nsapceSource)
    if not mc.namespace(ex=':' + nspaceDest):
        mc.namespace(add=nspaceDest, parent=nsapceSource)
    for nspace in lNspace:
        if not nspace == 'MOD':
            mc.namespace(add=nspace, parent=':' + nspaceDest)
            mc.namespace(moveNamespace=(':' + nspace, ':' + nspaceDest + ':' + nspace))
            mc.namespace(removeNamespace=':' + nspace)

# transNspace(':', 'TPL')
"""


def transNspace(nspaceSource, nspaceDest):
    # transfer tout le contenue du namespaceSource (nspace et nodes)
    # dans un nspaceDestination qui est frere du nspaceSource (sous le meme parent)
    lNspace = lsChildNspaceOf(nspaceSource)
    if not mc.namespace(q=True, ir=nspaceSource):
        nspace = nspaceSource.split(':')[-1]
        module = getModuleFromeNspace(nspace)
        side = getSide(nspace)
        nspaceFather = nspaceSource[:-len(nspaceSource.split(":")[-1]) - 1]
        mc.select(':' + nspaceDest + ':*')
    crtNewNspace = crtNspace(module + '_' + side, 1)

    for nspace in lNspace:
        mc.namespace(add=nspace, parent=':' + nspaceDest)
        mc.namespace(moveNamespace=(':' + nspace, ':' + nspaceDest + ':' + nspace))
        mc.namespace(removeNamespace=nspace)


# transNspace('WORLD:SPINE_1:CLAV_R_1:FOOT_L_1', 'WORLD:SPINE_1:CLAV_R_1:ARM_R_1')
"""


def rebuildnSpaceHI():
    hi = getNspaceHI(lsAllNspace())
    for i in range(2, (len(hi) / 2) + 1):
        leaf = hi['father' + str(i)]
        if naming.nsTpl in leaf:
            nspaceRigFather = hi['father' + str(i)][len(hi['father' + str(i)].split(':')[0]):]
            newNspace = mc.namespace(add=hi['namespace' + str(i)], parent=':' + nspaceRigFather)
        i += 1
# rebuildnSpaceHI()



def reparentNspace(child, nspaceDest):
        nspaceSource = getNspaceFromObj(child)
        chkNspaceFather = getNspaceFather(nspaceSource)
        nspace = nspaceSource.split(':')[-1]
        newNspace = nspaceDest+':'+nspace
        if not nspaceDest == chkNspaceFather:
            chkTwins = getClones(nspaceDest + ':' + nspace)
            if len(chkTwins) > 0:
                mc.warning('their is still a ' + nspace + ' in ' + nspaceDest + ' :', chkTwins)
            else:
                newNspace = mc.namespace(add=nspace, parent=':' + nspaceDest)
                mc.namespace(moveNamespace=(':' + nspaceSource, ':' + nspaceDest + ':' + nspace))
                mc.namespace(removeNamespace=':' + nspaceSource)
        return newNspace
#reparentNspace(mc.ls(sl=True))
