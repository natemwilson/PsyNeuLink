from Functions.Mechanisms.ProcessingMechanisms.DDM import *
from Functions.Process import Process_Base
from Globals.Keywords import *

# x = Process_Base()
# x.execute(10.0)


# DDM_prefs = FunctionPreferenceSet(
#                 owner=DDM,
#                 verbose_pref=PreferenceEntry(True,PreferenceLevel.INSTANCE),
#                 reportOutput_pref=PreferenceEntry(True,PreferenceLevel.SYSTEM),
#                 executeMethodRuntimeParams_pref=PreferenceEntry(ModulationOperation.OVERRIDE,PreferenceLevel.CATEGORY),
#                 name='Reassigned'

DDM_prefs = FunctionPreferenceSet(
# FIX: AttributeError: 'FunctionPreferenceSet' object has no attribute '_verbose_pref'
#                 owner=DDM,
                prefs = {
                    kpVerbosePref: PreferenceEntry(True,PreferenceLevel.INSTANCE),
                    kpReportOutputPref: PreferenceEntry(False,PreferenceLevel.SYSTEM),
                    kpExecuteMethodRuntimeParamsPref: PreferenceEntry(ModulationOperation.OVERRIDE,PreferenceLevel.CATEGORY)})


DDM_prefs.verbosePref = PreferenceEntry(True,PreferenceLevel.INSTANCE)
# FIX: HAD TO DISABLE PreferenceSet.validate_log
# DDM_prefs.logPref = LogEntry.TIME_STAMP
# DDM_prefs.logPref = (LogEntry.INPUT_VALUE | LogEntry.OUTPUT_VALUE)

# DDM_prefs.reportOutputPref = 'Hello'

DDM.classPreferences = DDM_prefs

DDM_prefs2 = FunctionPreferenceSet(
                owner=DDM,
                prefs = {
                    kpVerbosePref: PreferenceEntry(True,PreferenceLevel.INSTANCE),
                    kpReportOutputPref: PreferenceEntry(True,PreferenceLevel.SYSTEM),
                    kpExecuteMethodRuntimeParamsPref: PreferenceEntry(ModulationOperation.OVERRIDE,PreferenceLevel.INSTANCE)})

my_DDM = DDM(name='my_DDM')
my_DDM.prefs = DDM_prefs
my_DDM.prefs.level = PreferenceLevel.SYSTEM

# my_DDM.prefs.verbosePref = PreferenceLevel.SYSTEM
# from Functions.Projections.ControlSignal import LogEntry
# my_DDM.prefs.logPref = LogEntry.TIME_STAMP

# FIX: SHOULDN'T BE ABLE TO ASSIGN enum TO PREF THAT DOESN'T REQUIRE ONE:
# my_DDM.prefs.verbosePref = LogEntry.TIME_STAMP

my_DDM.prefs.inspect()

#region MAIN SCRIPT
myMechanism = DDM(params={kwExecuteMethodParams:{kwDDM_DriftRate:(2.0, kwControlSignal),
                                                 kwDDM_Threshold:(10.0, kwControlSignal),
                                                 kwKwDDM_StartingPoint:(0.5, kwControlSignal)},
# myMechanism = DDM(params={kwExecuteMethodParams:{kwDDM_DriftRate:2.0,
#                                                  kwDDM_Threshold:10.0},
                          # kwDDM_AnalyticSolution:kwDDM_NavarroAndFuss  # Note: this requires matlab engine be installed
                          kwDDM_AnalyticSolution:kwDDM_BogaczEtAl},
                  # prefs=DDM_prefs,
                  # prefs = {kpReportOutputPref: PreferenceEntry(True, PreferenceLevel.CATEGORY),
                  #          kpVerbosePref: PreferenceEntry(False, PreferenceLevel.INSTANCE)
                  #          },
                  prefs = {kpReportOutputPref: PreferenceLevel.SYSTEM,
                           # kpVerbosePref: PreferenceLevel.INSTANCE
                           },
                  # prefs = {kpReportOutputPref: False,
                  #          kpVerbosePref: False
                  #          },
                  name='My_DDM'
                  )


#region ADDITIONAL MECHANISMS
# # DDM.classPreferences.reportOutputPref = PreferenceEntry(False, PreferenceLevel.INSTANCE)
#
# # my_Mechanism_2 = DDM(params={kwExecuteMethodParams:{kwDDM_DriftRate:2.0,
# #                                                         kwDDM_Threshold:1.0},
# #                              # kwDDM_AnalyticSolution:kwDDM_NavarroAndFuss  # Note: this requires matlab engine be installed
# #                              kwDDM_AnalyticSolution:kwDDM_BogaczEtAl},
# #                      # prefs=DDM_prefs
# #                      # prefs = {kpReportOutputPref: PreferenceEntry(False, PreferenceLevel.INSTANCE),
# #                      #          kpVerbosePref: PreferenceEntry(False, PreferenceLevel.INSTANCE)
# #                      #          }
# #                      prefs = {kpReportOutputPref: True,
# #                               kpVerbosePref: False
# #                               },
# #                      name='My_DDM'
# #                      )
# #
# # my_Mechanism_3 = DDM(params={kwExecuteMethodParams:{kwDDM_DriftRate:2.0,
# #                                                         kwDDM_Threshold:1.0},
# #                              # kwDDM_AnalyticSolution:kwDDM_NavarroAndFuss  # Note: this requires matlab engine be installed
# #                              kwDDM_AnalyticSolution:kwDDM_BogaczEtAl},
# #                      # prefs=DDM_prefs
# #                      # prefs = {kpReportOutputPref: PreferenceEntry(False, PreferenceLevel.INSTANCE),
# #                      #          kpVerbosePref: PreferenceEntry(False, PreferenceLevel.INSTANCE)
# #                      #          }
# #                      prefs = {kpReportOutputPref: True,
# #                               kpVerbosePref: False
# #                               },
# #                      name='My_DDM'
# #                      )
#
# # process_prefs = FunctionPreferenceSet(reportOutput_pref=PreferenceEntry(True,PreferenceLevel.INSTANCE),
# #                                        verbose_pref=PreferenceEntry(True,PreferenceLevel.SYSTEM))
# from Functions.Utility import LinearCombination
# y = Process_Base(params={kwConfiguration:[(myMechanism,
#                                            {
#                                                # kwInputStateParams:{},
#                                                kwParameterStateParams:
#                                                    {kwParamModulationOperation: ModulationOperation.MULTIPLY, # B
#                                                     kwDDM_DriftRate:(30.0,
#                                                                      ModulationOperation.MULTIPLY), # C
#                                                     kwDDM_Threshold:20.0,
#                                                     kwExecuteMethodParams:
#                                                        {LinearCombination.kwOffset: 100}, # A
#                                                     # kwProjectionParams:
#                                                     #     {Linear.kwIntercept: 1},
#                                                     },
#                                            }),
#                                           (myMechanism,
#                                            {
#                                                # kwInputStateParams:{},
#                                                kwParameterStateParams:
#                                                    {kwParamModulationOperation: ModulationOperation.MULTIPLY, # B
#                                                     kwDDM_DriftRate:(30.0,
#                                                                      ModulationOperation.MULTIPLY), # C
#                                                     kwDDM_Threshold:20.0,
#                                                     kwExecuteMethodParams:
#                                                        {LinearCombination.kwOffset: 100}, # A
#                                                     # kwProjectionParams:
#                                                     #     {Linear.kwIntercept: 1},
#                                                     },
#                                            }),
#                                           myMechanism]},
#
#                  # prefs=process_prefs)
#                  # prefs = {kpReportOutputPref: PreferenceLevel.INSTANCE,
#                  #          kpVerbosePref: PreferenceLevel.INSTANCE},
#                  prefs = {kpReportOutputPref: True,
#                           kpVerbosePref: False,
#                           kpParamValidationPref: PreferenceEntry(True, PreferenceLevel.INSTANCE)},
#                  name='My_Process')
#
# y.execute(1.0)
# # y.execute(1.0)
# # y.execute(1.0)
#endregion

# z = Process_Base(params={kwConfiguration:[myMechanism]})
z = Process_Base(params={kwConfiguration:[myMechanism, myMechanism]})
# z = Process_Base(params={kwConfiguration:[DDM, DDM, DDM]})
# z = Process_Base(params={kwConfiguration:[mechanism()]})
z.execute(30)
# #

# myMechanism.log.print_entries(ALL_ENTRIES, kwTime, kwValue)
myMechanism.log.print_entries(ALL_ENTRIES, kwTime, kwValue)