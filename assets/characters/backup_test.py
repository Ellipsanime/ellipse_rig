######################### TEST  LOFT BY PART##############################################################
# ADJUST SA POSITION__________________________________________________
adjustNumb = 2
selDiv2 = int(math.ceil(float(len(lsChainFk))/adjustNumb))
val = 0
dictPart ={}
for each2 in range(selDiv2):
    part= []
    for each in range(adjustNumb):
        part.append(lsChainFk[each+val])
    val += 1
    dictPart[each2]= part

for key, value in dictPart.items():
    nTestLoft = gloss.name_format(prefix=gloss.lexicon('loft'),name=self.name,nFunc=gloss.lexicon('base')+'Test'+str(key),nSide=side,incP=incPart)
    valScl = float(mc.getAttr(self.nWorld + '.scaleX'))
    lsJntLoft =[]
    for i, each in enumerate(value):
        nJntLoft= gloss.renameSplit(selObj=each, namePart=['c','jnt'], newNamePart=['loftJnt%s'%(i+1),'loftJnt%s'%(i+1)], reNme=False)
        libRig.createObj(partial(mc.joint, **{'n': nJntLoft}), match=[each], father=each,
                    attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})
        lsJntLoft.append(nJntLoft)
    # Adjust Parentage to create a good oreintation curve
    [mc.parent(each,w=True) for each in lsJntLoft]
    [mc.parent(each,lsJntLoft[i]) for i, each in enumerate(lsJntLoft[1:])]

    getCrv = lib_curves.createDoubleCrv(objLst=lsJntLoft, axis='Z', offset=0.2 * valScl)
    [mc.parent(each,value[i]) for i, each in enumerate(lsJntLoft)]

    lsCv = []
    for i, each in enumerate(getCrv['crv']):
        nCv = mc.rename(each,gloss.name_format(prefix=gloss.lexicon('cv'),name=self.name,nFunc=gloss.lexicon('base')+str(key)+'Test'+str(i+1),nSide=side,incP=incPart))
        mc.skinCluster(lsJntLoft, nCv, tsb=1, mi=1)
        lsCv.append(nCv)
    degree =3
    loftBase = libRig.createObj(partial(mc.loft, lsCv[0], lsCv[1:],**{'n':nTestLoft, 'ch':True, 'u':True,'c':0,'ar':1,'d':degree,'ss':0,'rn':0,'po':0,'rsn':True})
                              , father=None, refObj=None, incPart=False, attributs=None)
    sbDvLoft = (degree*5)-1
    mc.rebuildSurface(nTestLoft,ch=True,rpo=True,rt=0,end=True, dir=2, su=sbDvLoft, sv=1, du=3,dv=3,tol=0.01)





     # concat Arc_________________
    lsConcatArc = lsArcCtr
    lenLs = 1
    for i, each in enumerate(lsCtrArcBisCtr):
        lsConcatArc.insert(lenLs + (i), each)
        lenLs += 1
    # create Jnt to skin LoftSK
    nLoftBaseSk = gloss.name_format(prefix=gloss.lexicon('loft'),name=self.name,nFunc=gloss.lexicon('base')+'Sk',nSide=side,incP=incPart)
    lsJntLoftSk =[]
    for i, each in enumerate(lsConcatArc):
        nJntLoftSk = gloss.name_format(prefix=gloss.lexicon('cv'), name=self.name, nFunc=gloss.lexicon('arc')+'Sk'+str(i+1),nSide=side,incP=incPart)
        libRig.createObj(partial(mc.joint, **{'n': nJntLoftSk}), match=[each], father=each,
                         attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})
        lsJntLoftSk.append(nJntLoftSk)
    # Adjust Parentage to create a good orientation curve
    [mc.parent(each,w=True) for each in lsJntLoftSk]
    [mc.parent(each,lsJntLoftSk[i]) for i, each in enumerate(lsJntLoftSk[1:])]
    [mc.parent(each,lsConcatArc[i]) for i, each in enumerate(lsJntLoftSk)]

    # Skin loft
    skinLoftSk = mc.skinCluster(lsJntLoftSk, nLoftBaseSk, tsb=1, bm=1, nw=1,mi=3, omi=True,dr=4, rui=True)

    # create Jnt bind to lsCtrArcBisCtr
    lsArcBindPBis =[]
    for i, each in enumerate(lsCtrArcBisCtr):
        nbindArcBis = gloss.name_format(prefix=gloss.lexicon('bindP'), name=self.name, nFunc=gloss.lexicon('arc')+'Sk'+str(i+1),nSide=side,incP=incPart)
        libRig.createObj(partial(mc.joint, **{'n': nbindArcBis}), match=[each], father=each,attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})
        mc.parent(nbindArcBis,lSaBindArcBis['sa'][i])
        lsArcBindPBis.append(nbindArcBis)

    # concat Bind_________________
    lsConcatArcBind = lsArcBindP
    lenLs = 1
    for i, each in enumerate(lsArcBindPBis):
        lsConcatArcBind.insert(lenLs + (i), each)
        lenLs += 1
    # get bind pre matrix_______________________________
    for i, each in enumerate(lsConcatArcBind):
        mc.connectAttr(each+".worldInverseMatrix[0]", "%s.bindPreMatrix[%s]" % (skinLoftSk[0],i), force=True)


    # SK KNOT IN ARM/LEG_________________________________________________
    lSaTwist = lib_connectNodes.surfAttach(selObj=[nLoftBaseSk], lNumb=2,parentInSA=True, parentSA=nSAGrp,delKnot=True,nameRef='c_Twist')
    valmaxU = (mc.getAttr(nLoftBaseSk + ".minMaxRangeU"))[0][1]
    mc.setAttr(lSaTwist['loc'][0] + ".U",0)
    mc.setAttr(lSaTwist['loc'][1] + ".U",valmaxU)
    nRootTwistUp = gloss.name_format(prefix=gloss.lexicon('root'),name=self.name, nFunc=gloss.lexicon('twist')+'Up',nSide=side,incP=incPart)
    nSkTwistUp = gloss.name_format(prefix=gloss.lexicon('sk'),name=self.name, nFunc=gloss.lexicon('twist')+'Up',nSide=side,incP=incPart)
    rootTwistUp =libRig.createObj(partial(mc.joint, **{'n':nRootTwistUp}),match=[lSaTwist['loc'][0]],father=lSaTwist['sa'][0],
                              attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2})
    skTwistUp =libRig.createObj(partial(mc.joint, **{'n':nSkTwistUp}),match=[rootTwistUp],father=rootTwistUp,
                              attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2})



    nRootTwistDn = gloss.name_format(prefix=gloss.lexicon('root'),name=self.name, nFunc=gloss.lexicon('twist')+'Dn',nSide=side,incP=incPart)
    nSkTwistDn = gloss.name_format(prefix=gloss.lexicon('sk'),name=self.name, nFunc=gloss.lexicon('twist')+'Dn',nSide=side,incP=incPart)
    rootTwistDn =libRig.createObj(partial(mc.joint, **{'n':nRootTwistDn}),match=[lSaTwist['loc'][1]],father=lSaTwist['sa'][1],
                              attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2})
    skTwistDn =libRig.createObj(partial(mc.joint, **{'n':nSkTwistDn}),match=[rootTwistDn],father=rootTwistDn,
                              attributs={"jointOrientX":0,"jointOrientY":0,"jointOrientZ":0,"drawStyle":2})
    mc.setAttr(rootTwistUp + '.rotateY',180)
    mc.setAttr(rootTwistDn + '.rotateY',180)
    if side == "R" and self.name == 'leg':
        mc.setAttr(rootTwistUp + '.rotateZ',-90)
        mc.setAttr(rootTwistDn + '.rotateZ',-90)
    elif side == "L" and self.name == 'arm':
        mc.setAttr(rootTwistUp + '.rotateZ',-90)
        mc.setAttr(rootTwistDn + '.rotateZ',-90)
    else:
        mc.setAttr(rootTwistUp + '.rotateZ',90)
        mc.setAttr(rootTwistDn + '.rotateZ',90)



'''
# create curve to connect CA
nCvDist = gloss.name_format(prefix=gloss.lexicon('cv'),name=self.name,nFunc=gloss.lexicon('dstD'),nSide=side,incP=incPart)
cvDist = mc.curve(n=nCvDist, p=getPos, d=1)
# create sks to skin cvDist
lsSkDist =[]
for i, each in enumerate([dstDimMb,dstDimMbEnd]):
    nSkDist = gloss.renameSplit(selObj=each, namePart=['dstD'], newNamePart=['dstDSk'],reNme=False)
    skDist = libRig.createObj(partial(mc.joint, **{'n': nSkDist}), match=[each], father=each,
             attributs={"jointOrientX": 0, "jointOrientY": 0, "jointOrientZ": 0, "drawStyle": 2})
    lsSkDist.append(skDist)
mc.skinCluster(lsSkDist, cvDist, tsb=1, mi=1)
mc.parent(cvDist,GrpNoTouch)
mc.setAttr (cvDist+".inheritsTransform", 0)
mc.setAttr (cvDist+".visibility", 0)
# CREATE curve info___________________________________________________
nArcLen = gloss.name_format(prefix=gloss.lexicon('arcLen'),name=self.name,nSide=side,incP=incPart)
arclen = mc.arclen(cvDist, ch=True)
nArclen = mc.rename(arclen, nArcLen)
cvLen = mc.getAttr(nArclen + ".arcLength")
# diff between number treads and curve length_________________________
tread = (float(cvLen)/(int(numbPart)+1))
# create CA to curve___________________________________________
numb = int(numbPart)
count = 1
lsCns = [dstDimMb]
lsCA = []
for each in range(numb):
    createSystCv = lib_connectNodes.ConnectCurve(cvLen,tread,numb,count,self.name,incPart,cvDist,side)
    nCnsDist = gloss.name_format(prefix=gloss.lexicon('cns'),name=self.name,nFunc=gloss.lexicon('dstD')+str(count),nSide=side,incP=incPart)
    cnsDist = libRig.createObj(partial(mc.group, **{'n':nCnsDist,'em': True}),match=[createSystCv[0]],father=createSystCv[0],attributs={"rotateX":0,"rotateY":0,"rotateZ":0})
    count += 1
    lsCns.append(cnsDist)
    lsCA.append(createSystCv[0])
lsCns.append(dstDimMbEnd)

## create Distances Dimensions
lsDistDim = []
for i, each in enumerate(lsCns[:-1]):
    getPos = [mc.xform(each2 , q=True, ws=True, translation=True) for j, each2 in enumerate((each,lsCns[i+1]))]
    nDstDimPart = gloss.name_format(prefix=gloss.lexicon('dstD'),name=self.name,nFunc=gloss.lexicon('info')+str(i+1),nSide=side,incP=incPart)
    distDimPart = mc.distanceDimension( sp=(getPos[0][0],getPos[0][1],getPos[0][2]), ep=(getPos[-1][0],getPos[-1][1],getPos[-1][2]))
    rootDstDimPart = mc.pickWalk(distDimPart, d='up')
    mc.rename(rootDstDimPart,nDstDimPart)
    #mc.parent(nDstDimPart,GrpNoTouch)
    getLoc =  mc.listConnections(nDstDimPart)
    NodDecompMatrix = mc.shadingNode( "decomposeMatrix",n="decMatDistDim_%s%s_%s_%s"%(self.name,(i+1),side,incPart), asUtility=True)
    NodDecompMatrix2 = mc.shadingNode( "decomposeMatrix",n="decMatDistDim2_%s%s_%s_%s"%(self.name,(i+1),side,incPart), asUtility=True)
    mc.connectAttr("%s.worldMatrix[0]" %(each), "%s.inputMatrix" %(NodDecompMatrix),force=True)
    mc.connectAttr( "%s.outputTranslate" %(NodDecompMatrix), "%s.startPoint" %(nDstDimPart),force=True)
    mc.connectAttr("%s.worldMatrix[0]" %(lsCns[i+1]), "%s.inputMatrix" %(NodDecompMatrix2),force=True)
    mc.connectAttr( "%s.outputTranslate" %(NodDecompMatrix2), "%s.endPoint" %(nDstDimPart),force=True)
    lsDistDim.append(nDstDimPart)



## parent_____________________________
for each in lsCA :
    mc.parent(each,GrpNoTouch)
for each in lsDistDim :
    mc.parent(each,GrpNoTouch)
'''