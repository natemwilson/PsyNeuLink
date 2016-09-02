from PsyNeuLink.Globals.Keywords import *

from PsyNeuLink.Functions.Mechanisms.ProcessingMechanisms.DDM import *
from PsyNeuLink.Functions.Mechanisms.ProcessingMechanisms.Transfer import Transfer
from PsyNeuLink.Functions.Mechanisms.MonitoringMechanisms.Comparator import kwComparatorTarget
from PsyNeuLink.Functions.Projections.Mapping import Mapping
from PsyNeuLink.Functions.Projections.LearningSignal import LearningSignal
from PsyNeuLink.Functions.Process import Process_Base
from PsyNeuLink.Functions.Utility import Logistic, LinearMatrix

Input_Layer = Transfer(name='Input Layer',
                       function=Logistic(),
                       default_input_value = [0,0])

Output_Layer = Transfer(name='Output Layer',
                        function=Logistic(),
                        default_input_value = [0,0])

Learned_Weights = Mapping(name='Learned Weights',
                          sender=Input_Layer,
                          receiver=Output_Layer,

                          # DEPRECATED:
                          # function=LinearMatrix(matrix=(kwDefaultMatrix,kwLearningSignal))
                          # params={kwFunctionParams:{kwMatrix:(kwIdentityMatrix,kwControlSignal)}}
                          # params={kwFunctionParams: {kwMatrix: (kwFullConnectivityMatrix,kwLearningSignal)}}

                          # SORT THROUGH / TRY THESE (from Multilayer:
                          # params={kwFunctionParams: {kwMatrix: kwIdentityMatrix}}
                          # params={kwFunctionParams: {kwMatrix: (kwIdentityMatrix,kwControlSignal)}}
                          # params={kwFunctionParams: {kwMatrix: (kwFullConnectivityMatrix,kwLearningSignal)}}
                          # params={kwFunctionParams: {kwMatrix: (random_weight_matrix, kwLearningSignal)}}
                          # matrix=random_weight_matrix
                          # matrix=(random_weight_matrix, kwLearningSignal)
                          # matrix=(kwFullConnectivityMatrix, kwLearningSignal)

                          # THESE ALL WORK:
                          # matrix=(kwDefaultMatrix, kwLearningSignal)
                          matrix=(kwDefaultMatrix, LearningSignal)
                          # matrix=(kwDefaultMatrix, LearningSignal())
                          # params={kwFunctionParams: {kwMatrix: (kwIdentityMatrix,kwLearningSignal)}},
                          # params={kwFunctionParams: {kwMatrix: (kwIdentityMatrix,LearningSignal)}}
                          )

# z = Process_Base(default_input_value=[0, 0],
#                  # params={kwConfiguration:[Input_Layer, Learned_Weights, Output_Layer]},
#                  params={kwConfiguration:[Input_Layer, Learned_Weights, Output_Layer]},
#                  prefs={kpVerbosePref: PreferenceEntry(True, PreferenceLevel.INSTANCE)})

z = Process_Base(default_input_value=[0, 0],
                 configuration=[Input_Layer, Learned_Weights, Output_Layer],
                 prefs={kpVerbosePref: PreferenceEntry(True, PreferenceLevel.INSTANCE)})


# Learned_Weights.monitoringMechanism.target = [1,1]
# Learned_Weights.monitoringMechanism.target = [0,0]
# from PsyNeuLink.Functions.Mechanisms.MonitoringMechanisms.Comparator import kwComparatorTarget
# Learned_Weights.monitoringMechanism.paramsCurrent[kwComparatorTarget] = [1,1]

# z.execute(input=[-1, 30],
#           runtime_params={kwComparatorTarget: [1, 1]})

for i in range(10):
    z.execute([[-1, 30],[1, 1]])
    print (Learned_Weights.matrix)