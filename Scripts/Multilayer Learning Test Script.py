from PsyNeuLink.Globals.Keywords import *

from PsyNeuLink.Functions.Mechanisms.ProcessingMechanisms.DDM import *
from PsyNeuLink.Functions.Mechanisms.ProcessingMechanisms.Transfer import Transfer
from PsyNeuLink.Functions.Projections.Mapping import Mapping
from PsyNeuLink.Functions.Projections.LearningSignal import LearningSignal
from PsyNeuLink.Functions.Process import process
from PsyNeuLink.Functions.Utility import Logistic, LinearMatrix, random_matrix

Input_Layer = Transfer(name='Input Layer',
                       function=Logistic(),
                       default_input_value = np.zeros((2,)))

Hidden_Layer_1 = Transfer(name='Hidden Layer_1',
                          function=Logistic(),
                          default_input_value = np.zeros((5,)))

Hidden_Layer_2 = Transfer(name='Hidden Layer_2',
                          function=Logistic(),
                          default_input_value = [0,0,0,0])

Output_Layer = Transfer(name='Output Layer',
                        function=Logistic(),
                        default_input_value = [0,0,0])

random_weight_matrix = lambda sender, receiver : random_matrix(sender, receiver, .2, -.1)

# TEST PROCESS.LEARNING WITH:
# CREATION OF FREE STANDING PROJECTIONS THAT HAVE NO LEARNING (Input_Weights, Middle_Weights and Output_Weights)
# INLINE CREATION OF PROJECTIONS (Input_Weights, Middle_Weights and Output_Weights)
# NO EXPLICIT CREATION OF PROJECTIONS (Input_Weights, Middle_Weights and Output_Weights)

# This projection will be used by the process below by referencing it in the process' configuration;
#    note: sender and receiver args don't need to be specified
Input_Weights = Mapping(name='Input Weights',
                        matrix=(random_weight_matrix, LearningSignal()),
                        )

# This projection will be used by the process below by assigning its sender and receiver args
#    to mechanismss in the configuration
Middle_Weights = Mapping(name='Middle Weights',
                         sender=Hidden_Layer_1,
                         receiver=Hidden_Layer_2,
                         matrix=FULL_CONNECTIVITY_MATRIX
                         # matrix=(FULL_CONNECTIVITY_MATRIX, LearningSignal())
                         )

# Commented lines in this projection illustrate variety of ways in which matrix and learning signals can be specified
Output_Weights = Mapping(name='Output Weights',
                         sender=Hidden_Layer_2,
                         receiver=Output_Layer,
                         # matrix=random_weight_matrix,
                         # matrix=(random_weight_matrix, LEARNING_SIGNAL),
                         # matrix=(random_weight_matrix, LearningSignal),
                         # matrix=(random_weight_matrix, LearningSignal()),
                         # matrix=(RANDOM_CONNECTIVITY_MATRIX),
                         # matrix=(RANDOM_CONNECTIVITY_MATRIX, LearningSignal),
                         matrix=FULL_CONNECTIVITY_MATRIX
                         # matrix=(FULL_CONNECTIVITY_MATRIX, LearningSignal)
                         )

z = process(default_input_value=[0, 0],
            configuration=[Input_Layer,
                           # The following reference to Input_Weights is needed to use it in the configuration
                           #    since it's sender and receiver args are not specified in its declaration above
                           Input_Weights,
                           Hidden_Layer_1,
                           # No projection specification is needed here since the sender arg for Middle_Weights
                           #    is Hidden_Layer_1 and its receiver arg is Hidden_Layer_2
                           # Middle_Weights,
                           Hidden_Layer_2,
                           # Output_Weights does not need to be listed for the same reason as Middle_Weights
                           # If Middle_Weights and/or Output_Weights is not declared above, then the process
                           #    will assign a default for missing projection
                           # Output_Weights,
                           Output_Layer],
            learning=LearningSignal,
            prefs={kpVerbosePref: PreferenceEntry(False, PreferenceLevel.INSTANCE)})

print ('Input Weights: \n', Input_Weights.matrix)
print ('Middle Weights: \n', Middle_Weights.matrix)
print ('Output Weights: \n', Output_Weights.matrix)

for i in range(10):

    z.execute([[-1, 30],[0, 0, 1]])

    print ('Input Weights: \n', Input_Weights.matrix)
    print ('Middle Weights: \n', Middle_Weights.matrix)
    print ('Output Weights: \n', Output_Weights.matrix)
