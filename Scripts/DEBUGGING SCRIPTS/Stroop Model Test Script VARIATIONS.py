from PsyNeuLink.Components.Functions.Function import Linear, Logistic
from PsyNeuLink.Components.Mechanisms.ProcessingMechanisms.TransferMechanism import TransferMechanism
from PsyNeuLink.Components.System import *
from PsyNeuLink.Globals.Keywords import *

process_prefs = {REPORT_OUTPUT_PREF: True,
                 VERBOSE_PREF: False}

system_prefs = {REPORT_OUTPUT_PREF: True,
                VERBOSE_PREF: False}

colors = TransferMechanism(default_input_value=[0,0],
                        function=Linear,
                        name="Colors")

words = TransferMechanism(default_input_value=[0,0],
                        function=Linear,
                        name="Words")

response = TransferMechanism(default_input_value=[0,0],
                           function=Logistic,
                           name="Response")

color_naming_process = process(
    default_input_value=[1, 2.5],
    # pathway=[(colors, 0), FULL_CONNECTIVITY_MATRIX, (response,0)],
    pathway=[colors, FULL_CONNECTIVITY_MATRIX, response],
    learning=LEARNING_PROJECTION,
    target=[1,2],
    name='Color Naming',
    prefs=process_prefs
)

word_reading_process = process(
    default_input_value=[.5, 3],
    pathway=[words, FULL_CONNECTIVITY_MATRIX, response],
    name='Word Reading',
    learning=LEARNING_PROJECTION,
    target=[3,4],
    prefs=process_prefs
)

mySystem = system(processes=[color_naming_process, word_reading_process],
                  name='Stroop Model',
                  targets=[0,0],
                  prefs=system_prefs,
                  )

# TEST REPORT_OUTPUT_PREFs:
# colors.reportOutputPref = True
# words.reportOutputPref = True
# response.reportOutputPref = True
# color_naming_process.reportOutputPref = False
# word_reading_process.reportOutputPref =  False
# process_prefs.reportOutputPref = PreferenceEntry(True, PreferenceLevel.CATEGORY)

# mySystem.reportOutputPref = True

# # Execute processes:
# for i in range(10):
#     color_naming_process.execute(input=[1, 1],target=[0,1])
#     print(response.inputState.receivesFromProjections[0].matrix)
#     print(response.inputState.receivesFromProjections[1].matrix)
#
#     word_reading_process.execute(input=[1, 1], target=[1,0])
#     print(response.inputState.receivesFromProjections[0].matrix)
#     print(response.inputState.receivesFromProjections[1].matrix)

# Execute system:
# mySystem.execute(input=[[1,1],[1,1]])

# mySystem.show_graph()

stim_dict = {colors:[[1,0],[0,1]],
             words:[[0,1],[1,0]]}
target_dict= {response:[[1,0],[0,1]]}

mySystem.run(num_executions=2,
             inputs=stim_dict,
             targets=target_dict)


# SHOW OPTIONS:
# mySystem.show()
# mySystem.controller.show()

