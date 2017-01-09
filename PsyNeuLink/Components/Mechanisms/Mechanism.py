# Princeton University licenses this file to You under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may obtain a copy of the License at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


# ****************************************  MECHANISM MODULE ***********************************************************

"""
..
    * :ref:`Mechanism_Overview`
    * :ref:`Mechanism_Creation`
    * :ref:`Mechanism_Structure`
     * :ref:`Mechanism_Function`
     * :ref:`Mechanism_States`
        * :ref:`Mechanism_InputStates`
        * :ref:`Mechanism_ParameterStates`
        * :ref:`Mechanism_OutputStates`
     * :ref:`Mechanism_Specifying_Parameters`
     * :ref:`Mechanism_Role_In_Processes_And_Systems`
    * :ref:`Mechanism_Execution`
     * :ref:`Mechanism_Runtime_Parameters`
    * :ref:`Mechanism_Class_Reference`


.. _Mechanism_Overview:

Overview
--------

Mechanisms are a core object type in PsyNeuLink.  A mechanism takes an input, transforms it in some way, and provides
it as an output that can be used for some purpose  There are three types of mechanisms that serve different purposes:

    * **ProcessingMechanisms** aggregrate the input they receive from other mechanisms in a process or system,
      and/or the input to a process or system, transform it in some way, and provide the result either as input for
      other mechanisms and/or the output of a
      process or system.
    ..
    * **MonitoringMechanisms** monitor the output of one or more other mechanisms, receive training (target) values,
      and compare these to generate error signals used for learning (see :doc:`Learning`).
    ..
    * **ControlMechanisms** evaluate the output of one or more other mechanisms, and use this to modify the
      parameters of those or other mechanisms.

..
    * :doc:`ProcessingMechanism`
        aggregrate the input they receive from other mechanisms in a process or system, and/or the input to a process or
        system, transform it in some way, and provide the result either as input for other mechanisms and/or the
        output of a process or system.

    * :doc:`MonitoringMechanism`
        monitor the output of one or more other mechanisms, receive training (target) values, and compare these to
        generate error signals used for learning (see :doc:`Learning`).

    * :doc:`ControlMechanism`
        evaluate the output of one or more other mechanisms, and use this to modify the parameters of those or other
        mechanisms.

A mechanism is made up of two fundamental components: the function it uses to transform its input; and the states it
uses to represent its input, function parameters, and output

.. _Mechanism_Creation:

Creating a Mechanism
--------------------

Mechanisms can be created in several ways.  The simplest is to use the standard Python method of calling the
constructor for the desired type of mechanism.  In addition, PsyNeuLink provides a
:py:func:`mechanism <Mechanism.mechanism>` function that can be used to instantiate a specified type of mechanism or
a default mechanism. Mechanisms can also be specified "in context," for example in the
:py:data:`pathway <Process.Process_Base.pathway>` attribute of a process.  This can be done in either of the ways
mentioned above, or one of the following ways:

  * name of an **existing mechanism**;
  ..
  * name of a **mechanism type** (subclass);
  ..
  * **specification dictionary** -- this can contain an entry specifying the type of mechanism,
    and/or entries specifiying the value of parameters used to instantiate it.
    These should take the following form:

      * :keyword:`MECHANISM_TYPE`: <name of a mechanism type>

          if this entry is absent, a :ref:`default mechanism <LINK> will be created.

      * <name of argument>:<value>

          this can contain any of the standard parameters for instantiating a mechanism
          (see :ref:`Mechanism_Specifying_Parameters`) or ones specific to a particular type of mechanism
          (see documentation for subclass).  Note that parameter values in the specification dict
          will be used to instantiate the mechanism.  These can be overridden during execution
          by specifying :ref:`Mechanism_Runtime_Parameters`, either when calling the
          :py:meth:`execute <Mechanism_Base.execute>` method for the mechanism, or where it is specified in the
          :py:data:`pathway <Process.Process_Base.pathway>` attribute of a :doc:`Process`.

  * **automatically** -- PsyNeuLink automatically creates one or more mechanisms under some circumstances.
    For example, :class:`MonitoringMechanisms` (and associated :class:`LearningProjection`) will be created
    automtically when :ref:`Process_Learning` is specified for a process.

Every mechanism has one or more :doc:`inputStates <InputState>`, :doc:`parameterStates <ParameterState>`, and
:doc:`outputStates <OutputStates>`, that allow it to receive and send projections, and to execute its ``function``
(see :ref:`Mechanism_Function`) --  these are summarized below under :ref:`Mechanism_States`.  When a mechanism is
created, it automatically creates the parameterStates it needs to represent its parameters, including those of its
``function``.  It also creates any inputStates and outputStates required for the projections it has been assigned.
However, inputStates and outputStates, and corresponding projections, can also be specified in the mechanism's
parameter dictionary, using entries with the keys :keyword:`INPUT_STATES` and :keyword:`OUTPUT_STATES``, respectively.
The value of each entry can be the name of the state's class (to create a default), an existing state,
a specification dictionary for one, a value (used as the state's ``variable``) or a list containing of any of these
to create multiple states (see :ref:`InputStates <InputState_Creation>` and :ref:`OutputStates <OutputStates_Creation>`
for details).

COMMENT:
    PUT EXAMPLE HERE
COMMENT

.. _Mechanism_Structure:

Structure
--------

.. _Mechanism_Function:

Function
~~~~~~~~

The core of every mechanism is its function, which transforms its input and generates its output.  The function is
specified by the mechanism's ``function`` parameter.  Each type of mechanism specifies one or more functions to use,
and generally these are from the :doc:`Function` class provided by PsyNeuLink.  Components are specified
in the same form that an object is instantiated in Python (by calling its constructor), and thus can be used to
specify its parameters.  For example, for a TransferMechanism, if the Logistic function is selected, then its gain
and bias parameters can also be specified as shown in the following example::

    my_mechanism = TransferMechanism(function=Logistic(gain=1.0, bias=-4))

COMMENT:
    NOT CURRENTLY IMPLEMENTED
While every mechanism type offers a standard set of functions, a custom function can also be specified.  Custom
functions can be any Python function, including an inline (lambda) function, so long as it generates a result
with a type that is consistent with the type expected by the mechanism (see :doc:`Function`;  also see
:ref:'Mechanism_Specifying_Parameters` below).
COMMENT

The input to a mechanism's ``function`` comes from the mechanism's ``variable`` attribute, which is a 2d array that
has one item for each of the mechanism's inputStates.  The result of the ``function`` is placed in the mechanism's
``value`` attribute, which is also a 2d array that may have one or more items.  This is used by the mechanism's
outputStates to generate their ``value`` attributes, each of which is assigned as an item in the mechanism's
:py:data:`outputValue <Mechanism_Base.outputValue>` attribute.

.. note::
   The input to a mechanism is not necessarily the same as the input to its ``function`` (i.e., its ``variable``
   attribute): the mechanism's input is processed by its inputState(s) before being submitted to its function
   (see :ref:`InputStates <Mechanism_InputStates>`).  Similarly, the result of a mechanism's function (i.e.,
   its ``value`` attribute)  is not necessarily the same as the mechanism's output:  the result of the ``function``
   is processed by the mechanism's outputstate(s), which is then assigned to the mechanism's :py:data:`outputValue
   <Mechanism_Base.outputValue>` attribute (see :ref:`OutputStates <Mechanism_OutputStates>`)

.. _Mechanism_States:

States
~~~~~~

Every mechanism has three types of states (shown schematically in the figure below):

.. figure:: _static/Mechanism_states_fig.*
   :alt: Mechanism States
   :scale: 75 %
   :align: center

   Schematic of a mechanism showing its three types of states (input, parameter and output).

.. _Mechanism_InputStates:

InputStates
^^^^^^^^^^^

These receive and represent the input to a mechanism. A mechanism usually has only one (**primary**) inputState, kept
in  its :py:data:`inputStates, <Mechanism_Base.inputStates>` attribute.  However some mechanisms have more than one.
For example, a :doc:`ComparatorMechanism` has one inputState for its ``sample`` and another for its ``target`` input.
If a mechanism has more than one inputState, they are kept in an OrderedDict in the mechanism's
:py:data:`inputStates <Mechanism_Base.inputStates>` attribute (note the plural).

COMMENT:
[TBI:]
If the inputState are created automatically, or are not assigned a name when specified, then each is named
using the following template: ???XXXX
COMMENT

Each inputState of a mechanism can receive one or more projections from other mechanisms.  If the mechanism is an
:keyword:`ORIGIN` mechanism of a process, it also receives a projection from the
:ref:`ProcessInputState <Process_Input_And_Ouput>` for that process. Each inputState's ``function`` aggregates the
values received from its projections (usually by summing them), and assigns the result to its ``value`` attribute.

.. _Mechanism_Variable:

The value of each inputState for the mechanism is assigned as the value of an item of the mechanism's ``variable``
attribute (a 2d np.array), as well as in a corresponding item of its :py:data:`inputValue <Mechanism_Base.inputValue>`
attribute (a list).  The ``variable`` provides the input to the mechanism's ``function``.

COMMENT:
Therefore, the number of inputStates for the mechanism must match the number of tems specified for the mechanism's
``variable`` (that is, its size along its first dimension, axis 0).  An exception is if the mechanism's ``variable``
has more than one item, but only a single inputState;  in that case, the ``value`` of that inputState must have the
same number of items as the mechanisms's ``variable``.
COMMENT

.. _Mechanism_ParameterStates:

ParameterStates
^^^^^^^^^^^^^^^

These represent the parameters of a mechanism's function, and are used to control the parameters of its ``function``.
PsyNeuLink assigns one parameterState for each parameter of the mechanism's ``function`` (which correspond to the
arguments in its constructor method). Like other states, parameterStates can receive projections. Typically these are
from the :doc:`ControlProjections <ControlProjection>` of a :doc:`ControlMechanism<ControlMechanism>`, that is used to
modify the function's parameter value in response to the outcome(s) of processing.  See
:ref:`ParameterState_Specifying_Parameters` for details of specifying the parameter values of a mechanism's ``function``.

.. _Mechanism_OutputStates:

OutputStates
^^^^^^^^^^^^
These represent the output(s) of a mechanism. A mechanism can have several outputStates, and each can serve as a
sender for projections, to transmit  its value to other  mechanisms and/or the output of a process or system.
Similar to inputStates, the ** *primary* (first or only) outputState** is assigned to the mechanism's ``outputState``
attribute, while all of its outputStates (including the primary one) are stored in an OrderedDict in its
:py:data:`outputStates <Mechanism_Base.outputStates>` attribute (note the plural);  the key for each entry is the name
of an outputState, and the value is the outputState itself.  Every mechanism has at least one ("primary")
outputState, the ``value`` of which is assigned an unmodified copy of the first item of the owner mechanism's
``value`` (usually the direct output of the mechanism's ``function``).  Other outputStates may be used for other
purposes.  For example, some Processing mechanisms (such as the :doc:`TransferMechanism`) use outputStates to
represent values derived from its primary output (e.g., its mean and variance).  :doc:`ControlMechanisms` assign one
outputState for each of their :doc:`ControlProjections  <ControlProjection>`.  The item of the mechanism's ``value``
to which an outputState is assigned can be specified using its ``INDEX`` parameter, and the function used to convert
that item into the outputState's ``value`` can be customized using its ``CALCULATE`` parameter (see
:ref:`OutputStates_Creation`). The ``value`` attributes of all of a mechanism's outputStates  are assigned to the
mechanism's :py:data:`outputValue <Mechanism_Base.outputValue>` attribute (a list), in the same order in which they
appear in the :py:data:`outputStates <Mechanism_Base.outputStates>`  attribute.  Note that this is distinct from the
mechanism's ``value`` attribute, which contains the full and unmodified results of its execution.

.. _Mechanism_Specifying_Parameters:

Specifying Mechanism Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a mechanism is created, its parameters can be specified either as arguments (where supported) or as entries
in a specification dictionary.  The entries can contain any of the following, where appropriate to a given
mechanism subclass, as well as those specific to a particular subclass (documented in each subclass):

    * :keyword:`INPUT_STATES` : Dict[str, InputState] -
      used to specify specialized inputStates required by a mechanism subclass
      (see :ref:`inputState specification <InputState_Creation>` for details of specification).
    ..
    * :keyword:`FUNCTION` : function or method :  default method implemented by subclass -
      specifies the function for the mechanism;  can be one implemented by the subclass or a custom function.
    ..
    * :keyword:`FUNCTION_PARAMS` : Dict[str, value] -
      dictionary of parameters for the mechanism's function.
      The key of each entry must be the name of the  parameter.
      The value of each entry can be one of the following (see :ref:`ParameterState_Specifying_Parameters` for details):

      * the value of the parameter itself;
      * a parameter state, the value of which specifies the parameter's value (see :ref:`ParameterState_Creation`);
      * a :ref:`ControlProjection or LearningProjection specification <Projection_In_Context_Specification>`,
        that assigns the parameter its default value, and a projection to it's parameterState of the specified type;
      * a tuple with exactly two items: the parameter value and a projection type specifying either a
        :doc:`ControlProjection` or a :doc:`LearningProjection`
        (a :any:`ParamValueProjection` namedtuple can be used for clarity).
      ..
      .. note::
         Many subclasses include the function parameters as arguments in the call to the mechanism subclass,
         (i.e., used to create the mechanism); any values specified in the :keyword:`FUNCTION__PARAMS` entry
         of the mechanism's params dict take precedence over values specified in such arguments.

    * :keyword:`OUTPUT_STATES` : Dict[str, OutputState] -
      used to specify specialized outputStates required by a mechanism subclass
      (see :ref:`OutputStates_Creation` for details of specification).
    ..
    * :keyword:`MONITOR_FOR_CONTROL` : List[OutputState] -
      used to specify mechanisms or specific outputStates to be monitored by a ControlMechanism
      (see :ref:`specifying monitored outputStates <ControlMechanism_Monitored_OutputStates>`
      for details of specification).
    ..
    * :keyword:`MONITOR_FOR_LEARNING` : List[OutputState] -
      used to specify outputStates to be used by a MonitoringMechanism for learning
      (see :ref:`MonitoringMechanisms_Monitored_For_Learning` for details of specification).

COMMENT:
    FOR DEVELOPERS:
    + FUNCTION : function or method :  method used to transform mechanism input to its output;
        This must be implemented by the subclass, or an exception will be raised;
        each item in the variable of this method must be compatible with a corresponding inputState;
        each item in the output of this method must be compatible  with the corresponding OutputState;
        for any parameter of the method that has been assigned a ParameterState,
        the output of the parameter state's own execute method must be compatible with
        the value of the parameter with the same name in params[FUNCTION_PARAMS] (EMP)
    + FUNCTION_PARAMS (dict):
        NOTE: function parameters can be specified either as arguments in the mechanism's __init__ method
        (** EXAMPLE ??), or by assignment of the function_params attribute for paramClassDefaults (** EXMAMPLE ??).
        Only one of these methods should be used, and should be chosen using the following principle:
        - if the mechanism implements one function, then its parameters should be provided as arguments in the __init__
        - if the mechanism implements several possible functions and they do not ALL share the SAME parameters,
            then the function should be provided as an argument but not they parameters; they should be specified
            as arguments in the specification of the function
        each parameter is instantiated as a ParameterState
        that will be placed in <mechanism>.parameterStates;  each parameter is also referenced in
        the <mechanism>.function_params dict, and assigned its own attribute (<mechanism>.<param>).
COMMENT

.. _Mechanism_Role_In_Processes_And_Systems:

Role in Processes and Systems
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mechanisms that are part of a process and/or system are assigned designations that indicate the role they play.  These
are listed in the mechanism's :py:data:`processes <>` and py:data:`systems` attributes, respectively

(see Process
:ref:`Process_Mechanisms` and System :ref:`System_Mechanisms` for designation labels and their meanings).
Any mechanism designated as :keyword:`ORIGIN` receives a projection to its primary inputState from the process(es)
to which it belongs.  Accordingly, when the process (or system of which the process is a part) is executed, those
mechainsms receive the input provided to the process (or system).  Note that a mechanism can be the :keyword:`ORIGIN`
of a process but not of a system to which that process belongs (see the note under System :ref:`System_Mechanisms` for
further explanation).  The output value of any mechanism designated as :keyword:`TERMINAL` is assigned to the output
of any process or system to which it belongs.


.. _Mechanism_Execution:

Execution
---------

A mechanism can be executed using its :py:data:`execute <Mechanism_Base.execute>` and
:py:data:`run <Mechanism_Base.run>` methods.  This can be useful in testing a mechanism and/or debugging.  However,
more typically, mechanisms are executed as part of a process or system (see Process :ref:`Process_Execution` and
System :ref:`System_Execution` for more details).  For either of these, the mechanism must be included in the
:py:data:`pathway <Process.Process_Base.pathway>` of a process.  There, it can be specified on its own, or as the
first item of a tuple that also has an optional set of runtime parameters (see below), and/or a phase specification
for use when executed in a system (see System :ref:`System_Phase` for an explanation of phases; and see Process
:ref:`Process_Mechanisms` for additional details about specifying a mechanism in a process
py:data:`pathway <Process.Process_Base.pathway>`).

.. note::
   Mechanisms cannot be specified directly in a system.  They must be specified in the
   py:data:`pathway <Process.Process_Base.pathway>` of a process,
   and then that process must be included in the ``processes`` argument for the system.

.. _Mechanism_Runtime_Parameters:

Runtime Parameters
~~~~~~~~~~~~~~~~~~

The parameters of a mechanism are usually specified when the mechanism is created.  However, these can be overridden
when it executed.  This can be done by using the ``runtime_param`` argument of its
:py:data:`execute <Mechanism_Base.execute>` method, or by specifying the runtime parameters in a tuple with the
mechanism in the :py:data:`pathway <Process.Process_Base.pathway>` of a process (see Process
:ref:`Process_Mechanisms`). In either case, runtime parameters  are specified using a dictionary that
contains one or more entries, each of which itself contains a dictionary corresponding to the mechanism's states
(inputStates, parameterStates and/or outputStates) or its function; those dictionaries, in turn, contain
entries for the values of the runtime parameters for a state, its function, or its projection(s) (see the
``runtime_params`` argument of the :py:data:`execute <Mechanism_Base.execute>` method below for more details).


.. _Mechanism_Class_Reference:

Class Reference
---------------

"""

from collections import OrderedDict
from inspect import isclass

from PsyNeuLink.Components.ShellClasses import *
from PsyNeuLink.Globals.Registry import register_category

MechanismRegistry = {}

class MonitoredOutputStatesOption(AutoNumber):
    ONLY_SPECIFIED_OUTPUT_STATES = ()
    PRIMARY_OUTPUT_STATES = ()
    ALL_OUTPUT_STATES = ()
    NUM_MONITOR_STATES_OPTIONS = ()


class MechanismError(Exception):
    def __init__(self, error_value):
        self.error_value = error_value

    def __str__(self):
        return repr(self.error_value)


def mechanism(mech_spec=None, params=None, context=None):
    """Factory method for Mechanism; returns the type of mechanism specified or a default mechanism.

    If called with no arguments, returns the default mechanism ([LINK for default]).

    Arguments
    ---------

    mech_spec : Optional[Mechanism subclass, str, or dict]
        specification for the mechanism to create.
        If it is :keyword:`None`, returns the default mechanism ([LINK for default]);
        if it is the name of a Mechanism subclass, a default instance of that subclass is returned;
        if it is the name of a Mechanism subclass registered in the :py:class:`MechanismRegistry`
        an instance of a default mechanism for that class is returned,
        otherwise the string is used to name an instance of the default mechanism;
        if it is a dict, it must be a mechanism specification dict (see :ref:`Mechanism_Creation`).
        Note: if a name is not specified, the nth instance created will be named by using the mechanism's
        ``componentType`` attribute as the base and adding an indexed suffix:  componentType-n.

    params : Optional[Dict[param keyword, param value]]
        a dictionary that can be used to specify the parameters for the mechanism, parameters for its function,
        and/or a custom function and its parameters (see :doc:`Mechanism` for specification of a params dict).
        It is passed to the relevant subclass to instantiate the mechanism. Entries can be any parameters described
        in :ref:`Mechanism_Specifying_Parameters` that are relevant to the mechanism's subclass, and/or any defined
        by a :doc:`Mechanism` subclass itself.

    COMMENT:
        context : str
            if it is the keyword :keyword:`VALIDATE`, returns :keyword:`True` if specification would return a valid
            subclass object; otherwise returns :keyword:`False`.
    COMMENT

    Returns
    -------

    Instance of specified Mechanism subclass or None : Mechanism
    """

    # Called with a keyword
    if mech_spec in MechanismRegistry:
        return MechanismRegistry[mech_spec].mechanismSubclass(params=params, context=context)

    # Called with a string that is not in the Registry, so return default type with the name specified by the string
    elif isinstance(mech_spec, str):
        return Mechanism_Base.defaultMechanism(name=mech_spec, params=params, context=context)

    # Called with a Mechanism type, so return instantiation of that type
    elif isclass(mech_spec) and issubclass(mech_spec, Mechanism):
        return mech_spec(params=params, context=context)

    # Called with Mechanism specification dict (with type and params as entries within it), so:
    #    - get mech_type from kwMechanismType entry in dict
    #    - pass all other entries as params
    elif isinstance(mech_spec, dict):
        # Get Mechanism type from kwMechanismType entry of specification dict
        try:
            mech_spec = mech_spec[kwMechanismType]
        # kwMechanismType config_entry is missing (or mis-specified), so use default (and warn if in VERBOSE mode)
        except (KeyError, NameError):
            if Mechanism.classPreferences.verbosePref:
                print("{0} entry missing from mechanisms dict specification ({1}); default ({2}) will be used".
                      format(kwMechanismType, mech_spec, Mechanism_Base.defaultMechanism))
            return Mechanism_Base.defaultMechanism(name=kwProcessDefaultMechanism, context=context)
        # Instantiate Mechanism using mech_spec dict as arguments
        else:
            return mech_spec(context=context, **mech_spec)

    # Called without a specification, so return default type
    elif mech_spec is None:
        return Mechanism_Base.defaultMechanism(name=kwProcessDefaultMechanism, context=context)

    # Can't be anything else, so return empty
    else:
        return None


class Mechanism_Base(Mechanism):
    """Abstract class for Mechanism

    .. note::
       Mechanisms should NEVER be instantiated by a direct call to the base class.
       They should be instantiated using the :class:`mechanism` factory method (see it for description of parameters),
       by calling the constructor for the desired subclass, or using other methods for specifying a mechanism in
       context (see :ref:`Mechanism_Creation`).

    COMMENT:
        Description
        -----------
            Mechanism is a Category of the Function class.
            A mechanism is associated with a name and:
            - one or more inputStates:
                two ways to get multiple inputStates, if supported by mechanism subclass being instantiated:
                    • specify 2d variable for mechanism (i.e., without explicit inputState specifications)
                        once the variable of the mechanism has been converted to a 2d array, an inputState is assigned
                        for each item of axis 0, and the corresponding item is assigned as the inputState's variable
                    • explicitly specify inputStates in params[INPUT_STATES] (each with its own variable specification);
                        those variables will be concantenated into a 2d array to create the mechanism's variable
                if both methods are used, they must generate the same sized variable for the mechanims
                ?? WHERE IS THIS CHECKED?  WHICH TAKES PRECEDENCE: inputState SPECIFICATION (IN _instantiate_state)??
            - an execute method:
                coordinates updating of inputStates, parameterStates (and params), execution of the function method
                implemented by the subclass, (by calling its __execute__ method), and updating of the outputStates
            - one or more parameters, each of which must be (or resolve to) a reference to a ParameterState
                these determine the operation of the function of the mechanism subclass being instantiated
            - one or more outputStates:
                the variable of each receives the corresponding item in the output of the mechanism's function
                the value of each is passed to corresponding MappingProjections for which the mechanism is a sender
                * Notes:
                    by default, a Mechanism has only one outputState, assigned to <mechanism>.outputState;  however:
                    if params[OUTPUT_STATES] is a list (of names) or specification dict (of MechanismOuput State
                    specs), <mechanism>.outputStates (note plural) is created and contains a dict of outputStates,
                    the first of which points to <mechanism>.outputState (note singular)
                [TBI * each outputState maintains a list of projections for which it serves as the sender]

        Constraints
        -----------
            - the number of inputStates must correspond to the length of the variable of the mechanism's execute method
            - the value of each inputState must be compatible with the corresponding item in the
                variable of the mechanism's execute method
            - the value of each parameterState must be compatible with the corresponding parameter of  the mechanism's
                 execute method
            - the number of outputStates must correspond to the length of the output of the mechanism's execute method,
                (self.value)
            - the value of each outputState must be compatible with the corresponding item of the self.value
                 (the output of the mechanism's execute method)

        Class attributes
        ----------------
            + componentCategory = kwMechanismFunctionCategory
            + className = componentCategory
            + suffix = " <className>"
            + className (str): kwMechanismFunctionCategory
            + suffix (str): " <className>"
            + registry (dict): MechanismRegistry
            + classPreference (PreferenceSet): Mechanism_BasePreferenceSet, instantiated in __init__()
            + classPreferenceLevel (PreferenceLevel): PreferenceLevel.CATEGORY
            + variableClassDefault (list)
            + paramClassDefaults (dict):
                + kwMechanismTimeScale (TimeScale): TimeScale.TRIAL (timeScale at which mechanism executes)
                + [TBI: kwMechanismExecutionSequenceTemplate (list of States):
                    specifies order in which types of States are executed;  used by self.execute]
            + paramNames (dict)
            + defaultMechanism (str): Currently kwDDM (class reference resolved in __init__.py)

        Class methods
        -------------
            - _validate_variable(variable, context)
            - _validate_params(request_set, target_set, context)
            - update_states_and_execute(time_scale, params, context):
                updates input, param values, executes <subclass>.function, returns outputState.value
            - terminate_execute(self, context=None): terminates execution of mechanism (for TimeScale = time_step)
            - adjust(params, context)
                modifies specified mechanism params (by calling Function._assign_defaults)
                returns output

        MechanismRegistry
        -----------------
            All Mechanisms are registered in MechanismRegistry, which maintains a dict for each subclass,
              a count for all instances of that type, and a dictionary of those instances
    COMMENT

    Attributes
    ----------

    variable : 2d np.array : default ``variableInstanceDefault``
        value used as input to the mechanism's ``function``.  When specified in the call to create an instance
        (i.e., the mechanism's __init__ method), it is used as a template to define the format of the function's input
        (length and type of elements), and the default value for the instance.

        .. _receivesProcessInput (bool): flags if Mechanism (as first in Pathway) receives Process input projection

    inputState : InputState : default default InputState
        primary inputState for the mechanism;  same as first entry in ``inputStates`` attribute.

    inputStates : OrderedDict[str, InputState]
        a dictionary of the mechanism's inputStates.
        The key of each entry is the name of the inputState, and its value is the inputState.
        There is always at least one entry, which contains the primary inputState
        (i.e., the one in the :py:data:`inputState <Mechanism_Base.inputState>` attribute).

    inputValue : List[List or 1d np.array] : default ``variableInstanceDefault``
        a list of values, one for the variable of each of the mechanism's inputStates.
        The value of each item is equal to the value of the corresponding item in the mechanism's ``variable``
        attribute (i.e., the item in the corresponding position of axis 0 of the ``variable`` 2d np.array).
        The :py:data:`inputValue <Mechanism_Base.inputValue>` provides this information in a simpler list format.

    parameterStates : OrderedDict[str, ParameterState]
        a dictionary of parameterStates, one for each parameter of the mechanism's function.
        The key of each entry is the name of the parameterState, and its value is the parameterState.
        Note: mechanism's function parameters are listed in the the
        :py:data:`function_params <Mechanism_Base.function_params>` attribute).

    function_params : Dict[str, value]
        has one entry for each parameter of the mechanism's function.
        The key of each entry is the name of (keyword for) a function parameter, and its value is the parameter's value.

    value : 2d np.array : default None
        output of the mechanism's function;
        Note: this is not necessarily equal to the :py:data:`outputValue <Mechanism_Base.outputValue>` attribute;
        it is :keyword:`None` until the mechanism has been executed at least once.

        .. _value_template : 2d np.array : default None
               set equal to the value attribute when the mechanism is first initialized;
               maintains its value even when value is reset to None when (re-)initialized prior to execution.

    outputState : OutputState : default default OutputState
        primary outputState for the mechanism;  same as first entry in
        :py:data:`outputStates <Mechanism_Base.outputStates>` attribute.

    outputStates : OrderedDict[str, InputState]
        a dictionary of the mechanism's outputStates.
        the key of each entry is the name of an outputState, and its value is the outputState.
        There is always at least one entry, which contains the primary outputState
        (i.e., the one in the :py:data:`outputState <Mechanism_Base.outputState>` attribute).

    outputValue : List[value] : default mechanism.function(variableInstanceDefault)
        a list of values, one for the value of each of the mechanism's outputStates.
        Note: this is not necessarily equal to the ``value`` attribute of the mechanism, since the outputState's
        ``function`` and/or its :py:data:`calculate <Mechanism_Base.calculate>` attributes may calculate a new quantity
        derived from an item of the mechanism's ``value``, and assign that to the outputState's ``value`` and the
        corresponding item of the mechanism's :py:data:`outputValue <Mechanism_Base.outputValue>` attribute.

        COMMENT:
            EXAMPLE HERE
        COMMENT

        .. _outputStateValueMapping : Dict[str, int]:
               contains the mappings of outputStates to their indices in the outputValue list
               The key of each entry is the name of an outputState, and the value is its position in the
                    :py:data:`outputStates <Mechanism_Base.outputStates>` OrderedDict.
               Used in ``_update_output_states`` to assign the value of each outputState to the correct item of
                   the mechanism's ``value`` attribute.
               Any mechanism with a function that returns a value with more than one item (i.e., len > 1) MUST implement
                   self.execute rather than just use the params[FUNCTION].  This is so that _outputStateValueMapping
                   can be implemented.
               TBI: if the function of a mechanism is specified only by params[FUNCTION]
                   (i.e., it does not implement self.execute) and it returns a value with len > 1
                   it MUST also specify kwFunctionOutputStateValueMapping.

    phaseSpec : int or float :  default 0
        Specifies the time_step(s) on which the mechanism is executed as part of a system
        (see :ref:`Process_Mechanisms` for specification, and :ref:`System Phase <System_Execution_Phase>`
        for how phases are used).

    processes : Dict[Process, str]:
        Contains a dictionary of the processes to which the mechanism belongs, and its designation in each.
        The key of each entry is a process to which the mechanism belongs, and its value the mechanism's designation
        in that process (see Process :ref:`Process_Mechanisms` for designations and their meanings).

    systems : Dict[System, str]:
        Contains a dictionary of the systems to which the mechanism belongs, and its designation in each.
        The key of each entry is a system to which the mechanism belongs, and its value the mechanism's designation
        in that system (see System :ref:`System_Mechanisms` for designations and their meanings).

    timeScale : TimeScale : default TimeScale.TRIAL
        Determines the default TimeScale value used by the mechanism when executed.

    name : str : default <Mechanism subclass>-<index>
        the name of the mechanism.
        Specified in the name argument of the call to create the mechanism;  if not is specified,
        a default is assigned by MechanismRegistry based on the mechanism's subclass
        (see :doc:`Registry <LINK>` for conventions used in naming, including for default and duplicate names).

    prefs : PreferenceSet or specification dict : Mechanism.classPreferences
        the PreferenceSet for the mechanism.
        Specified in the prefs argument of the call to create the mechanism;
        if it is not specified, a default is assigned using ``classPreferences`` defined in __init__.py
        (see :py:class:`PreferenceSet <LINK>` for details).

        .. _stateRegistry : Registry
               registry containing dicts for each state type (InputState, OutputState and ParameterState) with instance
               dicts for the instances of each type and an instance count for each state type in the mechanism.
               Note: registering instances of state types with the mechanism (rather than in the StateRegistry)
                     allows the same name to be used for instances of a state type belonging to different mechanisms
                     without adding index suffixes for that name across mechanisms
                     while still indexing multiple uses of the same base name within a mechanism.

    """

    #region CLASS ATTRIBUTES
    componentCategory = kwMechanismComponentCategory
    className = componentCategory
    suffix = " " + className

    registry = MechanismRegistry

    classPreferenceLevel = PreferenceLevel.CATEGORY
    # Any preferences specified below will override those specified in CategoryDefaultPreferences
    # Note: only need to specify setting;  level will be assigned to CATEGORY automatically
    # classPreferences = {
    #     kwPreferenceSetName: 'MechanismCustomClassPreferences',
    #     kp<pref>: <setting>...}


    #FIX:  WHEN CALLED BY HIGHER LEVEL OBJECTS DURING INIT (e.g., PROCESS AND SYSTEM), SHOULD USE FULL Mechanism.execute
    # By default, init only the __execute__ method of Mechanism subclass objects when their execute method is called;
    #    that is, DO NOT run the full Mechanism execute process, since some components may not yet be instantiated
    #    (such as outputStates)
    initMethod = INIT__EXECUTE__METHOD_ONLY

    # IMPLEMENTATION NOTE: move this to a preference
    defaultMechanism = kwDDM


    variableClassDefault = [0.0]
    # Note:  the following enforce encoding as 2D np.ndarrays,
    #        to accomodate multiple states:  one 1D np.ndarray per state
    variableEncodingDim = 2
    valueEncodingDim = 2

    # Category specific defaults:
    paramClassDefaults = Component.paramClassDefaults.copy()
    paramClassDefaults.update({
        kwMechanismTimeScale: TimeScale.TRIAL,
        MONITOR_FOR_CONTROL: NotImplemented,  # This has to be here to "register" it as a valid param for the class
                                              # but is set to NotImplemented so that it is ignored if it is not
                                              # assigned;  setting it to None actively disallows assignment
                                              # (see EVCMechanism_instantiate_input_states for more details)
        MONITOR_FOR_LEARNING: None
        # TBI - kwMechanismExecutionSequenceTemplate: [
        #     Components.States.InputState.InputState,
        #     Components.States.ParameterState.ParameterState,
        #     Components.States.OutputState.OutputState]
        })

    # def __new__(cls, *args, **kwargs):
    # def __new__(cls, name=NotImplemented, params=NotImplemented, context=None):
    #endregion

    def __init__(self,
                 variable=None,
                 params=None,
                 name=None,
                 prefs=None,
                 context=None):
        """Assign name, category-level preferences, register mechanism, and enforce category methods

        This is an abstract class, and can only be called from a subclass;
           it must be called by the subclass with a context value

        NOTES:
        * Since Mechanism is a subclass of Function, it calls super.__init__
            to validate variable_default and param_defaults, and assign params to paramInstanceDefaults;
            it uses kwInputState as the variable_default
        * registers mechanism with MechanismRegistry

        """

        # Forbid direct call to base class constructor
        if not isinstance(context, type(self)) and not kwValidate in context:
            raise MechanismError("Direct call to abstract class Mechanism() is not allowed; "
                                 "use mechanism() or one of the following subclasses: {0}".
                                 format(", ".join("{!s}".format(key) for (key) in MechanismRegistry.keys())))

# IMPLEMENT **args (PER State)

        # Register with MechanismRegistry or create one
        if not context is kwValidate:
            register_category(entry=self,
                              base_class=Mechanism_Base,
                              name=name,
                              registry=MechanismRegistry,
                              context=context)

        # Create mechanism's _stateRegistry and state type entries
        from PsyNeuLink.Components.States.State import State_Base
        self._stateRegistry = {}
        # InputState
        from PsyNeuLink.Components.States.InputState import InputState
        register_category(entry=InputState,
                          base_class=State_Base,
                          registry=self._stateRegistry,
                          context=context)
        # ParameterState
        from PsyNeuLink.Components.States.ParameterState import ParameterState
        register_category(entry=ParameterState,
                          base_class=State_Base,
                          registry=self._stateRegistry,
                          context=context)
        # OutputState
        from PsyNeuLink.Components.States.OutputState import OutputState
        register_category(entry=OutputState,
                          base_class=State_Base,
                          registry=self._stateRegistry,
                          context=context)

        # Mark initialization in context
        if not context or isinstance(context, object) or inspect.isclass(context):
            context = INITIALIZING + self.name + SEPARATOR_BAR + self.__class__.__name__
        else:
            context = context + SEPARATOR_BAR + INITIALIZING + self.name

        super(Mechanism_Base, self).__init__(variable_default=variable,
                                             param_defaults=params,
                                             prefs=prefs,
                                             name=name,
                                             context=context)

        # FUNCTIONS:

# IMPLEMENTATION NOTE:  REPLACE THIS WITH ABC (ABSTRACT CLASS)
        # Assign class functions
        self.classMethods = {
            kwMechanismExecuteFunction: self.execute,
            # kwMechanismAdjustFunction: self.adjust_function,
            # kwMechanismTerminateFunction: self.terminate_execute
        }
        self.classMethodNames = self.classMethods.keys()

        #  Validate class methods:
        #    make sure all required ones have been implemented in (i.e., overridden by) subclass
        for name, method in self.classMethods.items():
            try:
                method
            except (AttributeError):
                raise MechanismError("{0} is not implemented in mechanism class {1}".
                                     format(name, self.name))

        self.value = self._old_value = None
        self._status = INITIALIZING
        self._receivesProcessInput = False
        self.phaseSpec = None
        self.processes = {}
        self.systems = {}

    def _validate_variable(self, variable, context=None):
        """Convert variableClassDefault and self.variable to 2D np.array: one 1D value for each input state

        # VARIABLE SPECIFICATION:                                        ENCODING:
        # Simple value variable:                                         0 -> [array([0])]
        # Single state array (vector) variable:                         [0, 1] -> [array([0, 1])
        # Multiple state variables, each with a single value variable:  [[0], [0]] -> [array[0], array[0]]

        :param variable:
        :param context:
        :return:
        """

        super(Mechanism_Base, self)._validate_variable(variable, context)

        # Force Mechanism variable specification to be a 2D array (to accomodate multiple input states - see above):
        # Note: _instantiate_input_states (below) will parse into 1D arrays, one for each input state
        self.variableClassDefault = convert_to_np_array(self.variableClassDefault, 2)
        self.variable = convert_to_np_array(self.variable, 2)

    def _filter_params(self, params):
        """Add rather than override INPUT_STATES and/or OUTPUT_STATES

        Allows specification of INPUT_STATES or OUTPUT_STATES in params dictionary to be added to,
        rather than override those in paramClassDefaults (the default behavior)
        """

        # INPUT_STATES:
        try:
            input_states_spec = params[INPUT_STATES]
        except KeyError:
            pass
        else:
            # Convert input_states_spec to list if it is not one
            if not isinstance(input_states_spec, list):
                input_states_spec = [input_states_spec]
            # Get inputStates specified in paramClassDefaults
            default_input_states = self.paramClassDefaults[INPUT_STATES].copy()
            # Convert inputStates from paramClassDeafults to a list if it is not one
            if not isinstance(default_input_states, list):
                default_input_states = [default_input_states]
            # Add inputState specified in params to those in paramClassDefaults
            #    Note: order is important here;  new ones should be last, as paramClassDefaults defines the
            #          the primary inputState which must remain first for the inputStates OrderedDictionary
            default_input_states.extend(input_states_spec)
            # Assign full set back to params_arg
            params[INPUT_STATES] = default_input_states

        # OUTPUT_STATES:
        try:
            output_states_spec = params[OUTPUT_STATES]
        except KeyError:
            pass
        else:
            # Convert output_states_spec to list if it is not one
            if not isinstance(output_states_spec, list):
                output_states_spec = [output_states_spec]
            # Get outputStates specified in paramClassDefaults
            default_output_states = self.paramClassDefaults[OUTPUT_STATES].copy()
            # Convert outputStates from paramClassDeafults to a list if it is not one
            if not isinstance(default_output_states, list):
                default_output_states = [default_output_states]
            # Add outputState specified in params to those in paramClassDefaults
            #    Note: order is important here;  new ones should be last, as paramClassDefaults defines the
            #          the primary outputState which must remain first for the outputStates OrderedDictionary
            default_output_states.extend(output_states_spec)
            # Assign full set back to params_arg
            params[OUTPUT_STATES] = default_output_states

    def _validate_params(self, request_set, target_set=None, context=None):
        """validate TimeScale, INPUT_STATES, FUNCTION_PARAMS, OUTPUT_STATES and MONITOR_FOR_CONTROL

        Go through target_set params (populated by Function._validate_params) and validate values for:
            + TIME_SCALE:  <TimeScale>
            + INPUT_STATES:
                <MechanismsInputState or Projection object or class,
                specification dict for one, ParamValueProjection tuple, or numeric value(s)>;
                if it is missing or not one of the above types, it is set to self.variable
            + FUNCTION_PARAMS:  <dict>, every entry of which must be one of the following:
                ParameterState or Projection object or class, specification dict for one,
                ParamValueProjection tuple, or numeric value(s);
                if invalid, default (from paramInstanceDefaults or paramClassDefaults) is assigned
            + OUTPUT_STATES:
                <MechanismsOutputState object or class, specification dict, or numeric value(s);
                if it is missing or not one of the above types, it is set to None here;
                    and then to default value of self.value (output of execute method) in instantiate_outputState
                    (since execute method must be instantiated before self.value is known)
                if OUTPUT_STATES is a list or OrderedDict, it is passed along (to instantiate_outputStates)
                if it is a OutputState class ref, object or specification dict, it is placed in a list
            + MONITORED_STATES:
                ** DOCUMENT

        Note: PARAMETER_STATES are validated separately -- ** DOCUMENT WHY

        TBI - Generalize to go through all params, reading from each its type (from a registry),
                                   and calling on corresponding subclass to get default values (if param not found)
                                   (as PROJECTION_TYPE and PROJECTION_SENDER are currently handled)

        :param request_set: (dict)
        :param target_set: (dict)
        :param context: (str)
        :return:
        """

        # Perform first-pass validation in Function.__init__():
        # - returns full set of params based on subclass paramClassDefaults
        super(Mechanism, self)._validate_params(request_set,target_set,context)

        params = target_set

        #region VALIDATE TIME SCALE
        try:
            param_value = params[TIME_SCALE]
        except KeyError:
            self.timeScale = timeScaleSystemDefault
        else:
            if isinstance(param_value, TimeScale):
                self.timeScale = params[TIME_SCALE]
            else:
                if self.prefs.verbosePref:
                    print("Value for {0} ({1}) param of {2} must be of type {3};  default will be used: {4}".
                          format(TIME_SCALE, param_value, self.name, type(TimeScale), timeScaleSystemDefault))
        #endregion

        #region VALIDATE INPUT STATE(S)

        # MODIFIED 6/10/16
        # FIX: SHOULD CHECK LENGTH OF INPUT_STATES PARAM (LIST OF NAMES OR SPECIFICATION DICT) AGAINST LENGTH OF
        # FIX: self.variable 2D ARRAY AND COMPARE variable SPECS, IF PROVIDED, WITH CORRESPONDING ELEMENTS OF
        # FIX: self.variable 2D ARRAY
        try:
            param_value = params[INPUT_STATES]

        except KeyError:
            # INPUT_STATES not specified:
            # - set to None, so that it is set to default (self.variable) in instantiate_inputState
            # - if in VERBOSE mode, warn in instantiate_inputState, where default value is known
            params[INPUT_STATES] = None

        else:
            # INPUT_STATES is specified, so validate:
            # If it is a single item or a non-OrderedDict, place in a list (for use here and in instantiate_inputState)
            if not isinstance(param_value, (list, OrderedDict)):
                param_value = [param_value]
            # Validate each item in the list or OrderedDict
            # Note:
            # * number of inputStates is validated against length of the owner mechanism's execute method variable (EMV)
            #     in instantiate_inputState, where an inputState is assigned to each item (value) of the EMV
            i = 0
            for key, item in param_value if isinstance(param_value, dict) else enumerate(param_value):
                from PsyNeuLink.Components.States.InputState import InputState
                # If not valid...
                if not ((isclass(item) and (issubclass(item, InputState) or # InputState class ref
                                                issubclass(item, Projection))) or    # Project class ref
                            isinstance(item, InputState) or      # InputState object
                            isinstance(item, dict) or                     # InputState specification dict
                            isinstance(item, ParamValueProjection) or     # ParamValueProjection tuple
                            isinstance(item, str) or                      # Name (to be used as key in inputStates dict)
                            iscompatible(item, **{kwCompatibilityNumeric: True})):   # value
                    # set to None, so it is set to default (self.variable) in instantiate_inputState
                    param_value[key] = None
                    if self.prefs.verbosePref:
                        print("Item {0} of {1} param ({2}) in {3} is not a"
                              " InputState, specification dict or value, nor a list of dict of them; "
                              "variable ({4}) of execute method for {5} will be used"
                              " to create a default outputState for {3}".
                              format(i,
                                     INPUT_STATES,
                                     param_value,
                                     self.__class__.__name__,
                                     self.variable,
                                     self.execute.__self__.name))
                i += 1
            params[INPUT_STATES] = param_value
        #endregion

        #region VALIDATE EXECUTE METHOD PARAMS
        try:
            function_param_specs = params[FUNCTION_PARAMS]
        except KeyError:
            if self.prefs.verbosePref:
                print("No params specified for {0}".format(self.__class__.__name__))
        else:
            if not (isinstance(function_param_specs, dict)):
                raise MechanismError("{0} in {1} must be a dict of param specifications".
                                     format(FUNCTION_PARAMS, self.__class__.__name__))
            # Validate params
            from PsyNeuLink.Components.States.ParameterState import ParameterState
            for param_name, param_value in function_param_specs.items():
                try:
                    default_value = self.paramInstanceDefaults[FUNCTION_PARAMS][param_name]
                except KeyError:
                    raise MechanismError("{0} not recognized as a param of execute method for {1}".
                                         format(param_name, self.__class__.__name__))
                if not ((isclass(param_value) and
                             (issubclass(param_value, ParameterState) or
                                  issubclass(param_value, Projection))) or
                        isinstance(param_value, ParameterState) or
                        isinstance(param_value, Projection) or
                        isinstance(param_value, dict) or
                        isinstance(param_value, ParamValueProjection) or
                        iscompatible(param_value, default_value)):
                    params[FUNCTION_PARAMS][param_name] = default_value
                    if self.prefs.verbosePref:
                        print("{0} param ({1}) for execute method {2} of {3} is not a ParameterState, "
                              "projection, ParamValueProjection, or value; default value ({4}) will be used".
                              format(param_name,
                                     param_value,
                                     self.execute.__self__.componentName,
                                     self.__class__.__name__,
                                     default_value))
        #endregion
        # FIX: MAKE SURE OUTPUT OF EXECUTE FUNCTION / SELF.VALUE  IS 2D ARRAY, WITH LENGTH == NUM OUTPUT STATES

        #region VALIDATE OUTPUT STATE(S)

        # FIX: MAKE SURE # OF OUTPUTS == LENGTH OF OUTPUT OF EXECUTE FUNCTION / SELF.VALUE
        try:
            param_value = params[OUTPUT_STATES]

        except KeyError:
            # OUTPUT_STATES not specified:
            # - set to None, so that it is set to default (self.value) in instantiate_outputState
            # Notes:
            # * if in VERBOSE mode, warning will be issued in instantiate_outputState, where default value is known
            # * number of outputStates is validated against length of owner mechanism's execute method output (EMO)
            #     in instantiate_outputState, where an outputState is assigned to each item (value) of the EMO
            params[OUTPUT_STATES] = None

        else:
            # OUTPUT_STATES is specified, so validate:
            # If it is a single item or a non-OrderedDict, place in a list (for use here and in instantiate_outputState)
            if not isinstance(param_value, (list, OrderedDict)):
                param_value = [param_value]
            # Validate each item in the list or OrderedDict
            i = 0
            for key, item in param_value if isinstance(param_value, dict) else enumerate(param_value):
                from PsyNeuLink.Components.States.OutputState import OutputState
                # If not valid...
                if not ((isclass(item) and issubclass(item, OutputState)) or # OutputState class ref
                            isinstance(item, OutputState) or   # OutputState object
                            isinstance(item, dict) or                   # OutputState specification dict
                            isinstance(item, str) or                    # Name (to be used as key in outputStates dict)
                            iscompatible(item, **{kwCompatibilityNumeric: True})):  # value
                    # set to None, so it is set to default (self.value) in instantiate_outputState
                    param_value[key] = None
                    if self.prefs.verbosePref:
                        print("Item {0} of {1} param ({2}) in {3} is not a"
                              " OutputState, specification dict or value, nor a list of dict of them; "
                              "output ({4}) of execute method for {5} will be used"
                              " to create a default outputState for {3}".
                              format(i,
                                     OUTPUT_STATES,
                                     param_value,
                                     self.__class__.__name__,
                                     self.value,
                                     self.execute.__self__.name))
                i += 1
            params[OUTPUT_STATES] = param_value

        # MODIFIED 7/13/16 NEW: [MOVED FROM EVCMechanism]
        # FIX: MOVE THIS TO FUNCTION, OR ECHO IN SYSTEM
        #region VALIDATE MONITORED STATES (for use by ControlMechanism)
        # Note: this must be validated after OUTPUT_STATES as it can reference entries in that param
        try:
            # MODIFIED 7/16/16 NEW:
            if not target_set[MONITOR_FOR_CONTROL] or target_set[MONITOR_FOR_CONTROL] is NotImplemented:
                pass
            # MODIFIED END
            # It is a MonitoredOutputStatesOption specification
            elif isinstance(target_set[MONITOR_FOR_CONTROL], MonitoredOutputStatesOption):
                # Put in a list (standard format for processing by _instantiate_monitored_output_states)
                target_set[MONITOR_FOR_CONTROL] = [target_set[MONITOR_FOR_CONTROL]]
            # It is NOT a MonitoredOutputStatesOption specification, so assume it is a list of Mechanisms or States
            else:
                # Validate each item of MONITOR_FOR_CONTROL
                for item in target_set[MONITOR_FOR_CONTROL]:
                    self._validate_monitored_state(item, context=context)
                # FIX: PRINT WARNING (IF VERBOSE) IF WEIGHTS or EXPONENTS IS SPECIFIED,
                # FIX:     INDICATING THAT IT WILL BE IGNORED;
                # FIX:     weights AND exponents ARE SPECIFIED IN TUPLES
                # FIX:     WEIGHTS and EXPONENTS ARE VALIDATED IN SystemContro.Mechanism_instantiate_monitored_output_states
                # # Validate WEIGHTS if it is specified
                # try:
                #     num_weights = len(target_set[FUNCTION_PARAMS][WEIGHTS])
                # except KeyError:
                #     # WEIGHTS not specified, so ignore
                #     pass
                # else:
                #     # Insure that number of weights specified in WEIGHTS
                #     #    equals the number of states instantiated from MONITOR_FOR_CONTROL
                #     num_monitored_states = len(target_set[MONITOR_FOR_CONTROL])
                #     if not num_weights != num_monitored_states:
                #         raise MechanismError("Number of entries ({0}) in WEIGHTS of kwFunctionParam for EVC "
                #                        "does not match the number of monitored states ({1})".
                #                        format(num_weights, num_monitored_states))
        except KeyError:
            pass
        #endregion
        # MODIFIED END

# FIX: MAKE THIS A CLASS METHOD OR MODULE FUNCTION
# FIX:     SO THAT IT CAN BE CALLED BY System TO VALIDATE IT'S MONITOR_FOR_CONTROL param

    def _validate_monitored_state(self, state_spec, context=None):
        """Validate specification is a Mechanism or OutputState, the name of one, or a MonitoredOutpuStatesOption value

        Called by both self._validate_params() and self.add_monitored_state() (in ControlMechanism)
        """
        state_spec_is_OK = False

        if isinstance(state_spec, MonitoredOutputStatesOption):
            state_spec_is_OK = True

        if isinstance(state_spec, tuple):
            if len(state_spec) != 3:
                raise MechanismError("Specification of tuple ({0}) in MONITOR_FOR_CONTROL for {1} "
                                     "has {2} items;  it should be 3".
                                     format(state_spec, self.name, len(state_spec)))

            if not isinstance(state_spec[1], numbers.Number):
                raise MechanismError("Specification of the exponent ({0}) for MONITOR_FOR_CONTROL of {1} "
                                     "must be a number".
                                     format(state_spec, self.name, state_spec[0]))

            if not isinstance(state_spec[2], numbers.Number):
                raise MechanismError("Specification of the weight ({0}) for MONITOR_FOR_CONTROL of {1} "
                                     "must be a number".
                                     format(state_spec, self.name, state_spec[0]))

            # Set state_spec to the output_state item for validation below
            state_spec = state_spec[0]

        from PsyNeuLink.Components.States.OutputState import OutputState
        if isinstance(state_spec, (Mechanism, OutputState)):
            state_spec_is_OK = True

        if isinstance(state_spec, str):
            if state_spec in self.paramInstanceDefaults[OUTPUT_STATES]:
                state_spec_is_OK = True
        try:
            self.outputStates[state_spec]
        except (KeyError, AttributeError):
            pass
        else:
            state_spec_is_OK = True

        if not state_spec_is_OK:
            raise MechanismError("Specification ({0}) in MONITOR_FOR_CONTROL for {1} is not "
                                 "a Mechanism or OutputState object or the name of one".
                                 format(state_spec, self.name))
#endregion

    def _validate_inputs(self, inputs=None):
        # Only ProcessingMechanism supports run() method of Function;  ControlMechanism and MonitoringMechanism do not
        raise MechanismError("{} does not support run() method".format(self.__class__.__name__))

    def _instantiate_attributes_before_function(self, context=None):

        self._instantiate_input_states(context=context)
        self._instantiate_parameter_states(context=context)
        super()._instantiate_attributes_before_function(context=context)

    def _instantiate_parameter_states(self, context=None):

        from PsyNeuLink.Components.States.ParameterState import _instantiate_parameter_states
        _instantiate_parameter_states(owner=self, context=context)


    def _instantiate_attributes_after_function(self, context=None):
        from PsyNeuLink.Components.States.OutputState import _instantiate_output_states
        _instantiate_output_states(owner=self, context=context)

    def _instantiate_input_states(self, context=None):
        """Call State._instantiate_input_states to instantiate orderedDict of inputState(s)

        This is a stub, implemented to allow Mechanism subclasses to override _instantiate_input_states
        """

        from PsyNeuLink.Components.States.InputState import _instantiate_input_states
        _instantiate_input_states(owner=self, context=context)

    def _add_projection_to_mechanism(self, state, projection, context=None):

        from PsyNeuLink.Components.Projections.Projection import _add_projection_to
        _add_projection_to(receiver=self, state=state, projection_spec=projection, context=context)

    def _add_projection_from_mechanism(self, receiver, state, projection, context=None):
        """Add projection to specified state
        """
        from PsyNeuLink.Components.Projections.Projection import _add_projection_from
        _add_projection_from(sender=self, state=state, projection_spec=projection, receiver=receiver, context=context)

    def execute(self, input=None, runtime_params=None, clock=CentralClock, time_scale=TimeScale.TRIAL, context=None):
        """Carry out a single execution of the mechanism.

        Update inputState(s) and param(s), call subclass __execute__, update outputState(s), and assign self.value

        COMMENT:
            Execution sequence:
            - Call self.inputState.execute() for each entry in self.inputStates:
                + execute every self.inputState.receivesFromProjections.[<Projection>.execute()...]
                + aggregate results using self.inputState.params[FUNCTION]()
                + store the result in self.inputState.value
            - Call every self.params[<ParameterState>].execute(); for each:
                + execute self.params[<ParameterState>].receivesFromProjections.[<Projection>.execute()...]
                    (usually this is just a single ControlProjection)
                + aggregate results (if > one) using self.params[<ParameterState>].params[FUNCTION]()
                + apply the result to self.params[<ParameterState>].value
            - Call subclass' self.execute(params):
                - use self.inputState.value as its variable,
                - use params[kw<*>] or self.params[<ParameterState>].value for each param of subclass self.execute,
                - apply the output to self.outputState.value
                Note:
                * if execution is occuring as part of initialization, outputState(s) are reset to 0
                * otherwise, they are left in the current state until the next update

            - [TBI: Call self.outputState.execute() (output gating) to update self.outputState.value]
        COMMENT

        Arguments
        ---------

        input : List[value] or ndarray : default variableInstanceDefault
            input to use for execution of the mechanism.
            This must be consistent with the format mechanism's inputState(s):
            the number of items in the outermost level of list,
            or axis 0 of ndarray, must equal the number of inputStates (if there is more than one), and each
            item must be compatible with the format (number and type of elements) of each inputState's variable
            (see :ref:`Run_Inputs` for details of input specification formats).

        COMMENT:
          MOVE THE BULK OF THIS TO THE DESCRIPTION OF RUNTIME PARAMS ABOVE, AND REFERENCE THAT.
        COMMENT
        runtime_params : Optional[Dict[str, Dict[str, Dict[str, value]]]]:
            a dictionary that can include any of the parameters used as arguments to instantiate the object,
            its function, or projection(s) to any of its states.  Any value assigned to a parameter will override
            the current value of that parameter for this -- but only this execution of the mechanism; it will return
            to its previous value following execution.  Each entry is either the specification for one of the
            mechanism's params (in which case the key is the name of the param, and its value the value to be
            assigned to that param), or a dictionary for a specified type of state (in which case, the key is the
            name of a specific state or a keyword indicating the type of state (:keyword:`INPUT_STATE_PARAMS`,
            :keyword:`OUTPUT_STATE_PARAMS` or :keyword:`PARAMETER_STATE_PARAMS`), and the value is a dictionary
            containing parameter dictionaries for that state or all states of the specified type).  The latter
            (state dictionaries) contain entries that are themselves dictionaries containing parameters for the
            state's function or its projections. The key for each entry is a keyword indicating whether it is for
            the state's function (:keyword:`FUNCTON_PARAMS`), all of its projections (:keyword:`PROJECTION_PARAMS`),
            a particular type of projection (:keyword:`MAPPING_PROJECTION_PARAMS` or
            :keyword:`CONTROL_PROJECTION_PARAMS`), or to a specific projection (using its name), and the value of
            each entry is a dictionary containing the parameters for the function, projection, or set of projections
            (keys of which are parameter names, and values the values to be assigned).

          COMMENT:
            ?? DO PROJECTION DICTIONARIES PERTAIN TO INCOMING OR OUTGOING PROJECTIONS OR BOTH??
            ?? CAN THE KEY FOR A STATE DICTIONARY REFERENCE A SPECIFIC STATE BY NAME, OR ONLY STATE-TYPE??

            state keyword: dict for state's params
                function or projection keyword: dict for funtion or projection's params
                    parameter keyword: vaue of param

                dict: can be one (or more) of the following:
                    + INPUT_STATE_PARAMS:<dict>
                    + PARAMETER_STATE_PARAMS:<dict>
               [TBI + OUTPUT_STATE_PARAMS:<dict>]
                    - each dict will be passed to the corresponding State
                    - params can be any permissible executeParamSpecs for the corresponding State
                    - dicts can contain the following embedded dicts:
                        + FUNCTION_PARAMS:<dict>:
                             will be passed the State's execute method,
                                 overriding its paramInstanceDefaults for that call
                        + PROJECTION_PARAMS:<dict>:
                             entry will be passed to all of the State's projections, and used by
                             by their execute methods, overriding their paramInstanceDefaults for that call
                        + MAPPING_PROJECTION_PARAMS:<dict>:
                             entry will be passed to all of the State's MappingProjections,
                             along with any in a PROJECTION_PARAMS dict, and override paramInstanceDefaults
                        + CONTROL_PROJECTION_PARAMS:<dict>:
                             entry will be passed to all of the State's ControlProjections,
                             along with any in a PROJECTION_PARAMS dict, and override paramInstanceDefaults
                        + <projectionName>:<dict>:
                             entry will be passed to the State's projection with the key's name,
                             along with any in the PROJECTION_PARAMS and MappingProjection or ControlProjection dicts
          COMMENT

        time_scale : TimeScale :  default TimeScale.TRIAL
            specifies whether mechanisms are executed for a single time step or a trial.

        Returns
        -------

        output of mechanism : ndarray
            outputState.value containing the output of each of the mechanism's outputStates[]
            after either one time_step or the full trial

        """

        # context = context or  EXECUTING + ' ' + append_type_to_name(self)
        context = context or NO_CONTEXT


        # IMPLEMENTATION NOTE: Re-write by calling execute methods according to their order in functionDict:
        #         for func in self.functionDict:
        #             self.functionsDict[func]()

        # Limit init to scope specified by context
        if INITIALIZING in context:
            if kwProcessInit in context or kwSystemInit in context:
                # Run full execute method for init of Process and System
                pass
            # Only call mechanism's __execute__ method for init
            # # MODIFIED 12/8/16 OLD:
            # elif self.initMethod is INIT__EXECUTE__METHOD_ONLY:
            #     return self.__execute__(variable=self.variable,
            #                          params=runtime_params,
            #                          time_scale=time_scale,
            #                          context=context)
            # # Only call mechanism's function method for init
            # elif self.initMethod is INIT_FUNCTION_METHOD_ONLY:
            #     return self.function(variable=self.variable,
            #                          params=runtime_params,
            #                          time_scale=time_scale,
            #                          context=context)
            # MODIFIED 12/8/16 NEW:
            elif self.initMethod is INIT__EXECUTE__METHOD_ONLY:
                return_value =  self.__execute__(variable=self.variable,
                                                 runtime_params=runtime_params,
                                                 clock=clock,
                                                 time_scale=time_scale,
                                                 context=context)
                return np.atleast_2d(return_value)

            # Only call mechanism's function method for init
            elif self.initMethod is INIT_FUNCTION_METHOD_ONLY:
                return_value = self.function(variable=self.variable,
                                             params=runtime_params,
                                             time_scale=time_scale,
                                             context=context)
                return np.atleast_2d(return_value)
            # MODIFIED 12/8/16 END

        #region VALIDATE RUNTIME PARAMETER SETS
        # Insure that param set is for a States:
        if self.prefs.paramValidationPref:
            # if runtime_params != NotImplemented:
            if runtime_params:
                for param_set in runtime_params:
                    if not (INPUT_STATE_PARAMS in param_set or
                            PARAMETER_STATE_PARAMS in param_set or
                            OUTPUT_STATE_PARAMS in param_set):
                        raise MechanismError("{0} is not a valid parameter set for runtime specification".
                                             format(param_set))
        #endregion

        #region VALIDATE INPUT STATE(S) AND RUNTIME PARAMS
        self._check_args(variable=self.inputValue,
                        params=runtime_params,
                        target_set=runtime_params)
        #endregion

        #region UPDATE INPUT STATE(S)
        # Executing or simulating process or system, get input by updating inputStates
        if input is None and (EXECUTING in context or EVC_SIMULATION in context):
            self._update_input_states(runtime_params=runtime_params, time_scale=time_scale, context=context)

        # Direct call to execute mechanism with specified input, so assign input to mechanism's inputStates
        else:
            if context is NO_CONTEXT:
                context = EXECUTING + ' ' + append_type_to_name(self)
            if input is None:
                input = self.variableClassDefault
            self._assign_input(input)
        # MODIFIED 11/27/16 END

        #endregion

        #region UPDATE PARAMETER STATE(S)
        # #TEST:
        # print ("BEFORE param update:  DDM Drift Rate {}".
        #        format(self.parameterStates[DRIFT_RATE].value))
        self._update_parameter_states(runtime_params=runtime_params, time_scale=time_scale, context=context)
        #endregion

        # MODIFIED 11/27/16 NEW:
        # FIX ASSIGN PARAMETERSTATE PARAMETER VALUES TO PARAMS HERE AND PASS TO __EXECUTE__()
        # # If any runtime_params were assigned, assign values to params used to call mechanism's __execute__ method
        # if runtime_params:
        # Assign current paramameterState values to params used to call mechanism's __execute__ method
        # FIX: UPDATE THIS TO USE user_params ONCE THOSE HAVE ALL BEEN ASSIGNED parameterStates IN
        # _instantiate_parameter_states
        # FIX: MOVED TO _update_parameter_states BUT NOW ScratchPad doesn't work
        # runtime_params = {}
        # for param in self.function_params:
        #     try:
        #         runtime_params[param] = self.parameterStates[param].value
        #     except KeyError:
        #         runtime_params[param] = self.paramsCurrent[FUNCTION_PARAMS][param]
        # MODIFIED 11/27/16 END

        #region CALL SUBCLASS __execute__ method AND ASSIGN RESULT TO self.value
# CONFIRM: VALIDATION METHODS CHECK THE FOLLOWING CONSTRAINT: (AND ADD TO CONSTRAINT DOCUMENTATION):
# DOCUMENT: #OF OUTPUTSTATES MUST MATCH #ITEMS IN OUTPUT OF EXECUTE METHOD **

        self.value = self.__execute__(variable=self.inputValue,
                                      runtime_params=runtime_params,
                                      clock=clock,
                                      time_scale=time_scale,
                                      context=context)

        # MODIFIED 12/8/16 NEW:
        self.value = np.atleast_2d(self.value)
        # MODIFIED 12/8/16 END

        # MODIFIED 12/20/16 NEW:
        # Set status based on whether self.value has changed
        self.status = self.value
        # MODIFIED 12/20/16 END

        #endregion


        #region UPDATE OUTPUT STATE(S)
        self._update_output_states(runtime_params=runtime_params, time_scale=time_scale, context=context)
        #endregion

        #region REPORT EXECUTION
        if self.prefs.reportOutputPref and context and EXECUTING in context:
            self._report_mechanism_execution(self.inputValue, self.user_params, self.outputState.value)
        #endregion

        #region RE-SET STATE_VALUES AFTER INITIALIZATION
        # If this is (the end of) an initialization run, restore state values to initial condition
        if '_init_' in context:
            for state in self.inputStates:
                self.inputStates[state].value = self.inputStates[state].variable
            for state in self.parameterStates:
                self.parameterStates[state].value =  self.parameterStates[state].baseValue
            for state in self.outputStates:
                # Zero outputStates in case of recurrence:
                #    don't want any non-zero values as a residuum of initialization runs to be
                #    transmittted back via recurrent projections as initial inputs
# FIX: IMPLEMENT zero_all_values METHOD
                self.outputStates[state].value = self.outputStates[state].value * 0.0
        #endregion

        #endregion

        return self.value

    def run(self,
            inputs,
            num_executions=None,
            call_before_execution=None,
            call_after_execution=None,
            time_scale=None):
        """Run a sequence of executions

        Call execute method for each in a sequence of executions specified by the ``inputs`` argument
        (see :ref:`Run_Inputs` in :doc:`Run` for additional details of formatting input specifications)

        Arguments
        ---------

        inputs : List[input] or ndarray(input) : default default_input_value
            the inputs used for each in a sequence of executions of the mechanism (see :ref:`Run_Inputs` in
            :doc:`Run` for detailed description of formatting requirements and options).

        call_before_execution : Function : default= :keyword:`None`
            called before each execution of the mechanism.

        call_after_execution : Function : default= :keyword:`None`
            called after each execution of the mechanism.

        time_scale : TimeScale :  default TimeScale.TRIAL
            specifies whether mechanisms are executed for a single time step or a trial.

        Returns
        -------

        <mechanism>.results : List[outputState.value]
            list of the values of the outputStates for each execution of the mechanism

        """
        from PsyNeuLink.Globals.Run import run
        return run(self,
                   inputs=inputs,
                   num_executions=num_executions,
                   call_before_trial=call_before_execution,
                   call_after_trial=call_after_execution,
                   time_scale=time_scale)

    def _assign_input(self, input):

        input = np.atleast_2d(input)
        num_inputs = np.size(input,0)
        num_input_states = len(self.inputStates)
        if num_inputs != num_input_states:
            # Check if inputs are of different lengths (indicated by dtype == np.dtype('O'))
            num_inputs = np.size(input)
            if isinstance(input, np.ndarray) and input.dtype is np.dtype('O') and num_inputs == num_input_states:
                pass
            else:
                raise SystemError("Number of inputs ({0}) to {1} does not match "
                                  "its number of inputStates ({2})".
                                  format(num_inputs, self.name,  num_input_states ))
        for i in range(num_input_states):
            input_state = list(self.inputStates.values())[i]
            # input_item = np.ndarray(input[i])
            input_item = input[i]
            if len(input_state.variable) == len(input_item):
                input_state.value = input_item
            else:
                raise MechanismError("Length ({}) of input ({}) does not match "
                                     "required length ({}) for input to {} of {}".
                                     format(len(input_item),
                                            input[i],
                                            len(input_state.variable),
                                            input_state.name,
                                            append_type_to_name(self)))

    def _update_input_states(self, runtime_params=None, time_scale=None, context=None):
        """ Update value for each inputState in self.inputStates:

        Call execute method for all (MappingProjection) projections in inputState.receivesFromProjections
        Aggregate results (using inputState execute method)
        Update inputState.value
        """
        for i in range(len(self.inputStates)):
            state_name, state = list(self.inputStates.items())[i]
            state.update(params=runtime_params, time_scale=time_scale, context=context)
            self.inputValue[i] = state.value
        self.variable = np.array(self.inputValue)

    def _update_parameter_states(self, runtime_params=None, time_scale=None, context=None):

        for state_name, state in self.parameterStates.items():

            state.update(params=runtime_params, time_scale=time_scale, context=context)

            # Assign parameterState's value to parameter value in runtime_params
            if runtime_params and state_name in runtime_params[PARAMETER_STATE_PARAMS]:
                param = param_template = runtime_params
            # Otherwise use paramsCurrent
            else:
                param = param_template = self.paramsCurrent

            # Determine whether template (param to type-match) is at top level or in a function_params dictionary
            try:
                param_template[state_name]
            except KeyError:
                param_template = self.function_params

            # Get its type
            param_type = type(param_template[state_name])
            # If param is a tuple, get type of parameter itself (= 1st item;  2nd is projection or ModulationOperation)
            if param_type is tuple:
                param_type = type(param_template[state_name][0])

            # Assign version of parameterState.value matched to type of template
            #    to runtime param or paramsCurrent (per above)
            param[state_name] = type_match(state.value, param_type)

    def _update_output_states(self, runtime_params=None, time_scale=None, context=None):
        """Execute function for each outputState and assign result of each to corresponding item of self.outputValue

        """
        for i in range(len(self.outputStates)):
            state = list(self.outputStates.values())[i]
            state.update(params=runtime_params, time_scale=time_scale, context=context)
            # self.outputValue[i] = state.value

        # Assign value of each outputState to corresponding item in self.outputValue
        self.outputValue = list(state.value for state in list(self.outputStates.values()))


    def initialize(self, value):
        """Assign initial value to mechanism.value and update outputStates

        Takes a number or 1d array and assigns it to the first item of the mechanism's ``value`` attribute

        Parameters
        ----------
        value : List[value] or 1d ndarray

        """
        if self.paramValidationPref:
            if not iscompatible(value, self.value):
                raise MechanismError("Initialization value ({}) is not compatiable with value of {}".
                                     format(value, append_type_to_name(self)))
        self.value[0] = value
        self._update_output_states()

    def __execute__(self,
                    variable=None,
                    runtime_params=None,
                    clock=CentralClock,
                    time_scale=None,
                    context=None):
        return self.function(variable=variable, params=runtime_params, time_scale=time_scale, context=context)

    def _report_mechanism_execution(self, input=None, params=None, output=None):

        if input is None:
            input = self.inputValue
        if output is None:
            output = self.outputState.value
        params = params or self.user_params

        import re
        if 'mechanism' in self.name or 'Mechanism' in self.name:
            mechanism_string = ' '
        else:
            mechanism_string = ' mechanism'
        print ("\n\'{}\'{} executed:\n- input:  {}".
        # MODIFIED 12/9/16 OLD:
        #        format(self.name, mechanism_string, input.__str__().strip("[]")))
        # MODIFIED 12/9/16 NEW:
               format(self.name, mechanism_string, [float("{:0.3}".format(float(i))) for i in input].__str__().strip("[]")))
        # MODIFIED 12/9/16 END


        if params:
            print("- params:")
            # Sort for consistency of output
            params_keys_sorted = sorted(params.keys())
            for param_name in params_keys_sorted:
                # No need to report these here, as they will be reported for the function itself below
                if param_name is FUNCTION_PARAMS:
                    continue
                param_is_function = False
                param_value = params[param_name]
                if isinstance(param_value, Component):
                    param = param_value.__self__.__name__
                    param_is_function = True
                elif isinstance(param_value, type(Component)):
                    param = param_value.__name__
                    param_is_function = True
                else:
                    param = param_value
                print ("\t{}: {}".format(param_name, str(param).__str__().strip("[]")))
                if param_is_function:
                    # Sort for consistency of output
                    func_params_keys_sorted = sorted(self.function_object.user_params.keys())
                    for fct_param_name in func_params_keys_sorted:
                        print ("\t\t{}: {}".
                               format(fct_param_name,
                                      str(self.function_object.user_params[fct_param_name]).__str__().strip("[]")))
        # # MODIFIED 12/9/16 OLD:
        # print("- output: {}".
        #       format(re.sub('[\[,\],\n]','',str(output))))
        # MODIFIED 12/9/16 NEW:
        print("- output: {}".
              format(re.sub('[\[,\],\n]','',str([float("{:0.3}".format(float(i))) for i in output]))))
        # MODIFIED 12/9/16 END

#     def adjust_function(self, params, context=None):
#         """Modify control_signal_allocations while process is executing
#
#         called by process.adjust()
#         returns output after either one time_step or full trial (determined by current setting of time_scale)
#
#         :param self:
#         :param params: (dict)
#         :param context: (optional)
#         :rtype CurrentStateTuple(state, confidence, duration, controlModulatedParamValues)
#         """
#
#         self._assign_defaults(self.inputState, params)
# # IMPLEMENTATION NOTE: *** SHOULD THIS UPDATE AFFECTED PARAM(S) BY CALLING self._update_parameter_states??
#         return self.outputState.value

    # def terminate_execute(self, context=None):
    #     """Terminate the process
    #
    #     called by process.terminate() - MUST BE OVERRIDDEN BY SUBCLASS IMPLEMENTATION
    #     returns output
    #
    #     :rtype CurrentStateTuple(state, confidence, duration, controlModulatedParamValues)
    #     """
    #     if context==NotImplemented:
    #         raise MechanismError("terminate execute method not implemented by mechanism sublcass")

    def _get_mechanism_param_values(self):
        """Return dict with current value of each ParameterState in paramsCurrent
        :return: (dict)
        """
        from PsyNeuLink.Components.States.ParameterState import ParameterState
        return dict((param, value.value) for param, value in self.paramsCurrent.items()
                    if isinstance(value, ParameterState) )

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, assignment):
        self._value = assignment

    # MODIFIED 12/20/16 NEW:
    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, current_value):
        # if current_value != self._old_value:
        if np.array_equal(current_value, self._old_value):
            self._status = UNCHANGED
        else:
            self._status = CHANGED
            self._old_value = current_value
    # MODIFIED 12/20/16 END


    @property
    def inputState(self):
        return self._inputState

    @inputState.setter
    def inputState(self, assignment):
        self._inputState = assignment

    @property
    def outputState(self):
        return self._outputState

    @outputState.setter
    def outputState(self, assignment):
        self._outputState = assignment

def _is_mechanism_spec(spec):
    """Evaluate whether spec is a valid Mechanism specification

    Return true if spec is any of the following:
    + Mechanism class
    + Mechanism object:
    Otherwise, return :keyword:`False`

    Returns: (bool)
    """
    if inspect.isclass(spec) and issubclass(spec, Mechanism):
        return True
    if isinstance(spec, Mechanism):
        return True
    return False

OBJECT_ITEM = 0
PARAMS_ITEM = 1
PHASE_ITEM = 2

MechanismTuple = namedtuple('MechanismTuple', 'mechanism, params, phase')

from collections import UserList, Iterable
class MechanismList(UserList):
    """Provides access to items and their attributes in a list of :class:`MechanismTuples` for an owner.

    :class:`MechanismTuples` are of the form: (mechanism object, runtime_params dict, phaseSpec int).

    Attributes
    ----------
    mechanisms : list of Mechanism objects

    names : list of strings
        each item is a mechanism.name

    values : list of values
        each item is a mechanism.value

    outputStateNames : list of strings
        each item is an outputState.name

    outputStateValues : list of values
        each item is an outputState.value
    """

    def __init__(self, owner, tuples_list:list):
        super().__init__()
        self.mech_tuples = tuples_list
        self.owner = owner
        for item in tuples_list:
            if not isinstance(item, MechanismTuple):
                raise MechanismError("The following item in the tuples_list arg of MechanismList()"
                                     " is not a MechanismTuple: {}".format(item))
        self.process_tuples = tuples_list

    def __getitem__(self, item):
        """Return specified mechanism in MechanismList
        """
        # return list(self.mech_tuples[item])[MECHANISM]
        return self.mech_tuples[item].mechanism

    def __setitem__(self, key, value):
        raise ("MyList is read only ")

    def __len__(self):
        return (len(self.mech_tuples))

    def _get_tuple_for_mech(self, mech):
        """Return first mechanism tuple containing specified mechanism from the list of mech_tuples
        """
        if list(item.mechanism for item in self.mech_tuples).count(mech):
            if self.owner.verbosePref:
                print("PROGRAM ERROR:  {} found in more than one mech_tuple in {} in {}".
                      format(append_type_to_name(mech), self.__class__.__name__, self.owner.name))
        return next((mech_tuple for mech_tuple in self.mech_tuples if mech_tuple.mechanism is mech), None)

    @property
    def mech_tuples_sorted(self):
        """Return list of mech_tuples sorted by mechanism name"""
        return sorted(self.mech_tuples, key=lambda mech_tuple: mech_tuple[0].name)

    @property
    def mechanisms(self):
        """Return list of all mechanisms in MechanismList"""
        return list(self)

    @property
    def names(self):
        """Return names of all mechanisms in MechanismList"""
        return list(item.name for item in self.mechanisms)

    @property
    def values(self):
        """Return values of all mechanisms in MechanismList"""
        return list(item.value for item in self.mechanisms)

    @property
    def outputStateNames(self):
        """Return names of all outputStates for all mechanisms in MechanismList"""
        names = []
        for item in self.mechanisms:
            for output_state in item.outputStates:
                names.append(output_state)
        return names

    @property
    def outputStateValues(self):
        """Return values of outputStates for all mechanisms in MechanismList"""
        values = []
        for item in self.mechanisms:
            for output_state_name, output_state in list(item.outputStates.items()):
                values.append(output_state.value)
        return values