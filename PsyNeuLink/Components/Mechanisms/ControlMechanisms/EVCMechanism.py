# Princeton University licenses this file to You under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may obtain a copy of the License at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


# *************************************************  EVCMechanism ******************************************************

#FIX: SEARCH FOR :ref`xxx <LINK>`
"""

Overview
--------

An EVCMechanism is a :doc:`ControlMechanism <ControlMechanism>` that manages a "portfolio" of
:doc:`ControlSignals <ControlSignal>` that regulate the performance of the system to which it belongs. It implements
a form of the Expected Value of Control (EVC) Theory described in :ref:`Shenhav et al. (2013) <LINK>`.  Each
ControlSignal is associated with a :doc:`ControlProjection`.  The ControlSignal's `intensity` determines the value of
its ControlProjection, which in turn regulates the parameter of a mechanism or its function. A particular combination
of ControlSignal intensities is called an `allocationPolicy`.  When a system is executed, it concludes by executing
the EVCMechanism, which determines the `allocationPolicy`, and thereby the values of controlled parameters forthe next
round of execution.

.. _EVCMechanism_EVC:

The procedure by which the EVCMechanism selects an `allocationPolicy` when it is executed is determined by its
:py:data:`function <EVCMechanism.function>` attribute. By default, this evaluates the performance of the system under
every possible `allocationPolicy`, and chooses the best one. It does this by simulating the system under each
`allocationPolicy`, and evaluating the expected value of control (EVC), a cost-benefit analysis that weighs the cost
of the ControlSignals against the outcomes of performance for the given policy.  It then selects the one that generates
the maximum EVC, which is implemented for the next round of execution. Each step of this procedure can be modified,
or it can be replaced entirely, by assigning custom functions to corresponding parameters of the EVCMechanism, as
described under `EVC_Calculation`.

.. _EVCMechanism_Creation:

Creating an EVCMechanism
------------------------

An EVCMechanism can be created using the standard Python method of calling its constructor.  However,  more commonly,
it is generated automatically when a system is created and an EVCMechanism is specified as its
`controller` attribute (see :ref:`Controller <System_Execution_Control>`).
An EVCMechanism that has been constructed automatically can nevertheless be customized, like any other PsyNeuLink
component, either by assigning a params dictionary to the controller's ``params`` parameter, or by using its
`assign_params <LINK>` method.  In both cases, a parameter to be modified is referenced using a keyword corresponding
to the argument for that parameter in the EVCMechanism's constructor (and described under `EVCMechanism_Structure`
below).

When an EVCMechanism is constructed automatically, inputStates are created and assigned projections from the
outputStates of the mechanisms it uses to evaluate the system's performance. The EVCMechanism's outputStates are
used to implement :doc:`ControlSignals <ControlSignal>`, and those are assigned :doc:`ControlProjections
<ControlProjection>` that project to the parameterStates for the parameters of the mechanisms and/or functions to be
controlled.  In addition, a set of prediction mechanisms are created, that are used to generate input to the system
when the EVC executes it in order to evaluate its performance. These specialized components are described in the
section that follows.

.. _EVCMechanism_Structure:

Structure
---------

.. _EVCMechanism_InputStates:
.. _EVCMechanism_MonitoredOutputStates:

InputStates
~~~~~~~~~~~

Each inputState of an EVCMechanism represents an outcome of processing — that is, the value of an outputState of a
mechanism in the system — that the EVCMechanism uses to evaluate the system's performance under an `allocationPolicy`.
One inputState is assigned to each outputState evaluated in the system.  OutputStates are specified to be evaluated
using the EVCMechanism's `MONITOR_FOR_CONTROL <monitor_for_control>` parameter, and each can be assigned an exponent
and/or a weight to parameterize its contribution  to the evaluation (see `ControlMechanism_Monitored_OutputStates` for
specifying monitored outputStates; and `below <EVCMechanism_Examples>` for examples).  By default, the value of the
EVCMechanism's `MONITOR_FOR_CONTROL` parameter is `MonitoredOutputStatesOption.PRIMARY_OUTPUT_STATES`,
which specifies monitoring the :ref:`primary outputState <OutputState_Primary>` of every `TERMINAL` mechanism in the
system, each of which is assigned an exponent and weight of 1.  When an EVCMechanism is :ref:`created automatically
<EVCMechanism_Creation>`, an inputState is created for each outputState specified in its `MONITOR_FOR_CONTROL`
parameter, and a `MappingProjection` is created that projects to that inputState from the outputState to be
monitored.  The outputStates of a system being monitored by an EVCMechanism are listed in its `monitoredOutputStates`
attribute.

.. _EVC_Function

Function
~~~~~~~~

The `function` of an EVCMechanism determines the `allocationPolicy` -- that is, the `intensity` of each of its
ControlSignals -- that will be used in the next round of the system's execution.  Any function can be used that
returns an appropriate value (i.e., that has the same number of elements as the EVCMechanism's `controlSignals`
attribute, each of which specifies an `allocation` for the corresponding ControlSignal). The default function for an
EVCMechanism is an internal method (_control_signal_grid_search) that evaluates the performance of the system under
a set of specified allocationPolicies, and chooses the one that generates the best performance (the greatest EVC).
The procedure, including the four customizable functions it uses, is described below.

.. _EVC_Calculation:

EVC Calculation
^^^^^^^^^^^^^^^

The default EVC :py:data:`function <EVCMechanism.function>` calculates the expected value of control (EVC) for every
combination of `allocation` values specified to be sampled for its ControlSignals (i.e., every possible
`allocationPolicy`).  Each policy is constructed by drawing one value from the `allocation_samples <LINK>` attribute of
each of the EVCMechanism's ControlSignals.  An `allocationPolicy` is constructed for every possible combination of
values, and stored in the EVCMechanism's `controlSignalSearchSpace` attribute.  The EVCMechanism's `run_simulation
<LINK>` method is then used to simulate the system under each `allocationPolicy` in `controlSignalSearchSpace`,
calculate the EVC for each of those policies, and return the policy with the greatest EVC.  By default, only the
maximum EVC is saved and returned.  However, by setting the  `SAVE_ALL_VALUES_AND_POLICIES` parameter to true,
each policy and its EVC can be saved for each simulation run (in `EVCpolicies` and `EVCvalues`, respectively). The
EVC is calculated for each policy using the following four functions (each of which can be customized):

COMMENT:
  [TBI:]  The ``controlSignalSearchSpace`` described above is constructed by default.  However, this can be customized
          by assigning either a 2d array or a function that returns a 2d array to the ``controlSignalSearchSpace``
          attribute.  The first dimension (or axis 0) of the 2d array must be an array of control allocation
          policies (of any length), each of which contains a value for each ControlProjection in the
          EVCMechanism, assigned in the same order they are listed in its ``controlProjections`` attribute.
COMMENT

.. _EVC_Auxiliary_Functions:

COMMENT:
    MENTION HIERARCHY
COMMENT

* `VALUE_FUNCTION <value_function>` - this is an "orchestrating" function that simply calls the three subordinate
  functions described below, which do the actual work of evaluating the performance of the system and the cost of the
  controlSignals under the current `allocationPolicy`, and combining these to calculate the EVC.  This function can
  be replaced with a user-defined function to fully customize the calculation of the EVC, by assigning a function to
  the `VALUE_FUNCTION <value_function>` parameter of the EVCMechanism.
..
* `OUTCOME_FUNCTION <outcome_function>` - this combines the values of the outputStates in the EVCMechanism's
  `monitoredOutputStates` attribute to generate an aggregated outcome value for the current `allocationPolicy`. The
  default is the `LinearCombination` function, which computes an elementwise (Hadamard) product of the outputState
  values.  The ``weights`` and ``exponents`` arguments of the function can be used, respectively, to scale and/or
  exponentiate the contribution of each outputState's value to the aggregated outcome.  For example, one outcome value
  can be divided by another by assigning a negative exponent to the latter (see `EVCMechanism_Examples`). The length of
  the array for the ``weights`` and ``exponents`` arguments must equal the number of outputStates in
  `monitoredOutputStates`. These specifications will supercede any made for individual outputStates in the
  ``monitor_for_control`` argument, or `MONITOR_FOR_CONTROL <monitor_for_control>` entry of a params specification
  dictionary (see `ControlMechanism_Monitored_OutputStates`).  Evaluation of the system's performance can be further
  customized by specifying a custom function for the `OUTCOME_FUNCTION <outcome_function>` parameter.
..
* `COST_FUNCTION <cost_function>` - this combines the costs of the EVCMechanism's ControlSignals to generate an
  aggregated cost value for the current `allocationPolicy`.  The default is the `LinearCombination` function,
  which sums the costs.  The ``weights`` and ``exponents`` arguments of the function can be used, respectively,
  to scale and/or exponentiate the contribution of each ControlSignal's cost to the value to the aggregated cost.
  The length of the array for these arguments must equal the number of ControlSignals in the 'controlSignals`
  attribute. The evaluation of cost can be further customized by specifying a custom function for the
  `COST_FUNCTION <cost_function>` parameter.
..
* :keyword:`COMBINE_OUTCOME_AND_COST_FUNCTION <combine_outcome_and_cost_function>` - this combines the aggregated
  outcome and aggregated cost values for the current `allocationPolicy`, to determine the EVC for that policy.  The
  default is the `LinearCombination` function, which subtracts the aggregated cost from the aggregated outcome. The way
  in which the outcome and cost are combined to determine the EVC can be customized by specifying a custom function for
  the `COMBINE_OUTCOME_AND_COST_FUNCTION <combine_outcome_and_cost_function` parameter.

.. _EVCMechanism_ControlSignal:

ControlSignals
~~~~~~~~~~~~~~

A `ControlSignal` is used to regulate the parameter of mechanisms or its function. An EVCMechanism has one
ControlSignal for each parameter that it controls. Each ControlSignal is implemented as an `OutputState` of the
EVCMechanism, the value of which is the ControlSignal's `intensity`.  When an EVCMechanism is
:ref:`created automatically <EVCMechanism_Creation>`, it creates a ControlSignal for each parameter that has
been specified for control in the system (a parameter is specified  for control by assigning it a ControlProjection;
see `Mechanism_Specifying_Parameters`).  The ControlSignals of an EVCMechanism are listed in it `controlSignals`
attribute. Each ControlSignal is associated with a `ControlProjection` that projects to the
:doc:`parameterState <ParameterState>` for the parameter controlled by that ControlSignal. The EVCMechanism's
:py:data:`function <EVCMechanism.function>` assigns an `allocation` value to each of its ControlSignals.  Each
ControlSignal uses its allocation to compute its `intensity`, that is then assigned as the value of its
ControlProjection. The value of the ControlProjection is then used by the parameterState to which it projects to
modify the value of the parameter for which it is responsible.  A ControlSignal also calculates a `cost`,
based on its intensity and/or its time course, that is used by the EVCMechanism to adapt its `allocation` in the
future.  When the EVCMechanism chooses an `allocationPolicy` to evaluate, it selects an allocation value  from the
ControlSignal's `allocation_samples` attribute.


Prediction Mechanisms
~~~~~~~~~~~~~~~~~~~~~

.. _EVCMechanism_Prediction_Mechanisms:

Prediction mechanisms are used to generate the input for the system each time the EVCMechanism
:ref:`simulates its execution <EVCMechanism_Execution>`.  When an EVCMechanism is
:ref:`created automatically <EVCMechanism_Creation>`, a prediction mechanism is created for each `ORIGIN` (input)
mechanism in the system; a `MappingProjection` is created that projects to it from the corresponding `ORIGIN` mechanism;
and the pair are assigned to their own prediction `process <Process>`.  The type of mechanism used for the prediction
mechanisms can be specified using the EVCMechanism's `PREDICTION_MECHANISM_TYPE <prediction_mechanism_type>` parameter,
and their
parameters can
be specified in the EVCMechanism's `PREDICTION_MECHANISM_PARAMS <prediction_mechanism_params>` parameter.  The default
type is an
'IntegratorMechanism`, that generates an exponentially weighted time-average of its input.  The prediction
mechanisms for an EVCMechanism are listed in its `predictionMechanisms` attribute, and the prediction processes to
which they belong in its `predictionProcesses` attribute.

.. _EVCMechanism_Execution:

Execution
---------

When an EVCMechanism is executed, it updates the value of its `predictionMechanisms`, and then calls its
:py:data:`function <EVCMechanism.function>`, which determines and implements the `allocationPolicy` for the next round
of the system's execution.  By default, the EVCMechanism identifies and implements the `allocationPolicy` that maximizes
the EVC evaluated for the outputStates it is monitoring, as described below.  However, this procedure can be modified by
specifying a custom function for any or all of the ones described below.

.. _EVCMechanism_Default_Function:

The default :py:data:`function <EVCMechanism.function>` for an EVCMechanism selects an `allocationPolicy` by assessing
the performance of the system under each of the policies in its `controlSignalSearchSpace` and selecting the
one that yields the maximum EVC. The `controlSignalSearchSpace` is constructed by creating a set of
allocationPolicies that represent all permutations of the allocation values to be sampled for each ControlSignal.
Each `allocationPolicy` in the set is constructed by drawing one value from the `allocation_samples` of each
ControlSignal, and the set contains all combinations of these values.  For each `allocationPolicy`, the default
:py:data:`function <EVCMechanism.function>` calls the EVCMechanism's `value_function` which, in turn, carries out
the following steps:

* **Implement the allocationPolicy.** Assign the `allocation <ControlSignal.ControlSignal.allocation>` value specifed
  for each ControlSignal.
..
* **Simulate performance.**  Execute the system under the current `allocationPolicy` using the EVCMechanism's
  `run_simulation` method and the value of its `predictedInputs` attribute as the input to the system (this uses
  the history of previous trials to generate an average expected input value).
..
* **Calculate the EVC for the allocationPolicy.**  This uses three functions:

    * the `outcome_function` calculates the **outcome** for the allocationPolicy by aggregating the value of the
      outputStates the EVCMechanism monitors (listed in its `monitoredOutputStates` attribute);
    ..
    * the `cost_function` calculates the **cost** of the allocationPolicy by aggregating the `cost` of the
      EVCMechanism's ControlSignals;
    ..
    * the `combine_outcome_and_cost_function` calculates the **value** (EVC) of the allocationPolicy by subtracting the
      aggregated cost from the aggregated outcome.

If the `save_all_values_and_policies` attribute is :keyword:`True`, the allocation policy is saved in the
EVCMechanism's `EVCpolicies` attribute, and its value is saved in the `EVCvalues` attribute. The :py:data:`function
<EVCMechanism.function>` returns the `allocationPolicy` that yielded the maximum EVC. This is then implemented by
assigning the `allocation` specified for each ControlSignal by the designated `allocationPolicy`.  These allocations
determine the value of the parameters being controlled in the next round of the system's execution.

This procedure can be modified by assigning custom functions for any or all of the ones described above,
including the EVCMechanism's :py:data:`function <EVCMechanism.function>` itself.  The requirements for each are
described in the function attribute entries.

.. _EVCMechanism_Examples:

Examples
--------

The following example implements a system with an EVCMechanism (and two processes not shown)::

    mySystem = system(processes=[myRewardProcess, myDecisionProcess],
                      controller=EVCMechanism,
                      monitor_for_control=[Reward, DDM_DECISION_VARIABLE,(RESPONSE_TIME, -1, 1)],

It uses the system's `monitor_for_control` argument to assign three outputStates to be monitored.  The first one
references the Reward mechanism (not shown);  its primary outputState will be used by default.  The second and third
use keywords that are the names of outputStates of a  `DDM` mechanism (also not shown). The last one (RESPONSE_TIME)
is assigned an exponent of -1 and weight of 1. As a result, each calculation of the EVC computation will multiply
the value of the primary outputState of the Reward mechanism by the value of the DDM_DECISION_VARIABLE outputState
of the DDM mechanism, and then divide that by the value of the RESPONSE_TIME outputState of the DDM mechanism.

COMMENT:
ADD: This example specifies the EVCMechanism on its own, and then uses it for a system.
COMMENT


.. _EVCMechanism_Class_Reference:

Class Reference
---------------

"""

from PsyNeuLink.Components.Mechanisms.ControlMechanisms.ControlMechanism import *
from PsyNeuLink.Components.Mechanisms.ControlMechanisms.ControlMechanism import ControlMechanism_Base
from PsyNeuLink.Components.Mechanisms.Mechanism import MonitoredOutputStatesOption
from PsyNeuLink.Components.Mechanisms.ProcessingMechanisms.IntegratorMechanism import IntegratorMechanism
from PsyNeuLink.Components.ShellClasses import *

PY_MULTIPROCESSING = False

if PY_MULTIPROCESSING:
    from multiprocessing import Pool


if MPI_IMPLEMENTATION:
    from mpi4py import MPI

OBJECT = 0
EXPONENT = 1
WEIGHT = 2

# # Default control allocation mode values:
# class DefaultControlAllocationMode(Enum):
#     GUMBY_MODE = 0.0
#     BADGER_MODE = 1.0
#     TEST_MODE = 240
# defaultControlAllocation = DefaultControlAllocationMode.BADGER_MODE.value
DEFAULT_ALLOCATION_SAMPLES = np.arange(0.1, 1.01, 0.3)

# -------------------------------------------    KEY WORDS  -------------------------------------------------------

# ControlProjection Function Names
CONTROL_SIGNAL_COST_OPTIONS = 'controlSignalCostOptions'

INTENSITY_COST_FUNCTION = 'intensity_cost_function'
ADJUSTMENT_COST_FUNCTION = 'adjustment_cost_function'
DURATION_COST_FUNCTION = 'duration_cost_function'
COST_COMBINATION_FUNCTION = 'cost_combination_function'
costFunctionNames = [INTENSITY_COST_FUNCTION,
                     ADJUSTMENT_COST_FUNCTION,
                     DURATION_COST_FUNCTION,
                     COST_COMBINATION_FUNCTION]

# Attributes / KVO keypaths
# kpLog = "Control Signal Log"
kpAllocation = "Control Signal Allocation"
kpIntensity = "Control Signal Intensity"
kpCostRange = "Control Signal Cost Range"
kpIntensityCost = "Control Signal Intensity Cost"
kpAdjustmentCost = "Control Signal Adjustment Cost"
kpDurationCost = "Control Signal DurationCost"
kpCost = "Control Signal Cost"


class ControlSignalCostOptions(IntEnum):
    NONE               = 0
    INTENSITY_COST     = 1 << 1
    ADJUSTMENT_COST    = 1 << 2
    DURATION_COST      = 1 << 3
    ALL                = INTENSITY_COST | ADJUSTMENT_COST | DURATION_COST
    DEFAULTS           = INTENSITY_COST

class EVCError(Exception):
    def __init__(self, error_value):
        self.error_value = error_value

    def __str__(self):
        return repr(self.error_value)

# These are place-marker definitions to allow forward referencing of functions defined at end of module
# def _control_signal_grid_search(allocations=None, ctlr=None):
#     return __control_signal_grid_search(controller=None)
def _control_signal_grid_search(**kwargs):
    return __control_signal_grid_search(**kwargs)
CONTROLLER = 'controller'


def _value_function(ctlr, outcomes, costs, context):
    return __value_function(ctlr, outcomes, costs, context)


class EVCMechanism(ControlMechanism_Base):
    """EVCMechanism(                                                   \
    prediction_mechanism_type=IntegratorMechanism,                     \
    prediction_mechanism_params=None,                                  \
    monitor_for_control=None,                                          \
    function=_control_signal_grid_search,                              \
    value_function=_value_function,                                    \
    outcome_function=LinearCombination(operation=PRODUCT),             \
    cost_function=LinearCombination(operation=SUM),                    \
    combine_outcome_and_cost_function=LinearCombination(operation=SUM) \
    save_all_values_and_policies:bool=:keyword:`False`,                \
    params=None,                                                       \
    name=None,                                                         \
    prefs=None)

    Optimizes the ControlSignals for a System.

    COMMENT:
        Class attributes:
            + componentType (str): System Default Mechanism
            + paramClassDefaults (dict):
                + SYSTEM (System)
                + MONITOR_FOR_CONTROL (list of Mechanisms and/or OutputStates)

        Class methods:
            None

       **********************************************************************************************

       PUT SOME OF THIS STUFF IN ATTRIBUTES, BUT USE DEFAULTS HERE

        # - specification of system:  required param: SYSTEM
        # - kwDefaultController:  True =>
        #         takes over all projections from default Controller;
        #         does not take monitored states (those are created de-novo)
        # TBI: - CONTROL_PROJECTIONS:
        #         list of projections to add (and for which outputStates should be added)

        # - inputStates: one for each performance/environment variable monitiored

        ControlProjection Specification:
        #    - wherever a ControlProjection is specified, using kwEVC instead of CONTROL_PROJECTION
        #     this should override the default sender kwSystemDefaultController in ControlProjection._instantiate_sender
        #    ? expclitly, in call to "EVC.monitor(input_state, parameter_state=NotImplemented) method

        # - specification of function: default is default allocation policy (BADGER/GUMBY)
        #   constraint:  if specified, number of items in variable must match number of inputStates in INPUT_STATES
        #                  and names in list in kwMonitor must match those in INPUT_STATES

       **********************************************************************************************

       NOT CURRENTLY IN USE:

        system : System
            system for which the EVCMechanism is the controller;  this is a required parameter.

        default_input_value : Optional[number, list or np.ndarray] : `defaultControlAllocation <LINK]>`

    COMMENT


    Arguments
    ---------

    prediction_mechanism_type : CombinationFunction: default IntegratorMechanism
        the mechanism class used for prediction mechanism(s).
        Each instance is named using the name of the :keyword:`ORIGIN` mechanism + PREDICTION_MECHANISM
        and assigned an outputState named based on the same.

    prediction_mechanism_params : Optional[Dict[param keyword, param value]] : default None
        a parameter dictionary passed to the constructor for the `prediction_mechanism_type` mechanism.
        The same one is passed to all prediction mechanisms created for the EVCMechanism.

    monitor_for_control : List[OutputState or Tuple[OutputState, list or 1d np.array, list or 1d np.array]] : \
    default :keyword:`MonitoredOutputStatesOptions.PRIMARY_OUTPUT_STATES`
        specifies set of outputState values to monitor (see `ControlMechanism_Monitored_OutputStates` for
        specification options).

    function : function : _control_signal_grid_search
        specifies the function used to determine the `allocationPolicy` for the next execution of the system
        (see :py:data:`function <EVCMechanism.function>` attribute for description of default function).

    value_function : function : `_value_function <value_function>`
        specifies the function used to calculate the value of the current `allocationPolicy`.

    outcome_function : function : LinearCombination(operation=PRODUCT)
        specifies the function used to calculate the outcome associated with the current `allocationPolicy`.

    cost_function : function : LinearCombination(operation=SUM)
        specifies the function used to calculate the cost associated with the current `allocationPolicy`.

    combine_outcome_and_cost_function : function : LinearCombination(operation=SUM)
        specifies the function used to combine the outcome and cost associated with the current `allocationPolicy`,
        to determine its value.

    save_all_values_and_policies : bool : default :keyword:`False`
        when :keyword:`True`, saves all of the control allocation policies tested in ``EVCpolicies`` and their
        values in ``EVCvalues``.

    params : Optional[Dict[param keyword, param value]]
        a dictionary that can be used to specify the parameters for the mechanism, parameters for its function,
        and/or a custom function and its parameters (see :doc:`Mechanism` for specification of a params dict).

    name : str : default EVCMechanism-<index>
        a string used for the name of the mechanism.
        If not is specified, a default is assigned by MechanismRegistry
        (see :doc:`Registry <LINK>` for conventions used in naming, including for default and duplicate names).

    prefs : Optional[PreferenceSet or specification dict] : default Process.classPreferences
        the PreferenceSet for the mechanism.
        If it is not specified, a default is assigned using ``classPreferences`` defined in __init__.py
        (see `PreferenceSet <LINK>` for details).

    Attributes
    ----------

    make_default_controller : bool : default :keyword:`True`
        if True, assigns EVCMechanism when instantiated as the DefaultController

    system : System
        the system for which EVCMechanism is the ``controller``.

    predictionMechanisms : List[ProcessingMechanism]
        a list of predictionMechanisms added to the system, one for each of its :keyword:`ORIGIN` mechanisms

    predictionProcesses : List[Process]
        a list of prediction processes added to the system, each comprise of one of its :keyword:`ORIGIN` mechanisms
        and the associated ``predictionMechanism``.

    prediction_mechanism_type : ProcessingMechanism : default IntegratorMechanism
        the processingMechanism class used for prediction mechanism(s).
        Note: each instance will be named based on origin mechanism + PREDICTION_MECHANISM,
              and assigned an outputState named based on the same

    prediction_mechanism_params : Dict[param key, param value] : default :keyword:`None`
        a parameter dictionary passed to ``prediction_mechanism_type`` on instantiation.
        The same dictionary will be passed to all instances of ``prediction_mechanism_type`` created.

    monitoredOutputStates : List[OutputState]
        each item is an outputState of a mechanism in the system that has been assigned a projection to a corresponding
        inputState of the EVCMechanism.

    monitoredValues : 3D np.nparray
        an array of values of the outputStates in ``monitoredOutputStates`` (equivalent to the values of
        self.inputStates).

    function : function : default _control_signal_grid_search
        determines the `allocationPolicy <EVCMechanism.allocationPolicy>` to use for the next round of the system's
        execution. The default function (`_control_signal_grid_search`) conducts an exhaustive (*grid*) search of all
        combinations of the `allocation_samples` of its :doc:`control signals <ControlSignal>`, executing the system
        (using `run_simulation`) for each combination, evaluating the result using the `value_function`, and returning
        the allocationPolicy that generated the highest value.  If a custom function is specified, it must take a
        ``controller`` argument that specifies an EVCMechanism, and must return an array with the same format
        (number and type of elements) as the EVCMechanism's `allocationPolicy` attribute.

    allocationPolicy : 2d np.array : `defaultControlAllocation <LINK>`
        determines the value assigned as the variable for each control signal and its associated
        :doc:`ControlProjection`.  Each item of the array must be a 1d array (usually containing a scalar)
        that specifies an allocation for the corresponding control signal, and the number of items must equal the
        number of the EVCMechanism's control signals.

    value_function : function : default _value_function()
        calculates the value for a given `allocationPolicy`.  The default uses `outcome_function` to determine the
        outcome of the policy, and `cost_function` to determine its cost, combines these using
        `combine_outcome_and_cost_function`, and returns the result in a tuple, along with outcome and cost
        values used to determine it.  The default can be replaced by any function that returns a tuple with three items:
        the calculated EVC (which must be a scalar value), and the outcome and cost from which it was calculated
        (these can be scalar values or :keyword:`None`).  If used with EVCMechanism's default
        de:py:data:`function <EVCMechanism.function>` parameter, a custom value_function must take three arguments
        (that it will be passed by name): a `controller` argument that is the EVCMechanism for
        which it is carrying out the calculation; an `outcomes` argument that is a 2d array of values, each item of
        which is the value of an outputState in `monitoredOutputStates`; and a `costs` argument that is a 2d array of
        costs, each item of which is the cost of a controlSignal in `controlSignals`.

    outcome_function : function : default LinearCombination(operation=PRODUCT)
        calculates the outcome for a given `allocationPolicy`.  The default combines the values of the outputStates in
        `monitoredOutputStates` by taking their product, using the `LinearCombination` function.  The `weights`
        and `exponents` arguments of the function can be used to parameterize the contribution that each outputState
        makes to the result (see `above <EVCMechanism_Examples>` for an example).  The length of each of these arguments
        must equal the number of outputStates in `monitoredOutputStates`. The default function can be replaced with any
        function that returns a scalar value.  If used with the EVCMechanism's default `value_function`, a custom
        outcome_function must take three arguments (that it will be passed by name): a :keyword:`variable` argument
        that is a 1d array, each element of which is the value of an outputState in `monitoredOutputStates`; a
        `weights` argument that is a 1d array specifying coefficient for each value in :keyword:`variable`; and an
        `exponents` argument that is a 1d array specifying the exponent for each value in :keyword:`variable`.

    cost_function : function : default LinearCombination(operation=PRODUCT)
        calculates the cost for a given `allocationPolicy`.  The default combines the costs of the ControlSignals in
        `controlSignals` by summing them using the `LinearCombination` function.  The `weights` and `exponents`
        arguments of the function can be used to parameterize the contribution that each makes to the result.  The
        length of each of these arguments must equal the number of ControlSignals in `controlSignals`. The default
        function can be replaced with any function that returns a scalar value.  If used with the EVCMechanism's
        default `value_function`, a custom cost_function must take three arguments (that it will be passed by name): a
        :keyword:`variable` argument that is a 1d array, each element of which is the cost of a ControlSignal in
        `controlSignals`; a `weights` argument that is a 1d array specifying coefficient for each cost in
        :keyword:`variable`; and an `exponents` argument that is a 1d array specifying the exponent for each cost in
        :keyword:`variable`.

    combine_outcome_and_cost_function : function : default LinearCombination(operation=SUM)
        combines the outcome and cost for given `allocationPolicy` to determine its value.  The default uses the
        `LinearCombination` function to subtract the cost from the outcome, and returns the difference. The `weights`
        and `exponents` arguments of the function can be used to parameterize the contribution that each makes to the
        result, each of which must have two elements (one for the outcome and one for the cost). The default function
        can be replaced with any function that returns a scalar value.  If used with the EVCMechanism's default
        `value_function`, a custom combine_outcome_and_cost_function must take three arguments (that it will be
        passed by name): a :keyword:`variable` argument that is a 2d array, the first item of which is 1d array
        containing the outcome for the current `allocationPolicy`, and the second a 1d array containing its cost;  a
        `weights` argument that is a 1d array with two elements, one for the outcome and the other for the cost in the
        :keyword:`variable` argument;  and an `exponents` argument that is a 1d array with two elements, one for the
        outcome and the other for the cost.

    controlSignalSearchSpace : 2d np.array
        an array that contains arrays of control allocation policies.  Each control allocation policy contains one
        value for each of the mechanism's control signals (i.e., ControlProjections).  By default,
        it is assigned a set of all possible control allocation policies (using np.meshgrid to construct all
        permutations of control signal values).

    EVCmax : 1d np.array with single value
        the maximum EVC value over all control allocation policies in ``controlSignalSearchSpace``.

    EVCmaxStateValues : 2d np.array
        an array of the values for the outputStates in ``monitoredOutputStates`` using the control allocation policy
        that generated ``EVCmax``.

    EVCmaxPolicy : 1d np.array
        an array of the control signal values (value of ControlProjections) for the control allocation policy
        that generated ``EVCmax``.

    save_all_values_and_policies : bool : default :keyword:`False`
        specifies whether or not to save all ControlAllocationPolicies and associated EVC values (in addition to max).
        If it is specified, each policy tested in the ``controlSignalSearchSpace`` is saved in ``EVCpolicies`` and
        their values are saved in ``EVCvalues``.

    EVCpolicies : 2d np.array
        array of allocation policies tested in ``controlSignalSearchSpace``.  The values of each are stored in
        ``EVCvalues``.

    EVCvalues :  1d np.array
        array of EVC values corresponding to the policies in ``EVCPolicies``.

    controlSignals : OrderedDict[str, ControlSignal]
        list of :doc:`outputStates <OutputState>` for the EVCMechanism.

    """

    componentType = "EVCMechanism"
    initMethod = INIT_FUNCTION_METHOD_ONLY


    classPreferenceLevel = PreferenceLevel.SUBTYPE
    # classPreferenceLevel = PreferenceLevel.TYPE
    # Any preferences specified below will override those specified in TypeDefaultPreferences
    # Note: only need to specify setting;  level will be assigned to Type automatically
    # classPreferences = {
    #     kwPreferenceSetName: 'DefaultControlMechanismCustomClassPreferences',
    #     kp<pref>: <setting>...}

    # This must be a list, as there may be more than one (e.g., one per controlSignal)
    variableClassDefault = defaultControlAllocation

    from PsyNeuLink.Components.Functions.Function import LinearCombination
    # from Components.__init__ import DefaultSystem
    paramClassDefaults = ControlMechanism_Base.paramClassDefaults.copy()
    paramClassDefaults.update({MAKE_DEFAULT_CONTROLLER: True,
                               PARAMETER_STATES: False})

    @tc.typecheck
    def __init__(self,
                 # system:System,
                 # default_input_value=None,
                 prediction_mechanism_type=IntegratorMechanism,
                 prediction_mechanism_params:tc.optional(dict)=None,
                 monitor_for_control:tc.optional(list)=None,
                 function=_control_signal_grid_search,
                 value_function=_value_function,
                 outcome_function=LinearCombination(operation=PRODUCT),
                 cost_function=LinearCombination(operation=SUM,
                                                 context=componentType+COST_FUNCTION),
                 combine_outcome_and_cost_function=LinearCombination(operation=SUM,
                                                                     context=componentType+FUNCTION),
                 save_all_values_and_policies:bool=False,
                 params=None,
                 name=None,
                 prefs:is_pref_set=None,
                 context=componentType+INITIALIZING):

        prediction_mechanism_params = prediction_mechanism_params or {MONITOR_FOR_CONTROL:None}

        # Assign args to params and functionParams dicts (kwConstants must == arg names)
        params = self._assign_args_to_param_dicts(# system=system,
                                              prediction_mechanism_type=prediction_mechanism_type,
                                              prediction_mechanism_params=prediction_mechanism_params,
                                              monitor_for_control=monitor_for_control,
                                              function=function,
                                              value_function=value_function,
                                              outcome_function=outcome_function,
                                              cost_function=cost_function,
                                              combine_outcome_and_cost_function=combine_outcome_and_cost_function,
                                              save_all_values_and_policies=save_all_values_and_policies,
                                              params=params)

        super(EVCMechanism, self).__init__(# default_input_value=default_input_value,
                                           monitor_for_control=monitor_for_control,
                                           function=function,
                                           params=params,
                                           name=name,
                                           prefs=prefs,
                                           context=self)

    def _instantiate_input_states(self, context=None):
        """Instantiate inputState and MappingProjections for list of Mechanisms and/or States to be monitored

        Instantiate PredictionMechanisms for ORIGIN mechanisms in self.system; these will now be TERMINAL mechanisms
            - if their associated input mechanisms were TERMINAL MECHANISMS, they will no longer be so
            - therefore if an associated input mechanism must be monitored by the EVCMechanism, it must be specified
                explicitly in an outputState, mechanism, controller or systsem MONITOR_FOR_CONTROL param (see below)

        Parse paramsCurent[MONITOR_FOR_CONTROL] for system, controller, mechanisms and/or their outputStates:
            - if specification in outputState is None:
                 do NOT monitor this state (this overrides any other specifications)
            - if an outputState is specified in *any* MONITOR_FOR_CONTROL, monitor it (this overrides any other specs)
            - if a mechanism is terminal and/or specified in the system or controller:
                if MonitoredOutputStatesOptions is PRIMARY_OUTPUT_STATES:  monitor only its primary (first) outputState
                if MonitoredOutputStatesOptions is ALL_OUTPUT_STATES:  monitor all of its outputStates
            Note: precedence is given to MonitoredOutputStatesOptions specification in mechanism > controller > system

        Assign inputState to controller for each state to be monitored;
            uses _instantiate_monitoring_input_state and _instantiate_control_mechanism_input_state to do so.
            For each item in self.monitoredOutputStates:
            - if it is a OutputState, call _instantiate_monitoring_input_state()
            - if it is a Mechanism, call _instantiate_monitoring_input_state for relevant Mechanism.outputStates
                (determined by whether it is a terminal mechanism and/or MonitoredOutputStatesOption specification)
            - each inputState is assigned a name with the following format:
                '<name of mechanism that owns the monitoredOutputState>_<name of monitoredOutputState>_Monitor'

        Notes:
        * MonitoredOutputStatesOption is an AutoNumbered Enum declared in ControlMechanism
            - it specifies options for assigning outputStates of terminal Mechanisms in the System
                to self.monitoredOutputStates;  the options are:
                + PRIMARY_OUTPUT_STATES: assign only the primary outputState for each terminal Mechanism
                + ALL_OUTPUT_STATES: assign all of the outputStates of each terminal Mechanism
            - precedence is given to MonitoredOutputStatesOptions specification in mechanism > controller > system
        * self.monitoredOutputStates is a list, each item of which is a Mechanism.outputState from which a projection
            will be instantiated to a corresponding inputState of the ControlMechanism
        * self.inputStates is the usual ordered dict of states,
            each of which receives a projection from a corresponding outputState in self.monitoredOutputStates

        """

        self._instantiate_prediction_mechanisms(context=context)

        from PsyNeuLink.Components.Mechanisms.Mechanism import MonitoredOutputStatesOption
        from PsyNeuLink.Components.States.OutputState import OutputState

        # Clear self.variable, as items will be assigned in call(s) to _instantiate_monitoring_input_state()
        self.variable = None

        # PARSE SPECS

        controller_specs = []
        system_specs = []
        mech_specs = []
        all_specs = []

        # Get controller's MONITOR_FOR_CONTROL specifications (optional, so need to try)
        try:
            controller_specs = self.paramsCurrent[MONITOR_FOR_CONTROL] or []
        except KeyError:
            controller_specs = []

        # Get system's MONITOR_FOR_CONTROL specifications (specified in paramClassDefaults, so must be there)
        system_specs = self.system.paramsCurrent[MONITOR_FOR_CONTROL]

        # If the controller has a MonitoredOutputStatesOption specification, remove any such spec from system specs
        if controller_specs:
            if (any(isinstance(item, MonitoredOutputStatesOption) for item in controller_specs)):
                option_item = next((item for item in system_specs if isinstance(item, MonitoredOutputStatesOption)),None)
                if option_item is not None:
                    del system_specs[option_item]

        # Combine controller and system specs
        # If there are none, assign PRIMARY_OUTPUT_STATES as default
        all_specs = controller_specs + system_specs or [MonitoredOutputStatesOption.PRIMARY_OUTPUT_STATES]

        # Extract references to mechanisms and/or outputStates from any tuples
        # Note: leave tuples in all_specs for use in generating exponent and weight arrays below
        all_specs_extracted_from_tuples = []
        for item in all_specs:
            # Extract references from specification tuples
            if isinstance(item, tuple):
                all_specs_extracted_from_tuples.append(item[OBJECT])
                continue
            # Validate remaining items as one of the following:
            elif isinstance(item, (Mechanism, OutputState, MonitoredOutputStatesOption, str)):
                all_specs_extracted_from_tuples.append(item)
            # IMPLEMENTATION NOTE: This should never occur, as should have been found in _validate_monitored_state()
            else:
                raise EVCError("PROGRAM ERROR:  illegal specification ({0}) encountered by {1} "
                               "in MONITOR_FOR_CONTROL for a mechanism, controller or system in its scope".
                               format(item, self.name))

        # Get MonitoredOutputStatesOptions if specified for controller or System, and make sure there is only one:
        option_specs = [item for item in all_specs if isinstance(item, MonitoredOutputStatesOption)]
        if not option_specs:
            ctlr_or_sys_option_spec = None
        elif len(option_specs) == 1:
            ctlr_or_sys_option_spec = option_specs[0]
        else:
            raise EVCError("PROGRAM ERROR: More than one MonitoredOutputStatesOption specified in {}: {}".
                           format(self.name, option_specs))

        # Get MONITOR_FOR_CONTROL specifications for each mechanism and outputState in the System
        # Assign outputStates to self.monitoredOutputStates
        self.monitoredOutputStates = []
        
        # Notes:
        # * Use all_specs to accumulate specs from all mechanisms and their outputStates
        #     (for use in generating exponents and weights below)
        # * Use local_specs to combine *only current* mechanism's specs with those from controller and system specs;
        #     this allows the specs for each mechanism and its outputStates to be evaluated independently of any others
        controller_and_system_specs = all_specs_extracted_from_tuples.copy()

        for mech in self.system.mechanisms:

            # For each mechanism:
            # - add its specifications to all_specs (for use below in generating exponents and weights)
            # - extract references to Mechanisms and outputStates from any tuples, and add specs to local_specs
            # - assign MonitoredOutputStatesOptions (if any) to option_spec, (overrides one from controller or system)
            # - use local_specs (which now has this mechanism's specs with those from controller and system specs)
            #     to assign outputStates to self.monitoredOutputStates

            mech_specs = []
            output_state_specs = []
            local_specs = controller_and_system_specs.copy()
            option_spec = ctlr_or_sys_option_spec

            # PARSE MECHANISM'S SPECS

            # Get MONITOR_FOR_CONTROL specification from mechanism
            try:
                mech_specs = mech.paramsCurrent[MONITOR_FOR_CONTROL]

                if mech_specs is NotImplemented:
                    raise AttributeError

                # Setting MONITOR_FOR_CONTROL to None specifies mechanism's outputState(s) should NOT be monitored
                if mech_specs is None:
                    raise ValueError

            # Mechanism's MONITOR_FOR_CONTROL is absent or NotImplemented, so proceed to parse outputState(s) specs
            except (KeyError, AttributeError):
                pass

            # Mechanism's MONITOR_FOR_CONTROL is set to None, so do NOT monitor any of its outputStates
            except ValueError:
                continue

            # Parse specs in mechanism's MONITOR_FOR_CONTROL
            else:

                # Add mech_specs to all_specs
                all_specs.extend(mech_specs)

                # Extract refs from tuples and add to local_specs
                for item in mech_specs:
                    if isinstance(item, tuple):
                        local_specs.append(item[OBJECT])
                        continue
                    local_specs.append(item)

                # Get MonitoredOutputStatesOptions if specified for mechanism, and make sure there is only one:
                #    if there is one, use it in place of any specified for controller or system
                option_specs = [item for item in mech_specs if isinstance(item, MonitoredOutputStatesOption)]
                if not option_specs:
                    option_spec = ctlr_or_sys_option_spec
                elif option_specs and len(option_specs) == 1:
                    option_spec = option_specs[0]
                else:
                    raise EVCError("PROGRAM ERROR: More than one MonitoredOutputStatesOption specified in {}: {}".
                                   format(mech.name, option_specs))

            # PARSE OUTPUT STATE'S SPECS

            # for output_state_name, output_state in list(mech.outputStates.items()):
            for output_state_name, output_state in mech.outputStates.items():

                # Get MONITOR_FOR_CONTROL specification from outputState
                try:
                    output_state_specs = output_state.paramsCurrent[MONITOR_FOR_CONTROL]
                    if output_state_specs is NotImplemented:
                        raise AttributeError

                    # Setting MONITOR_FOR_CONTROL to None specifies outputState should NOT be monitored
                    if output_state_specs is None:
                        raise ValueError

                # outputState's MONITOR_FOR_CONTROL is absent or NotImplemented, so ignore
                except (KeyError, AttributeError):
                    pass

                # outputState's MONITOR_FOR_CONTROL is set to None, so do NOT monitor it
                except ValueError:
                    continue

                # Parse specs in outputState's MONITOR_FOR_CONTROL
                else:

                    # Note: no need to look for MonitoredOutputStatesOption as it has no meaning
                    #       as a specification for an outputState

                    # Add outputState specs to all_specs and local_specs
                    all_specs.extend(output_state_specs)

                    # Extract refs from tuples and add to local_specs
                    for item in output_state_specs:
                        if isinstance(item, tuple):
                            local_specs.append(item[OBJECT])
                            continue
                        local_specs.append(item)

            # Ignore MonitoredOutputStatesOption if any outputStates are explicitly specified for the mechanism
            for output_state_name, output_state in list(mech.outputStates.items()):
                if (output_state in local_specs or output_state.name in local_specs):
                    option_spec = None


            # ASSIGN SPECIFIED OUTPUT STATES FOR MECHANISM TO self.monitoredOutputStates

            for output_state_name, output_state in list(mech.outputStates.items()):

                # If outputState is named or referenced anywhere, include it
                if (output_state in local_specs or output_state.name in local_specs):
                    self.monitoredOutputStates.append(output_state)
                    continue

# FIX: NEED TO DEAL WITH SITUATION IN WHICH MonitoredOutputStatesOptions IS SPECIFIED, BUT MECHANISM IS NEITHER IN
# THE LIST NOR IS IT A TERMINAL MECHANISM

                # If:
                #   mechanism is named or referenced in any specification
                #   or a MonitoredOutputStatesOptions value is in local_specs (i.e., was specified for a mechanism)
                #   or it is a terminal mechanism
                elif (mech.name in local_specs or mech in local_specs or
                              any(isinstance(spec, MonitoredOutputStatesOption) for spec in local_specs) or
                              mech in self.system.terminalMechanisms.mechanisms):
                    #
                    if (not (mech.name in local_specs or mech in local_specs) and
                            not mech in self.system.terminalMechanisms.mechanisms):
                        continue

                    # If MonitoredOutputStatesOption is PRIMARY_OUTPUT_STATES and outputState is primary, include it 
                    if option_spec is MonitoredOutputStatesOption.PRIMARY_OUTPUT_STATES:
                        if output_state is mech.outputState:
                            self.monitoredOutputStates.append(output_state)
                            continue
                    # If MonitoredOutputStatesOption is ALL_OUTPUT_STATES, include it
                    elif option_spec is MonitoredOutputStatesOption.ALL_OUTPUT_STATES:
                        self.monitoredOutputStates.append(output_state)
                    elif mech.name in local_specs or mech in local_specs:
                        if output_state is mech.outputState:
                            self.monitoredOutputStates.append(output_state)
                            continue
                    elif option_spec is None:
                        continue
                    else:
                        raise EVCError("PROGRAM ERROR: unrecognized specification of MONITOR_FOR_CONTROL for "
                                       "{0} of {1}".
                                       format(output_state_name, mech.name))


        # ASSIGN WEIGHTS AND EXPONENTS

        # Note: these values will be superceded by any assigned as arguments to the outcome_function
        #       if it is specified in the constructor for the mechanism

        num_monitored_output_states = len(self.monitoredOutputStates)
        exponents = np.ones((num_monitored_output_states,1))
        weights = np.ones_like(exponents)

        # Get and assign specification of exponents and weights for mechanisms or outputStates specified in tuples
        for spec in all_specs:
            if isinstance(spec, tuple):
                object_spec = spec[OBJECT]
                # For each outputState in monitoredOutputStates
                for item in self.monitoredOutputStates:
                    # If either that outputState or its owner is the object specified in the tuple
                    if item is object_spec or item.name is object_spec or item.owner is object_spec:
                        # Assign the exponent and weight specified in the tuple to that outputState
                        i = self.monitoredOutputStates.index(item)
                        exponents[i] = spec[EXPONENT]
                        weights[i] = spec[WEIGHT]

        self.paramsCurrent[OUTCOME_FUNCTION].exponents = exponents
        self.paramsCurrent[OUTCOME_FUNCTION].weights = weights


        # INSTANTIATE INPUT STATES

        # Instantiate inputState for each monitored state in the list
        # from Components.States.OutputState import OutputState
        for monitored_state in self.monitoredOutputStates:
            if isinstance(monitored_state, OutputState):
                self._instantiate_monitoring_input_state(monitored_state, context=context)
            elif isinstance(monitored_state, Mechanism):
                for output_state in monitored_state.outputStates:
                    self._instantiate_monitoring_input_state(output_state, context=context)
            else:
                raise EVCError("PROGRAM ERROR: outputState specification ({0}) slipped through that is "
                               "neither a OutputState nor Mechanism".format(monitored_state))


        if self.prefs.verbosePref:
            print ("{0} monitoring:".format(self.name))
            for state in self.monitoredOutputStates:
                exponent =  np.ndarray.item(self.paramsCurrent[OUTCOME_FUNCTION].weights[
                                                self.monitoredOutputStates.index(state)])
                weight = np.ndarray.item(self.paramsCurrent[OUTCOME_FUNCTION].exponents[
                                             self.monitoredOutputStates.index(state)])
                print ("\t{0} (exp: {1}; wt: {2})".format(state.name, exponent, weight))

        self.inputValue = self.variable.copy() * 0.0

        return self.inputStates

    def _instantiate_control_projection(self, projection, params=None, context=None):
        """
        """
        try:
            self.allocationPolicy = np.append(self.allocationPolicy, defaultControlAllocation)
        except AttributeError:
            # self.allocationPolicy = np.atleast_2d(defaultControlAllocation)
            self.allocationPolicy = np.array(defaultControlAllocation)

        # Call super to instantiate outputStates
        super()._instantiate_control_projection(projection=projection,
                                                params=None,
                                                context=context)

        self.controlSignals = self.outputStates

    def _instantiate_prediction_mechanisms(self, context=None):
        """Add prediction mechanism and associated process for each ORIGIN (input) mechanism in the system

        For each ORIGIN mechanism in self.system:
            - instantiate a corresponding predictionMechanism
            - instantiate a Process, with a pathway that projects from the ORIGIN to the prediction mechanism
            - add the process to self.system.processes

        Instantiate self.predictedInput:
            - one item of axis 0 for each predictionMechanism
            - one item of axis 1 for each inputState of a predictionMechanism
            - one item of axis 2 for each element of the input to an inputState of the predictionMechanism

        Args:
            context:
        """

        from PsyNeuLink.Components.Process import Process_Base

        self.predictionMechanisms = []
        self.predictionProcesses = []

        for mech in self.system.originMechanisms.mechanisms:

            # Get any params specified for predictionMechanism(s) by EVCMechanism
            try:
                prediction_mechanism_params = self.paramsCurrent[PREDICTION_MECHANISM_PARAMS]
            except KeyError:
                prediction_mechanism_params = {}

            # Add outputState with name based on originMechanism
            output_state_name = mech.name + '_' + PREDICTION_MECHANISM_OUTPUT
            prediction_mechanism_params[OUTPUT_STATES] = [output_state_name]

            # Instantiate predictionMechanism
            prediction_mechanism = self.paramsCurrent[PREDICTION_MECHANISM_TYPE](
                                                            name=mech.name + "_" + PREDICTION_MECHANISM,
                                                            params = prediction_mechanism_params,
                                                            context=context)

            # Assign list of processes for which prediction_mechanism will provide input during the simulation
            # - used in _get_simulation_system_inputs()
            # - assign copy, since don't want to include the prediction process itself assigned to mech.processes below
            prediction_mechanism.use_for_processes = list(mech.processes.copy())

            self.predictionMechanisms.append(prediction_mechanism)

            # Instantiate process with originMechanism projecting to predictionMechanism, and phase = originMechanism
            prediction_process = Process_Base(default_input_value=None,
                                              params={
                                                  PATHWAY:[(mech, mech.phaseSpec),
                                                                   IDENTITY_MATRIX,
                                                                   (prediction_mechanism, mech.phaseSpec)]},
                                              name=mech.name + "_" + kwPredictionProcess,
                                              context=context
                                              )
            prediction_process._isControllerProcess = True
            # Add the process to the system's processes param (with None as input)
            self.system.params[kwProcesses].append((prediction_process, None))
            # Add the process to the controller's list of prediction processes
            self.predictionProcesses.append(prediction_process)

        # MODIFIED 12/27 NEW:
        # Assign predictedInputs
        self.predictedInput = []
        for i in range(len(self.system.originMechanisms)):
            # self.predictedInput.append(process[0].originMechanisms[0].inputValue)
            self.predictedInput.append(self.system.processes[i].originMechanisms[0].inputValue)
        self.predictedInput = np.array(self.predictedInput)
        # MODIFIED 12/27 END

        # Re-instantiate system with predictionMechanism Process(es) added
        self.system._instantiate_processes(input=self.system.variable, context=context)
        self.system._instantiate_graph(context=context)

    def _instantiate_monitoring_input_state(self, monitored_state, context=None):
        """Instantiate inputState with projection from monitoredOutputState

        Validate specification for outputState to be monitored
        Instantiate inputState with value of monitoredOutputState
        Instantiate MappingProjection to inputState from monitoredOutputState

        Args:
            monitored_state (OutputState):
            context:
        """

        self._validate_monitored_state_spec(monitored_state, context=context)

        state_name = monitored_state.owner.name + '_' + monitored_state.name + '_Monitor'

        # Instantiate inputState
        input_state = self._instantiate_control_mechanism_input_state(state_name,
                                                                      monitored_state.value,
                                                                      context=context)

        # Instantiate MappingProjection from monitored_state to new input_state
        from PsyNeuLink.Components.Projections.MappingProjection import MappingProjection
        MappingProjection(sender=monitored_state, receiver=input_state, matrix=IDENTITY_MATRIX)

    def _instantiate_function(self, context=None):
        super()._instantiate_function(context=context)

    def _instantiate_attributes_after_function(self, context=None):

        super()._instantiate_attributes_after_function(context=context)

        # Insure that length of the weights and/or exponents arguments for the outcome_function
        #    matches the number of monitoredOutputStates
        num_monitored_output_states = len(self.monitoredOutputStates)
        if self.outcome_function.weights is not None:
            num_outcome_weights = len(self.outcome_function.weights)
            if  num_outcome_weights != num_monitored_output_states:
                raise EVCError("The length of the weights argument {} for the {} of {} "
                               "must equal the number of its monitoredOutputStates {}".
                               format(num_outcome_weights,
                                      OUTCOME_FUNCTION,
                                      self.name,
                                      num_monitored_output_states))
        if self.outcome_function.exponents is not None:
            num_outcome_exponents = len(self.outcome_function.exponents)
            if  num_outcome_exponents != num_monitored_output_states:
                raise EVCError("The length of the exponents argument {} for the {} of {} "
                               "must equal the number of its control signals {}".
                               format(num_outcome_exponents,
                                      OUTCOME_FUNCTION,
                                      self.name,
                                      num_monitored_output_states))

        # Insure that length of the weights and/or exponents arguments for the cost_function
        #    matches the number of control signals
        num_control_projections = len(self.controlProjections)
        if self.cost_function.weights is not None:
            num_cost_weights = len(self.cost_function.weights)
            if  num_cost_weights != num_control_projections:
                raise EVCError("The length of the weights argument {} for the {} of {} "
                               "must equal the number of its control signals {}".
                               format(num_cost_weights,
                                      COST_FUNCTION,
                                      self.name,
                                      num_control_projections))
        if self.cost_function.exponents is not None:
            num_cost_exponents = len(self.cost_function.exponents)
            if  num_cost_exponents != num_control_projections:
                raise EVCError("The length of the exponents argument {} for the {} of {} "
                               "must equal the number of its control signals {}".
                               format(num_cost_exponents,
                                      COST_FUNCTION,
                                      self.name,
                                      num_control_projections))

    def _add_monitored_states(self, states_spec, context=None):
        """Validate and then instantiate outputStates to be monitored by EVC

        Use by other objects to add a state or list of states to be monitored by EVC
        states_spec can be a Mechanism, OutputState or list of either or both
        If item is a Mechanism, each of its outputStates will be used
        All of the outputStates specified must be for a Mechanism that is in self.System

        Args:
            states_spec (Mechanism, MechanimsOutputState or list of either or both:
            context:
        """
        states_spec = list(states_spec)
        self._validate_monitored_state_spec(states_spec, context=context)
        self._instantiate_monitored_output_states(states_spec, context=context)

    def __execute__(self,
                    variable=None,
                    runtime_params=None,
                    clock=CentralClock,
                    time_scale=TimeScale.TRIAL,
                    context=None):
        """Determine allocationPolicy for next run of system

        Calls self._update_predicted_input() and ``function``
        Default for ``function`` is _control_signal_grid_search()

        Returns an allocation_policy

        """

        self._update_predicted_input()
        # self.system._cache_state()

        allocation_policy = self.function(controller=self,
                                          variable=variable,
                                          runtime_params=runtime_params,
                                          time_scale=time_scale,
                                          context=context)

        # self.system._restore_state()

        return allocation_policy

    def _update_predicted_input(self):
        """Assign values of predictionMechanisms to predictedInput

        Assign value of each predictionMechanism.value to corresponding item of self.predictedIinput
        Note: must be assigned in order of self.system.processes

        """

        # Assign predictedInput for each process in system.processes

        # The number of originMechanisms requiring input should = the number of predictionMechanisms
        for i in range(len(self.predictionMechanisms)):
            # Get origin mechanism for each process
            origin_mech = self.system.processes[i].originMechanisms[0]
            # Get prediction process for which that is the origin mechanism
            # FIX: PUT TEST HERE THAT THERE IS ONLY ONE (PUT NEXT INSIDE ALL, AND ASSIGN RESULT TO LIST AND CHECK LEN)
            process = next((p for p in self.predictionProcesses if p.originMechanisms[0] is origin_mech), None)
            # Get predictionMechanism for that process
            prediction_mech = process.terminalMechanisms[0]
            # Assign outputState.value of predictionMechanism to each inputState of the originMechanism
            #  (in case more than one process uses that (and therefore projects to) originMechanism
            for value, j in zip(origin_mech.inputValue, range(len(origin_mech.inputValue))):
                self.predictedInput[i][j] = prediction_mech.outputState.value

    def run_simulation(self,
                       inputs,
                       allocation_vector,
                       runtime_params=None,
                       time_scale=TimeScale.TRIAL,
                       context=None):

        if self.value is None:
            # Initialize value if it is None
            self.value = self.allocationPolicy

        # Implement the current allocationPolicy over ControlSignals (outputStates),
        #    by assigning allocation values to EVCMechanism.value, and then calling _update_output_states
        for i in range(len(self.controlSignals)):
            # self.controlSignals[list(self.controlSignals.values())[i]].value = np.atleast_1d(allocation_vector[i])
            self.value[i] = np.atleast_1d(allocation_vector[i])
        self._update_output_states(runtime_params=runtime_params, time_scale=time_scale,context=context)

        # Execute simulation run of system for the current allocationPolicy
        sim_clock = Clock('EVC SIMULATION CLOCK')

        # # MODIFIED 12/25/16 OLD [EXECUTES SYSTEM DIRECTLY]:
        # for i in range(self.system._phaseSpecMax+1):
        #     sim_clock.time_step = i
        #     simulation_inputs = self._get_simulation_system_inputs(phase=i)
        #     self.system.execute(input=simulation_inputs, clock=sim_clock, time_scale=time_scale, context=context)
        #     # # TEST PRINT:
        #     # print ("SIMULATION INPUT: ", simulation_inputs)

        # MODIFIED 12/25/16 NEW [USES SYSTEM.RUN]:
        self.system.run(inputs=inputs, clock=sim_clock, time_scale=time_scale, context=context)

        # Get cost of each controlSignal
        for control_signal in self.controlSignals.values():
            self.controlSignalCosts = np.append(self.controlSignalCosts, np.atleast_2d(control_signal.cost),axis=0)
        # Get outcomes for current allocationPolicy
        #    = the values of the monitored output states (self.inputStates)
        #    stored in self.inputValue = list(self.variable)
            self._update_input_states(runtime_params=runtime_params, time_scale=time_scale,context=context)

    # MODIFIED 12/27/16 OLD:
    # [USED BY __control_signal_grid_search() FOR DIRECT EXECUTION OF system;
    #  REPLACED BY self.predictedInputs and system.run()]
    #
    # def _get_simulation_system_inputs(self, phase):
    #     """Return array of predictionMechanism values for use as inputs to processes in simulation run of System
    #
    #     Returns: 2D np.array
    #
    #     """
    #
    #     simulation_inputs = np.empty_like(self.system.input, dtype=float)
    #
    #     # For each prediction mechanism
    #     for prediction_mech in self.predictionMechanisms:
    #
    #         # Get the index for each process that uses simulated input from the prediction mechanism
    #         for predicted_process in prediction_mech.use_for_processes:
    #             # process_index = self.system.processes.index(predicted_process)
    #             process_index = self.system._processList.processes.index(predicted_process)
    #             # Assign the prediction mechanism's value as the simulated input for the process
    #             #    in the phase at which it is used
    #             if prediction_mech.phaseSpec == phase:
    #                 simulation_inputs[process_index] = prediction_mech.value
    #             # For other phases, assign zero as the simulated input to the process
    #             else:
    #                 simulation_inputs[process_index] = np.atleast_1d(0)
    #     return simulation_inputs
    #
    # def _assign_simulation_inputs(self):
    #
    #     # For each prediction mechanism, assign its value as input to corresponding process for the simulation
    #     for mech in self.predictionMechanisms:
    #         # For each outputState of the predictionMechanism, assign its value as the value of the corresponding
    #         # Process.inputState for the ORIGIN mechanism corresponding to mech
    #         for output_state in mech.outputStates:
    #             for input_state_name, input_state in list(mech.inputStates.items()):
    #                 for projection in input_state.receivesFromProjections:
    #                     input = mech.outputStates[output_state].value
    #                     projection.sender.owner.inputState.receivesFromProjections[0].sender.value = input
    # MODIFIED 12/27/16 END


def __control_signal_grid_search(controller=None, **kwargs):
    """Grid searches combinations of controlSignals in specified allocation ranges to find one that maximizes EVC

    COMMENT:
        NOTES ON API FOR CUSTOM VERSIONS:
            Gets controller as argument (along with any standard params specified in call)
            Must include **kwargs to receive standard args (variable, params, time_scale, and context)
            Must return an allocation policy compatible with controller.allocationPolicy:
                2d np.array with one array for each allocation value

            Following attributes are available:
            controller._get_simulation_system_inputs gets inputs for a simulated run (using predictionMechamisms)
            controller._assign_simulation_inputs assigns value of predictionMechanisms to inputs of ORIGIN mechanisms
            controller.run will execute a specified number of trials with the simulation inputs
            controller.monitored_states is a list of the mechanism outputStates being monitored for outcomes
            controller.inputValue is a list of current outcome values (values for monitored_states)
            controller.controlSignals is a list of controlSignal objects
            controlSignal.allocationSamples is the set of samples specified for that controlSignal
            [TBI:] controlSignal.allocation_range is the range that the controlSignal value can take
            controller.allocationPolicy - holds current allocationPolicy
            controller.outputValue is a list of current controlSignal values
            controller.value_function - calls the three following functions (done explicitly, so each can be specified)
            controller.outcome_aggregation function - aggregates outcomes (using specified weights and exponentiation)
            controller.cost_function  aggregate costs of control signals
            controller.combine_outcome_and_cost_function - combines outcoms and costs
    COMMENT

    Description
    -----------
        Construct and search space of control signals for maximum EVC and set value of controlSignals accordingly

        * Get ``allocationSamples`` for each ``controlSignal``
        * Construct ``controlSignalSearchSpace``: a 2D np.array of control allocation policies, each policy of which
          is a different combination of values, one from the ``allocationSamples`` of each control signal.
        * Call ``system``.execute for each control allocation policy in ``controlSignalSearchSpace``
        * Store an array of values for ControlSignals in ``monitoredOutputStates`` (i.e., the inputStates in
          ``inputStates``) for each control allocation policy.
        * Call ``execute`` to calculate the EVC for each control allocation policy, identify the maxium, and assign to
          ``EVCmax``.
        * Set ``EVCmaxPolicy`` to the control allocation policy (outputState.values) corresponding to EVCmax
        * Set value for each control signal (outputState.value) to the values in ``EVCmaxPolicy``
        * Return ``allocationPolicy``

         Note:
         * runtime_params is used for self.execute (that calculates the EVC for each call to system.execute);
             it is NOT used for system.execute -- that uses the runtime_params provided for the Mechanisms in each
             Process.congiruation

        Returns (2D np.array): value of outputState for each monitored state (in self.inputStates) for EVCMax
    FROM EXECUTE END

    """

    # Get value of, or set default for standard args
    try:
        context = kwargs[VARIABLE]
    except KeyError:
        variable = None
    try:
        runtime_params = kwargs[PARAMS]
    except KeyError:
        runtime_params = None
    try:
        clock = kwargs[CLOCK]
    except KeyError:
        clock = CentralClock
    try:
        time_scale = kwargs[TIME_SCALE]
    except KeyError:
        time_scale = TimeScale.TRIAL
    try:
        context = kwargs[CONTEXT]
    except KeyError:
        context = None

    if not controller:
        if INITIALIZING in context:
            # If this is an initialization call, rReturn default allocation value as place marker, since
            #    controller has not yet been instantiated, so allocationPolicy (actual return value) not yet determined
            return defaultControlAllocation
        else:
            raise EVCError("controller argument must be specified in call to "
                           "EVCMechanism.__control_signal_grid_search")

    #region CONSTRUCT SEARCH SPACE
    # IMPLEMENTATION NOTE: MOVED FROM _instantiate_function
    #                      TO BE SURE LATEST VALUES OF allocationSamples ARE USED (IN CASE THEY HAVE CHANGED)
    #                      SHOULD BE PROFILED, AS MAY BE INEFFICIENT TO EXECUTE THIS FOR EVERY RUN
    control_signal_sample_lists = []
    control_signals = controller.controlSignals

    # Get allocationSamples for all ControlSignals
    num_control_signals = len(control_signals)

    for control_signal in controller.controlSignals.values():
        control_signal_sample_lists.append(control_signal.allocationSamples)

    # Construct controlSignalSearchSpace:  set of all permutations of ControlProjection allocations
    #                                     (one sample from the allocationSample of each ControlProjection)
    # Reference for implementation below:
    # http://stackoverflow.com/questions/1208118/using-numpy-to-build-an-array-of-all-combinations-of-two-arrays
    controller.controlSignalSearchSpace = \
        np.array(np.meshgrid(*control_signal_sample_lists)).T.reshape(-1,num_control_signals)
    # END MOVE
    #endregion

    # MODIFIED 12/27/16 OLD:
    # controller._assign_simulation_inputs()
    # MODIFIED 12/27/16 END

    #region RUN SIMULATION

    controller.EVCmax = None
    controller.EVCvalues = []
    controller.EVCpolicies = []

    # Reset context so that System knows this is a simulation (to avoid infinitely recursive loop)
    context = context.replace(EXECUTING, '{0} {1}'.format(controller.name, EVC_SIMULATION))

    if controller.prefs.reportOutputPref:
        progress_bar_rate_str = ""
        search_space_size = len(controller.controlSignalSearchSpace)
        progress_bar_rate = int(10 ** (np.log10(search_space_size)-2))
        if progress_bar_rate > 1:
            progress_bar_rate_str = str(progress_bar_rate) + " "
        print("\n{0} evaluating EVC for {1} (one dot for each {2}of {3} samples): ".
              format(controller.name, controller.system.name, progress_bar_rate_str, search_space_size))

    # Evaluate all combinations of controlSignals (policies)
    sample = 0
    controller.EVCmaxStateValues = controller.variable.copy()
    controller.EVCmaxPolicy = controller.controlSignalSearchSpace[0] * 0.0

    # Parallelize using multiprocessing.Pool
    # NOTE:  currently fails on attempt to pickle lambda functions
    #        preserved here for possible future restoration
    if PY_MULTIPROCESSING:
        EVC_pool = Pool()
        results = EVC_pool.map(_compute_EVC, [(controller, arg, runtime_params, time_scale, context)
                                             for arg in controller.controlSignalSearchSpace])

    else:

        # Parallelize using MPI
        if MPI_IMPLEMENTATION:
            Comm = MPI.COMM_WORLD
            rank = Comm.Get_rank()
            size = Comm.Get_size()

            chunk_size = (len(controller.controlSignalSearchSpace) + (size-1)) // size
            print("Rank: {}\nChunk size: {}".format(rank, chunk_size))
            start = chunk_size * rank
            end = chunk_size * (rank+1)
            if start > len(controller.controlSignalSearchSpace):
                start = len(controller.controlSignalSearchSpace)
            if end > len(controller.controlSignalSearchSpace):
                end = len(controller.controlSignalSearchSpace)
        else:
            start = 0
            end = len(controller.controlSignalSearchSpace)

        if MPI_IMPLEMENTATION:
            print("START: {0}\nEND: {1}".format(start,end))

        #region EVALUATE EVC

        # Compute EVC for each allocation policy in controlSignalSearchSpace
        # Notes on MPI:
        # * breaks up search into chunks of size chunk_size for each process (rank)
        # * each process computes max for its chunk and returns
        # * result for each chunk contains EVC max and associated allocation policy for that chunk

        result = None
        EVC_max = float('-Infinity')
        EVC_max_policy = np.empty_like(controller.controlSignalSearchSpace[0])
        EVC_max_state_values = np.empty_like(controller.inputValue)
        max_value_state_policy_tuple = (EVC_max, EVC_max_state_values, EVC_max_policy)
        # FIX:  INITIALIZE TO FULL LENGTH AND ASSIGN DEFAULT VALUES (MORE EFFICIENT):
        EVC_values = np.array([])
        EVC_policies = np.array([[]])

        for allocation_vector in controller.controlSignalSearchSpace[start:end,:]:
        # for iter in range(rank, len(controller.controlSignalSearchSpace), size):
        #     allocation_vector = controller.controlSignalSearchSpace[iter,:]:

            if controller.prefs.reportOutputPref:
                increment_progress_bar = (progress_bar_rate < 1) or not (sample % progress_bar_rate)
                if increment_progress_bar:
                    print(kwProgressBarChar, end='', flush=True)
            sample +=1

            # Calculate EVC for specified allocation policy
            result_tuple = _compute_EVC(args=(controller, allocation_vector,
                                              runtime_params,
                                              time_scale,
                                              context))
            EVC, outcome, cost = result_tuple

            EVC_max = max(EVC, EVC_max)
            # max_result([t1, t2], key=lambda x: x1)

            # Add to list of EVC values and allocation policies if save option is set
            if controller.paramsCurrent[SAVE_ALL_VALUES_AND_POLICIES]:
                # FIX:  ASSIGN BY INDEX (MORE EFFICIENT)
                EVC_values = np.append(EVC_values, np.atleast_1d(EVC), axis=0)
                # Save policy associated with EVC for each process, as order of chunks
                #     might not correspond to order of policies in controlSignalSearchSpace
                if len(EVC_policies[0])==0:
                    EVC_policies = np.atleast_2d(allocation_vector)
                else:
                    EVC_policies = np.append(EVC_policies, np.atleast_2d(allocation_vector), axis=0)

            # If EVC is greater than the previous value:
            # - store the current set of monitored state value in EVCmaxStateValues
            # - store the current set of controlSignals in EVCmaxPolicy
            # if EVC_max > EVC:
            if EVC == EVC_max:
                # Keep track of state values and allocation policy associated with EVC max
                # EVC_max_state_values = controller.inputValue.copy()
                # EVC_max_policy = allocation_vector.copy()
                EVC_max_state_values = controller.inputValue
                EVC_max_policy = allocation_vector
                max_value_state_policy_tuple = (EVC_max, EVC_max_state_values, EVC_max_policy)

        #endregion

        # Aggregate, reduce and assign global results

        if MPI_IMPLEMENTATION:
            # combine max result tuples from all processes and distribute to all processes
            max_tuples = Comm.allgather(max_value_state_policy_tuple)
            # get tuple with "EVC max of maxes"
            max_of_max_tuples = max(max_tuples, key=lambda max_tuple: max_tuple[0])
            # get EVCmax, state values and allocation policy associated with "max of maxes"
            controller.EVCmax = max_of_max_tuples[0]
            controller.EVCmaxStateValues = max_of_max_tuples[1]
            controller.EVCmaxPolicy = max_of_max_tuples[2]

            if controller.paramsCurrent[SAVE_ALL_VALUES_AND_POLICIES]:
                controller.EVCvalues = np.concatenate(Comm.allgather(EVC_values), axis=0)
                controller.EVCpolicies = np.concatenate(Comm.allgather(EVC_policies), axis=0)
        else:
            controller.EVCmax = EVC_max
            controller.EVCmaxStateValues = EVC_max_state_values
            controller.EVCmaxPolicy = EVC_max_policy
            if controller.paramsCurrent[SAVE_ALL_VALUES_AND_POLICIES]:
                controller.EVCvalues = EVC_values
                controller.EVCpolicies = EVC_policies
        # # TEST PRINT:
        # import re
        # print("\nFINAL:\n\tmax tuple:\n\t\tEVC_max: {}\n\t\tEVC_max_state_values: {}\n\t\tEVC_max_policy: {}".
        #       format(re.sub('[\[,\],\n]','',str(max_value_state_policy_tuple[0])),
        #              re.sub('[\[,\],\n]','',str(max_value_state_policy_tuple[1])),
        #              re.sub('[\[,\],\n]','',str(max_value_state_policy_tuple[2]))),
        #       flush=True)

        # FROM MIKE ANDERSON (ALTERNTATIVE TO allgather:  REDUCE USING A FUNCTION OVER LOCAL VERSION)
        # a = np.random.random()
        # mymax=Comm.allreduce(a, MPI.MAX)
        # print(mymax)

    if controller.prefs.reportOutputPref:
        print("\nEVC simulation completed")
#endregion

    # -----------------------------------------------------------------

    #region ASSIGN CONTROL SIGNAL VALUES

    # Assign allocations to controlSignals for optimal allocation policy:
    EVCmaxStateValue = iter(controller.EVCmaxStateValues)

    # Assign max values for optimal allocation policy to controller.inputStates (for reference only)
    for i in range(len(controller.inputStates)):
        controller.inputStates[list(controller.inputStates.keys())[i]].value = np.atleast_1d(next(EVCmaxStateValue))


    # Report EVC max info
    if controller.prefs.reportOutputPref:
        print ("\nMaximum EVC for {0}: {1}".format(controller.system.name, float(controller.EVCmax)))
        print ("ControlProjection allocation(s) for maximum EVC:")
        for i in range(len(controller.controlSignals)):
            print("\t{0}: {1}".format(list(controller.controlSignals.values())[i].name,
                                    controller.EVCmaxPolicy[i]))
        print()

    #endregion

    # TEST PRINT:
    # print ("\nEND OF TRIAL 1 EVC outputState: {0}\n".format(controller.outputState.value))

    #region ASSIGN AND RETURN allocationPolicy
    # Convert EVCmaxPolicy into 2d array with one controlSignal allocation per item,
    #     assign to controller.allocationPolicy, and return (where it will be assigned to controller.value).
    #     (note:  the conversion is to be consistent with use of controller.value for assignments to controlSignals.value)
    controller.allocationPolicy = np.array(controller.EVCmaxPolicy).reshape(len(controller.EVCmaxPolicy), -1)
    return controller.allocationPolicy
    #endregion

def _compute_EVC(args):
    """compute EVC for a specified allocation policy

    IMPLEMENTATION NOTE:  implemented as a function so it can be used with multiprocessing Pool

    Args:
        ctlr (EVCMechanism)
        allocation_vector (1D np.array): allocation policy for which to compute EVC
        runtime_params (dict): runtime params passed to ctlr.update
        time_scale (TimeScale): time_scale passed to ctlr.update
        context (value): context passed to ctlr.update

    Returns (float, float, float):
        (EVC_current, aggregated_outcomes, aggregated_costs)

    """

    ctlr, allocation_vector, runtime_params, time_scale, context = args

    ctlr.run_simulation(inputs=list(ctlr.predictedInput),
                        allocation_vector=allocation_vector,
                        runtime_params=runtime_params,
                        time_scale=time_scale,
                        context=context)

    EVC_current = ctlr.paramsCurrent[VALUE_FUNCTION](ctlr, ctlr.inputValue, ctlr.controlSignalCosts, context=context)

    if PY_MULTIPROCESSING:
        return

    else:
        return (EVC_current)


def __value_function(controller, outcomes, costs, context):
    """aggregate outcomes, costs, combine, and return value
    """

    # Aggregate outcome values (= weighted sum of exponentiated values of monitored output states)
    aggregated_outcomes = controller.paramsCurrent[OUTCOME_FUNCTION].function(variable=outcomes,
                                                                                          context=context)

    # Aggregate costs
    aggregated_costs = controller.paramsCurrent[COST_FUNCTION].function(costs)

    # Combine aggregate outcomes and costs to determine value
    value = controller.paramsCurrent[COMBINE_OUTCOME_AND_COST_FUNCTION].function([aggregated_outcomes,
                                                                                    -aggregated_costs])

    return (value, aggregated_outcomes, aggregated_costs)
