#
# *********************************************  Process ***************************************************************
#

# *****************************************    PROCESS CLASS    ********************************************************

"""
Sections:
  * :ref:`Process_Overview`
  * :ref:`Process_Creating_A_Process`
  * :ref:`Process_Structure`
     * :ref:`Process_Pathway`
     * :ref:`Process_Mechanisms`
     * :ref:`Process_Projections`
     * :ref:`Process_Input_And_Ouput`
     * :ref:`Process_Learning`
  * :ref:`Process_Execution`
  * :ref:`Process_Class_Reference`


.. _Process_Overview:

Overview
--------

A process is a sequence of mechanisms connected by projections.  A process can be created by calling process(),
or by specifying it in the processes attribute of a system. Executing a process executes all of its mechanisms
in the order in which they are listed in its pathway:  a list of mechanisms and (optional)
projection specifications.  Projections can be specified among any mechanisms in a process, including
to themselves.  Mechanisms in a process can also project to mechanisms in other processes, but these will only
have an effect if all of the processes involved are members of a single system (see System).  Projections
between mechanisms can also be trained, by assigning learning signals to those projections.  Learning can
also be specified for the entire process, in which case the projections between all of its mechanisms are trained.

.. _Process_Creating_A_Process:

Creating a Process
------------------

Processes are created by calling the ``process`` "factory" method.  If no arguments are provided, a process with a
single default mechanism will be returned (see [LINK for default] for default mechanism).

.. _Process_Structure:

Structure
---------

.. _Process_Pathway:

Pathway
~~~~~~~

A process is defined primarily by its ``pathway`` attribute, which is a list of mechanisms and projections.  The
list defines an array of mechanisms that will executed in sequence.  Each mechanism in the pathway must project
at least to the next one in the pathway, though it can project to others, and also receive recurrent (feedback)
projections from them.  However, pathways cannot be used to construct branching patterns;  that requires the use of
a :doc:`System`.  the mechanisms in a process pathway are generally :doc:`ProcessingMechanisms`, which receive an input,
transform it in some way, and make the transformed value available as their output.  The projections between mechanisms
in a process must be  :doc:`Mapping` projections (see Projections).  These transmit the output of a mechanism
(the projection's sender)  to the input of another mechanism (the projection's receiver).  Specification of a pathway
requires, at the least, a list of mechanisms.  These can be specified directly, or in a tuple that also contains a set
of runtime parameters and/or a phase specification.  Projections between a pair of mechanisms can be specified by
interposing them in the list between the pair.  When no projection appears between two adjacent mechanisms in the
pathway, and there is no otherwise specified projection between them, PsyNeuLink assigns a default projection.
Specifying the components of a pathway is described in more detail below.

.. _Process_Mechanisms:

Mechanisms
~~~~~~~~~~

The mechanisms of a process must be listed in its pathway explicitly, in the order to be executed.  The first
mechanism in the process is designated as the :keyword:`ORIGIN`, and receives as its input any input provided to the
process. The last mechanism is designated at the :keyword:`TERMINAL`, and its output is assigned as the output of the
process. (Note:: The :keyword:`ORIGIN` and :keyword:`TERMINAL` mechanisms of a process are not necessarily
:keyword:`ORIGIN` and :keyword:`TERMINAL` mechanisms of a system; see System).
.. note: designations are stored in the mechanism.processes attribute (see _instantiate_graph below, and Mechanism)

Mechanisms are specified in one of two ways:  directly or in a tuple.  Direct specification can
use any supported format for specifying a mechanism (see :ref:`Mechanism_Creating_A_Mechanism`).  Alternatively,
mechanisms can be specified as the first item of a tuple, along with a set of runtime parameters and/or a phase
specification.  The runtime parameters will be used for that mechanism whenever the process (or a system to which it
belongs) is executed, but otherwise they do not remain associated with the mechanism
(see :ref:`Mechanism_Runtime_Parameters`).  The phase specification is determines the time_step at which the mechanism
is executed when it is executed as part of a system (see System :ref:`System_Phase` for an explanation of phases).
Either the runtime params or the phase can be omitted (if the phase is omitted, the default value of 0 will be
assigned). The same mechanism can appear more than once in a pathway list, to generate recurrent processing loops.
(Note: irrespective of the format in which a mechanism is specified in a pathway, it's entry is converted internally
to a :class:`MechanismTuple` namedtuple, information about which is stored in a :class:`MechanismList`
and can be accessed in the process' ``mechanisms`` attribute.)

.. _Process_Projections:

Projections
~~~~~~~~~~~

Projections between mechanisms in the process are specified in one of three ways:

* Inline specification
    Projection specifications can be interposed between any two mechanisms in the pathway list.  This creates
    a projection from the preceding mechanism in the list to the one that follows it.  The projection specification
    can be an instance of a Mapping projection, the class name Mapping, a keyword for a type of Mapping projection
    (:keyword:`IDENTITY_MATRIX`, :keyword:`FULL_CONNECTIVITY_MATRIX`, :keyword:`RANDOM_CONNECTIVITY_MATRIX`),
    or a dictionary with specifications for the projection (see Projection for details of how to specify projections).

* Stand-alone projection
    When a projection is created on its own, it can be assigned a sender and receiver mechanism (see Projection).
    If both are in the process, then it will be used when creating that process.  Stand-alone specification
    of a projection between two mechanisms in a process takes precedence over default or inline specification;
    that is, the stand-alone projection will be used in place of any that is specified in the pathway.
    Stand-alone specification is required to implement projections between mechanisms that are not adjacent in the
    pathway list.

* Default assignment
    For any mechanism that does not receive a projection from another mechanism in the process (specified using one of
    the methods above), a Mapping projection is automatically created from the mechanism that precedes it in the
    pathway.  If the format of the preceding mechanism's output matches that of the next mechanism, then
    IDENTITY_MATRIX is used for the projection;  if the formats do not match, or learning has been specified either
    for the projection or the process, then ''FULL_CONNECTIVITY_MATRIX'' is used (see Projection).

.. _Process_Input_And_Ouput:

Process input and output
~~~~~~~~~~~~~~~~~~~~~~~~

The input to a process is a list or 2D np.array provided as an arg in its execute() method or the run() function,
and assigned to its input attribute.  When a process is created, a set of ProcessInputStates and Mapping projections
are automatically generated to transmit the process' input to its :keyword:`ORIGIN` mechanism, as follows:

* if the number of items in the input is the same as the number of :keyword:`ORIGIN` inputStates:
    a Mapping projection is created for each value of the input to an inputState of the :keyword:`ORIGIN` mechanism

* if the input has only one item but the :keyword:`ORIGIN` mechanism has more than one inputState:
    a single ProcessInputState is created with projections to each of the :keyword:`ORIGIN` mechanism inputStates

* if the input has more than one item but the :keyword:`ORIGIN` mechanism has only one inputState:
    a ProcessInputState is created for each input item, and all project to the :keyword:`ORIGIN` mechanism's
    inputState

* otherwise, if the input has > 1 item, and the :keyword:`ORIGIN` mechanism has > 1 inputState but the numbers are not
    equal: an error message is generated indicating that the there is an ambiguous
    mapping from the Process' input value to :keyword:`ORIGIN` mechanism's inputStates

The output of a process is a 2D np.array containing the values of its :keyword:`TERMINAL` mechanism's outputStates

.. _Process_Learning:

Learning
~~~~~~~~

Learning modifies projections so that the input to a given mechanism generates a desired output ("target").
Learning can be configured for a projection to a particular mechanism (see Projection), or for the entire process
(using its ''learning'' attribute).  Specifying learning for a process will implement it for all projections
# XXX TEST WHICH IS TRUE:  in the process [???] OR
# XXX that have been assigned by default (but not ones created using either inline or stand-alone specification).
When it is specified for the process, then it will train all projections in the process so that a given input to the
first mechanism in the process (i.e, the input to the process) will generate the target value as the output of the
last mechanism in the process (i.e., the output of the process).  In either case, all mechanisms that receive
projections for which learning has been specified must be compatiable with learnin (see LearningSignal).

When learning is specified, the following objects are automatically created (see figure below):
MonitoringMechanism, used to evaluate the output of a mechanism against a target value.
Mapping projection from the mechanism being monitored to the MonitoringMechanism
LearningSignal that projects from the MonitoringMechanism to the projection being learned (i.e., the one that
projects to the mechanism being monitored).

Different learning algorithms can be specified (e.g., Reinforcement Learning, Backpropagation), that will implement
the appropriate type of, and specifications for the MonitoringMechanisms and LearningSignals required for the
specified type of learning.  As noted above, however, all mechanisms that receive projections being learned must
be compatible with learning.

**Figure: Learning in PsyNeuLink**

.. figure:: _static/PNL_learning_fig.png
   :alt: Schematic of learning mechanisms and LearningSignal projections in a process

   Learning in a connectionist network with two layers

.. _Process_Execution:

Execution
---------

A process can be executed as part of a system (see System) or on its own.  On its own, it can be executed by calling
either its ``execute`` or ``run`` methods.  When a process is executed, its input is conveyed to the :keyword:`ORIGIN`
mechanism (first mechanism in the pathway).  By default, the the input value is presented only once.  If the mechanism
is executed again in the same round of execution (e.g., if it appears again in the pathway, or receives recurrent
projections), the input is not presented again.  However, the input can be "clamped" on using the clamp_input argument
of execute() or run().  After the :keyword:`ORIGIN` mechanism is executed, each subsequent mechanism in the pathway
is executed in sequence (irrespective of any phase specification).  If a mechanism is specified in the pathway in a
(mechanisms, runtime_params, phase) tuple, then the runtime parameters are applied and the mechanism is executed using
them (see Mechanism for parameter specification).  Finally the output of the :keyword:`TERMINAL` mechanism (last one in
the pathway) is assigned as the output of the process.  If learning has been specified for the process or any of the
projections among the mechanisms in its pathway, then the relevant learning mechanims are executed.  These calculate
changes that will be made to the corresponding projections (note: these changes are not applied until the mechanisms
that receive those projections are next executed; see Projection for an explanation of lazy updating of projections).

Examples
--------

*Specification of mechanisms in a pathway:*

The first mechanism is specified as a reference to an instance, the second as a default instance of a mechanism type,
and the third in tuple format (specifying a reference to a mechanism that should receive some_params at runtime;
note: the phase is omitted and so will be assigned the default value of 0)::

    mechanism_1 = Transfer()
    mechanism_2 = DDM()
    some_params = {PARAMETER_STATE_PARAMS:{FUNCTION_PARAMS:{THRESHOLD:2,NOISE:0.1}}}
    my_process = process(pathway=[mechanism_1, Transfer, (mechanism_2, some_params)])

*Default projection specification:*

The pathway for this process uses default projection specification::

    my_process = process(pathway=[mechanism_1, mechanism_2, mechanism_3])

A mapping projection is automatically instantiated between each of the mechanisms

*Inline projection specification using an existing projection:*

In this pathway, projection_A is specified as the projection between the first and second mechanisms; a
default projection will be created between mechanism_2 and mechanism_3::

    projection_A = Mapping()
    my_process = process(pathway=[mechanism_1, projection_A, mechanism_2, mechanism_3])

*Inline projection specification using a keyword:*

In this pathway, a random connectivity mattrix is assigned as the projection between the first and second
mechanisms::

    my_process = process(pathway=[mechanism_1, RANDOM_CONNECTIVITY_MATRIX, mechanism_2, mechanism_3])

*Stand-alone projection specification:*

In this pathway, projection_A is explicilty specified as a projection between mechansim_1 and mechanism_2,
and so will be used as the projection between them in my_process; a default projection will be created between
mechanism_2 and mechanism_3::

    projection_A = Mapping(sender=mechanism_1, receiver=mechanism_2)
    my_process = process(pathway=[mechanism_1, mechanism_2, mechanism_3])

*Process that implements learning:*

This pathway implements a series of mechanisms with projections between them all of which will be learned
using backpropagation (the default learning algorithm).  Note that it uses the logistic function, which is compatible
with backpropagation::

    mechanism_1 = Transfer(function=Logistic)
    mechanism_2 = Transfer(function=Logistic)
    mechanism_3 = Transfer(function=Logistic)

.. XXX USE EXAMPLE BELOW THAT CORRESPONDS TO CURRENT FUNCTIONALITY (WHETHER TARGET MUST BE SPECIFIED)
    # my_process = process(pathway=[mechanism_1, mechanism_2, mechanism_3],
    #                      learning=LEARNING_SIGNAL)
    my_process = process(pathway=[mechanism_1, mechanism_2, mechanism_3],
                         learning=LEARNING_SIGNAL,
                         target=[0])

.. ADD EXAMPLE HERE WHEN FUNCTIONALITY IS AVAILABLE
   *Process with individual projections that implement learning:*

    mechanism_1 = Transfer(function=Logistic)
    mechanism_2 = Transfer(function=Logistic)
    mechanism_3 = Transfer(function=Logistic)
    # my_process = process(pathway=[mechanism_1, mechanism_2, mechanism_3],
    #                      learning=LEARNING_SIGNAL)



COMMENT:
    Module Contents
        process() factory method:  instantiate process
        Process_Base: class definition
        ProcessInputState: class definition
        ProcessList: class definition
COMMENT

.. _Process_Class_Reference:

Class Reference
---------------

"""

import re
import math
from collections import Iterable
import PsyNeuLink.Functions
from PsyNeuLink.Functions.ShellClasses import *
from PsyNeuLink.Globals.Registry import register_category
from PsyNeuLink.Functions.Mechanisms.Mechanism import Mechanism_Base, mechanism, _is_mechanism_spec
from PsyNeuLink.Functions.Projections.Projection import _is_projection_spec, _is_projection_subclass, _add_projection_to
from PsyNeuLink.Functions.Projections.Mapping import Mapping
from PsyNeuLink.Functions.Projections.LearningSignal import LearningSignal, kwWeightChangeParams
from PsyNeuLink.Functions.States.State import instantiate_state_list, instantiate_state
from PsyNeuLink.Functions.States.ParameterState import ParameterState
from PsyNeuLink.Functions.Mechanisms.MonitoringMechanisms.Comparator import *

# *****************************************    PROCESS CLASS    ********************************************************

# ProcessRegistry ------------------------------------------------------------------------------------------------------

defaultInstanceCount = 0 # Number of default instances (used to index name)

# Labels for items in pathway entry tuples
OBJECT = 0
PARAMS = 1
PHASE = 2
DEFAULT_PHASE_SPEC = 0

# FIX: NOT WORKING WHEN ACCESSED AS DEFAULT:
DEFAULT_PROJECTION_MATRIX = AUTO_ASSIGN_MATRIX
# DEFAULT_PROJECTION_MATRIX = IDENTITY_MATRIX

ProcessRegistry = {}


class ProcessError(Exception):
     def __init__(self, error_value):
         self.error_value = error_value

     def __str__(self):
         return repr(self.error_value)


# Process factory method:
@tc.typecheck
def process(process_spec=None,
            default_input_value=None,
            pathway=None,
            initial_values:dict={},
            clamp_input:tc.optional(tc.enum(SOFT_CLAMP, HARD_CLAMP))=None,
            default_projection_matrix=DEFAULT_PROJECTION_MATRIX,
            learning:tc.optional(_is_projection_spec)=None,
            target:tc.optional(is_numerical)=None,
            params=None,
            name=None,
            prefs:is_pref_set=None,
            context=None):

    """
    process(                                                \
    process_spec=None,                                      \
    default_input_value=None,                               \
    pathway=None,                                           \
    initial_values=None,                                    \
    clamp_input=None,                                       \
    default_projection_matrix=None,                         \
    learning=None,                                          \
    target=None,                                            \
    params=None,                                            \
    name=None,                                              \
    prefs=None)

    Factory method for Process: returns instance of Process.

    If called with no arguments, returns an instance of Process with a single DefaultMechanism [LINK for default].

    See :any:`Process_Base` for class description.

    COMMENT:
       REPLACE DefaultMechanism BELOW USING Inline markup
    COMMENT

    Arguments
    ---------

    process_spec : Optional[str or Dict[param keyword, param value]]
        if it is :keyword:`None`, returns an instance of Process with a single DefaultMechanism [LINK for default];
        if it is a string, uses it as the name for the process;
        if it is a dict, the key for each entry must be a parameter name, and its value the value to assign to that
        parameter (these values will be used to instantiate the process, and will override any values assigned
        to the arguments in the call to ``process``).
        Note: if a name is not specified, the nth instance created will be named by using the process'
        ``functionType`` attribute as the base and adding an indexed suffix:  functionType-n.

    default_input_value : List[values] or ndarray :  default default input value of :keyword:`ORIGIN` mechanism
        use as the input to the process if none is provided in a call to the ``execute`` method or ``run`` function.
        Must the same length as the :keyword:`ORIGIN` mechanism's input.

    pathway : List[mechanism spec[, projection spec], mechanism spec...] : default List[``DefaultMechanism``]
        mechanisms must be from the ProcessingMechanism class [LINK], and the specification can be an instance,
        a class name (creates a default instance), or a specification dictionary [LINK];
        projections must be from the Mapping [LINK] projection class, and can be an instance, a class name
        (creates a default instance), or a specification dictionary [LINK].

    initial_values : Optional[Dict[mechanism, param value]] : default ``None``
        dictionary of values used to initialize specified mechanisms. The key for each entry is a mechanism object,
        and the value is a number, list or np.array that must be compatible with the format of mechanism.value.
        Mechanisms not specified will be initialized with their default input value.

    clamp_input : Optional[keyword]
        determines whether the process' input continues to be applied to the :keyword:`ORIGIN` mechanism
        after its initial execution.

        ``None``: Process input is used only for the first execution of the :keyword:`ORIGIN` mechanism in a round of
        executions.

        :keyword:`SOFT_CLAMP`: combines the process' input with input from any other projections to the
        :keyword:`ORIGIN` mechanism every time it is executed in a round of executions.

        :keyword:`HARD_CLAMP`: applies the process' input in place of any other sources of input to the
        :keyword:`ORIGIN` mechanism every time it is executed in a round of executions.

    default_projection_matrix : keyword, list or ndarray : default ``DEFAULT_PROJECTION_MATRIX``,
        type of matrix used for default projections (see ''matrix'' parameter for ''Mapping()'' projection) [LINK]

    learning : Optional[LearningSignal spec]
        implements learning for all eligible projections in the process
        (see LearningSignal [LINK] for specifications)

    target : List or ndarray : default ndarray of zeroes
        must be the same length as the :keyword:`TERMINAL` mechanism's output

    params : Optional[Dict[param keyword, param value]
        dictionary that can include any of the parameters above. Use the parameter's name as the keyword for its entry;
        values in the dictionary will override argument values.

    name : str : default Process-[index]
        string used for the name of the process
        (see Registry module for conventions used in naming, including for default and duplicate names)

    prefs : PreferenceSet or specification dict : Process.classPreferences
        preference set for process (see FunctionPreferenceSet module for specification of PreferenceSet)

    COMMENT:
    context : str : default ''None''
           string used for contextualization of instantiation, hierarchical calls, executions, etc.
    COMMENT

    Returns
    -------
    instance of Process : Process

    """

    # MODIFIED 9/20/16 NEW:  REPLACED IN ARG ABOVE WITH None
    pathway = pathway or [Mechanism_Base.defaultMechanism]
    # MODIFIED 9/20/16 END

    # # Called with a keyword
    # if process_spec in ProcessRegistry:
    #     return ProcessRegistry[process_spec].processSubclass(params=params, context=context)
    #
    # Called with a string that is not in the Registry, so return default type with the name specified by the string
    if isinstance(process_spec, str):
        return Process_Base(name=process_spec, params=params, context=context)

    # Called with Process specification dict (with type and params as entries within it), so:
    #    - return a Process instantiated using args passed in process_spec
    elif isinstance(process_spec, dict):
        return Process_Base(context=context, **process_spec)

    # Called without a specification, so return Process with default mechanism
    elif process_spec is None:
        return Process_Base(default_input_value=default_input_value,
                            pathway=pathway,
                            initial_values=initial_values,
                            clamp_input=clamp_input,
                            default_projection_matrix=default_projection_matrix,
                            learning=learning,
                            target=target,
                            params=params,
                            name=name,
                            prefs=prefs,
                            context=context)

    # Can't be anything else, so return empty
    else:
        return None


kwProcessInputState = 'ProcessInputState'
kwTarget = 'target'
from PsyNeuLink.Functions.States.OutputState import OutputState

# DOCUMENT:  HOW DO MULTIPLE PROCESS INPUTS RELATE TO # OF INPUTSTATES IN FIRST MECHANISM
#            WHAT HAPPENS IF LENGTH OF INPUT TO PROCESS DOESN'T MATCH LENGTH OF VARIABLE FOR FIRST MECHANISM??


class Process_Base(Process):
    """
    Process_Base(process_spec=None,                         \
    default_input_value=None,                               \
    pathway=None,                                           \
    initial_values={},                                      \
    clamp_input:=None,                                      \
    default_projection_matrix=DEFAULT_PROJECTION_MATRIX,    \
    learning=None,                                          \
    target=None,                                            \
    params=None,                                            \
    name=None,                                              \
    prefs=None,                                             \
    context=None)

    Abstract class for Process.

    .. note::
       Processes should NEVER be instantiated by a direct call to the base class.
       They should be instantiated using the :class:`process` factory method (see it for description of parameters).

    COMMENT:
        Description
        -----------
            Process is a Category of the Function class.
            It implements a Process that is used to execute a sequence of mechanisms connected by projections.
            NOTES:
                * if no pathway or time_scale is provided:
                    a single mechanism of Mechanism class default mechanism and TRIAL are used
                * process.input is set to the inputState.value of the first mechanism in the pathway
                * process.output is set to the outputState.value of the last mechanism in the pathway

        Class attributes
        ----------------
        functionCategory : str : default kwProcessFunctionCategory
        className : str : default kwProcessFunctionCategory
        suffix : str : default "<kwMechanismFunctionCategory>"
        registry : dict : default ProcessRegistry
        classPreference : PreferenceSet : default ProcessPreferenceSet instantiated in __init__()
        classPreferenceLevel (PreferenceLevel): PreferenceLevel.CATEGORY
        + variableClassDefault = inputValueSystemDefault                     # Used as default input value to Process)
        + paramClassDefaults = {PATHWAY: [Mechanism_Base.defaultMechanism],
                                kwTimeScale: TimeScale.TRIAL}

        Class methods
        -------------
            - execute(input, control_signal_allocations, time_scale):
                executes the process by calling execute_functions of the mechanisms (in order) in the pathway list
                assigns input to sender.output (and passed through mapping) of first mechanism in the pathway list
                assigns output of last mechanism in the pathway list to self.output
                returns output after either one time_step or the full trial (determined by time_scale)
            - register_process(): registers process with ProcessRegistry
            [TBI: - adjust(control_signal_allocations=NotImplemented):
                modifies the control_signal_allocations while the process is executing;
                calling it without control_signal_allocations functions like interrogate
                returns (responseState, accuracy)
            [TBI: - interrogate(): returns (responseState, accuracy)
            [TBI: - terminate(): terminates the process and returns output
            [TBI: - accuracy(target):
                a function that uses target together with the pathway's output.value(s)
                and its accuracyFunction to return an accuracy measure;
                the target must be in a pathway-appropriate format (checked with call)

        ProcessRegistry
        ---------------
            All Processes are registered in ProcessRegistry, which maintains a dict for the subclass,
              a count for all instances of it, and a dictionary of those instances
    COMMENT

    Attributes
    ----------

    pathway : List[(mechanism, dict, int), (projection, LearningSignal spec, None), (mechanism, dict, int)...]
        Entries are alternating tuples specifying mechanisms and projections.  For mechanism tuples, the dict specifies
        a set of runtime parameters to use for execution of the mechanism, and the int specifies the phase at which
        the mechanism should be executed in a round of executions [LINK].  For projection tuples, the LearningSignal
        spec can be a LearningSignal projection object, the class (which specifies a default instance) or a function
        call to instantiate a LearningSignal (including parameters).  The second and third items of mechanism tuples,
        and the second item of projection tuples are optional and therefore may be ``None``.
        The third item of projection tuples is currenlty not used and is always ``None``.

        .. note::
             This is constructed from the :keyword:`PATHWAY` argument, the entries of which do not necessarily
             have to have all items in a tuple, or even be in tuple form.  All entries of the :keyword:`PATHWAY`
             argument are converted to tuples when assigned to the ``pathway`` attribute.  Entries that are
             not tuples must be a mechanism or projection.  For tuple entries, the first item must be a
             mechanism or projection;  the second is optional, and ``None`` is entered for missing values;  the third
             is optional for mechanism tuples (0 is the default) and ignored for projection tuples.

    processInputStates : Optional[List[ProcessInputState]]
        Each processInputState sends a Mapping projection to one or more inputStates of the :keyword:`ORIGIN`
        mechanism.

    input :  Optional[List[value] or ndarray]
        Value of input arg in a call to process' execute() method or run() function; assigned to process.variable.
        Each item of the input must match the format of the corresponding inputState of the :keyword:`ORIGIN` mechanism.

        .. note:: The ``input`` attribute of a process preserves its value throughout the execution of the process.
                  It's value is assigned to the `variable` attribute of the :keyword:`ORIGIN` mechanism at the start
                  of execution.  After that, by default, its `variable` attribute is zeroed. This is so that if the
                  :keyword:`ORIGIN` mechanism is executed again in the same round of execution (e.g., if it is part of
                  a recurrent loop) it does not continue to receive the Process' input.  However, this behavior can be
                  modified with the ``clamp_input`` attribute of the process.

    inputValue :  2d np.array : default ``variableInstanceDefault``
        Synonym for the ``variable`` attribute of the process, and contains the values of its ``ProcessInputStates``.

    clamp_input : Optional[keyword]
        Determines whether the process' input continues to be applied to the :keyword:`ORIGIN` mechanism
        after its initial execution.

        ``None``: Process input is used only for the first execution of the :keyword:`ORIGIN` mechanism in a round of
        execution.

        :keyword:`SOFT_CLAMP`: combines the process' input with input from any other projections to the
        :keyword:`ORIGIN` mechanism every time it is executed within a round of execution.

        :keyword:`HARD_CLAMP`: applies the process' input in place of any other sources of input to the
        :keyword:`ORIGIN` mechanism every time it is executed in a round of execution.

    value: 2d. np.array
        Value of the primary outputState of the :keyword:`TERMINAL` mechanism(s)
        (see State for an explanation of a primary state).[LINK]

    outputState : State
        Reference to the primary outputState of the :keyword:`TERMINAL` mechanism
        (see State for an explanation of a primary state).[LINK]

      .. _mech_tuples : List[MechanismTuple]
             :class:`MechanismTuple` for all mechanisms in the process, listed in the order specified in pathway.
             MechanismTuples are of the form: (mechanism, runtime_params, phase) where runtime_params is dictionary
             of {argument keyword: argument values} entries and phase is an int.
             Note:  the list includes monitoring mechanisms (used for learning).

      .. _allMechanisms : MechanismList
             Contains all mechanisms in the system (based on _mech_tuples).

      .. _origin_mech_tuples : List[MechanismTuple]
             Contains a tuple for the :keyword:`ORIGIN` mechanism of the process.

      .. _terminal_mech_tuples : List[MechanismTuple]
             Contains a tuple for the :keyword:`TERMINAL` mechanism of the process.

      .. _monitoring_mech_tuples : List[MechanismTuple]
             MechanismTuples [LINK] for all MonitoringMechanisms [LINK] in the process (used for learning)

      .. mechanisms : List[Mechanism]
             List of all mechanisms in the process.
             property that points to _allMechanisms.mechanisms (see below).

    mechanismNames : List[str]
        Names of all mechanisms in the process.

        .. property that points to _allMechanisms.names (see below).

    originMechanisms : MechanismList
        Contains :keyword:`ORIGIN` mechanism of the process.

        .. based on _origin_mech_tuples
           process.input contains the input to :keyword:`ORIGIN` mechanism.

    terminalMechanisms : MechanismList
        Contains :keyword:`TERMINAL` mechanism of the process.

        .. based on _terminal_mech_tuples
           system.ouput contains the output of :keyword:`TERMINAL` mechanism.

    monitoringMechanisms : MechanismList
        Contains all monitoring mechanisms in the process.

        .. based on _monitoring_mech_tuples

    systems : List[System]
        Systems to which the process belongs.

      .. _phaseSpecMax : int : default 0
             phase of last (set of) ProcessingMechanism(s) to be executed in the process.
             It is assigned to the ``phaseSpec`` for the mechanism in the pathway with the largest ``phaseSpec`` value.

    numPhases : int : default 1
        Number of phases for the process.
        It is assigned as ``_phaseSpecMax + 1``.

      .. _isControllerProcess : bool : False
             identifies whether the process is an internal one created by a ControlMechanism.

    learning : Optional[LearningSignal]
        Specifies whether process should be configured for learning;  value can be the name of the class, the name of
        a learningSignal object, or a call to the class.  Note that if it is an instance (or a call to create one),
        that object itself will not be used as the learningSignal for the process; rather it will be used as a template
        (including any parameters that are specified) for creating learningSignal projections for the process.

      .. _learning_enabled : bool
             indicates whether or not learning is enabled.  This only has effect if the ``learning`` parameter
             has been specified (see above).

    results : List[outputState.value]
        List of return values (outputState.value) from a sequence of executions.

    timeScale : TimeScale : default TimeScale.TRIAL
        Determines the default TimeScale value used by mechanisms in the pathway.

    name : str : default Process-[index]
        Name of the process.
        Specified in the name argument of the call to create the process;
        if not is specified, a default is assigned by ProcessRegistry
        (see :doc:`Registry` for conventions used in naming, including for default and duplicate names).[LINK]

    prefs : PreferenceSet or specification dict : Process.classPreferences
        Preference set for process.
        Specified in the prefs argument of the call to create the process;  if it is not specified, a default is
        assigned using ``classPreferences`` defined in __init__.py
        (see Description under PreferenceSet for details).[LINK]


    """

    functionCategory = kwProcessFunctionCategory
    className = functionCategory
    suffix = " " + className
    functionType = "Process"

    registry = ProcessRegistry

    classPreferenceLevel = PreferenceLevel.CATEGORY
    # These will override those specified in TypeDefaultPreferences
    # classPreferences = {
    #     kwPreferenceSetName: 'ProcessCustomClassPreferences',
    #     kpReportOutputPref: PreferenceEntry(False, PreferenceLevel.INSTANCE)}
    # Use inputValueSystemDefault as default input to process

    # # MODIFIED 10/2/16 OLD:
    # variableClassDefault = inputValueSystemDefault
    # MODIFIED 10/2/16 NEW:
    variableClassDefault = None
    # MODIFIED 10/2/16 END

    paramClassDefaults = Function.paramClassDefaults.copy()
    paramClassDefaults.update({kwTimeScale: TimeScale.TRIAL})

    default_pathway = [Mechanism_Base.defaultMechanism]

    @tc.typecheck
    def __init__(self,
                 default_input_value=None,
                 pathway=default_pathway,
                 initial_values=None,
                 clamp_input=None,
                 default_projection_matrix=DEFAULT_PROJECTION_MATRIX,
                 # learning:tc.optional(_is_projection_spec)=None,
                 learning=None,
                 target:tc.optional(is_numerical)=None,
                 params=None,
                 name=None,
                 prefs:is_pref_set=None,
                 context=None):

        # Assign args to params and functionParams dicts (kwConstants must == arg names)
        params = self._assign_args_to_param_dicts(pathway=pathway,
                                                 initial_values=initial_values,
                                                 clamp_input=clamp_input,
                                                 default_projection_matrix=default_projection_matrix,
                                                 learning=learning,
                                                 target=target,
                                                 params=params)

        self.pathway = NotImplemented
        self.input = None
        self.processInputStates = []
        self.function = self.execute
        self.targetInputStates = []
        self.systems = []
        self._phaseSpecMax = 0
        self._isControllerProcess = False

        register_category(entry=self,
                          base_class=Process_Base,
                          name=name,
                          registry=ProcessRegistry,
                          context=context)

        if not context:
            # context = self.__class__.__name__
            context = kwInit + self.name + kwSeparator + kwProcessInit

        super(Process_Base, self).__init__(variable_default=default_input_value,
                                           param_defaults=params,
                                           name=self.name,
                                           prefs=prefs,
                                           context=context)

    def _validate_variable(self, variable, context=None):
        """Convert variableClassDefault and self.variable to 2D np.array: one 1D value for each input state

        :param variable:
        :param context:
        :return:
        """

        super(Process_Base, self)._validate_variable(variable, context)

        # Force Process variable specification to be a 2D array (to accommodate multiple input states of 1st mech):
        if self.variableClassDefault:
            self.variableClassDefault = convert_to_np_array(self.variableClassDefault, 2)
        if variable:
            self.variable = convert_to_np_array(self.variable, 2)

    def _validate_params(self, request_set, target_set=NotImplemented, context=None):
        """Validate learning and initial_values args
        """

        super()._validate_params(request_set=request_set, target_set=target_set, context=context)

        # FIX:  WARN BUT SET TARGET TO self.terminal.outputState
        if self.learning:
            if self.target is None:
                raise ProcessError("Learning has been specified ({}) for {} so target must be as well".
                                   format(self.learning, self.name))

        # Note: don't confuse target_set (argument of validate_params) with self.target (process attribute for learning)
        if target_set[kwInitialValues]:
            for mech, value in target_set[kwInitialValues].items():
                if not isinstance(mech, Mechanism):
                    raise SystemError("{} (key for entry in initial_values arg for \'{}\') "
                                      "is not a Mechanism object".format(mech, self.name))

    def _instantiate_attributes_before_function(self, context=None):
        """Call methods that must be run before function method is instantiated

        Need to do this before _instantiate_function as mechanisms in pathway must be instantiated
            in order to assign input projection and self.outputState to first and last mechanisms, respectively

        :param context:
        :return:
        """
        self._instantiate_pathway(context=context)
        # super(Process_Base, self)._instantiate_function(context=context)

    def _instantiate_function(self, context=None):
        """Override Function._instantiate_function:

        This is necessary to:
        - insure there is no FUNCTION specified (not allowed for a Process object)
        - suppress validation (and attendant execution) of Process execute method (unless VALIDATE_PROCESS is set)
            since generally there is no need, as all of the mechanisms in the pathway have already been validated;
            Note: this means learning is not validated either
        """

        if self.paramsCurrent[FUNCTION] != self.execute:
            print("Process object ({0}) should not have a specification ({1}) for a {2} param;  it will be ignored").\
                format(self.name, self.paramsCurrent[FUNCTION], FUNCTION)
            self.paramsCurrent[FUNCTION] = self.execute
        # If validation pref is set, instantiate and execute the Process
        if self.prefs.paramValidationPref:
            super(Process_Base, self)._instantiate_function(context=context)
        # Otherwise, just set Process output info to the corresponding info for the last mechanism in the pathway
        else:
            self.value = self.pathway[-1][OBJECT].outputState.value

# DOCUMENTATION:
#         Uses paramClassDefaults[PATHWAY] == [Mechanism_Base.defaultMechanism] as default
#         1) ITERATE THROUGH CONFIG LIST TO PARSE AND INSTANTIATE EACH MECHANISM ITEM
#             - RAISE EXCEPTION IF TWO PROJECTIONS IN A ROW
#         2) ITERATE THROUGH CONFIG LIST AND ASSIGN PROJECTIONS (NOW THAT ALL MECHANISMS ARE INSTANTIATED)
#
#

    def _instantiate_pathway(self, context):
        # DOCUMENT:  Projections SPECIFIED IN A PATHWAY MUST BE A Mapping Projection
        # DOCUMENT:
        # Each item in Pathway can be a Mechanism or Projection object, class ref, or specification dict,
        #     str as name for a default Mechanism,
        #     keyword (IDENTITY_MATRIX or FULL_CONNECTIVITY_MATRIX) as specification for a default Projection,
        #     or a tuple with any of the above as the first item and a param dict as the second
        """Construct pathway list of Mechanisms and Projections used to execute process

        Iterate through Pathway, parsing and instantiating each Mechanism item;
            - raise exception if two Projections are found in a row;
            - for last Mechanism in Pathway, assign ouputState to Process.outputState
        Iterate through Pathway, assigning Projections to Mechanisms:
            - first Mechanism in Pathway:
                if it does NOT already have any projections:
                    assign projection(s) from ProcessInputState(s) to corresponding Mechanism.inputState(s):
                if it DOES already has a projection, and it is from:
                    (A) the current Process input, leave intact
                    (B) another Process input, if verbose warn
                    (C) another mechanism in the current process, if verbose warn about recurrence
                    (D) a mechanism not in the current Process or System, if verbose warn
                    (E) another mechanism in the current System, OK so ignore
                    (F) from something other than a mechanism in the system, so warn (irrespective of verbose)
                    (G) a Process in something other than a System, so warn (irrespective of verbose)
            - subsequent Mechanisms:
                assign projections from each Mechanism to the next one in the list:
                - if Projection is explicitly specified as item between them in the list, use that;
                - if Projection is NOT explicitly specified,
                    but the next Mechanism already has a projection from the previous one, use that;
                - otherwise, instantiate a default Mapping projection from previous mechanism to next:
                    use kwIdentity (identity matrix) if len(sender.value == len(receiver.variable)
                    use FULL_CONNECTIVITY_MATRIX (full connectivity matrix with unit weights) if the lengths are not equal
                    use FULL_CONNECTIVITY_MATRIX (full connectivity matrix with unit weights) if kwLearning has been set

        :param context:
        :return:
        """
        pathway = self.paramsCurrent[PATHWAY]
        self._mech_tuples = []
        self._monitoring__mech_tuples = []

        self._standardize_config_entries(pathway=pathway, context=context)

        # VALIDATE PATHWAY THEN PARSE AND INSTANTIATE MECHANISM ENTRIES  ------------------------------------
        self._parse_and_instantiate_mechanism_entries(pathway=pathway, context=context)

        # Identify origin and terminal mechanisms in the process and
        #    and assign the mechanism's status in the process to its entry in the mechanism's processes dict
        self.firstMechanism = pathway[0][OBJECT]
        self.firstMechanism.processes[self] = ORIGIN
        self._origin_mech_tuples = [pathway[0]]
        self.originMechanisms = MechanismList(self, self._origin_mech_tuples)

        self.lastMechanism = pathway[-1][OBJECT]
        if self.lastMechanism is self.firstMechanism:
            self.lastMechanism.processes[self] = SINGLETON
        else:
            self.lastMechanism.processes[self] = TERMINAL
        self._terminal_mech_tuples = [pathway[-1]]
        self.terminalMechanisms = MechanismList(self, self._terminal_mech_tuples)

        # # Assign process outputState to last mechanisms in pathway
        # self.outputState = self.lastMechanism.outputState

        # PARSE AND INSTANTIATE PROJECTION ENTRIES  ------------------------------------

        self._parse_and_instantiate_projection_entries(pathway=pathway, context=context)

        self.pathway = pathway

        self._instantiate__deferred_inits(context=context)

        if self.learning:
            self._check_for_comparator()
            self._instantiate_target_input()
            self._learning_enabled = True
        else:
            self._learning_enabled = False

        self._allMechanisms = MechanismList(self, self._mech_tuples)
        self.monitoringMechanisms = MechanismList(self, self._monitoring__mech_tuples)


    def _standardize_config_entries(self, pathway, context=None):

# FIX: SHOULD MOVE VALIDATION COMPONENTS BELOW TO Process._validate_params
        # Convert all entries to (item, params, phaseSpec) tuples, padded with None for absent params and/or phaseSpec
        for i in range(len(pathway)):
            config_item = pathway[i]
            if isinstance(config_item, tuple):
                if len(config_item) is 3:
                    # Check that first item is either a mechanism or projection specification
                    if not _is_mechanism_spec(config_item[0]) or _is_projection_spec(config_item[0]):
                        raise ProcessError("First item of tuple ({}) in entry {} of pathway for {}"
                                           " is neither a mechanism nor a projection specification".
                                           format(config_item[0], i, self.name))
                    # Check that second item is a dict (presumably of params)
                    if not isinstance(config_item[1], dict):
                        raise ProcessError("Second item of tuple ({}) in entry {} of pathway for {}"
                                           " must be a params dict".
                                           format(config_item[1], i, self.name))
                    # Check that third item is a int (presumably a phase spec)
                    if not isinstance(config_item[2], numbers.Number):
                        raise ProcessError("Third item of tuple ({}) in entry {} of pathway for {}"
                                           " must be a phase value".
                                           format(config_item[2], i, self.name))
                    pathway[i] = MechanismTuple(config_item[0], config_item[1], config_item[2])

                # If the tuple has only one item, check that it is a Mechanism or Projection specification
                if len(config_item) is 1:
                    if _is_mechanism_spec(config_item[0]) or _is_projection_spec(config_item[0]):
                        # Pad with None
                        pathway[i] = MechanismTuple(config_item[0],
                                                          None,
                                                          DEFAULT_PHASE_SPEC)
                    else:
                        raise ProcessError("First item of tuple ({}) in entry {} of pathway for {}"
                                           " is neither a mechanism nor a projection specification".
                                           format(config_item[0], i, self.name))
                # If the tuple has two items
                if len(config_item) is 2:
                    # Mechanism
                    #     check whether second item is a params dict or a phaseSpec
                    #     and assign it to the appropriate position in the tuple, padding other with None
                    second_tuple_item = config_item[1]
                    if _is_mechanism_spec(config_item[0]):
                        if isinstance(second_tuple_item, dict):
                            pathway[i] = MechanismTuple(config_item[0],
                                                              second_tuple_item,
                                                              DEFAULT_PHASE_SPEC)
                        # If the second item is a number, assume it is meant as a phase spec and move it to third item
                        elif isinstance(second_tuple_item, (int, float)):
                            pathway[i] = MechanismTuple(config_item[0],
                                                              None,
                                                              second_tuple_item)
                        else:
                            raise ProcessError("Second item of tuple ((}) in item {} of pathway for {}"
                                               " is neither a params dict nor phaseSpec (int or float)".
                                               format(second_tuple_item, i, self.name))
                    # Projection
                    #     check that second item is a projection spec for a LearningSignal
                    #     if so, leave it there, and pad third item with None
                    elif _is_projection_spec(config_item[0]):
                        if (_is_projection_spec(second_tuple_item) and
                                _is_projection_subclass(second_tuple_item, LEARNING_SIGNAL)):
                            pathway[i] = MechanismTuple(config_item[0],
                                                              second_tuple_item,
                                                              DEFAULT_PHASE_SPEC)
                        else:
                            raise ProcessError("Second item of tuple ({}) in item {} of pathway for {}"
                                               " should be 'LearningSignal' or absent".
                                               format(second_tuple_item, i, self.name))
                    else:
                        raise ProcessError("First item of tuple ({}) in item {} of pathway for {}"
                                           " is neither a mechanism nor a projection spec".
                                           format(config_item[0], i, self.name))
                # tuple should not have more than 3 items
                if len(config_item) > 3:
                    raise ProcessError("The tuple for item {} of pathway for {} has more than three items {}".
                                       format(i, self.name, config_item))
            else:
                # Convert item to tuple, padded with None
                if _is_mechanism_spec(pathway[i]) or _is_projection_spec(pathway[i]):
                    # Pad with None for param and DEFAULT_PHASE_SPEC for phase
                    pathway[i] = MechanismTuple(pathway[i],
                                                      None,
                                                      DEFAULT_PHASE_SPEC)
                else:
                    raise ProcessError("Item of {} of pathway for {}"
                                       " is neither a mechanism nor a projection specification".
                                       format(i, self.name))

    def _parse_and_instantiate_mechanism_entries(self, pathway, context=None):

# FIX: SHOULD MOVE VALIDATION COMPONENTS BELOW TO Process._validate_params
        # - make sure first entry is not a Projection
        # - make sure Projection entries do NOT occur back-to-back (i.e., no two in a row)
        # - instantiate Mechanism entries

        previous_item_was_projection = False

        from PsyNeuLink.Functions.Projections.Projection import Projection_Base
        for i in range(len(pathway)):
            item, params, phase_spec = pathway[i]

            # Get max phaseSpec for Mechanisms in pathway
            if not phase_spec:
                phase_spec = 0
            self._phaseSpecMax = int(max(math.floor(float(phase_spec)), self._phaseSpecMax))

            # VALIDATE PLACEMENT OF PROJECTION ENTRIES  ----------------------------------------------------------

            # Can't be first entry, and can never have two in a row

            # Config entry is a Projection
            if _is_projection_spec(item):
                # Projection not allowed as first entry
                if i==0:
                    raise ProcessError("Projection cannot be first entry in pathway ({0})".format(self.name))
                # Projections not allowed back-to-back
                if previous_item_was_projection:
                    raise ProcessError("Illegal sequence of two adjacent projections ({0}:{1} and {1}:{2})"
                                       " in pathway for {3}".
                                       format(i-1, pathway[i-1], i, pathway[i], self.name))
                previous_item_was_projection = True
                continue

            previous_item_was_projection = False
            mech = item

            # INSTANTIATE MECHANISM  -----------------------------------------------------------------------------

            # Must do this before assigning projections (below)
            # Mechanism entry must be a Mechanism object, class, specification dict, str, or (Mechanism, params) tuple
            # Don't use params item of tuple (if present) to instantiate Mechanism, as they are runtime only params

            # Entry is NOT already a Mechanism object
            if not isinstance(mech, Mechanism):
                # Note: need full pathname for mechanism factory method, as "mechanism" is used as local variable below
                mech = PsyNeuLink.Functions.Mechanisms.Mechanism.mechanism(mech, context=context)
                if not mech:
                    raise ProcessError("Entry {0} ({1}) is not a recognized form of Mechanism specification".
                                       format(i, mech))
                # Params in mech tuple must be a dict or None
                if params and not isinstance(params, dict):
                    raise ProcessError("Params entry ({0}) of tuple in item {1} of pathway for {2} is not a dict".
                                          format(params, i, self.name))
                # Replace Pathway entry with new tuple containing instantiated Mechanism object and params
                pathway[i] = MechanismTuple(mech, params, phase_spec)

            # Entry IS already a Mechanism object
            # Add entry to _mech_tuples and name to mechanismNames list
            mech.phaseSpec = phase_spec
            # Add Process to the mechanism's list of processes to which it belongs
            if not self in mech.processes:
                mech.processes[self] = INTERNAL
            self._mech_tuples.append(pathway[i])
            # self.mechanismNames.append(mech.name)

        # Validate initial values
        # FIX: CHECK WHETHER ALL MECHANISMS DESIGNATED AS INITALIZE HAVE AN INITIAL_VALUES ENTRY
        if self.initial_values:
            for mech, value in self.initial_values.items():
                if not mech in self.mechanisms:
                    raise SystemError("{} (entry in initial_values arg) is not a Mechanism in pathway for \'{}\'".
                                      format(mech.name, self.name))
                if not iscompatible(value, mech.variable):
                    raise SystemError("{} (in initial_values arg for {}) is not a valid value for {}".
                                      format(value,
                                             append_type_to_name(self),
                                             append_type_to_name(mech)))

    def _parse_and_instantiate_projection_entries(self, pathway, context=None):

        # ASSIGN DEFAULT PROJECTION PARAMS

        # If learning is specified for the Process, add to default projection params
        if self.learning:
            # FIX: IF self.learning IS AN ACTUAL LearningSignal OBJECT, NEED TO RESPECIFY AS CLASS + PARAMS
            # FIX:     OR CAN THE SAME LearningSignal OBJECT BE SHARED BY MULTIPLE PROJECTIONS?
            # FIX:     DOES IT HAVE ANY INTERNAL STATE VARIABLES OR PARAMS THAT NEED TO BE PROJECTIONS-SPECIFIC?
            # FIX:     MAKE IT A COPY?
            matrix_spec = (self.default_projection_matrix, self.learning)
        else:
            matrix_spec = self.default_projection_matrix

        projection_params = {FUNCTION_PARAMS:
                                 {MATRIX: matrix_spec}}

        for i in range(len(pathway)):
                item, params, phase_spec = pathway[i]

                #region FIRST ENTRY

                # Must be a Mechanism (enforced above)
                # Assign input(s) from Process to it if it doesn't already have any
                if i == 0:
                    # Relabel for clarity
                    mechanism = item

                    # Check if first Mechanism already has any projections and, if so, issue appropriate warning
                    if mechanism.inputState.receivesFromProjections:
                        self._issue_warning_about_existing_projections(mechanism, context)

                    # Assign input projection from Process
                    self._assign_process_input_projections(mechanism, context=context)
                    continue
                #endregion

                #region SUBSEQUENT ENTRIES

                # Item is a Mechanism
                if isinstance(item, Mechanism):

                    preceding_item = pathway[i-1][OBJECT]

                    # PRECEDING ITEM IS A PROJECTION
                    if isinstance(preceding_item, Projection):
                        if self.learning:
                            # from PsyNeuLink.Functions.Projections.LearningSignal import LearningSignal

                            # Check if preceding_item has a matrix parameterState and, if so, it has any learningSignals
                            # If it does, assign them to learning_signals
                            try:
                                # learning_signals = None
                                learning_signals = list(projection for
                                                        projection in
                                                        preceding_item.parameterStates[MATRIX].receivesFromProjections
                                                        if isinstance(projection, LearningSignal))
                                # if learning_signals:
                                #     learning_signal = learning_signals[0]
                                #     if len(learning_signals) > 1:
                                #         print("{} in {} has more than LearningSignal; only the first ({}) will be used".
                                #               format(preceding_item.name, self.name, learning_signal.name))
                                # # if (any(isinstance(projection, LearningSignal) for
                                # #         projection in preceding_item.parameterStates[MATRIX].receivesFromProjections)):

                            # preceding_item doesn't have a parameterStates attrib, so assign one with self.learning
                            except AttributeError:
                                # Instantiate parameterStates Ordered dict with ParameterState for self.learning
                                preceding_item.parameterStates = instantiate_state_list(
                                                                                owner=preceding_item,
                                                                                state_list=[(MATRIX,
                                                                                             self.learning)],
                                                                                state_type=ParameterState,
                                                                                state_param_identifier=kwParameterState,
                                                                                constraint_value=self.learning,
                                                                                constraint_value_name=LEARNING_SIGNAL,
                                                                                context=context)

                            # preceding_item has parameterStates but not (yet!) one for MATRIX, so instantiate it
                            except KeyError:
                                # Instantiate ParameterState for MATRIX
                                preceding_item.parameterStates[MATRIX] = instantiate_state(
                                                                                owner=preceding_item,
                                                                                state_type=ParameterState,
                                                                                state_name=MATRIX,
                                                                                state_spec=kwParameterState,
                                                                                state_params=self.learning,
                                                                                constraint_value=self.learning,
                                                                                constraint_value_name=LEARNING_SIGNAL,
                                                                                context=context)
                            # preceding_item has parameterState for MATRIX,
                            else:
                                # # MODIFIED 9/19/16 OLD:
                                # if learning_signals:
                                #     for learning_signal in learning_signals:
                                #         # FIX: ?? SHOULD THIS USE assign_defaults:
                                #         # Update matrix params with any specified by LearningSignal
                                #         try:
                                #             preceding_item.parameterStates[MATRIX].paramsCurrent.\
                                #                                                     update(learning_signal.user_params)
                                #             # FIX:  PROBLEM IS THAT learningSignal HAS NOT BEEN INIT'ED YET:
                                #                          # update(learning_signal.paramsCurrent['weight_change_params']
                                #         except TypeError:
                                #             pass
                                # else:
                                # MODIFIED 9/19/16 NEW:
                                if not learning_signals:
                                # MODIFIED 9/19/16 END
                                    # Add learning signal to projection
                                    _add_projection_to(preceding_item,
                                                      preceding_item.parameterStates[MATRIX],
                                                      projection_spec=self.learning)
                        continue

                    # Preceding item was a Mechanism, so check if a Projection needs to be instantiated between them
                    # Check if Mechanism already has a projection from the preceding Mechanism, by testing whether the
                    #    preceding mechanism is the sender of any projections received by the current one's inputState
    # FIX: THIS SHOULD BE DONE FOR ALL INPUTSTATES
    # FIX: POTENTIAL PROBLEM - EVC *CAN* HAVE MULTIPLE PROJECTIONS FROM (DIFFERENT outputStates OF) THE SAME MECHANISM

                    # PRECEDING ITEM IS A MECHANISM
                    projection_list = item.inputState.receivesFromProjections
                    projection_found = False
                    for projection in projection_list:
                        # Current mechanism DOES receive a projection from the preceding item
                        if preceding_item == projection.sender.owner:
                            projection_found = True
                            if self.learning:
                                # Make sure projection includes a learningSignal and add one if it doesn't
                                try:
                                    matrix_param_state = projection.parameterStates[MATRIX]

                                # projection doesn't have a parameterStates attrib, so assign one with self.learning
                                except AttributeError:
                                    # Instantiate parameterStates Ordered dict with ParameterState for self.learning
                                    projection.parameterStates = instantiate_state_list(
                                                                                owner=preceding_item,
                                                                                state_list=[(MATRIX,
                                                                                             self.learning)],
                                                                                state_type=ParameterState,
                                                                                state_param_identifier=kwParameterState,
                                                                                constraint_value=self.learning,
                                                                                constraint_value_name=LEARNING_SIGNAL,
                                                                                context=context)

                                # projection has parameterStates but not (yet!) one for MATRIX,
                                #    so instantiate it with self.learning
                                except KeyError:
                                    # Instantiate ParameterState for MATRIX
                                    projection.parameterStates[MATRIX] = instantiate_state(
                                                                                owner=preceding_item,
                                                                                state_type=ParameterState,
                                                                                state_name=MATRIX,
                                                                                state_spec=kwParameterState,
                                                                                state_params=self.learning,
                                                                                constraint_value=self.learning,
                                                                                constraint_value_name=LEARNING_SIGNAL,
                                                                                context=context)

                                # Check if projection's matrix param has a learningSignal
                                else:
                                    if not (any(isinstance(projection, LearningSignal) for
                                                projection in matrix_param_state.receivesFromProjections)):
                                        _add_projection_to(projection,
                                                          matrix_param_state,
                                                          projection_spec=self.learning)

                                if self.prefs.verbosePref:
                                    print("LearningSignal added to projection from mechanism {0} to mechanism {1} "
                                          "in pathway of {2}".format(preceding_item.name, item.name, self.name))
                            break

                    if not projection_found:
                        # No projection found, so instantiate mapping projection from preceding mech to current one;
                        # Note:  If self.learning arg is specified, it has already been added to projection_params above
                        Mapping(sender=preceding_item,
                                receiver=item,
                                params=projection_params
                                )
                        if self.prefs.verbosePref:
                            print("Mapping projection added from mechanism {0} to mechanism {1}"
                                  " in pathway of {2}".format(preceding_item.name, item.name, self.name))

                # Item is a Projection or specification for one
                else:
                    # Instantiate Projection, assigning mechanism in previous entry as sender and next one as receiver
                    # IMPLEMENTATION NOTE:  FOR NOW:
                    #    - ASSUME THAT PROJECTION SPECIFICATION (IN item) IS ONE OF THE FOLLOWING:
                    #        + Projection object
                    #        + Matrix object
                    # #        +  Matrix keyword (IDENTITY_MATRIX or FULL_CONNECTIVITY_MATRIX)
                    #        +  Matrix keyword (use "is_projection" to validate)
                    #    - params IS IGNORED
    # 9/5/16:
    # FIX: IMPLEMENT _validate_params TO VALIDATE PROJECTION SPEC USING Projection.is_projection
    # FIX: ADD SPECIFICATION OF PROJECTION BY KEYWORD:
    # FIX: ADD learningSignal spec if specified at Process level (overrided individual projection spec?)

                    # FIX: PARSE/VALIDATE ALL FORMS OF PROJECTION SPEC (ITEM PART OF TUPLE) HERE:
                    # FIX:                                                          CLASS, OBJECT, DICT, STR, TUPLE??
                    # IMPLEMENT: MOVE State.instantiate_projections_to_state(), check_projection_receiver()
                    #            and parse_projection_ref() all to Projection_Base.__init__() and call that
                    #           VALIDATION OF PROJECTION OBJECT:
                    #                MAKE SURE IT IS A Mapping PROJECTION
                    #                CHECK THAT SENDER IS pathway[i-1][OBJECT]
                    #                CHECK THAT RECEVIER IS pathway[i+1][OBJECT]

                    sender_mech=pathway[i-1][OBJECT]
                    receiver_mech=pathway[i+1][OBJECT]

                    # projection spec is an instance of a Mapping projection
                    if isinstance(item, Mapping):
                        # Check that Projection's sender and receiver are to the mech before and after it in the list
                        # IMPLEMENT: CONSIDER ADDING LEARNING TO ITS SPECIFICATION?
    # FIX: SHOULD MOVE VALIDATION COMPONENTS BELOW TO Process._validate_params

                        # MODIFIED 9/12/16 NEW:
                        # If initialization of mapping projection has been deferred,
                        #    check sender and receiver, assign them if they have not been assigned, and initialize it
                        if item.value is kwDeferredInit:
                            # Check sender arg
                            try:
                                sender_arg = item.init_args[kwSenderArg]
                            except AttributeError:
                                raise ProcessError("PROGRAM ERROR: Value of {} is {} but it does not have init_args".
                                                   format(item, kwDeferredInit))
                            except KeyError:
                                raise ProcessError("PROGRAM ERROR: Value of {} is {} "
                                                   "but init_args does not have entry for {}".
                                                   format(item.init_args[kwNameArg], kwDeferredInit, kwSenderArg))
                            else:
                                # If sender is not specified for the projection,
                                #    assign mechanism that precedes in pathway
                                if sender_arg is NotImplemented:
                                    item.init_args[kwSenderArg] = sender_mech
                                elif sender_arg is not sender_mech:
                                    raise ProcessError("Sender of projection ({}) specified in item {} of"
                                                       " pathway for {} is not the mechanism ({}) "
                                                       "that precedes it in the pathway".
                                                       format(item.init_args[kwNameArg],
                                                              i, self.name, sender_mech.name))
                            # Check receiver arg
                            try:
                                receiver_arg = item.init_args[kwReceiverArg]
                            except AttributeError:
                                raise ProcessError("PROGRAM ERROR: Value of {} is {} but it does not have init_args".
                                                   format(item, kwDeferredInit))
                            except KeyError:
                                raise ProcessError("PROGRAM ERROR: Value of {} is {} "
                                                   "but init_args does not have entry for {}".
                                                   format(item.init_args[kwNameArg], kwDeferredInit, kwReceiverArg))
                            else:
                                # If receiver is not specified for the projection,
                                #    assign mechanism that follows it in the pathway
                                if receiver_arg is NotImplemented:
                                    item.init_args[kwReceiverArg] = receiver_mech
                                elif receiver_arg is not receiver_mech:
                                    raise ProcessError("Receiver of projection ({}) specified in item {} of"
                                                       " pathway for {} is not the mechanism ({}) "
                                                       "that follows it in the pathway".
                                                       format(item.init_args[kwNameArg],
                                                              i, self.name, receiver_mech.name))

                            # Complete initialization of projection
                            item._deferred_init()
                        # MODIFIED 9/12/16 END

                        if not item.sender.owner is sender_mech:
                            raise ProcessError("Sender of projection ({}) specified in item {} of pathway for {} "
                                               "is not the mechanism ({}) that precedes it in the pathway".
                                               format(item.name, i, self.name, sender_mech.name))
                        if not item.receiver.owner is receiver_mech:
                            raise ProcessError("Receiver of projection ({}) specified in item {} of pathway for "
                                               "{} is not the mechanism ({}) that follows it in the pathway".
                                               format(item.name, i, self.name, sender_mech.name))
                        projection = item

                        # TEST
                        if params:
                            projection.matrix = params

                    # projection spec is a Mapping class reference
                    elif inspect.isclass(item) and issubclass(item, Mapping):
                        if params:
                            # Note:  If self.learning is specified, it has already been added to projection_params above
                            projection_params = params
                        projection = Mapping(sender=sender_mech,
                                             receiver=receiver_mech,
                                             params=projection_params)

                    # projection spec is a matrix specification, a keyword for one, or a (matrix, LearningSignal) tuple
                    # Note: this is tested above by call to _is_projection_spec()
                    elif (isinstance(item, (np.matrix, str, tuple) or
                              (isinstance(item, np.ndarray) and item.ndim == 2))):
                        # If a LearningSignal is explicitly specified for this projection, use it
                        if params:
                            matrix_spec = (item, params)
                        # If a LearningSignal is not specified for this projection but self.learning is, use that
                        elif self.learning:
                            matrix_spec = (item, self.learning)
                        # Otherwise, do not include any LearningSignal
                        else:
                            matrix_spec = item
                        projection = Mapping(sender=sender_mech,
                                             receiver=receiver_mech,
                                             matrix=matrix_spec)
                    else:
                        raise ProcessError("Item {0} ({1}) of pathway for {2} is not "
                                           "a valid mechanism or projection specification".format(i, item, self.name))
                    # Reassign Pathway entry
                    #    with Projection as OBJECT item and original params as PARAMS item of the tuple
                    # IMPLEMENTATION NOTE:  params is currently ignored
                    # # MODIFIED 10/16/16 OLD:
                    # pathway[i] = (projection, params)
                    # MODIFIED 10/16/16 NEW:
                    pathway[i] = MechanismTuple(projection, params, DEFAULT_PHASE_SPEC)
                    # MODIFIED 10/16/16 END

    def _issue_warning_about_existing_projections(self, mechanism, context=None):

        # Check where the projection(s) is/are from and, if verbose pref is set, issue appropriate warnings
        for projection in mechanism.inputState.receivesFromProjections:

            # Projection to first Mechanism in Pathway comes from a Process input
            if isinstance(projection.sender, ProcessInputState):
                # If it is:
                # (A) from self, ignore
                # (B) from another Process, warn if verbose pref is set
                if not projection.sender.owner is self:
                    if self.prefs.verbosePref:
                        print("WARNING: {0} in pathway for {1} already has an input from {2} "
                              "that will be used".
                              format(mechanism.name, self.name, projection.sender.owner.name))
                    return

            # (C) Projection to first Mechanism in Pathway comes from one in the Process' _mech_tuples;
            #     so warn if verbose pref is set
            if projection.sender.owner in list(item[0] for item in self._mech_tuples):
                if self.prefs.verbosePref:
                    print("WARNING: first mechanism ({0}) in pathway for {1} receives "
                          "a (recurrent) projection from another mechanism {2} in {1}".
                          format(mechanism.name, self.name, projection.sender.owner.name))

            # Projection to first Mechanism in Pathway comes from a Mechanism not in the Process;
            #    check if Process is in a System, and projection is from another Mechanism in the System
            else:
                try:
                    if (inspect.isclass(context) and issubclass(context, System)):
                        # Relabel for clarity
                        system = context
                    else:
                        system = None
                except:
                    # Process is NOT being implemented as part of a System, so projection is from elsewhere;
                    #  (D)  Issue warning if verbose
                    if self.prefs.verbosePref:
                        print("WARNING: first mechanism ({0}) in pathway for {1} receives a "
                              "projection ({2}) that is not part of {1} or the System it is in".
                              format(mechanism.name, self.name, projection.sender.owner.name))
                else:
                    # Process IS being implemented as part of a System,
                    if system:
                        # (E) Projection is from another Mechanism in the System
                        #    (most likely the last in a previous Process)
                        if mechanism in system.mechanisms:
                            pass
                        # (F) Projection is from something other than a mechanism,
                        #     so warn irrespective of verbose (since can't be a Process input
                        #     which was checked above)
                        else:
                            print("First mechanism ({0}) in pathway for {1}"
                                  " receives a projection {2} that is not in {1} "
                                  "or its System ({3}); it will be ignored and "
                                  "a projection assigned to it by {3}".
                                  format(mechanism.name,
                                         self.name,
                                         projection.sender.owner.name,
                                         context.name))
                    # Process is being implemented in something other than a System
                    #    so warn (irrespecive of verbose)
                    else:
                        print("WARNING:  Process ({0}) being instantiated in context "
                                           "({1}) other than a System ".format(self.name, context))

    def _assign_process_input_projections(self, mechanism, context=None):
        """Create projection(s) for each item in Process input to inputState(s) of the specified Mechanism

        For each item in Process input:
        - create process_input_state, as sender for Mapping Projection to the mechanism.inputState
        - create the Mapping projection (with process_input_state as sender, and mechanism as receiver)

        If len(Process.input) == len(mechanism.variable):
            - create one projection for each of the mechanism.inputState(s)
        If len(Process.input) == 1 but len(mechanism.variable) > 1:
            - create a projection for each of the mechanism.inputStates, and provide Process.input[value] to each
        If len(Process.input) > 1 but len(mechanism.variable) == 1:
            - create one projection for each Process.input[value] and assign all to mechanism.inputState
        Otherwise,  if len(Process.input) != len(mechanism.variable) and both > 1:
            - raise exception:  ambiguous mapping from Process input values to mechanism's inputStates

        :param mechanism:
        :return:
        """

        # FIX: LENGTH OF EACH PROCESS INPUT STATE SHOUD BE MATCHED TO LENGTH OF INPUT STATE FOR CORRESPONDING ORIGIN MECHANISM

        # If input was not provided, generate defaults to match format of ORIGIN mechanisms for process
        if self.variable is None:
            self.variable = []
            seen = set()
            mech_list = list(mech_tuple[OBJECT] for mech_tuple in self._mech_tuples)
            for mech in mech_list:
                # Skip repeat mechansims (don't add another element to self.variable)
                if mech in seen:
                    continue
                else:
                    seen.add(mech)
                if mech.processes[self] in {ORIGIN, SINGLETON}:
                    self.variable.extend(mech.variable)
        process_input = convert_to_np_array(self.variable,2)

        # Get number of Process inputs
        num_process_inputs = len(process_input)

        # Get number of mechanism.inputStates
        #    - assume mechanism.variable is a 2D np.array, and that
        #    - there is one inputState for each item (1D array) in mechanism.variable
        num_mechanism_input_states = len(mechanism.variable)

        # There is a mismatch between number of Process inputs and number of mechanism.inputStates:
        if num_process_inputs > 1 and num_mechanism_input_states > 1 and num_process_inputs != num_mechanism_input_states:
            raise ProcessError("Mismatch between number of input values ({0}) for {1} and "
                               "number of inputStates ({2}) for {3}".format(num_process_inputs,
                                                                            self.name,
                                                                            num_mechanism_input_states,
                                                                            mechanism.name))

        # Create input state for each item of Process input, and assign to list
        for i in range(num_process_inputs):
            process_input_state = ProcessInputState(owner=self,
                                                    variable=process_input[i],
                                                    prefs=self.prefs)
            self.processInputStates.append(process_input_state)

        from PsyNeuLink.Functions.Projections.Mapping import Mapping

        # If there is the same number of Process input values and mechanism.inputStates, assign one to each
        if num_process_inputs == num_mechanism_input_states:
            for i in range(num_mechanism_input_states):
                # Insure that each Process input value is compatible with corresponding variable of mechanism.inputState
                if not iscompatible(process_input[i], mechanism.variable[i]):
                    raise ProcessError("Input value {0} ({1}) for {2} is not compatible with "
                                       "variable for corresponding inputState of {3}".
                                       format(i, process_input[i], self.name, mechanism.name))
                # Create Mapping projection from Process input state to corresponding mechanism.inputState
                Mapping(sender=self.processInputStates[i],
                        receiver=list(mechanism.inputStates.items())[i][1],
                        name=self.name+'_Input Projection',
                        context=context)
                if self.prefs.verbosePref:
                    print("Assigned input value {0} ({1}) of {2} to corresponding inputState of {3}".
                          format(i, process_input[i], self.name, mechanism.name))

        # If the number of Process inputs and mechanism.inputStates is unequal, but only a single of one or the other:
        # - if there is a single Process input value and multiple mechanism.inputStates,
        #     instantiate a single Process input state with projections to each of the mechanism.inputStates
        # - if there are multiple Process input values and a single mechanism.inputState,
        #     instantiate multiple Process input states each with a projection to the single mechanism.inputState
        else:
            for i in range(num_mechanism_input_states):
                for j in range(num_process_inputs):
                    if not iscompatible(process_input[j], mechanism.variable[i]):
                        raise ProcessError("Input value {0} ({1}) for {2} is not compatible with "
                                           "variable ({3}) for inputState {4} of {5}".
                                           format(j, process_input[j], self.name,
                                                  mechanism.variable[i], i, mechanism.name))
                    # Create Mapping projection from Process buffer_intput_state to corresponding mechanism.inputState
                    Mapping(sender=self.processInputStates[j],
                            receiver=list(mechanism.inputStates.items())[i][1],
                            name=self.name+'_Input Projection')
                    if self.prefs.verbosePref:
                        print("Assigned input value {0} ({1}) of {2} to inputState {3} of {4}".
                              format(j, process_input[j], self.name, i, mechanism.name))

        mechanism._receivesProcessInput = True

    def _assign_input_values(self, input, context=None):
        """Validate input, assign each item (1D array) in input to corresponding process_input_state

        Returns converted version of input

        Args:
            input:

        Returns:

        """
        # Validate input
        if input is NotImplemented:
            input = self.firstMechanism.variableInstanceDefault
            if (self.prefs.verbosePref and
                    not (not context or kwFunctionInit in context)):
                print("- No input provided;  default will be used: {0}")

        else:
            # MODIFIED 8/19/16 OLD:
            # PROBLEM: IF INPUT IS ALREADY A 2D ARRAY OR A LIST OF ITEMS, COMPRESSES THEM INTO A SINGLE ITEM IN AXIS 0
            # input = convert_to_np_array(input, 2)
            # ??SOLUTION: input = atleast_1d??
            # MODIFIED 8/19/16 NEW:
            # Insure that input is a list of 1D array items, one for each processInputState
            # If input is a single number, wrap in a list
            from numpy import ndarray
            if isinstance(input, numbers.Number) or (isinstance(input, ndarray) and input.ndim == 0):
                input = [input]
            # If input is a list of numbers, wrap in an outer list (for processing below)
            if all(isinstance(i, numbers.Number) for i in input):
                input = [input]

        if len(self.processInputStates) != len(input):
            raise ProcessError("Length ({}) of input to {} does not match the number "
                               "required for the inputs of its origin mechanisms ({}) ".
                               format(len(input), self.name, len(self.processInputStates)))

        # Assign items in input to value of each process_input_state
        for i in range (len(self.processInputStates)):
            self.processInputStates[i].value = input[i]

        return input

    def _instantiate__deferred_inits(self, context=None):
        """Instantiate any objects in the Process that have deferred their initialization

        Description:
            go through _mech_tuples in reverse order of pathway since
                learning signals are processed from the output (where the training signal is provided) backwards
            exhaustively check all of components of each mechanism,
                including all projections to its inputStates and parameterStates
            initialize all items that specified deferred initialization
            construct a _monitoring__mech_tuples of mechanism tuples (mech, params, phase_spec):
                assign phase_spec for each MonitoringMechanism = self._phaseSpecMax + 1 (i.e., execute them last)
            add _monitoring__mech_tuples to the Process' _mech_tuples
            assign input projection from Process to first mechanism in _monitoring__mech_tuples

        IMPLEMENTATION NOTE: assume that the only projection to a projection is a LearningSignal

        IMPLEMENTATION NOTE: this is implemented to be fully general, but at present may be overkill
                             since the only objects that currently use deferred initialization are LearningSignals
        """

        # For each mechanism in the Process, in backwards order through its _mech_tuples
        for item in reversed(self._mech_tuples):
            mech = item[OBJECT]
            mech._deferred_init()

            # For each inputState of the mechanism
            for input_state in mech.inputStates.values():
                input_state._deferred_init()
                self._instantiate__deferred_init_projections(input_state.receivesFromProjections, context=context)

            # For each parameterState of the mechanism
            for parameter_state in mech.parameterStates.values():
                parameter_state._deferred_init()
                self._instantiate__deferred_init_projections(parameter_state.receivesFromProjections)

        # Add _monitoring__mech_tuples to _mech_tuples for execution
        if self._monitoring__mech_tuples:
            self._mech_tuples.extend(self._monitoring__mech_tuples)
            # MODIFIED 10/2/16 OLD:
            # # They have been assigned self._phaseSpecMax+1, so increment self.phaseSpeMax
            # self._phaseSpecMax = self._phaseSpecMax + 1
            # MODIFIED 10/2/16 NEW:
            # # FIX: MONITORING MECHANISMS FOR LEARNING NOW ASSIGNED _phaseSpecMax, SO LEAVE IT ALONE
            # # FIX: THIS IS SO THAT THEY WILL RUN AFTER THE LAST ProcessingMechanisms HAVE RUN
            # MODIFIED 10/2/16 END

    def _instantiate__deferred_init_projections(self, projection_list, context=None):

        # For each projection in the list
        for projection in projection_list:
            projection._deferred_init()

            # For each parameter_state of the projection
            try:
                for parameter_state in projection.parameterStates.values():
                    # Initialize each LearningSignal projection
                    for learning_signal in parameter_state.receivesFromProjections:
                        learning_signal._deferred_init(context=context)
            # Not all Projection subclasses instantiate parameterStates
            except AttributeError as e:
                if 'parameterStates' in e.args[0]:
                    pass
                else:
                    error_msg = 'Error in attempt to initialize learningSignal ({}) for {}: \"{}\"'.\
                        format(learning_signal.name, projection.name, e.args[0])
                    raise ProcessError(error_msg)

            # Check if projection has monitoringMechanism attribute
            try:
                monitoring_mechanism = projection.monitoringMechanism
            except AttributeError:
                pass
            else:
                # If a *new* monitoringMechanism has been assigned, pack in tuple and assign to _monitoring__mech_tuples
                if monitoring_mechanism and not any(monitoring_mechanism is mech_tuple.mechanism for
                                                    mech_tuple in self._monitoring__mech_tuples):
                    # # MODIFIED 10/2/16 OLD:
                    # monitoring_mech_tuple = (monitoring_mechanism, None, self._phaseSpecMax+1)
                    # # MODIFIED 10/2/16 NEW:
                    # mech_tuple = (monitoring_mechanism, None, self._phaseSpecMax)
                    # MODIFIED 10/16/16 NEWER:
                    monitoring_mech_tuple = MechanismTuple(monitoring_mechanism, None, self._phaseSpecMax+1)
                    # MODIFIED 10/2/16 END
                    self._monitoring__mech_tuples.append(monitoring_mech_tuple)

    def _check_for_comparator(self):
        """Check for and assign comparator mechanism to use for reporting error during learning.

         This should only be called if self.learning is specified
         Check that there is one and only one Comparator for the process
         Assign comparator to self.comparator, assign self to comparator.processes, and report assignment if verbose
        """

        if not self.learning:
            raise ProcessError("PROGRAM ERROR: _check_for_comparator should only be called"
                               " for a process if it has a learning specification")

        comparators = list(mech_tuple.mechanism
                           for mech_tuple in self._mech_tuples if isinstance(mech_tuple.mechanism, Comparator))

        if not comparators:
            raise ProcessError("PROGRAM ERROR: {} has a learning specification ({}) "
                               "but no Comparator mechanism".format(self.name, self.learning))

        elif len(comparators) > 1:
            comparator_names = list(comparator.name for comparator in comparators)
            raise ProcessError("PROGRAM ERROR: {} has more than one comparator mechanism: {}".
                               format(self.name, comparator_names))

        else:
            self.comparator = comparators[0]
            self.comparator.processes[self] = COMPARATOR
            if self.prefs.verbosePref:
                print("\'{}\' assigned as Comparator for output of \'{}\'".format(self.comparator.name, self.name))

    def _instantiate_target_input(self):

        # # MODIFIED 9/20/16 OLD:
        # target = self.target
        # MODIFIED 9/20/16 NEW:
        target = np.atleast_1d(self.target)
        # MODIFIED 9/20/16 END

        # Create ProcessInputState for target and assign to comparator's target inputState
        comparator_target = self.comparator.inputStates[COMPARATOR_TARGET]

        # Check that length of process' target input matches length of comparator's target input
        if len(target) != len(comparator_target.variable):
            raise ProcessError("Length of target ({}) does not match length of input for comparator in {}".
                               format(len(target), len(comparator_target.variable)))

        target_input_state = ProcessInputState(owner=self,
                                                variable=target,
                                                prefs=self.prefs,
                                                name=COMPARATOR_TARGET)
        self.targetInputStates.append(target_input_state)

        # Add Mapping projection from target_input_state to MonitoringMechanism's target inputState
        from PsyNeuLink.Functions.Projections.Mapping import Mapping
        Mapping(sender=target_input_state,
                receiver=comparator_target,
                name=self.name+'_Input Projection to '+comparator_target.name)

    def initialize(self):
        # FIX:  INITIALIZE PROCESS INPUTS??
        for mech, value in self.initial_values.items():
            mech.initialize(value)

    def execute(self,
                input=NotImplemented,
                # params=None,
                target=None,
                time_scale=None,
                runtime_params=NotImplemented,
                context=None
                ):
        """Coordinate execution of mechanisms in project list (self.pathway)

        First check that input is provided (required).
        Then go through mechanisms in pathway list, and execute each one in the order they appear in the list.

        Arguments
        ---------

        input : List[value] or ndarray: default input to process
            must be consistent with input of the first mechanism in the process' ``pathway``

        time_scale : TimeScale :  default TimeScale.TRIAL
            determines whether mechanisms are executed for a single time step or a trial

        params : Dict[param keyword, param value] :  default None
            dictionary that can include any of the parameters used as arguments to instantiate the object.
            Use parameter's name as the keyword for its entry; values will override current parameter values
            only for the current execution.

        context : str : default kwExecuting + self.name
            string used for contextualization of instantiation, hierarchical calls, executions, etc.

        Returns
        -------

        output of process : ndarray
            output of last mechanism in pathway

        .. IMPLEMENTATION NOTE:
             Still need to:
             * coordinate execution of multiple processes (in particular, mechanisms that appear in more than one process)
             * deal with different time scales

        """

        if not context:
            context = kwExecuting + self.name

        # Report output if reporting preference is on and this is not an initialization run
        report_output = self.prefs.reportOutputPref and context and kwExecuting in context


        # FIX: CONSOLIDATE/REARRANGE _assign_input_values, _check_args, AND ASIGNMENT OF input TO self.variable
        # FIX: (SO THAT assign_input_value DOESN'T HAVE TO RETURN input

        self.input = self._assign_input_values(input=input, context=context)

        self._check_args(self.input,runtime_params)

        self.timeScale = time_scale or TimeScale.TRIAL

        # Use Process self.input as input to first Mechanism in Pathway
        self.variable = self.input

        # If target was not provided to execute, use value provided on instantiation
        if not target is None:
            self.target = target

        # Generate header and report input
        if report_output:
            self._report_process_initiation(separator=True)

        # Execute each Mechanism in the pathway, in the order listed
        for i in range(len(self._mech_tuples)):
            mechanism, params, phase_spec = self._mech_tuples[i]

            # FIX:  DOES THIS BELONG HERE OR IN SYSTEM?
            # CentralClock.time_step = i

            # Note:  DON'T include input arg, as that will be resolved by mechanism from its sender projections
            mechanism.execute(time_scale=self.timeScale,
                              runtime_params=params,
                              context=context)
            if report_output:
                # FIX: USE clamp_input OPTION HERE, AND ADD HARD_CLAMP AND SOFT_CLAMP
                self._report_mechanism_execution(mechanism)

            if not i and not self.clamp_input:
                # Zero self.input to first mechanism after first run
                #     in case it is repeated in the pathway or receives a recurrent projection
                self.variable = self.variable * 0
            i += 1

        # Execute learningSignals
        if self._learning_enabled:
            self._execute_learning(context=context)

        if report_output:
            self._report_process_completion(separator=True)

        # FIX:  SHOULD THIS BE JUST THE VALUE OF THE PRIMARY OUTPUTSTATE, OR OF ALL OF THEM?
        return self.outputState.value

    def _execute_learning(self, context=None):
        """ Update each LearningSignal for mechanisms in _mech_tuples of process

        Begin with projection(s) to last Mechanism in _mech_tuples, and work backwards

        """
        for item in reversed(self._mech_tuples):
            mech = item.mechanism
            params = item.params

            # For each inputState of the mechanism
            for input_state in mech.inputStates.values():
                # For each projection in the list
                for projection in input_state.receivesFromProjections:
                    # For each parameter_state of the projection
                    try:
                        for parameter_state in projection.parameterStates.values():
                            # Call parameter_state.update with kwLearning in context to update LearningSignals
                            # Note: do this rather just calling LearningSignals directly
                            #       since parameter_state.update() handles parsing of LearningSignal-specific params
                            context = context + kwSeparatorBar + kwLearning
                            parameter_state.update(params=params, time_scale=TimeScale.TRIAL, context=context)

                    # Not all Projection subclasses instantiate parameterStates
                    except AttributeError as e:
                        pass

    def run(self,
            inputs,
            num_executions=None,
            reset_clock=True,
            initialize=False,
            targets=None,
            learning=None,
            call_before_trial=None,
            call_after_trial=None,
            call_before_time_step=None,
            call_after_time_step=None,
            time_scale=None):
        """Run a sequence of executions

        Call execute method for each execution in a sequence specified by inputs.  See ``run`` function [LINK] for
        details of formatting input specifications.

        Arguments
        ---------

        inputs : List[input] or ndarray(input) : default default_input_value for a single execution
            input for each in a sequence of executions (see ``run`` function [LINK] for detailed
            description of formatting requirements and options).

        reset_clock : bool : default True
            reset ``CentralClock`` to 0 before a sequence of executions.

        initialize : bool default False
            calls the ``initialize`` method of the process before a sequence of executions.

        targets : List[input] or np.ndarray(input) : default ``None``
            target values for monitoring mechanisms for each execution (used for learning).  The length (of the
            outermost level if a nested list, or lowest axis if an ndarray) must be equal to that of inputs.

        learning : bool :  default ``None``
            enables or disables learning during execution.
            If it is not specified, current state is left intact.
            If True, learning is forced on; if False, learning is forced off.

        call_before_trial : Function : default= ``None``
            called before each trial in the sequence is executed.

        call_after_trial : Function : default= ``None``
            called after each trial in the sequence is executed.

        call_before_time_step : Function : default= ``None``
            called before each time_step of each trial is executed.

        call_after_time_step : Function : default= ``None``
            called after each time_step of each trial is executed.

        time_scale : TimeScale :  default TimeScale.TRIAL
            determines whether mechanisms are executed for a single time step or a trial.

        Returns
        -------

        <process>.results : List[outputState.value]
            list of the value of the outputState for each :keyword:`TERMINAL` mechanism of the system returned for
            each execution.

        """
        from PsyNeuLink.Globals.Run import run
        return run(self,
                   inputs=inputs,
                   num_executions=num_executions,
                   reset_clock=reset_clock,
                   initialize=initialize,
                   targets=targets,
                   learning=learning,
                   call_before_trial=call_before_trial,
                   call_after_trial=call_after_trial,
                   call_before_time_step=call_before_time_step,
                   call_after_time_step=call_after_time_step,
                   time_scale=time_scale)
    def _report_process_initiation(self, separator=False):
        if separator:
            print("\n\n****************************************\n")

        print("\n\'{}' executing with:\n- pathway: [{}]".
              format(append_type_to_name(self),
                     re.sub('[\[,\],\n]','',str(self.mechanismNames))))
        print("- input: {1}".format(self, re.sub('[\[,\],\n]','',str(self.variable))))

    def _report_mechanism_execution(self, mechanism):
        # DEPRECATED: Reporting of mechanism execution relegated to individual mechanism prefs
        pass
        # print("\n{0} executed {1}:\n- output: {2}\n\n--------------------------------------".
        #       format(self.name,
        #              mechanism.name,
        #              re.sub('[\[,\],\n]','',
        #                     str(mechanism.outputState.value))))

    def _report_process_completion(self, separator=False):

        print("\n\'{}' completed:\n- output: {}".
              format(append_type_to_name(self),
                     re.sub('[\[,\],\n]','',str(self.outputState.value))))

        if self.learning:
            print("\n- MSE: {}".
                  format(self.comparator.outputValue[ComparatorOutput.COMPARISON_MSE.value]))

        elif separator:
            print("\n\n****************************************\n")

    @property
    def mechanisms(self):
        return self._allMechanisms.mechanisms

    @property
    def mechanismNames(self):
        return self._allMechanisms.names

    @property
    def variableInstanceDefault(self):
        return self._variableInstanceDefault

    @variableInstanceDefault.setter
    def variableInstanceDefault(self, value):
        assigned = -1
        try:
            value
        except ValueError as e:
            pass
        self._variableInstanceDefault = value

    @property
    def inputValue(self):
        return self.variable

    # @property
    # def input(self):
    #     # input = self._input or np.array(list(item.value for item in self.processInputStates))
    #     # return input
    #     try:
    #         return self._input
    #     except AttributeError:
    #         return None
    #
    # @input.setter
    # def input(self, value):
    #     self._input = value

    @property
    def outputState(self):
        return self.lastMechanism.outputState

    @property
    def output(self):
        # FIX: THESE NEED TO BE PROPERLY MAPPED
        return np.array(list(item.value for item in self.lastMechanism.outputStates.values()))

    @property
    def numPhases(self):
        return self._phaseSpecMax + 1

class ProcessInputState(OutputState):
    """Encodes input to the process and transmits it to the :keyword:`ORIGIN` mechanism in the process

    Each instance encodes an item of the input to the process (a 1d array in the 2d input array) and provides it to a
    Mapping projection that projects to one or more inputStates of the :keyword:`ORIGIN` mechanism in the process.

    (See Process input and output [LINK] for an explantion of the mapping from processInputStates to :keyword:`ORIGIN`
    mechanism inputStates when there is more than one process input value and/or mechanism inputState)

    .. Declared as a sublcass of OutputState so that it is recognized as a legitimate sender to a Projection
       in Projection._instantiate_sender()

       self.value is used to represent the corresponding element of the input arg to process.execute or run(process)

    """
    def __init__(self, owner=None, variable=NotImplemented, name=None, prefs=None):
        """Pass variable to mapping projection from Process to first Mechanism in Pathway

        :param variable:
        """
        if not name:
            self.name = owner.name + "_" + kwProcessInputState
        else:
            self.name = owner.name + "_" + name
        self.prefs = prefs
        self.sendsToProjections = []
        self.owner = owner
        self.value = variable


ProcessTuple = namedtuple('ProcessTuple', 'process, input')


class ProcessList(UserList):
    """Provides access to items in (process, process_input) tuples in a list of ProcessTuples
    """

    def __init__(self, owner, tuples_list:list):
        super().__init__()
        self.owner = owner
        for item in tuples_list:
            if not isinstance(item, ProcessTuple):
                raise ProcessError("{} in the tuples_list arg of ProcessList() is not a ProcessTuple".format(item))
        self.process_tuples = tuples_list

    def __getitem__(self, item):
        # return list(self.process_tuples[item])[PROCESS]
        return self.process_tuples[item].process


    def __setitem__(self, key, value):
        raise ("MyList is read only ")

    def __len__(self):
        return (len(self.process_tuples))

    def _get_tuple_for_process(self, process):
        """Return first process tuple containing specified process from list of process_tuples
        """
        # FIX:
        # if list(item[MECHANISM] for item in self.mech_tuples).count(mech):
        #     if self.owner.verbosePref:
        #         print("PROGRAM ERROR:  {} found in more than one mech_tuple in {} in {}".
        #               format(append_type_to_name(mech), self.__class__.__name__, self.owner.name))
        return next((ProcessTuple for ProcessTuple in self.process_tuples if ProcessTuple.process is process), None)

    @property
    def process_tuples_sorted(self):
        """Return list of mech_tuples sorted by mechanism name"""
        return sorted(self.process_tuples, key=lambda process_tuple: process_tuple[0].name)

    @property
    def processes(self):
        """Return list of all processes in ProcessList
        """
        # MODIFIED 11/1/16 OLD:
        return list(item.process for item in self.process_tuples)
        # # MODIFIED 11/1/16 NEW:
        # return sorted(list(item.process for item in self.process_tuples), key=lambda process: process.name)
        # MODIFIED 11/1/16 END

    @property
    def processNames(self):
        """Return names of all processes in ProcessList
        """
        # MODIFIED 11/1/16 OLD:
        return list(item.process.name for item in self.process_tuples)
        # # MODIFIED 11/1/16 NEW:
        # return sorted(list(item.process.name for item in self.process_tuples))
        # MODIFIED 11/1/16 END

    @property
    def _mech_tuples(self):
        return self.__mech_tuples__

    @_mech_tuples.setter
    def _mech_tuples(self, value):
        self.__mech_tuples__ = value