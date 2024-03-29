# Princeton University licenses this file to You under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may obtain a copy of the License at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.
#
#
# ********************************************  Keywords ***************************************************************

# **********************************************************************************************************************
# ******************************************    CLASSES    *************************************************************
# **********************************************************************************************************************

# IMPLEMENTATION NOTE:
#  These classes are used for documentation purposes only.
#  The attributes of each are assigned to constants (listed in the next section of this module)
#    that are the ones actually used by the code.

class Keywords:
    """
    Attributes
    ----------

    ORIGIN
        A `ProcessingMechanism <ProcessingMechanism>` that is the first mechanism of a process and/or system,
        and that receives the input to the process or system when it is :ref:`executed or run <Run>`.  A process may
        have only one `ORIGIN` mechanism, but a system may have many.  Note that the `ORIGIN`
        mechanism of a process is not necessarily an `ORIGIN` of the system to which it belongs, as it may
        receive projections from other processes in the system. The `ORIGIN` mechanisms of a process or
        system are listed in its :keyword:`originMechanisms` attribute, and can be displayed using its :keyword:`show`
        method.  For additional details about `ORIGIN` mechanisms in processes, see
        `Process Mechanisms <Process_Mechanisms>` and `Process Input and Output <Process_Input_And_Ouput>`;
        and for systems see `System Mechanisms <System_Mechanisms>` and
        `System Input and Initialization <System_Execution_Input_And_Initialization>`.

    INTERNAL
        A `ProcessingMechanism <ProcessingMechanism>` that is not designated as having any other status.

    CYCLE
        A `ProcessingMechanism <ProcessingMechanism>` that is *not* an `ORIGIN` mechanism, and receives a projection
        that closes a recurrent loop in a process and/or system.  If it is an `ORIGIN` mechanism, then it is simply
        designated as such (since it will be assigned input and therefore be initialized in any event).

    INITIALIZE_CYCLE
        A `ProcessingMechanism <ProcessingMechanism>` that is the `sender <Projection.Projection.sender>` of a
        projection that closes a loop in a process or system, and that is not an `ORIGIN` mechanism (since in that
        case it will be initialized in any event). An `initial value  <Run_InitialValues>` can be assigned to such
        mechanisms, that will be used to initialize the process or system when it is first run.  For additional
        information, see `Run <Run_Initial_Values>`, `System Mechanisms <System_Mechanisms>` and
        `System Input and Initialization <System_Execution_Input_And_Initialization>`.

    TERMINAL
        A `ProcessingMechanism <ProcessingMechanism>` that is the last mechanism of a process and/or system, and
        that provides the output to the process or system when it is `executed or run <Run>`.  A process may
        have only one `TERMINAL` mechanism, but a system may have many.  Note that the `TERMINAL`
        mechanism of a process is not necessarily a `TERMINAL` mechanism of the system to which it belongs,
        as it may send projections to other processes in the system.  The `TERMINAL` mechanisms of a process
        or system are listed in its :keyword:`terminalMechanisms` attribute, and can be displayed using its
        :keyword:`show` method.  For additional details about `TERMINAL` mechanisms in processes, see
        `Process_Mechanisms` and `Process_Input_And_Ouput`; and for systems see `System_Mechanisms`.

    SINGLETON
        A `ProcessingMechanism` that is the only mechanism in a process and/or system.  It can serve the functions
        of an `ORIGIN` and/or a `TERMINAL` mechanism.

    MONITORING
        A `MonitoringMechanism <MonitoringMechanism>` configured for learning that is not a `TARGET`; that is, it
        is associated with an `INTERNAL` rather than a `TERMINAL` ProcessingMechanism in the process and/or system to
        which it belongs. For `backpropagation <Function.BackPropagation>` learning, it is a `WeightedErrorMechanism`.
        See `MonitoringMechanisms <LearningProjection_MonitoringMechanism> for additional details.

    TARGET
        A `ComparatorMechanism` of a process and/or system configured for learning that receives a target value from
        its `execute <ComparatorMechanism.ComparatorMechanism.execute>` or
        `run <ComparatorMechanism.ComparatorMechanism.execute>` method.  It must be associated with the `TERMINAL`
        mechanism of the process or system. The `TARGET` mechanisms of a process or system are listed in its
        :keyword:`targetMechanisms` attribute, and can be displayed using its :keyword:`show` method.  For additional
        details, see `TARGET mechanisms <LearningProjection_Targets>` and specifying `target values <Run_Targets>`.


    """
    def __init__(self):
        self.ORIGIN = ORIGIN
        self.INTERNAL = INTERNAL
        self.CYCLE = CYCLE
        self.INITIALIZE_CYCLE = INITIALIZE_CYCLE
        self.TERMINAL = TERMINAL
        self.SINGLETON = SINGLETON
        self.MONITORING = MONITORING
        self.TARGET = TARGET


class MatrixKeywords:
    """
    Attributes
    ----------

    IDENTITY_MATRIX
        a square matrix of 1's; this requires that the length of the sender and receiver values are the same.

    FULL_CONNECTIVITY_MATRIX
        a matrix that has a number of rows equal to the length of the sender's value, and a number of columns equal
        to the length of the receiver's value, all the elements of which are 1's.

    RANDOM_CONNECTIVITY_MATRIX
        a matrix that has a number of rows equal to the length of the sender's value, and a number of columns equal
        to the length of the receiver's value, all the elements of which are filled with random values uniformly
        distributed between 0 and 1.

    AUTO_ASSIGN_MATRIX
        if the sender and receiver are of equal length, an `IDENTITY_MATRIX` is assigned;  otherwise, a
        `FULL_CONNECTIVITY_MATRIX` is assigned.

    DEFAULT_MATRIX
        used if no matrix specification is provided in the constructor;  it presently assigns an `IDENTITY_MATRIX`.

    """
    def __init__(self):
        self.MATRIX = MATRIX
        self.IDENTITY_MATRIX = IDENTITY_MATRIX
        self.FULL_CONNECTIVITY_MATRIX = FULL_CONNECTIVITY_MATRIX
        self.RANDOM_CONNECTIVITY_MATRIX = RANDOM_CONNECTIVITY_MATRIX
        self.AUTO_ASSIGN_MATRIX = AUTO_ASSIGN_MATRIX
        self.DEFAULT_MATRIX = DEFAULT_MATRIX

    def _values(self):
        return list(self.__dict__.values())

    def _names(self):
        return list(self.__dict__)

MATRIX = "matrix"
IDENTITY_MATRIX = "IdentityMatrix"
FULL_CONNECTIVITY_MATRIX = "FullConnectivityMatrix"
RANDOM_CONNECTIVITY_MATRIX = "RandomConnectivityMatrix"
AUTO_ASSIGN_MATRIX = 'AutoAssignMatrix'
# DEFAULT_MATRIX = AUTO_ASSIGN_MATRIX
DEFAULT_MATRIX = IDENTITY_MATRIX

MATRIX_KEYWORDS = MatrixKeywords()
MATRIX_KEYWORD_VALUES = MATRIX_KEYWORDS._values()
MATRIX_KEYWORD_NAMES = MATRIX_KEYWORDS._names()
# MATRIX_KEYWORD_VALUES = list(MATRIX_KEYWORDS.__dict__.values())
# MATRIX_KEYWORD_NAMES = list(MATRIX_KEYWORDS.__dict__)

# **********************************************************************************************************************
# ******************************************    CONSTANTS  *************************************************************
# **********************************************************************************************************************

ON = True
OFF = False
DEFAULT = False
AUTO = True

# Used by initDirective
INIT_FULL_EXECUTE_METHOD = 'init using the full base class execute method'
INIT__EXECUTE__METHOD_ONLY = 'init using only the subclass _execute method'
INIT_FUNCTION_METHOD_ONLY = 'init using only the subclass __function__ method'


#region ---------------------------------------------    GENERAL    ----------------------------------------------------
# General

kwSeparator = ': '
SEPARATOR_BAR = ' | '
kwProgressBarChar = '.'
# kwValueSuffix = '_value'
NO_CONTEXT = "NO_CONTEXT"
INITIALIZING = " INITIALIZING "  # Used as context for Log
kwInstantiate = " INSTANTIATING "  # Used as context for Log
EXECUTING = " EXECUTING " # Used in context for Log and ReportOutput pref
kwAssign = ': Assign' # Used in context for Log
ASSIGN_VALUE = ': Assign value'
kwAggregate = ': Aggregate' # Used in context for Log
kwReceiver = "receiver"
kwValidate = 'Validate'
VALIDATE = kwValidate
COMMAND_LINE = "COMMAND_LINE"
kwParams = 'params'
CHANGED = 'CHANGED'
UNCHANGED = 'UNCHANGED'


#endregion

#region -------------------------------------------    Preferences    --------------------------------------------------

kwPrefs = "Prefs"
kwPrefsOwner = "kwPrefsOwner"
kwPrefLevel = 'kwPrefLevel'
kwPrefCurrentValue = 'kwPrefCurrentValue'
kwPrefBaseValue = 'kwPrefBaseValue'
kwPreferenceSetName = 'kwPreferenceSetName'
kwDefaultPreferenceSetOwner = 'DefaultPreferenceSetOwner'
# kpLogPref = '_log_pref'
# kpParamValidationPref = '_param_validation_pref'
# kpVerbosePref = '_verbose_pref'
#endregion

#region --------------------------------------------    TIME SCALE    --------------------------------------------------

CENTRAL_CLOCK = "CentralClock"
TIME_SCALE = "time_scale"
CLOCK = "clock"
#endregion

#region --------------------------------------------    PREFERENCES    -------------------------------------------------

kwPreferenceSet = 'PreferenceSet'
kwComponentPreferenceSet = 'PreferenceSet'
#endregion

#region ------------------------------------------------   LOG    ------------------------------------------------------

kwTime = 'Time'
kwContext = 'Context'
kwValue = 'Value'
#endregion

#region -----------------------------------------------  UTILITIES  ----------------------------------------------------

kpMechanismTimeScaleLogEntry = "Mechanism TimeScale"
kpMechanismInputLogEntry = "Mechanism Input"
kpMechanismOutputLogEntry = "Mechanism Output"
kpMechanismControlAllocationsLogEntry = "Mechanism Control Allocations"
#endregion

#region ----------------------------------------------   COMPONENT   ---------------------------------------------------

# General:
PREFS_ARG = "prefs"
VARIABLE = "variable"
NAME = "name"
PARAMS = "params"
CONTEXT = "context"

kwInitialValues = 'initial_values'

# inputs list/ndarray:
TRIALS_DIM = 0
TIME_STEPS_DIM = 1
PROCESSES_DIM = 2
INPUTS_DIM = 3

COMPONENT_INIT = 'Function.__init__'
DEFERRED_INITIALIZATION = 'Deferred Init'
DEFERRED_DEFAULT_NAME = 'DEFERRED_DEFAULT_NAME'
FUNCTION = "function" # Param name for function, method, or type to instantiate and assign to self.execute
FUNCTION_PARAMS  = "function_params" # Params used to instantiate or assign to a FUNCTION

PARAM_CLASS_DEFAULTS = "paramClassDefaults"        # "Factory" default params for a Function
PARAM_INSTANCE_DEFAULTS = "paramsInstanceDefaults" # Params used to instantiate a Function; supercede paramClassDefaults
PARAMS_CURRENT = "paramsCurrent"                  # Params currently in effect for an instance of a Function
                                                   #    in general, this includes params specifed as arg in a
                                                   #    to Function.execute;  however, there are some exceptions
                                                   #    in which those are kept separate from paramsCurrent (see DDM)

FUNCTION_CHECK_ARGS = 'super._check_args' # Use for "context" arg
kwFunctionOutputTypeConversion = "FunctionOutputTypeConversion" # Used in Function Components to set output type

#endregion

#region ----------------------------------------    COMPONENT SUBCLASSES  ----------------------------------------------

# Component Categories   -----------------

kwSystemComponentCategory = "System_Base"
kwProcessComponentCategory = "Process_Base"
kwMechanismComponentCategory = "Mechanism_Base"
kwStateComponentCategory = "State_Base"
kwProjectionComponentCategory = "Projection_Base"
kwComponentCategory = "Function_Base"

# Component TYPES  -----------------

# Mechanisms:
PROCESSING_MECHANISM = "ProcessingMechanism"
MONITORING_MECHANISM = "MonitoringMechanism"
CONTROL_MECHANISM = "ControlMechanism"
LEARNING_MECHANISM = "LearningMechanism"

# States:
INPUT_STATE = "InputState"
OUTPUT_STATE = "OutputState"
PARAMETER_STATE = "ParameterState"

# Projections:
MAPPING_PROJECTION = "MappingProjection"
CONTROL_PROJECTION = "ControlProjection"
LEARNING_PROJECTION = "LearningProjection"

# Function:
EXAMPLE_FUNCTION_TYPE = "EXAMPLE FUNCTION"
USER_DEFINED_FUNCTION_TYPE = "USER DEFINED FUNCTION TYPE"
COMBINATION_FUNCTION_TYPE = "COMBINATION FUNCTION TYPE"
DIST_FUNCTION_TYPE = "DIST FUNCTION TYPE"
INTEGRATOR_FUNCTION_TYPE = "INTEGRATOR FUNCTION TYPE"
TRANFER_FUNCTION_TYPE = "TRANSFER FUNCTION TYPE"
LEARNING_FUNCTION_TYPE = 'LEARNING FUNCTION TYPE'
DISTRIBUTION_FUNCTION_TYPE = "DISTRIBUTION FUNCTION TYPE"



# Component SUBTYPES -----------------

# ControlMechanisms:
DEFAULT_CONTROL_MECHANISM = "DefaultControlMechanism"
EVC_MECHANISM = "EVCMechanism"

# MonitoringMechanisms:
COMPARATOR_MECHANISM = "ComparatorMechanism"
WEIGHTED_ERROR_MECHANISM = "WeightedErrorMechanism"
OBJECTIVE_MECHANISM = "ObjectiveMechanism"

# ProcessingMechanisms:
DDM_MECHANISM = "DDM"
TRANSFER_MECHANISM = "TransferMechanism"
INTEGRATOR_MECHANISM = "IntegratorMechanmism"

# Function:
ARGUMENT_THERAPY_FUNCTION = "Contradiction"
USER_DEFINED_FUNCTION = "USER DEFINED FUNCTION"
REDUCE_FUNCTION = "Reduce"
LINEAR_COMBINATION_FUNCTION = "LinearCombination"
WEIGHTED_ERROR_FUNCTION = "WeighedErrorFunction"
LINEAR_FUNCTION = "Linear"
EXPONENTIAL_FUNCTION = "Exponential"
LOGISTIC_FUNCTION = "Logistic"
SOFTMAX_FUNCTION = 'SoftMax'
INTEGRATOR_FUNCTION = "Integrator"
DDM_INTEGRATOR_FUNCTION = "DDMIntegrator"
LINEAR_MATRIX_FUNCTION = "Linear Matrix"
BACKPROPAGATION_FUNCTION = 'Backpropagation Learning Algorithm'
RL_FUNCTION = 'Reinforcement Learning Algorithm'
ERROR_DERIVATIVE_FUNCTION = 'Error Derivative'

#Distribution functions 

NORMAL_DIST_FUNCTION = "Normal Distribution"
UNIFORM_DIST_FUNCTION = "Uniform Distribution"
EXPONENTIAL_DIST_FUNCTION = "Exponential Distribution"
GAMMA_DIST_FUNCTION = "Gamma Distribution"
WALD_DIST_FUNCTION = "Wald Distribution"


#endregion

#region ----------------------------------------------    SYSTEM   ----------------------------------------------------

SYSTEM = "System"
SYSTEM_INIT = 'System.__init__'
DEFAULT_SYSTEM = "DefaultSystem"
CONTROLLER = "controller"
ENABLE_CONTROLLER = "enable_controller"
CONROLLER_PHASE_SPEC = 'ControllerPhaseSpec'

RUN = 'Run'

#endregion

#region ----------------------------------------------    PROCESS   ----------------------------------------------------

PROCESS = "PROCESS"
kwProcesses = "processes"
PROCESS_INIT = 'Process.__init__'
PATHWAY = "pathway"
CLAMP_INPUT = "clamp_input"
SOFT_CLAMP = "soft_clamp"
HARD_CLAMP = "hard_clamp"
LEARNING = 'learning'
LEARNING_RATE = "learning_rate"
CONTROL = 'control'
kwProjections = "projections"
kwProcessDefaultProjectionFunction = "Default Projection Function"
kwProcessExecute = "ProcessExecute"
kpMechanismExecutedLogEntry = "Mechanism Executed"
#endregion

#region ---------------------------------------------    MECHANISM   ---------------------------------------------------

MECHANISM = 'MECHANISM'
kwMechanism = "MECHANISM"
kwMechanismName = "MECHANISM NAME"
kwMechanismDefault = "DEFAULT MECHANISM"
DEFAULT_PROCESSING_MECHANISM = "DefaultProcessingMechanism"
DEFAULT_MONITORING_MECHANISM = "DefaultMonitoringMechanism"
kwProcessDefaultMechanism = "ProcessDefaultMechanism"
kwMechanismType = "Mechanism Type" # Used in mechanism dict specification (e.g., in process.pathway[])
kwMechanismDefaultInputValue = "Mechanism Default Input Value " # Used in mechanism specification dict
kwMechanismParamValue = "Mechanism Param Value"                 # Used to specify mechanism param value
kwMechanismDefaultParams = "Mechanism Default Params"           # Used in mechanism specification dict

ORIGIN = 'ORIGIN'
INTERNAL = 'INTERNAL'
CYCLE = 'CYCLE'
INITIALIZE_CYCLE = 'INITIALIZE_CYCLE'
TERMINAL = 'TERMINAL'
SINGLETON = 'ORIGIN AND TERMINAL'
MONITORING = 'MONITORING'
SAMPLE = 'SAMPLE'
TARGET = 'TARGET'

kwStateValue = "State value"   # Used in State specification dict
                                                 #  to specify State value
STATE_PARAMS = "State params" # Used in State specification dict

# ParamClassDefaults:
kwMechanismTimeScale = "Mechanism Time Scale"
kwMechanismExecutionSequenceTemplate = "Mechanism Execution Sequence Template"

# Entries for output OrderedDict, describing the current state of the Mechanism
kwMechanismOutputValue = "MechanismOutputValue" # points to <mechanism>.outputStateValue
kwMechanismConfidence = "MechanismConfidence"   # contains confidence of current kwMechanismValue
kwMechanismPerformance = "MechanismPerformance" # contains value from objective function
kwMechanismDuration = "MechanismDuration"       # contains number of time steps since process.execute was called
kwMechanismParams = "MechanismParams"           # dict of ParameterState objects in <mechanism>.params

kwMechanismExecuteFunction = "MECHANISM EXECUTE FUNCTION"
kwMechanismAdjustFunction = "MECHANISM ADJUST FUNCTION"
kwMechanismInterrogateFunction = "MECHANISM INTERROGATE FUNCTION"
kwMechanismTerminateFunction = "MECHANISM TERMINATE FUNCTION"
# TBI: kwMechanismAccuracyFunction = "MECHANISM ACCURACY FUNCTION"
#endregion


#region ------------------------------------------    CONTROL MECHANISM   ----------------------------------------------

MAKE_DEFAULT_CONTROLLER = "make_default_controller"
MONITOR_FOR_CONTROL = "monitor_for_control"
PREDICTION_MECHANISM = "PredictionMechanism"
PREDICTION_MECHANISM_TYPE = "prediction_mechanism_type"
PREDICTION_MECHANISM_PARAMS = "prediction_mechanism_params"
PREDICTION_MECHANISM_OUTPUT = "PredictionMechanismOutput"
kwPredictionProcess = "PredictionProcess"
CONTROL_SIGNAL = 'control_signal'
CONTROL_PROJECTIONS = 'ControlProjections'
OUTCOME_FUNCTION = 'outcome_function'
COST_FUNCTION = 'cost_function'
COMBINE_OUTCOME_AND_COST_FUNCTION = 'combine_outcome_and_cost_function'
VALUE_FUNCTION = 'value_function'
SAVE_ALL_VALUES_AND_POLICIES = 'save_all_values_and_policies'
SYSTEM_DEFAULT_CONTROLLER = "DefaultController"
EVC_SIMULATION = 'SIMULATING'
ALLOCATION_SAMPLES = "allocation_samples"

#endregion

#region ----------------------------------------------    STATES  ------------------------------------------------------

kwState = "State"
# These are use for dict specification of State
STATE_PROJECTIONS = "StateProjections"  # Used to specify projection list to State
kwStateName = "StateName"
kwStatePrefs = "StatePrefs"
kwStateContext = "StateContext"

INPUT_STATES = 'input_states'
INPUT_STATE_PARAMS = 'input_state_params'
kwAddInputState = 'kwAddNewInputState'     # Used by Mechanism._add_projection_to()
kwAddOutputState = 'kwAddNewOutputState'   # Used by Mechanism._add_projection_from()
PARAMETER_STATES = 'parameter_states'
PARAMETER_STATE_PARAMS = 'parameter_state_params'
PARAMETER_MODULATION_OPERATION = 'parameter_modulation_operation'
OUTPUT_STATES = 'output_states'
OUTPUT_STATE_PARAMS = 'output_states_params'
INDEX = 'index'
CALCULATE = 'calculate'
#endregion

#region ---------------------------------------------    PROJECTION  ---------------------------------------------------

# Attributes / KVO keypaths / Params
PROJECTION = "Projection"
PROJECTION_TYPE = "ProjectionType"
PROJECTION_PARAMS = "ProjectionParams"
MAPPING_PROJECTION_PARAMS = "MappingProjectionParams"
CONTROL_PROJECTION_PARAMS = "ControlProjectionParams"
LEARNING_PROJECTION_PARAMS = 'LearningProjectionParams'
PROJECTION_SENDER = 'projectionSender'
kwSenderArg = 'sender'
PROJECTION_SENDER_VALUE =  "projectionSenderValue"
kwProjectionReceiver = 'ProjectionReceiver'
kwReceiverArg = 'receiver'
# kpLog = "ProjectionLog"
MONITOR_FOR_LEARNING = 'monitor_for_learning'


#endregion

#region ----------------------------------------------    FUNCTION   ---------------------------------------------------


SUM = 'sum'
DIFFERENCE = 'difference'
PRODUCT = 'product'
QUOTIENT = 'quotient'
SUBTRACTION = 'subtraction'
DIVISION = 'division'
SCALAR = 'scalar'
VECTOR = 'vector'

GAIN = 'gain'
BIAS = 'bias'
SLOPE = 'slope'
INTERCEPT = 'intercept'
RATE = 'rate'
SCALE = 'scale'
NOISE = 'noise'

DRIFT_RATE = 'drift_rate'
TIME_STEP_SIZE = 'time_step_size'

MEAN = 'mean'
STANDARD_DEV = 'standard_dev'

LOW = 'low'
HIGH = 'high'

BETA = 'beta'

SHAPE = 'shape'

WEIGHTING = "weighting"

OUTPUT_TYPE = 'output'
ALL = 'all'
MAX_VAL = 'max_val'
MAX_INDICATOR = 'max_indicator'
PROB = 'prob'
MUTUAL_ENTROPY = 'mutual entropy'

INITIALIZER = 'initializer'
WEIGHTS = "weights"
EXPONENTS = "exponents"
OPERATION = "operation"
OFFSET = "offset"
LINEAR = 'linear'
CONSTANT = 'constant'
SIMPLE = 'scaled'
ADAPTIVE = 'apaptive'
DIFFUSION = 'diffusion'

#endregion
