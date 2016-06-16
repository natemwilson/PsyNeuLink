from Globals.Preferences.PreferenceSet import *
from Globals.Log import *
from Main import ModulationOperation


# Keypaths for preferences:
kpReportOutputPref = '_report_output_pref'
kpLogPref = '_log_pref'
kpParamValidationPref = '_param_validation_pref'
kpVerbosePref = '_verbose_pref'
kpExecuteMethodRuntimeParamsPref = '_execute_method_runtime_params_pref'

# Keywords for generic level default preference sets
kwSystemDefaultPreferences = 'SystemDefaultPreferences'
kwCategoryDefaultPreferences = 'CategoryDefaultPreferences'
kwTypeDefaultPreferences = 'TypeDefaultPreferences'
kwInstanceDefaultPreferences = 'InstanceDefaultPreferences'

# Level default preferences dicts:

SystemDefaultPreferencesDict = {
    kwPreferenceSetName: kwSystemDefaultPreferences,
    kpVerbosePref: PreferenceEntry(False, PreferenceLevel.SYSTEM),
    kpParamValidationPref: PreferenceEntry(True, PreferenceLevel.SYSTEM),
    kpReportOutputPref: PreferenceEntry(True, PreferenceLevel.SYSTEM),
    kpLogPref: PreferenceEntry(LogLevel.OFF, PreferenceLevel.CATEGORY),
    kpExecuteMethodRuntimeParamsPref: PreferenceEntry(ModulationOperation.MULTIPLY, PreferenceLevel.SYSTEM)}

CategoryDefaultPreferencesDict = {
    kwPreferenceSetName: kwCategoryDefaultPreferences,
    kpVerbosePref: PreferenceEntry(False, PreferenceLevel.CATEGORY),
    kpParamValidationPref: PreferenceEntry(True, PreferenceLevel.CATEGORY),
    kpReportOutputPref: PreferenceEntry(True, PreferenceLevel.CATEGORY),
    kpLogPref: PreferenceEntry(LogLevel.VALUE_ASSIGNMENT, PreferenceLevel.CATEGORY),
    kpExecuteMethodRuntimeParamsPref: PreferenceEntry(ModulationOperation.MULTIPLY,PreferenceLevel.CATEGORY)}

TypeDefaultPreferencesDict = {
    kwPreferenceSetName: kwTypeDefaultPreferences,
    kpVerbosePref: PreferenceEntry(False, PreferenceLevel.TYPE),
    kpParamValidationPref: PreferenceEntry(True, PreferenceLevel.TYPE),
    kpReportOutputPref: PreferenceEntry(False, PreferenceLevel.TYPE),
    kpLogPref: PreferenceEntry(LogLevel.OFF, PreferenceLevel.CATEGORY),   # This gives control to Mechanisms
    kpExecuteMethodRuntimeParamsPref: PreferenceEntry(ModulationOperation.ADD,PreferenceLevel.TYPE)}

InstanceDefaultPreferencesDict = {
    kwPreferenceSetName: kwInstanceDefaultPreferences,
    kpVerbosePref: PreferenceEntry(False, PreferenceLevel.INSTANCE),
    kpParamValidationPref: PreferenceEntry(False, PreferenceLevel.INSTANCE),
    kpReportOutputPref: PreferenceEntry(False, PreferenceLevel.INSTANCE),
    kpLogPref: PreferenceEntry(LogLevel.OFF, PreferenceLevel.CATEGORY),   # This gives control to Mechanisms
    kpExecuteMethodRuntimeParamsPref: PreferenceEntry(ModulationOperation.OVERRIDE, PreferenceLevel.INSTANCE)}

# Dict of default dicts
FunctionDefaultPrefDicts = {
    PreferenceLevel.SYSTEM: SystemDefaultPreferencesDict,
    PreferenceLevel.CATEGORY: CategoryDefaultPreferencesDict,
    PreferenceLevel.TYPE: TypeDefaultPreferencesDict,
    PreferenceLevel.INSTANCE: InstanceDefaultPreferencesDict}


class FunctionPreferenceSet(PreferenceSet):
    """Implement and manage PreferenceSets for Function class hierarchy

    Description:
        Implement the following preferences:
            - verbose (bool): enables/disables reporting of (non-exception) warnings and system function
            - paramValidation (bool):  enables/disables run-time validation of the execute method of a Function object
            - reportOutput (bool): enables/disables reporting of execution of execute method
            - log (bool): enables/disables logging for a given object
            - executeMethodRunTimeParams (ModulationOperation): uses run-time params to modulate execute method params
        Implement the following preference levels:
            - SYSTEM: system level default settings (Function.classPreferences)
            - CATEGORY: category-level default settings:
                Mechanism.classPreferences
                MechanismState.classPreferences
                Projection.classPreferences
                Utility.classPreferences
            - TYPE: type-level default settings (if one exists for the category, else category-level settings are used):
                MechanismTypes:
                    DDM.classPreferences
                MechanismState types:             
                    MechanismInputState.classPreferences
                    MechanismParameterState.classPreferences
                    MechanismOutputState.classPreferences
                Projection types:             
                    ControlSignal.classPreferences
                    Mapping.classPreferences
            - INSTANCE: returns the setting specified in the PreferenceSetEntry of the specified object itself

    Initialization arguments:
        - owner (Function object): object to which the PreferenceSet belongs;  (default: SystemDefaultMechanism)
            Note:  this is used to get appropriate default preferences (from class) for instantiation;
                   however, since a PreferenceSet can be assigned to multiple objects, when accessing the preference
                   the owner is set dynamically, to insure context-relevant PreferenceLevels for returning the setting
        - prefs (dict):  a specification dict, each entry of which must have a:
            key that is a keypath (kp<*>) corresponding to an attribute of the PreferenceSet, from the following set:
                + kwPreferenceSetName: specifies the name of the PreferenceSet
                + kpVerbosePref: print non-exception-related information during execution
                + kpParamValidationPref: validate parameters during execution
                + kpReportOutputPref: report object's ouptut during execution
                + kpLogPref: record attribute data for the object during execution
                + kpExecuteMethodRuntimeParamsPref: modulate parameters using runtime specification (in configuration)
            value that is either a PreferenceSet, valid setting for the preference, or a PreferenceLevel; defaults
        - level (PreferenceLevel): ??
        - name (str): name of PreferenceSet
        - context (value): must be self (to call super's abstract class: PreferenceSet)
        - **kargs (dict): dictionary of arguments, that takes precedence over the individual args above

    Class attributes:
        + defaultPreferencesDict (PreferenceSet): SystemDefaultPreferences
        + baseClass (class): Function

    Class methods:
        Note:
        * All of the setters below use PreferenceSet.set_preference, which validates any preference info passed to it,
            and can take a PreferenceEntry, setting, or PreferenceLevel
        • verbosePref():
            returns setting for verbosePref preference at level specified in verbosePref PreferenceEntry of
             owner's PreferenceSet
        • verbosePref(setting=<value>):
            assigns the value of the setting arg to the verbosePref of the owner's PreferenceSet
        • paramValidationPref():
            returns setting for paramValidationPref preference at level specified in paramValidationPref PreferenceEntry
            of owner's PreferenceSet
        • paramValidationPref(setting=<value>):
            assigns the value of the setting arg to the paramValidationPref of the owner's PreferenceSet
        • reportOutputPref():
            returns setting for reportOutputPref preference at level specified in reportOutputPref PreferenceEntry
            of owner's Preference object
        • reportOutputPref(setting=<value>):
            assigns the value of the setting arg to the reportOutputPref of the owner's PreferenceSet
        • logPref():
            returns setting for log preference at level specified in log PreferenceEntry of owner's Preference object
        • logPref(setting=<value>):
            assigns the value of the setting arg to the logPref of the owner's PreferenceSet
                and, if it contains log entries, it adds them to the owner's log
        • executeMethodRuntimeParamsPref():
            returns setting for executeMethodRuntimeParams preference at level specified in
             executeMethodRuntimeParams PreferenceEntry of owner's Preference object
        • executeMethodRuntimeParamsPref(setting=<value>):
            assigns the value of the setting arg to the executeMethodRuntimeParamsPref of the owner's Preference object
    """

    # Use this as both:
    # - a template for the type of each preference used for validation
    # - a default set of preferences where defaults are not otherwise specified
    defaultPreferencesDict = {
            kwPreferenceSetName: 'FunctionPreferenceSetDefaults',
            kpVerbosePref: PreferenceEntry(False, PreferenceLevel.SYSTEM),
            kpParamValidationPref: PreferenceEntry(True, PreferenceLevel.SYSTEM),
            kpReportOutputPref: PreferenceEntry(True, PreferenceLevel.SYSTEM),
            kpLogPref: PreferenceEntry(LogLevel.OFF, PreferenceLevel.CATEGORY),
            kpExecuteMethodRuntimeParamsPref: PreferenceEntry(ModulationOperation.MULTIPLY, PreferenceLevel.SYSTEM)
    }

    baseClass = NotImplemented

    def __init__(self,
                 owner=NotImplemented,
                 prefs=NotImplemented,
                 level=PreferenceLevel.SYSTEM,
                 name=NotImplemented,
                 context=NotImplemented,
                 **kargs):
        """Instantiate PreferenceSet for owner and/or classPreferences for owner's class

        If owner is a class, instantiate its classPreferences attribute if that does not already exist,
            using its classPreferenceLevel attribute, and the corresponding preference dict in FunctionDefaultPrefDicts
        If owner is an object:
        - if the owner's classPreferences do not yet exist, instantiate it (as described above)
        - use the owner's <class>.classPreferenceLevel to create a base set of preferences from its classPreferences
        - use PreferenceEntries, settings, or level specifications from dict in prefs arg to replace entries in base set
        If owner is omitted:
        - assigns SystemDefaultMechanism as owner (this is updated if PreferenceSet is assigned to another object)

        :param owner:
        :param prefs:
        :param level:
        :param name:
        :param context:
        :param kargs:
        """
        if kargs:
            try:
                owner = kargs[kwPrefsOwner]
            except (KeyError, NameError):
                pass
            try:
                prefs = kargs[kwPrefs]
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

        # If baseClass has not been assigned, do so here:
        if self.baseClass is NotImplemented:
            from Functions.Function import Function
            self.baseClass = Function

        # If owner is not specified, assign SystemDefaultMechanism_Base as default owner
        if owner is NotImplemented:
            from Functions.Mechanisms.Mechanism import SystemDefaultMechanism_Base
            DefaultPreferenceSetOwner = SystemDefaultMechanism_Base(name=kwDefaultPreferenceSetOwner)
            owner = DefaultPreferenceSetOwner

        # Get class
        if inspect.isclass(owner):
            owner_class = owner
        else:
            owner_class = owner.__class__

        # If classPreferences have not be instantiated for owner's class, do so here:
        try:
            owner_class.classPreferences
        except AttributeError:
            super(FunctionPreferenceSet, self).__init__(
                owner=owner_class,
                level=owner_class.classPreferenceLevel,
                prefs=FunctionDefaultPrefDicts[owner_class.classPreferenceLevel],
                name=name,
                context=self)

        # Instantiate PreferenceSet
        super(FunctionPreferenceSet, self).__init__(owner=owner,
                                                    level=owner_class.classPreferenceLevel,
                                                    prefs=prefs,
                                                    name=name,
                                                    context=self)
        # FIX:  NECESSARY?? 5/30/16
        self._level = level

    #region verbose entry ----------------------------------------------------------------------------------------------

    @property
    def verbosePref(self):
        """Return setting of owner's verbosePref at level specified in its PreferenceEntry.level
        :param level:
        :return:
        """
        # If the level of the object is below the Preference level,
        #    recursively calls base (super) classes to get preference at specified level
        return self.get_pref_setting_for_level(kpVerbosePref, self._verbose_pref.level)[0]

    @verbosePref.setter
    def verbosePref(self, setting):
        """Assign setting to owner's verbosePref
        :param setting:
        :return:
        """
        self.set_preference(candidate_info=setting, pref_ivar_name=kpVerbosePref)

    # region param_validation ----------------------------------------------------------------------------------------------

    @property
    def paramValidationPref(self):
        """Return setting of owner's param_validationPref at level specified in its PreferenceEntry.level
        :param level:
        :return:
        """
        # If the level of the object is below the Preference level,
        #    recursively calls base (super) classes to get preference at specified level
        return self.get_pref_setting_for_level(kpParamValidationPref, self._param_validation_pref.level)[0]


    @paramValidationPref.setter
    def paramValidationPref(self, setting):
        """Assign setting to owner's param_validationPref
        :param setting:
        :return:
        """
        self.set_preference(setting,kpParamValidationPref)

    #region reportOutput entry -----------------------------------------------------------------------------------------

    @property
    def reportOutputPref(self):
        """Return setting of owner's reportOutputPref at level specified in its PreferenceEntry.level
        :param level:
        :return:
        """
        # If the level of the object is below the Preference level,
        #    recursively calls base (super) classes to get preference at specified level
        return self.get_pref_setting_for_level(kpReportOutputPref, self._report_output_pref.level)[0]


    @reportOutputPref.setter
    def reportOutputPref(self, setting):
        """Assign setting to owner's reportOutputPref
        :param setting:
        :return:
        """
        self.set_preference(candidate_info=setting, pref_ivar_name=kpReportOutputPref)

    #region log entry --------------------------------------------------------------------------------------------------

    @property
    def logPref(self):
        """Return setting of owner's logPref at level specified in its PreferenceEntry.level
        :param level:
        :return:
        """
        # If the level of the object is below the Preference level,
        #    recursively calls base (super) classes to get preference at specified level
        return self.get_pref_setting_for_level(kpLogPref, self._log_pref.level)[0]

    # # VERSION THAT USES OWNER'S logPref TO LIST ENTRIES TO BE RECORDED
    # @logPref.setter
    # def logPref(self, setting):
    #     """Assign setting to owner's logPref and, if it has log entries, add them to owner's log
    #     :param setting:
    #     :return:
    #     """
    #
    #     entries, level = self.set_preference(candidate_info=setting, pref_ivar_name=kpLogPref, [str, list])
    #
    #     if entries:
    #         # Add entries to owner's log
    #         from Globals.Log import Log
    #
    #         try:
    #             self.owner.log.add_entries(entries=entries)
    #         except AttributeError:
    #             self.owner.log = Log(owner=self, entries=entries)

    # VERSION THAT USES OWNER'S logPref AS RECORDING SWITCH
    @logPref.setter
    def logPref(self, setting):
        """Assign setting to owner's logPref
        :param setting:
        :return:
        """
        self.set_preference(candidate_info=setting, pref_ivar_name=kpLogPref)


    #region executeMethodRuntimeParams ----------------------------------------------------------------------------------

    @property
    def executeMethodRuntimeParamsPref(self):
        """Returns owner's executeMethodRuntimeParamsPref
        :return:
        """
        return self._execute_method_runtime_params_pref

    @executeMethodRuntimeParamsPref.setter
    def executeMethodRuntimeParamsPref(self, setting):
        """Assign executeMethodRuntimeParamsPref
        :param entry:
        :return:
        """
        self.set_preference(candidate_info=setting, pref_ivar_name=kpExecuteMethodRuntimeParamsPref)

