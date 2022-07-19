# coding: utf-8

import maya.cmds as mc
import re


def configAxis(mb=None,side=None):
    base = "Base"
    ############################## AXIS ######################################
    nTypes ={}
    try :
        if base == "Base":
            # CONFIG HEAD_________________________________________________________________
            nTypes["aimJtHead"] = {"aimOri":(0,1,0), "aimUpV":(0,0,1), "aimOriEnd":(0,-1,0), "aimUpVEnd":(0,0,1)}
            nTypes["rOrdHead"] = {"rOrdFk":3, "rOrdIk":3, "rOrdEnd":3}
            # CONFIG NECK_________________________________________________________________
            nTypes["aimJtNeck"] = {"aimOri":(0,1,0), "aimUpV":(0,0,1), "aimOriEnd":(0,-1,0), "aimUpVEnd":(0,0,1)}
            nTypes["rOrdNeck"] = {"rOrdFk":3, "rOrdIk":3, "rOrdEnd":3}
            # CONFIG SPINE________________________________________________________________
            nTypes["aimJtSpine"] = {"aimOri":(0,1,0), "aimUpV":(0,0,1), "aimOriEnd":(0,-1,0), "aimUpVEnd":(0,0,1)}
            nTypes["rOrdSpine"] = {"rOrdFk":3, "rOrdIk":3, "rOrdEnd":3}
            # CONFIG TAIL_________________________________________________________________
            nTypes["aimJtTail"] = {"aimOri":(0,1,0), "aimUpV":(1,0,0), "aimOriEnd":(0,-1,0), "aimUpVEnd":(1,0,0)}
            nTypes["rOrdTail"] = {"rOrdFk":3, "rOrdIk":3, "rOrdEnd":3}
            # CONFIG MEMBER LEFT__________________________________________________________
            nTypes["aimJtShouldL"] = {"aimOri":(0,1,0), "aimUpV":(-1,0,0), "aimOriEnd":(0,-1,0), "aimUpVEnd":(1,0,0)}
            nTypes["aimJtScapulaL"] = {"aimOri":(0,1,0), "aimUpV":(-1,0,0), "aimOriEnd":(0,-1,0), "aimUpVEnd":(1,0,0)}
            nTypes["aimJtArmL"] = {"aimOri":(0,1,0), "aimUpV":(0,0,1)}
            nTypes["aimJtHandL"] = {"aimOri":(0,1,0), "aimUpV":(0,0,1), "aimOriEnd":(0,-1,0), "aimUpVEnd":(0,0,1)}
            nTypes["aimJtFingerL"] = {"aimOri":(0,1,0), "aimUpV":(1,0,0), "aimOriEnd":(0,-1,0), "aimUpVEnd":(1,0,0)}
            nTypes["aimJtThumbL"] = {"aimOri":(0,1,0), "aimUpV":(1,0,0), "aimOriEnd":(0,-1,0), "aimUpVEnd":(1,0,0)}
            nTypes["aimJtLegL"] = {"aimOri":(0,1,0), "aimUpV":(0,0,1)}
            nTypes["aimJtFootL"] = {"aimOri":(0,1,0), "aimUpV":(0,0,1), "aimOriEnd":(0,-1,0), "aimUpVEnd":(0,0,1)}
            nTypes["aimJtToeL"] = {"aimOri":(0,1,0), "aimUpV":(1,0,0), "aimOriEnd":(0,-1,0), "aimUpVEnd":(1,0,0)}

            if side =='R':
                nTypes["aimJtShouldR"] = {"aimOri":(0,-1,0), "aimUpV":(1,0,0), "aimOriEnd":(0,1,0), "aimUpVEnd":(-1,0,0)}
                nTypes["aimJtScapulaR"] = {"aimOri":(0,-1,0), "aimUpV":(1,0,0), "aimOriEnd":(0,1,0), "aimUpVEnd":(-1,0,0)}
                nTypes["aimJtArmR"] = {"aimOri":(0,-1,0), "aimUpV":(0,0,1)}
                nTypes["aimJtHandR"] = {"aimOri":(0,-1,0), "aimUpV":(0,0,1), "aimOriEnd":(0,1,0), "aimUpVEnd":(0,0,1)}
                nTypes["aimJtFingerR"] = {"aimOri":(0,-1,0), "aimUpV":(1,0,0), "aimOriEnd":(0,1,0), "aimUpVEnd":(1,0,0)}
                nTypes["aimJtThumbR"] = {"aimOri":(0,-1,0), "aimUpV":(1,0,0), "aimOriEnd":(0,1,0), "aimUpVEnd":(1,0,0)}
                nTypes["aimJtLegR"] = {"aimOri":(0,-1,0), "aimUpV":(0,0,1)}
                nTypes["aimJtFootR"] = {"aimOri":(0,-1,0), "aimUpV":(0,0,1), "aimOriEnd":(0,1,0), "aimUpVEnd":(0,0,1)}
                nTypes["aimJtToeR"] = {"aimOri":(0,-1,0), "aimUpV":(1,0,0), "aimOriEnd":(0,1,0), "aimUpVEnd":(1,0,0)}

            nTypes["rOrdShould"] = {"rOrdFk":1, "rOrdIk":4, "rOrdEnd":0}
            nTypes["rOrdScapula"] = {"rOrdFk":1, "rOrdIk":4, "rOrdEnd":0}
            nTypes["rOrdArm"] = {"rOrdFk":5, "rOrdIk":0, "rOrdEnd":0}
            nTypes["rOrdHand"] = {"rOrdFk":0, "rOrdIk":0, "rOrdEnd":0}
            nTypes["rOrdFinger"] = {"rOrdFk":4, "rOrdIk":4, "rOrdEnd":4}
            nTypes["rOrdLeg"] = {"rOrdFk":4, "rOrdIk":3, "rOrdEnd":5}
            nTypes["rOrdFoot"] = {"rOrdFk":5, "rOrdIk":3, "rOrdEnd":5}
            nTypes["rOrdToe"] = {"rOrdFk":4, "rOrdIk":4, "rOrdEnd":4}



        elif base == "TeamTo":
            # CONFIG HEAD_________________________________________________________________
            nTypes["aimJtHead"] = {"aimOri":(0,1,0), "aimUpV":(0,0,1), "aimOriEnd":(0,-1,0), "aimUpVEnd":(0,0,1)}
            nTypes["rOrdHead"] = {"rOrdStart":3, "rOrd":3, "rOrdEnd":3}
            # CONFIG NECK_________________________________________________________________
            nTypes["aimJtNeck"] = {"aimOri":(0,1,0), "aimUpV":(0,0,1), "aimOriEnd":(0,-1,0), "aimUpVEnd":(0,0,1)}
            nTypes["rOrdNeck"] = {"rOrdStart":3, "rOrd":3, "rOrdEnd":3}
            # CONFIG SPINE________________________________________________________________
            nTypes["aimJtSpine"] = {"aimOri":(0,1,0), "aimUpV":(0,0,1), "aimOriEnd":(0,-1,0), "aimUpVEnd":(0,0,1)}
            nTypes["rOrdSpine"] = {"rOrdStart":3, "rOrd":3, "rOrdEnd":3}
            # CONFIG TAIL_________________________________________________________________
            nTypes["aimJtTail"] = {"aimOri":(0,1,0), "aimUpV":(1,0,0), "aimOriEnd":(0,-1,0), "aimUpVEnd":(1,0,0)}
            nTypes["rOrdTail"] = {"rOrdStart":3, "rOrd":3, "rOrdEnd":3}
            # CONFIG MEMBER LEFT__________________________________________________________
            nTypes["aimJtShouldL"] = {"aimOri":(0,1,0), "aimUpV":(-1,0,0), "aimOriEnd":(0,-1,0), "aimUpVEnd":(1,0,0)}
            nTypes["aimJtScapulaL"] = {"aimOri":(0,1,0), "aimUpV":(-1,0,0), "aimOriEnd":(0,-1,0), "aimUpVEnd":(1,0,0)}
            nTypes["aimJtArmL"] = {"aimOri":(0,1,0), "aimUpV":(0,0,-1)}
            nTypes["aimJtHandL"] = {"aimOri":(0,1,0), "aimUpV":(0,0,1), "aimOriEnd":(0,-1,0), "aimUpVEnd":(0,0,1)}
            nTypes["aimJtFingerL"] = {"aimOri":(0,1,0), "aimUpV":(1,0,0), "aimOriEnd":(0,-1,0), "aimUpVEnd":(1,0,0)}
            nTypes["aimJtThumbL"] = {"aimOri":(0,1,0), "aimUpV":(1,0,0), "aimOriEnd":(0,-1,0), "aimUpVEnd":(1,0,0)}
            nTypes["aimJtLegL"] = {"aimOri":(0,1,0), "aimUpV":(0,0,1)}
            nTypes["aimJtFootL"] = {"aimOri":(0,1,0), "aimUpV":(0,0,1), "aimOriEnd":(0,-1,0), "aimUpVEnd":(0,0,1)}
            nTypes["aimJtToeL"] = {"aimOri":(0,1,0), "aimUpV":(1,0,0), "aimOriEnd":(0,-1,0), "aimUpVEnd":(1,0,0)}

            if side =='R':
                nTypes["aimJtShouldR"] = {"aimOri":(0,-1,0), "aimUpV":(1,0,0), "aimOriEnd":(0,1,0), "aimUpVEnd":(-1,0,0)}
                nTypes["aimJtScapulaR"] = {"aimOri":(0,-1,0), "aimUpV":(1,0,0), "aimOriEnd":(0,1,0), "aimUpVEnd":(-1,0,0)}
                nTypes["aimJtArmR"] = {"aimOri":(0,-1,0), "aimUpV":(0,0,-1)}
                nTypes["aimJtHandR"] = {"aimOri":(0,-1,0), "aimUpV":(0,0,1), "aimOriEnd":(0,1,0), "aimUpVEnd":(0,0,1)}
                nTypes["aimJtFingerR"] = {"aimOri":(0,-1,0), "aimUpV":(1,0,0), "aimOriEnd":(0,1,0), "aimUpVEnd":(1,0,0)}
                nTypes["aimJtThumbR"] = {"aimOri":(0,-1,0), "aimUpV":(1,0,0), "aimOriEnd":(0,1,0), "aimUpVEnd":(1,0,0)}
                nTypes["aimJtLegR"] = {"aimOri":(0,-1,0), "aimUpV":(0,0,1)}
                nTypes["aimJtFootR"] = {"aimOri":(0,-1,0), "aimUpV":(0,0,1), "aimOriEnd":(0,1,0), "aimUpVEnd":(0,0,1)}
                nTypes["aimJtToeR"] = {"aimOri":(0,-1,0), "aimUpV":(1,0,0), "aimOriEnd":(0,1,0), "aimUpVEnd":(1,0,0)}

            nTypes["rOrdShould"] = {"rOrdStart":1, "rOrd":4, "rOrdEnd":0}
            nTypes["rOrdScapula"] = {"rOrdStart":1, "rOrd":4, "rOrdEnd":0}
            nTypes["rOrdArm"] = {"rOrdStart":1, "rOrd":4, "rOrdEnd":0}
            nTypes["rOrdHand"] = {"rOrdStart":0, "rOrd":0, "rOrdEnd":0}
            nTypes["rOrdFinger"] = {"rOrdStart":4, "rOrd":4, "rOrdEnd":4}
            nTypes["rOrdLeg"] = {"rOrdStart":4, "rOrd":4, "rOrdEnd":5}
            nTypes["rOrdFoot"] = {"rOrdStart":5, "rOrd":5, "rOrdEnd":5}
            nTypes["rOrdToe"] = {"rOrdStart":4, "rOrd":4, "rOrdEnd":4}

        return nTypes[mb]
    except:
        mc.warning( "{} n'existe pas !!!!".format(mb))

# configAxis('set')