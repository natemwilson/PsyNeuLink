# Princeton University licenses this file to You under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may obtain a copy of the License at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.
#
#
# ******************************************** MechanismPreferenceSet **************************************************
#
#
from PsyNeuLink.Globals.Preferences.ComponentPreferenceSet import *
from PsyNeuLink.Globals.Utilities import ModulationOperation
from PsyNeuLink.Globals.Preferences import *

# Keypaths for preferences:
kpRuntimeParamModulationPref = '_function_runtime_params_pref'

# Default PreferenceSets:
runtimeParamModulationPrefInstanceDefault = PreferenceEntry(ModulationOperation.OVERRIDE,
                                                                PreferenceLevel.INSTANCE)
runtimeParamModulationPrefTypeDefault = PreferenceEntry(ModulationOperation.ADD,
                                                            PreferenceLevel.TYPE)
# runtimeParamModulationPrefCategoryDefault = PreferenceEntry(ModulationOperation.MULTIPLY,
#                                                                 PreferenceLevel.CATEGORY)
runtimeParamModulationPrefCategoryDefault = PreferenceEntry(ModulationOperation.OVERRIDE,
                                                                PreferenceLevel.CATEGORY)


class MechanismPreferenceSet(ComponentPreferenceSet):
    """Extends ComponentPreferenceSet to include Mechanism-specific preferences
     
    Description:
        Implements the following preference:
            - functionRuntimeParams (bool): uses specification of run-time params to update execute method params

    Class methods:
        - runtimeParamModulationPref():
            returns setting for functionRuntimeParams preference at level specified in functionRuntimeParams PreferenceEntry of owner's Preference object
        - runtimeParamModulationPref(setting=<value>):
            assigns the value of the setting item in the runtimeParamModulationPref PreferenceEntry of the owner's Preference object
        - runtimeParamModulationPrefLevel()
            returns level in the runtimeParamModulationPref PreferenceEntry of the owner's Preference object
        - runtimeParamModulationPrefLevel(level=<PreferenceLevel>):
            assigns the value of the level item in the runtimeParamModulationPref PreferenceEntry of the owner's Preference object
        - runtimeParamModulationPrefEntry():
            assigns PreferenceEntry to runtimeParamModulationPref attribute of the owner's Preference object
        - runtimeParamModulationPrefEntry(entry=<PreferenceEntry>):
            returns PreferenceEntry for the runtimeParamModulationPref attribute of the owner's Preference object
    """
    def __init__(self,
                 owner=NotImplemented,
                 reportOutput_pref=reportOutputPrefInstanceDefault,
                 functionRuntimeParams_pref=runtimeParamModulationPrefInstanceDefault,
                 log_pref=logPrefInstanceDefault,
                 verbose_pref=verbosePrefInstanceDefault,
                 param_validation_pref=paramValidationPrefInstanceDefault,
                 level=PreferenceLevel.SYSTEM,
                 name=None,
                 **kargs):
        if kargs:
            try:
                owner = kargs[kwPrefsOwner]
            except (KeyError, NameError):
                pass
            try:
                reportOutput_pref = kargs[kpReportOutputPref]
            except (KeyError, NameError):
                pass
            try:
                functionRuntimeParams_pref = kargs[kpRuntimeParamModulationPref]
            except (KeyError, NameError):
                pass
            try:
                log_pref = kargs[kpLogPref]
            except (KeyError, NameError):
                pass
            try:
                param_validation_pref = kargs[kpParamValidationPref]
            except (KeyError, NameError):
                pass
            try:
                verbose_pref = kargs[kpVerbosePref]
            except (KeyError, NameError):
                pass
            try:
                name = kargs[kwNameArg]
            except (KeyError, NameError):
                pass
            try:
                level = kargs[kwPrefLevel]
            except (KeyError, NameError):
                pass

        super(MechanismPreferenceSet, self).__init__(owner=owner,
                                                     reportOutput_pref=reportOutput_pref,
                                                     log_pref=log_pref,
                                                     verbose_pref=verbose_pref,
                                                     param_validation_pref=param_validation_pref,
                                                     level=level,
                                                     name=name)
        # self._report_output_pref = reportOutput_pref
        self._function_runtime_params_pref = functionRuntimeParams_pref

    # functionRuntimeParams entry ------------------------------------------------------------------------------------

    @property
    def runtimeParamModulationPref(self):
        """Returns setting of owner's functionRuntimeParams pref at level specified in its PreferenceEntry.level
        :param level:
        :return:
        """
        # If the level of the object is below the Preference level,
        #    recursively calls base (super) classes to get preference at specified level
        return self.get_pref_setting_for_level(kpRuntimeParamModulationPref,
                                               self._function_runtime_params_pref.level)[0]


    @runtimeParamModulationPref.setter
    def runtimeParamModulationPref(self, setting):
        """Assigns setting to owner's functionRuntimeParams pref
        :param setting:
        :return:
        """
        if isinstance(setting, PreferenceEntry):
            self._function_runtime_params_pref = setting

        # elif not iscompatible(setting, runtimeParamModulationPrefInstanceDefault.setting):
        elif not inspect.isfunction(runtimeParamModulationPrefInstanceDefault.setting):
            print("setting of functionRuntimeParams preference ({0}) must be a {1} or a function;"
                  " it will remain unchanged ({2})".
                  format(setting,
                         ModulationOperation.__class__.__name__,
                         self._function_runtime_params_pref.setting))
            return

        else:
            self._function_runtime_params_pref = self._function_runtime_params_pref._replace(setting=setting)

    @property
    def runtimeParamModulationPrefLevel(self):
        """Returns level for owner's functionRuntimeParams pref
        :return:
        """
        return self._function_runtime_params_pref.level

    @runtimeParamModulationPrefLevel.setter
    def runtimeParamModulationPrefLevel(self, level):
        """Sets level for owner's functionRuntimeParams pref
        :param level:
        :return:
        """
        if not isinstance(level, PreferenceLevel):
            print("Level of functionRuntimeParams preference ({0}) must be a PreferenceLevel setting; it will remain unchanged ({1})".
                  format(level, self._function_runtime_params_pref.setting))
            return
        self._function_runtime_params_pref = self._function_runtime_params_pref._replace(level=level)

    @property
    def runtimeParamModulationPrefEntry(self):
        """Returns owner's functionRuntimeParams PreferenceEntry tuple (setting, level)
        :return:
        """
        return self._function_runtime_params_pref

    @runtimeParamModulationPrefEntry.setter
    def runtimeParamModulationPrefEntry(self, entry):
        """Assigns functionRuntimeParams PreferenceEntry to owner
        :param entry:
        :return:
        """
        if not isinstance(entry, PreferenceEntry):
            print("runtimeParamModulationPrefEntry ({0}) must be a PreferenceEntry; it will remain unchanged ({1})".
                  format(entry, self._function_runtime_params_pref))
            return
        self._function_runtime_params_pref = entry



