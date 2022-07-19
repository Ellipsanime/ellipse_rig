


import maya.cmds as mc


class weightTest:

    valModif =["coucou"]


    # COPY SKINNING_________________________________________________________________________________________________________
    def copySkin(*args):
        # get list selection
        lsObj = mc.ls(sl=True)
        # get skinCluster
        skinCls = mc.listConnections(mc.ls(lsObj[0],o=True)[0],t="skinCluster")[0]
        # list vertex
        lsVtx = mc.filterExpand(lsObj,sm=(31,28,36,47,46))
        # joints influences
        lsJntInf = [mc.skinCluster(skinCls,q=True,wi=True) for each in lsVtx]
        # values skinning
        lsValSkin =[[mc.skinPercent(skinCls, lsVtx[i], query=True,t=jt) for jt in jnt] for i, jnt in enumerate(lsJntInf)]
        # zip list
        lsZip = zip(*lsValSkin)
        # concat list
        lsConcat=[sum(each) for each in lsZip]
        # result new skin
        valSkin =[round(float(each/(len(lsValSkin))),5) for each in lsConcat]
        infoSk = zip(lsJntInf[0],valSkin)
        print infoSk
        return infoSk

    # PASTE SKINNING________________________________________________________________________________________________________
    def pasteSkin(*args):
        print "toto"
        return "toto"
    def copySkin2(*args):
        print "toto"

    # WEIGHT TOOLS__________________________________________________________________________________________________________
    def weightsTools(*args):
        if mc.window("weightsUi", q=1, exists=1) == True:
            mc.deleteUI("weightsUi")

        mc.window("weightsUi", width=250, height=200, mxb=False, mnb=True)
        mc.columnLayout("weightMainLayout", width=350, height=100, parent="weightsUi")
        mc.text(label="Copy/Paste json", width=350, height=50, align="center")

        mc.rowLayout("weightBtnLayout", numberOfColumns=2, width=350, height=50, parent="weightsUi")

        mc.button("CopyB", width=165, label="Copy Weights", command=copySkin, parent="weightBtnLayout")
        mc.button("PasteB", width=165, label="Paste Weights", command=copySkin2, parent="weightBtnLayout")
        mc.showWindow("weightsUi")

inst3 = weightTest()
inst3.weightsTools()

















# CREATE CV SPLINE______________________________________________
nCvSpline1 = gloss.name_format(prefix=gloss.lexicon('cv'),name=self.name, nFunc="Spline"+ str(1),nSide=side,incP=incPart)
nCvSpline2 = gloss.name_format(prefix=gloss.lexicon('cv'),name=self.name, nFunc="Spline"+ str(2),nSide=side,incP=incPart)
crvSpline = lib_curves.createDoubleCrv(objLst=lsTplMidIk, axis='X', offset=0.2 * self.valScl)
# adjust Subdivision Crv
#### WARNING numbSubDv must to be a impair number and >3_________________________________
numbSubDv = 5
createCrvSpline1 = lib_curves.crvSubdivide(crv=crvSpline['crv'][0], subDiv=numbSubDv, subDivKnot=0, degree=3)
nCvSpline1 = mc.rename(crvSpline['crv'][0], gloss.name_format(prefix=gloss.lexicon('cv'), name=self.name,
nFunc='Spline'+ str(1), nSide=side,incP=incPart))
mc.setAttr(nCvSpline1+ ".visibility", 1)
createCrvSpline2 = lib_curves.crvSubdivide(crv=crvSpline['crv'][1], subDiv=numbSubDv, subDivKnot=0, degree=3)
nCvSpline2 = mc.rename(crvSpline['crv'][1], gloss.name_format(prefix=gloss.lexicon('cv'), name=self.name,
nFunc='Spline'+ str(2), nSide=side,incP=incPart))
mc.setAttr(nCvSpline2+ ".visibility", 1)

# skin crvs______________________________________
skinCrvSpline1 = mc.skinCluster(lsSkIk,nCvSpline1, tsb=1, mi=1)[0]
skinCrvSpline2 = mc.skinCluster(lsSkIk,nCvSpline2, tsb=1, mi=1)[0]
# dic to param points _______________________________
listCv1 = mc.ls(nCvSpline1 + '.cv[*]', fl=True)
listCv2 = mc.ls(nCvSpline2 + '.cv[*]', fl=True)
adjNumb = numbSubDv+2
selDiv2 = int(math.ceil(float(len(listCv1))/adjNumb))
val = 0
val2 = 0
dictPartCv1 = {}
dictPartCv2 = {}
for each2 in range(selDiv2):
    lsPartCv1 = []
    lsPartCv2 = []
    for each in range(adjNumb):
        lsPartCv1.append(listCv1[each + val + val2])
        lsPartCv2.append(listCv2[each + val + val2])
    val += adjNumb
    val2 -= 1
    dictPartCv1[each2] = lsPartCv1
    dictPartCv2[each2] = lsPartCv2
# get values Skin___________________________
numbByPart = numbSubDv+2
nbByPart = numbSubDv+2
count = 0
getVal = []
for each in range(numbByPart):
    val = round(abs(float(count)/float(nbByPart -1)), 4)
    count += 1
    getVal.append(val)
invertVal = getVal[::-1]
# MODIFY SKIN VALUES CRVS_________________________________________________
for i, each in enumerate(sorted(dictPartCv1.items())):
    for j, eachPart in enumerate(dictPartCv1.values()[i]):
        mc.skinPercent(skinCrvSpline1,eachPart, r=False,
                       transformValue=[(lsSkIk[i], invertVal[j]),(lsSkIk[i+1], getVal[j])])
for i, each in enumerate(sorted(dictPartCv2.items())):
    for j, eachPart in enumerate(dictPartCv2.values()[i]):
        mc.skinPercent(skinCrvSpline2,eachPart, r=False,
                       transformValue=[(lsSkIk[i], invertVal[j]),(lsSkIk[i+1], getVal[j])])
# create loftBase____________________________________________
nLoftCtr = gloss.name_format(prefix=gloss.lexicon('loft'), name=self.name, nFunc='ctr',nSide=side, incP=incPart)
loftCtr = libRig.createObj(partial(mc.loft,nCvSpline1,nCvSpline2, **{'n': nLoftCtr, 'ch': True, 'u': True, 'c': 0, 'ar': 1,
'd': 3, 'ss': 0, 'rn': 0, 'po': 0, 'rsn': True}), father=None,refObj=None, incPart=False, attributs={"visibility": 1})
