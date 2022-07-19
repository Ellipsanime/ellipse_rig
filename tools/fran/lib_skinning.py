from maya import cmds as mc
from maya import mel
from maya.OpenMaya import *
import cStringIO, re
from math import pow, sqrt
from ellipse_rig.library import lib_kdTree
reload(lib_kdTree)



class SkinningTools(object):

    def __init__(self,*args):
        self.Default = ''


    ### RETURN SKIN CLUSTER_____________________________________________________________________________________________
    @staticmethod
    def returnSkinCluster(mesh, silent=False):
        '''
        static function to get the skincluster from any mesh
        @param mesh=None: mesh to get the skinCluster
        @param silent: flag to display warning dialog or to silently continue the current function
        '''
        skinCluster = "please select object"
        if mesh != []:
            try:
                shp = mc.listRelatives(mesh, s=True)[0]
                if mc.objectType(shp) == 'mesh':
                    skinCluster = mel.eval('findRelatedSkinCluster("%s");' % shp)
                    if not skinCluster:
                        if silent == False:
                            mc.confirmDialog(title='Error', message='no SkinCluster found on: %s!' % shp, button=['Ok'],
                                               defaultButton='Ok', cancelButton='Ok', dismissString='Ok')
                        else:
                            skinCluster = None
            except:
                skinCluster = mc.warning("object's not a mesh")
        else:
            skinCluster = mc.warning("please select object")
        return skinCluster
    """ returnSkin = lib_skinning.SkinningTools.returnSkinCluster(mc.ls(sl=True))"""

    ### CONVERT TO VERTEX LIST__________________________________________________________________________________________
    def convertToVertexList(self, object):
        '''
        conveniently converts every polygonal selection to vertices as vertices are the components on which skin is applied
        @param object: can be either the mesh, the shape or a component based selection
        selection will be flattened so each vertix is listed without nesting (i.e. ['.vtx[0:20]'] becomes ['.vtx[0]', '.vtx[1]', .....])
        '''
        convertedVertices = mc.polyListComponentConversion(object, tv=True)
        expandedVertices = mc.filterExpand(convertedVertices, sm=31)
        return expandedVertices
    """lsObj = mc.ls(sl=True); conv = lib_skinning.SkinningTools(); print conv.convertToVertexList(lsObj)"""

    ### GET INFLUENCE JOINT_____________________________________________________________________________________________
    def getInfluencingjoints(self, mesh=None):
        '''returns all the joints that influence the mesh'''
        skinClusterName = SkinningTools.returnSkinCluster(mesh, silent=True)
        if skinClusterName != None:
            jointInfls = mc.skinCluster(skinClusterName, q=True, inf=True)
            return jointInfls

    ### RESET SKIN JOINT________________________________________________________________________________________________
    def resetSkinnedJoints(self, lsJnt=None):
        '''recomputes all prebind matrices in this pose, joints will stay in place while the mesh goes back to bindpose'''
        # http://leftbulb.blogspot.nl/2012/09/resetting-skin-deformation-for-joint.html
        for joint in lsJnt:
            skinClusterPlugs = mc.listConnections(joint + ".worldMatrix[0]", type="skinCluster", p=1)
            if skinClusterPlugs:
                for skinClstPlug in skinClusterPlugs:
                    index = skinClstPlug[skinClstPlug.index("[") + 1: -1]
                    skinCluster = skinClstPlug[: skinClstPlug.index(".")]
                    curInvMat = mc.getAttr(joint + ".worldInverseMatrix")
                    mc.setAttr(skinCluster + ".bindPreMatrix[%s]" % index, type="matrix", *curInvMat)
            else:
                mc.warning("no skinCluster attached to %s!" % joint)
    """lsObj=mc.ls(sl=True);resetSkinJnt = lib_skinning.SkinningTools();
    print resetSkinJnt.resetSkinnedJoints(lsJnt =lsObj)"""

    ### REMOVE BIND POSE________________________________________________________________________________________________
    def removeBindPoses(self):
        '''deletes all bindpose nodes from current scene'''
        dagPoses = mc.ls(type="dagPose")
        for dagPose in dagPoses:
            if not mc.getAttr("%s.bindPose" % dagPose):
                continue
            mc.delete(dagPose)

    ### RESET BIND POSE_________________________________________________________________________________________________
    def resetToBindPose(self, in_mesh):
        ''' reset the object back to bindpose without the need of the bindpose node!
        calculates the bindpose through the prebind matrix of the joints'''

        def getMayaMatrix(data):
            mMat = MMatrix()
            MScriptUtil.createMatrixFromList(data, mMat)
            return mMat

        def mayaMatrixToList(mMatrix):
            d = []
            for x in range(4):
                for y in range(4):
                    d.append(mMatrix(x, y))
            return d

        skinCluster = SkinningTools.returnSkinCluster(in_mesh, silent=True)
        if skinCluster == None:
            return

        infjnts = mc.skinCluster(skinCluster, q=True, inf=True)
        bindPoseNode = mc.dagPose(infjnts[0], q=True, bindPose=True)
        if bindPoseNode != None:
            mc.select(in_mesh)
            mel.eval("gotoBindPose;")
        else:
            ''' reset the object back to bindpose without the need of the bindpose node!'''
            for i, joint in enumerate(infjnts):
                prebindMatrix = mc.getAttr(skinCluster + ".bindPreMatrix[%s]" % i)
                matrix = mayaMatrixToList(getMayaMatrix(prebindMatrix).inverse())
                mc.xform(joint, ws=True, m=matrix)

    ### UNLOCK ZERO INFLUENCE JOINT_____________________________________________________________________________________
    def addUnlockedZeroInf(self,lsJnt=None,refMesh=None):
        '''adds joints to the current mesh without altering the weights, and makes sure that the joints are unlocked
        @param lsJnt: joints to be added to the mesh
        @param refMesh: mesh onto which the joints will be added as an influence
        '''
        skinClusterName = SkinningTools.returnSkinCluster(refMesh, silent=True)
        if skinClusterName != None:
            jointInfls = mc.skinCluster(skinClusterName, q=True, inf=True)
            for joint in lsJnt:
                if joint in jointInfls:
                    continue
                mc.skinCluster(skinClusterName, e=True, lw=False, wt=0.0, ai=joint)
    """lsObj = mc.ls(sl=True);unlockJnt = lib_skinning.SkinningTools()
    ;print unlockJnt.addUnlockedZeroInf(lsJnt=lsObj[:-1], refMesh=lsObj[-1])"""

    ### SYNCHRONISATION JOINTS BETWEEN MESH_____________________________________________________________________________
    def synchroJntsBetweenMesh(self, skinObjects, query=False):
        '''makes sure that given skinobjects have the same joints influencing,
        its a safety measure when copying weights between different objects'''
        compareLists = []
        for skinObject in skinObjects:
            skinClusterName = SkinningTools.returnSkinCluster(skinObject, True)
            if skinClusterName == None:
                continue
            joints = mc.skinCluster(skinClusterName, q=True, inf=True)
            compareLists.append([skinObject, joints])

        totalCompares = len(compareLists)
        missingJointsList = []
        for i in range(totalCompares):
            for list in compareLists:
                if list == compareLists[i]:
                    continue
                missedjoints = []
                for match in list[1]:
                    if not any(match in value for value in compareLists[i][1]):
                        missedjoints.append(match)

                missingJointsList.append([compareLists[i][0], missedjoints])
        if query == True:
            joints = []
            for missingList in missingJointsList:
                for joint in missingList[1]:
                    joints.append(joint)
            if len(joints) == 0:
                return None
            else:
                return True
        else:
            for missingJoints in missingJointsList:
                skinClusterName = SkinningTools.returnSkinCluster(missingJoints[0], True)
                for joint in missingJoints[1]:
                    try:
                        mc.skinCluster(skinClusterName, e=True, lw=False, wt=0.0, ai=joint)
                    except:
                        pass

    """lsObj = mc.ls(sl=True);compareJntInf = lib_skinning.SkinningTools();
    print compareJntInf.synchroJntsBetweenMesh(lsObj)"""



    ### COPY SOURCE TARGET______________________________________________________________________________________________
    def execCopySourceTarget(self, TargetSkinCluster, SourceSkinCluster, TargetSelection, SourceSelection,
                             smoothValue=1, progressBar=None, amount=1, undoState=True):
        if undoState:
            mc.undoInfo(state=True)
            mc.undoInfo(ock=True)

        self.sourcePoints = []
        self.sourcePointPos = []
        # make sure that both objects have the same joints
        mesh1 = TargetSelection[0].split('.')[0]
        mesh2 = SourceSelection[0].split('.')[0]
        joint = mc.skinCluster(SourceSkinCluster, q=True, inf=True)
        joint1 = mc.skinCluster(TargetSkinCluster, q=True, inf=True)
        jointAmount = len(joint)
        skinClusterName = SkinningTools.returnSkinCluster(mesh1, True)
        bindPoseNode = mc.dagPose(joint[0], q=True, bindPose=True)
        if bindPoseNode:
            outOfPose = mc.dagPose(bindPoseNode, q=True, atPose=True)

        sourceInflArray = mc.SkinWeights([mesh2, SourceSkinCluster], q=True)
        targetInflArray = mc.SkinWeights([mesh1, TargetSkinCluster], q=True)

        sameMesh = True
        if mesh1 != mesh2:
            sameMesh = False
            compared = self.synchroJntsBetweenMesh([mesh1, mesh2], True)
            if compared != None:
                if outOfPose != None:
                    result = mc.confirmDialog(title='Confirm',
                                                message='object is not in BindPose,\ndo you want to continue out of bindpose?\npressing "No" will exit the operation! ',
                                                button=['Yes', 'No'],
                                                defaultButton='Yes',
                                                cancelButton='No',
                                                dismissString='No')
                    if result == "Yes":
                        self.synchroJntsBetweenMesh([mesh1, mesh2])
                    else:
                        return
                else:
                    self.synchroJntsBetweenMesh([mesh1, mesh2])

        for sourceVert in SourceSelection:
            pos = mc.xform(sourceVert, q=True, ws=True, t=True)
            self.sourcePoints.append(pos)
            self.sourcePointPos.append([sourceVert, pos])
        sourceKDTree = lib_kdTree.KDTree.construct_from_data(self.sourcePoints)

        if progressBar:
            oldValue = progressBar.value()
            if oldValue == 100:
                oldValue = 0
            totalVertices = len(TargetSelection)
            percentage = (99.0 / totalVertices) / amount
            iteration = 1;

        weightlist = []
        for targetVertex in TargetSelection:
            pos = mc.xform(targetVertex, q=True, ws=True, t=True)
            pts = sourceKDTree.query(query_point=pos, t=smoothValue)

            weights = []
            distanceWeightsArray = []
            totalDistanceWeights = 0
            for positionList in self.sourcePointPos:
                for index in range(smoothValue):
                    if pts[index] != positionList[1]:
                        continue
                    length = sqrt(pow((pos[0] - pts[index][0]), 2) +
                                  pow((pos[1] - pts[index][1]), 2) +
                                  pow((pos[2] - pts[index][2]), 2))

                    distanceWeight = (1.0 / (1.0 + length))
                    distanceWeightsArray.append(distanceWeight)
                    totalDistanceWeights += distanceWeight

                    weight = []
                    indexing = int(positionList[0].split('.vtx[')[-1].split(']')[0])
                    for i in range(jointAmount):
                        weight.append(sourceInflArray[(indexing * jointAmount) + i])
                    weights.append(weight)

            newWeights = []
            for index in range(smoothValue):
                for i, wght in enumerate(weights[index]):
                    # distance/totalDistance is weight of the distance caluclated
                    weights[index][i] = (distanceWeightsArray[index] / totalDistanceWeights) * wght

                if len(newWeights) == 0:
                    newWeights = list(range(len(weights[index])))
                    for j in range(len(newWeights)):
                        newWeights[j] = 0.0

                for j in range(len(weights[index])):
                    newWeights[j] = newWeights[j] + weights[index][j]

            divider = 0.0
            for wght in newWeights:
                divider = divider + wght
            weightsCreation = []
            for jnt in joint1:
                for count, skinJoint in enumerate(joint):
                    if jnt != skinJoint:
                        continue
                    weightsCreation.append((newWeights[count] / divider))
            weightlist.extend(weightsCreation)

            if progressBar:
                progressBar.setValue(oldValue + (percentage * iteration))
                qApp.processEvents()
                iteration += 1;

        index = 0
        for vertex in TargetSelection:
            number = int(vertex.split('.vtx[')[-1].split(']')[0])
            for jointIndex in range(jointAmount):
                weightindex = (number * jointAmount) + jointIndex
                targetInflArray[weightindex] = weightlist[index]
                index += 1

        mc.SkinWeights([mesh1, TargetSkinCluster], nwt=targetInflArray)

        if progressBar:
            if amount == 1:
                progressBar.setValue(100)

        if undoState:
            mc.undoInfo(cck=True)

    '''
    ### TRANSFERT CLOSEST SKINNING______________________________________________________________________________________
    def transferClosestSkinning(self, objects, smoothValue, progressbar):
        object1 = objects[0]
        skinCluster = SkinningTools.returnSkinCluster(object1)
        baseJoints = mc.skinCluster(skinCluster, q=True, inf=True)
        amount = len(objects) - 1

        mc.undoInfo(state=True)
        mc.undoInfo(ock=True, cn="transferClosestSkinning")

        for object in objects:
            if object == object1:
                continue

            skinCluster1 = SkinningTools.returnSkinCluster(object, silent=True)
            if skinCluster1 == None:
                skinCluster1 = mc.skinCluster(object, baseJoints)[0]
            else:
                self.synchroJntsBetweenMesh([object1, object])

            self.execCopySourceTarget(skinCluster1, skinCluster, self.convertToVertexList(object),
                                      self.convertToVertexList(object1), smoothValue, progressbar, amount, False)
        #progressbar.setValue(100)

        mc.undoInfo(cck=True, cn="transferClosestSkinning")
    '''




    ### TRANSFER SKIN___________________________________________________________________________________________________
    def transferSkinning(self, refMesh=None, lsTargetMesh=None, inPlace=True):
        '''using native maya copyskinweight to generate similar weight values
        @param refMesh: mesh to copy skinning information from
        @param lsTargetMesh: all other meshes that will gather weight information from the refMesh
        @param inPlace: if True will make sure to cleanup the mesh and apply the skinning (also to be used for freezin the mesh in pose),
                        when false it assumes skinning is already applied to lsTargetMesh and just copies the weights'''
        skinclusterBase = SkinningTools.returnSkinCluster(refMesh, silent=False)
        if skinclusterBase == None:
            return

        for skin in lsTargetMesh:
            if inPlace:
                mc.delete(skin, ch=True)
            else:
                skincluster = SkinningTools.returnSkinCluster(skin, silent=False)
                if skincluster == None:
                    continue
                mc.skinCluster(skincluster, e=True, ub=True)

            jointInfls = mc.skinCluster(skinclusterBase, q=True, inf=True)
            maxInfls = mc.skinCluster(skinclusterBase, q=True, mi=True)
            self.removeBindPoses()
            newSkinCl = mc.skinCluster(jointInfls, skin, mi=maxInfls)
            mc.copySkinWeights(ss=skinclusterBase, ds=newSkinCl[0], nm=True, surfaceAssociation="closestComponent",
                                 influenceAssociation=["label", "closestBone"], normalize=True)
    """lsObj = mc.ls(sl=True); transfSkin = lib_skinning.SkinningTools(); 
    print transfSkin.transferSkinning(refMesh=lsObj[0],lsTargetMesh=[lsObj[1]])"""

    ### ???????_________________________________________________________________________________________________________
    def Copy2MultVertex(self):
        mc.undoInfo(ock=True)
        selection = mc.ls(os=True,fl=True)
        print selection
        lastSelected  = selection[-1]
        pointList     = [x for x in selection if x!= lastSelected ]

        baseMesh = lastSelected.split('.')[0]
        meshShapeName = mc.listRelatives(baseMesh, s=True)[0]
        skinClusterName = SkinningTools.returnSkinCluster(baseMesh, True)

        SkinWeightCopyInfluences = mc.skinCluster(skinClusterName,q=True, inf=True)
        print SkinWeightCopyInfluences
        SkinWeightCopyWeights = mc.skinPercent(skinClusterName, lastSelected , query=True, value=True )
        print SkinWeightCopyWeights
        # using selection is faster then going through for loop ... thank you maya!
        mc.select(pointList)
        command = cStringIO.StringIO()
        command.write('mc.skinPercent("%s", transformValue=['%(skinClusterName))

        for count, skinJoint in enumerate( SkinWeightCopyInfluences ):
            command.write('("%s", %s)'%(skinJoint, SkinWeightCopyWeights[count]))
            if not count == len(SkinWeightCopyInfluences)-1:
                 command.write(', ')
        command.write('], normalize=False, zeroRemainingInfluences=True)')
        eval(command.getvalue())

        mc.undoInfo(cck=True)
        '''
        if mc.selectPref(trackSelectionOrder=True,q=True):
            mc.selectPref(trackSelectionOrder=False)
        else:
            mc.selectPref(trackSelectionOrder=True)
        '''




    ### AVERAGE VERTEX__________________________________________________________________________________________________
    def AverageVertex(self):
        '''generate an average weigth from all selected vertices to apply to the last selected vertice'''
        mc.undoInfo(state=True)
        mc.undoInfo(ock=True)

        selection = mc.ls(os=True, fl=True)
        vertexAmount = len(selection)
        if vertexAmount < 2:
            mc.error("not enough vertices selected! select a minimum of 2")
        elif vertexAmount == 2:
            # just need 2 and check if selection is a vertex otherwise dont do anything
            if ".vtx" in selection[0] and ".vtx" in selection[-1]:
                vertexNumber1 = int(selection[0].split('vtx[')[-1].split("]")[0])
                vertexNumber2 = int(selection[-1].split('vtx[')[-1].split("]")[0])
                object1 = selection[0].split('.')[0]
            else:
                mc.error("please select 2 vertices!")

            # first choice:
            firstExtendedEdges = mc.polyListComponentConversion(selection[0], te=True)
            firstExtended = mc.filterExpand(firstExtendedEdges, sm=32)
            print firstExtended
            secondExtendedEdges = mc.polyListComponentConversion(selection[-1], te=True)
            secondExtended = mc.filterExpand(secondExtendedEdges, sm=32)

            found = []
            for e1 in firstExtended:
                for e2 in secondExtended:
                    e1n = int(e1.split(".e[")[-1].split("]")[0])
                    e2n = int(e2.split(".e[")[-1].split("]")[0])
                    edgeSel = mc.polySelect(object1, elp=[e1n, e2n], ns=True)
                    if edgeSel == None:
                        continue
                    found.append(edgeSel)
            amountFound = len(found)
            if amountFound != 0:
                if amountFound == 1:
                    edgeSelection = found[0]
                else:
                    edgeSelection = found[0]
                    for sepList in found:
                        if not len(sepList) < len(edgeSelection):
                            continue
                        edgeSelection = sepList
            else:
                # second choice:
                edgeSelection = mc.polySelect(object1, shortestEdgePath=[vertexNumber1, vertexNumber2])
                if edgeSelection == None:
                    mc.error("selected vertices are not part of the same polyShell!")

            skinClusterName = SkinningTools.returnSkinCluster(object1, True)
            listBoneInfluences = mc.skinCluster(object1, q=True, inf=True)

            allEdges = []
            newVertexSelection = []
            for edge in edgeSelection:
                allEdges.append("%s.e[%s]" % (object1, edge))
                midexpand = self.convertToVertexList("%s.e[%s]" % (object1, edge))
                newVertexSelection.append(midexpand)

            firstVert = selection[0]
            lastVert = selection[-1]

            if firstVert in newVertexSelection[0]:
                reverse = False
            else:
                reverse = True

            inOrder = []
            lastVertex = None
            for listVerts in newVertexSelection:
                if firstVert in listVerts:
                    listVerts.remove(firstVert)
                if lastVertex != None:
                    listVerts.remove(lastVertex)
                if lastVert in listVerts:
                    listVerts.remove(lastVert)
                if len(listVerts) != 0:
                    lastVertex = listVerts[0]
                    inOrder.append(lastVertex)

            amount = len(inOrder) + 1

            if reverse:
                inOrder.reverse()

            weights1 = mc.skinPercent(skinClusterName, firstVert, q=True, v=True)
            weights2 = mc.skinPercent(skinClusterName, lastVert, q=True, v=True)

            percentage = float(1.0) / amount
            for index, vertex in enumerate(inOrder):
                currentPercentage = (1 + index) * percentage

                newWeightsList = []
                for idx, weight in enumerate(weights1):
                    value1 = weights2[idx] * currentPercentage
                    value2 = weights1[idx] * (1 - currentPercentage)
                    newWeightsList.append((listBoneInfluences[idx], value1 + value2))

                mc.skinPercent(skinClusterName, vertex, transformValue=newWeightsList)
        else:
            lastSelected = selection[-1]
            pointList = [x for x in selection if x != lastSelected]

            meshName = lastSelected.split('.')[0]
            skinClusterName = SkinningTools.returnSkinCluster(meshName, True)
            mc.skinCluster(meshName, e=True, nw=1)

            listBoneInfluences = mc.skinCluster(meshName, q=True, weightedInfluence=True)
            influenceSize = len(listBoneInfluences)

            TemporaryVertexJoints = []
            TemporaryVertexWeights = []
            for point in pointList:
                for bone in xrange(influenceSize):
                    pointWeights = mc.skinPercent(skinClusterName, point, transform=listBoneInfluences[bone], q=True,
                                                    value=True)
                    if pointWeights < 0.000001:
                        continue
                    TemporaryVertexJoints.append(listBoneInfluences[bone])
                    TemporaryVertexWeights.append(pointWeights)

            totalValues = 0.0
            AvarageValues = []
            CleanList = []
            for i in TemporaryVertexJoints:
                if i not in CleanList:
                    CleanList.append(i)

            for i in xrange(len(CleanList)):
                WorkingValue = 0.0
                for j in xrange(len(TemporaryVertexJoints)):
                    if not TemporaryVertexJoints[j] == CleanList[i]:
                        continue
                    WorkingValue += TemporaryVertexWeights[j]
                numberOfPoints = len(pointList)
                AvarageValues.append((WorkingValue / numberOfPoints))
                totalValues += AvarageValues[i];

            summary = 0
            for Value in xrange(len(AvarageValues)):
                temporaryValue = AvarageValues[Value] / totalValues
                AvarageValues[Value] = temporaryValue
                summary += AvarageValues[Value]

            command = cStringIO.StringIO()
            command.write('mc.skinPercent("%s","%s", transformValue=[' % (skinClusterName, lastSelected))

            for count, skinJoint in enumerate(CleanList):
                command.write('("%s", %s)' % (skinJoint, AvarageValues[count]))
                if not count == len(CleanList) - 1:
                    command.write(', ')
            command.write('])')
            eval(command.getvalue())
        mc.undoInfo(cck=True)















    ############ A DEBUG #################################################

    ### GET VERTEX WITH MAX INFLUENCE NUMBER____________________________________________________________________________
    def getOverMaxInfVertex(self, singleObject=None, maxInfVal=8, notSelect=False, progressBar=None):
        # select all vertices that have more influences then the set Maximum
        if not notSelect:
            mc.undoInfo(ock=True)
        allVerticesOvermaxInfVal = []

        mc.select(singleObject, r=True)
        mel.eval('doPruneSkinClusterWeightsArgList 1 { "0.001" };')

        expandedVertices = self.convertToVertexList(singleObject)
        skinClusterName = SkinningTools.returnSkinCluster(singleObject)
        bones = mc.skinCluster(skinClusterName, q=True, inf=None)

        if progressBar:
            totalVertices = len(expandedVertices)
            percentage = 99.0 / totalVertices
            iteration = 1

        for vert in expandedVertices:
            # faster way then iteration over values
            numOfVertInfluences = len(mc.skinPercent(skinClusterName, vert, q=True, value=True, ignoreBelow=0.001))
            if numOfVertInfluences > maxInfVal:
                allVerticesOvermaxInfVal.append(vert)

            if progressBar:
                progressBar.setValue(percentage * iteration)
                qApp.processEvents()
                iteration += 1

        if progressBar:
            progressBar.setValue(100)

        if not notSelect:
            mc.undoInfo(cck=True)

        return allVerticesOvermaxInfVal
    """lsObj = mc.ls(sl=True);getVtx = lib_skinning.SkinningTools();
    print getVtx.getOverMaxInfVertex(singleObject=lsObj,maxInfVal=2)"""



    ### SET VERTEX WITH MAX INFLUENCE NUMBER____________________________________________________________________________
    def setMaxJointInf(self, objects=None, maxInfVal=8, progressBar=None):
        mc.undoInfo(ock=True)
        for singleObject in objects:
            toMuchinfls = self.getOverMaxInfVertex(singleObject=singleObject, maxInfVal=maxInfVal,
                                                       notSelect=True)  # returns the vertices that have too much influences
            if toMuchinfls == None:
                print "no vertices over limit"
                continue

            skinClusterName = SkinningTools.returnSkinCluster(singleObject)
            meshShapeName = mc.listRelatives(singleObject, type="shape")[0]
            outInfluencesArray = mc.SkinWeights([meshShapeName, skinClusterName], q=True)

            infjnts = mc.skinCluster(skinClusterName, q=True, inf=True)
            infLengt = len(infjnts)

            lenOutInfArray = len(outInfluencesArray)
            amountToLoop = (lenOutInfArray / infLengt)

            if progressBar:
                totalVertices = len(toMuchinfls)
                percentage = 99.0 / totalVertices
                iteration = 1;

            for vertex in toMuchinfls:
                vtxNumber = int(vertex.split('.vtx[')[-1].split(']')[0])

                infArraycurrentVtx = []
                infPosition = []
                for index in range(infLengt):
                    currentInf = outInfluencesArray[(vtxNumber * infLengt) + index]
                    if currentInf > 0.0:
                        infArraycurrentVtx.append(currentInf)
                        infPosition.append((vtxNumber * infLengt) + index)

                toconvert = len(infArraycurrentVtx) - maxInflVal
                for i in range(toconvert):
                    index = infArraycurrentVtx.index(min(infArraycurrentVtx))
                    setValue = infArraycurrentVtx[index] / (len(infArraycurrentVtx) - (i + 1))
                    for j in range(len(infArraycurrentVtx)):
                        if j != index:
                            value = infArraycurrentVtx[j]
                            infArraycurrentVtx[j] = setValue + value
                            indexinterMediate = infPosition[j]
                            outInfluencesArray[indexinterMediate] = infArraycurrentVtx[j]

                    infArraycurrentVtx[index] = 0.0
                    indexInTotal = infPosition[index]
                    outInfluencesArray[indexInTotal] = infArraycurrentVtx[index]

                if progressBar:
                    progressBar.setValue(percentage * iteration)
                    qApp.processEvents()
                    iteration += 1;

            mc.SkinWeights([meshShapeName, skinClusterName], nwt=outInfluencesArray)
            if progressBar:
                progressBar.setValue(100)

        mc.undoInfo(cck=True)
