from ump.common import emon_file
import emon_api as eapi
import maya.cmds as mc
import json

import switch_fonction, name_lib
from name_lib import SwitchName
from llc.pipeline.defines import LLCNodeName
from llc.maya.utils import setup, controller
from ump.maya.common.utils import set_shape_color
from ump.pipeline.defines import UMPColors

reload(switch_fonction)
reload(name_lib)

class CreateAttributSwitch():
    def __init__(self, asset, step):
        self.dict_mod = {}
        self.dict_tex = {}
        self.dict_ani = {}
        self.attr_info_name = ''

        self.step = step
        self.asset = asset

        self.switch_tex = asset.switchTex() if hasattr(asset, 'switchTex') else ''
        self.switch_mod = asset.switchMod() if hasattr(asset, 'switchMod') else ''
        self.switch_ani = asset.switchAni() if hasattr(asset, 'switchAni') else ''

        self.ctrl_switch, self.prefix_attr = switch_fonction.find_ctrl_switch(step)

        if step == 'modeling':
            self.attr_info_name = SwitchName.MOD_DICT
            self.create_mod_attribut()
        if step == 'surfacing':
            self.attr_info_name = SwitchName.SHD_DICT
            mc.addAttr(LLCNodeName.SHD_CTRL, longName=self.attr_info_name, dataType='string')
            self.create_tex_attribut()
        if step == 'setup':
            self.attr_info_name = SwitchName.ANI_DICT
            if not mc.objExists(LLCNodeName.SETUP_CTRL_RIG_ADD):
                setup.create_rigAdd_ctrl(worldConstraint=False)
            mc.addAttr(LLCNodeName.SETUP_CTRL_RIG_ADD, longName=self.attr_info_name, dataType='string')

            self.create_ani_attribut()

    def convert_tech_note_to_dict_vis(self, string_gattaca):
        '''
        switch_MOD = 'mod_state:\n0_Base = msh_cup\n1_Squeeze.1 = msh_cupSqueeze.1\n2_Squash = msh_cupSquash.1'
        :return:
        dict_vis = {
            'mod_state':
                {'0_Base':
                    {'msh_cup' : 1},
                 '1_Squeeze':
                    {'msh_cupSqueeze' : 1}
                 '2_Squash':
                     {'msh_cupSquash': 1}
                }
            }
        }
        '''
        dict_vis = {}
        l_state_data = []
        print 'string_gattaca', string_gattaca
        if string_gattaca:
            if '\n\n' in string_gattaca:
                for state_data in range(string_gattaca.count('\n\n') + 1):
                    state_data_string = string_gattaca.split('\n\n')[state_data]
                    l_state_data.append(state_data_string.replace(' ', ''))
            else:
                l_state_data = [string_gattaca.replace(' ', '')]

            for string_data in l_state_data:
                attr = string_data.split(':')[0]
                state_param = string_data.split(':')[-1]
                dict_vis[attr] = {}
                for line in range(state_param.count('\n')):
                    if '=' in state_param:
                        state = state_param.split('\n')[line + 1].split('=')[0]
                        values = state_param.split('\n')[line + 1].split('=')[-1]
                    else:
                        state = state_param.split('\n')[line + 1]
                        values = ''  # NO VALUE

                    dict_value = {}

                    if ',' in values:  # MULTIPLE VALUES
                        l_values = []
                        for i in range(values.count(',') + 1):
                            l_values.append(values.split(',')[i])
                    else: # SIMPLE VALUE
                        l_values = [values]

                    for value in l_values:
                        if '.' in value:
                            attr_value = value.split('.')[-1]
                            if attr_value.isdigit():
                                attr_value = int(attr_value)
                            if value.count('.') == 1:
                                attr_to_set = value.split('.')[0]
                            if value.count('.') == 2: # IF NAMESPACE/REF
                                attr_to_set = value[:value.rindex('.')]
                            dict_value[attr_to_set] = attr_value
                        else:
                            dict_value[value] = 1
                        dict_vis[attr][state] = dict_value

            print dict_vis

        else:
            print "Pas d'info de switch " + self.step + " dans gattaca"
        return dict_vis

    def convert_tech_note_to_dict_tex(self, string_gattaca):
        '''
        switch_MOD = 'mod_state:\n0_Base = msh_cup\n1_Squeeze.1 = msh_cupSqueeze.1\n2_Squash = msh_cupSquash.1'
        :return:
        dict_vis = {
            'mod_state':
                {'0_Base':
                    {'msh_cup' : 1},
                 '1_Squeeze':
                    {'msh_cupSqueeze' : 1}
                 '2_Squash':
                     {'msh_cupSquash': 1}
                }
            }
        }
        '''
        dict_tex = {}
        l_state_data = []

        if string_gattaca:
            if '\n\n' in string_gattaca:
                for state_data in range(string_gattaca.count('\n\n') + 1):
                    state_data_string = string_gattaca.split('\n\n')[state_data]
                    l_state_data.append(state_data_string.replace(' ', ''))
            else:
                l_state_data = [string_gattaca.replace(' ', '')]

            for string_data in l_state_data:
                attr = string_data.split(':')[0]
                state_param = string_data.split(':')[-1]
                dict_tex[attr] = {}
                for line in range(state_param.count('\n')):
                    if '=' in state_param:
                        state = state_param.split('\n')[line + 1].split('=')[0]
                        values = state_param.split('\n')[line + 1].split('=')[-1]
                    else:
                        state = state_param.split('\n')[line + 1]
                        values = ''  # NO VALUE

                    dict_value = {}

                    if ',' in values:  # MULTIPLE VALUES
                        l_values = []
                        for i in range(values.count(',') + 1):
                            l_values.append(values.split(',')[i])
                    else: # SIMPLE VALUE
                        l_values = [values]

                    for value in l_values:
                        if '.' in value:
                            attr_value = value.split('.')[-1]
                            if attr_value.isdigit():
                                attr_value = int(attr_value)
                            if value.count('.') == 1:
                                attr_to_set = value.split('.')[0]
                            if value.count('.') == 2: # IF NAMESPACE/REF
                                attr_to_set = value[:value.rindex('.')]
                            dict_value[attr_to_set] = attr_value
                        else:
                            dict_tex[attr][state] = {}
                            print "No value for " + state

            print dict_tex

        else:
            print "Pas d'info de switch " + self.step + " dans gattaca"
        return dict_tex

    def create_mod_attribut(self):
        # Add attr avec dico les generer des la creation du MOD_CTRL
        if not mc.objExists(SwitchName.MOD_CTRL):
            # If not exist create MOD_CTRL
            MOD_CTRL, MOD_CTRL_shape = controller.create_department_ctrl(LLCNodeName.TOP_NODE, LLCNodeName.MOD_CTRL,
                                                                         hide=False)
            set_shape_color(MOD_CTRL_shape, UMPColors.MOD_CTRL)
            self.ctrl_switch = MOD_CTRL
        # Add attr for dict info switch
        if not mc.objExists(SwitchName.MOD_CTRL + '.' + self.attr_info_name):
            mc.addAttr(self.ctrl_switch, longName = self.attr_info_name, dataType='string')
        self.dict_mod = self.convert_tech_note_to_dict_vis(self.switch_mod)
        self.create_attribut(self.dict_mod)

        mc.setAttr(LLCNodeName.MOD_CTRL + '.' + SwitchName.MOD_DICT, json.dumps(self.dict_mod), type='string')

    def create_tex_attribut(self):
        self.dict_tex = self.convert_tech_note_to_dict_tex(self.switch_tex)
        mc.setAttr(LLCNodeName.SHD_CTRL + '.' + name_lib.SwitchName.SHD_DICT, json.dumps(self.dict_tex), type='string')
        self.create_attribut(self.dict_tex)

    def create_ani_attribut(self):
        self.dict_ani = self.convert_tech_note_to_dict_vis(self.switch_ani)
        mc.setAttr(LLCNodeName.SETUP_CTRL_RIG_ADD + '.' + name_lib.SwitchName.ANI_DICT, json.dumps(self.dict_ani), type='string')
        self.create_attribut(self.dict_ani)

    def create_attribut(self, dico):
        '''
        :param dico:
          Create attribute(s) contain in the dict info switch if not exist
        :return:
        '''
        for attr_name in dico.keys():
            states = ''
            for state in sorted(dico[attr_name].keys(), key=lambda k: int(k.split('_')[0])):
                states = states + state.split('_')[1] + ':'
            # check prefix
            if not attr_name.startswith(self.prefix_attr):
                attr_name = self.prefix_attr + attr_name

            if not mc.objExists(self.ctrl_switch + '.' + attr_name):
                mc.addAttr(self.ctrl_switch, attributeType='enum', shortName=attr_name, keyable=True, enumName=states)
            else:
                mc.addAttr(self.ctrl_switch + '.' + attr_name, edit=True, attributeType='enum', keyable=True, enumName=states)