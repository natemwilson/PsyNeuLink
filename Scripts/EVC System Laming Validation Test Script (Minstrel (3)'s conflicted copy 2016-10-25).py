# from PsyNeuLink.Components.Mechanisms.ProcessingMechanisms.Deprecated.LinearMechanism import *
from PsyNeuLink.Components.Mechanisms.ProcessingMechanisms.DDM import *
from PsyNeuLink.Components.Mechanisms.ProcessingMechanisms.Transfer import *
from PsyNeuLink.Components.Process import process
from PsyNeuLink.Components.Projections.ControlSignal import ControlSignal
from PsyNeuLink.Components.System import system
from PsyNeuLink.Components.Mechanisms.ControlMechanisms.EVCMechanism import EVCMechanism
from PsyNeuLink.Globals.Keywords import *
from PsyNeuLink.Globals.Run import run, _construct_inputs


# Preferences:
DDM_prefs = ComponentPreferenceSet(
                prefs = {
                    kpVerbosePref: PreferenceEntry(False,PreferenceLevel.INSTANCE),
                    kpReportOutputPref: PreferenceEntry(True,PreferenceLevel.INSTANCE)})

process_prefs = ComponentPreferenceSet(reportOutput_pref=PreferenceEntry(False,PreferenceLevel.INSTANCE),
                                      verbose_pref=PreferenceEntry(True,PreferenceLevel.INSTANCE))

# Mechanisms:
Input = Transfer(name='Input')
Reward = Transfer(name='Reward')
Decision = DDM(function=BogaczEtAl(drift_rate=(1.0, ControlSignal(function=Linear)),
                                   threshold=(1.0, ControlSignal(function=Linear)),
                                   noise=(0.5),
                                   starting_point=(0),
                                   t0=0.45),
               prefs = DDM_prefs,
               name='Decision')

# Processes:
TaskExecutionProcess = process(
    default_input_value=[0],
    pathway=[(Input, 0), IDENTITY_MATRIX, (Decision, 0)],
    prefs = process_prefs,
    name = 'TaskExecutionProcess')

RewardProcess = process(
    default_input_value=[0],
    pathway=[(Reward, 1)],
    prefs = process_prefs,
    name = 'RewardProcess')

# System:
mySystem = system(processes=[TaskExecutionProcess, RewardProcess],
                  controller=EVCMechanism,
                  enable_controller=True,
                  monitored_output_states=[Reward, PROBABILITY_UPPER_BOUND,(RESPONSE_TIME, -1, 1)],
                  # monitored_output_states=[Reward, DECISION_VARIABLE,(RESPONSE_TIME, -1, 1)],
                  name='EVC Test System')

# Show characteristics of system:
mySystem.show()
mySystem.controller.show()

# Specify stimuli for run:
#   two ways to do so:

#   - as a dictionary of stimulus lists; for each entry:
#     key is name of an origin mechanism in the system
#     value is a list of its sequence of stimuli (one for each trial)
inputList = [0.5, 0.123]
rewardList = [20, 20]
# stim_list_dict = {Input:[0.5, 0.123],
#               Reward:[20, 20]}
stim_list_dict = {Input:[[0.5], [0.123]],
              Reward:[[20], [20]]}

#   - as a list of trials;
#     each item in the list contains the stimuli for a given trial,
#     one for each origin mechanism in the system
trial_list = [[0.5, 20], [0.123, 20]]
reversed_trial_list = [[Reward, Input], [20, 0.5], [20, 0.123]]

# Create printouts function (to call in run):
def show_trial_header():
    print("\n############################ TRIAL {} ############################".format(CentralClock.trial))

def show_results():
    results = sorted(zip(mySystem.terminalMechanisms.outputStateNames, mySystem.terminalMechanisms.outputStateValues))
    print('\nRESULTS (time step {}): '.format(CentralClock.time_step))
    print ('\tDrift rate control signal (from EVC): {}'.format(Decision.parameterStates[DRIFT_RATE].value))
    print ('\tThreshold control signal (from EVC): {}'.format(Decision.parameterStates[THRESHOLD].value))
    for result in results:
        print("\t{}: {}".format(result[0], result[1]))

# Run system:

# mySystem.run(inputs=trial_list,
# # mySystem.run(inputs=reversed_trial_list,
mySystem.run(inputs=stim_list_dict,
             call_before_trial=show_trial_header,
             call_after_time_step=show_results
             )