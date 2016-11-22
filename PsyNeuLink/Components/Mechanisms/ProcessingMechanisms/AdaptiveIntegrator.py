# Princeton University licenses this file to You under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may obtain a copy of the License at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


# **************************************  AdaptiveIntegrator Mechanism *************************************************

"""
Overview
--------

An AdaptiveIntegrator mechanism integrates its input, possibly based on its prior values.  The input can be a single
scalar value or an array of scalars (list or 1d np.array).  The default function (:any:`Integrator`) can be
parameterized to implement either a simple increment rate, additive accumulator, or an (exponentially weighted)
time-averaging of its input.  It can also be assigned a custom function.

.. _AdaptiveIntegrator_Creation:

Creating an AdaptiveIntegrator
------------------------------

An AdaptiveIntegrator mechanism can be created either directly, by calling its constructor, or using the
:class:`mechanism` function and specifying "AdaptiveIntegrator" as its ``mech_spec`` argument.  Its function is
specified in the ``function`` argument, which can be parameterized by calling to its constructor with parameter values::

    my_time_averaging_mechanism = AdaptiveIntegrator(function=Integrator(weighting=TIME_AVERAGED, rate=0.5))

.. _AdaptiveIntegrator_Structure

Structure
---------

An AdaptiveIntegrator mechanism has a single inputState, the ``value`` of which is used as the ``variable`` for its
``function``.   The ``default_input_value`` argument specifies the format of the ``value`` (i.e., whether it is a
single scalar or an array), as well as the value to use if none is provided when mechanism is executed.  The default
``function`` is Integrator, with ``weighting=:keyword`TIME_AVERAGED```  and ``rate=0.5``.  However a custom function
can also be specified,  so long as it  takes a numeric value or  list or np.ndarray of numeric values as its input and
returns a value of the same type  and format.  The :any:`Integrator` function has two parameters (``weighting`` and
``rate``) that determine the type and,  well, yes, the *rate* of integration.  An AdaptiveIntegrator mechanism has a
single outputState that contains the result of the call to its ``function``.

.. _AdaptiveIntegrator_Execution

Execution
---------

When an AdaptiveIntegrator mechanism is executed, it carries out the specified integration, and assigns the
result to the ``value`` of its (primary) outputState.


.. _AdaptiveIntegrator_Class_Reference:

Class Reference
---------------

"""

from PsyNeuLink.Components.Mechanisms.ProcessingMechanisms.ProcessingMechanism import *

# AdaptiveIntegrator parameter keywords:
DEFAULT_RATE = 0.5

class AdaptiveIntegratorMechanismError(Exception):
    def __init__(self, error_value):
        self.error_value = error_value

    def __str__(self):
        return repr(self.error_value)


class AdaptiveIntegratorMechanism(ProcessingMechanism_Base):
    """
    AdaptiveIntegratorMechanism(                            \
    default_input_value=None,                               \
    function=Integrator(weighting=TIME_AVERAGED, rate=0.5), \
    time_scale=TimeScale.TRIAL,                             \
    params=None,                                            \
    name=None,                                              \
    prefs=None)

    Implements AdaptiveIntegrator subclass of Mechanism.

    COMMENT:
        Description:
            - DOCUMENT:

        Class attributes:
            + componentType (str): SigmoidLayer
            + classPreference (PreferenceSet): SigmoidLayer_PreferenceSet, instantiated in __init__()
            + classPreferenceLevel (PreferenceLevel): PreferenceLevel.TYPE
            + variableClassDefault (value):  SigmoidLayer_DEFAULT_BIAS
            + paramClassDefaults (dict): {TIME_SCALE: TimeScale.TRIAL,
                                          FUNCTION_PARAMS:{kwSigmoidLayer_Unitst: kwSigmoidLayer_NetInput
                                                                     kwSigmoidLayer_Gain: SigmoidLayer_DEFAULT_GAIN
                                                                     kwSigmoidLayer_Bias: SigmoidLayer_DEFAULT_BIAS}}
            + paramNames (dict): names as above

        Class methods:
            None

        MechanismRegistry:
            All instances of SigmoidLayer are registered in MechanismRegistry, which maintains an entry for the subclass,
              a count for all instances of it, and a dictionary of those instances

    COMMENT

    Arguments
    ---------

    default_input_value : number, list or np.ndarray
        the input to the mechanism to use if none is provided in a call to its ``execute`` or ``run`` methods;
        also serves as a template to specify the length of ``variable`` for ``function``, and the primary  outputState
        of the mechanism.

    function : TransferFunction : default Linear
        specifies function used to transform input;  can be :class:`Linear`, :class:`Logistic`, :class:`Exponential`,
        or a custom function.

    params : Optional[Dict[param keyword, param value]]
        a dictionary that can be used to specify the parameters for the mechanism, parameters for its function,
        and/or a custom function and its parameters (see :doc:`Mechanism` for specification of a parms dict).

    time_scale :  TimeScale : TimeScale.TRIAL
        specifies whether the mechanism is executed on the :keyword:`TIME_STEP` or :keyword:`TRIAL` time scale.
        This must be set to :keyword:`TimeScale.TIME_STEP` for the ``rate`` parameter to have an effect.

    name : str : default Transfer-<index>
        a string used for the name of the mechanism.
        If not is specified, a default is assigned by MechanismRegistry
        (see :doc:`Registry` for conventions used in naming, including for default and duplicate names).[LINK]

    prefs : Optional[PreferenceSet or specification dict : Process.classPreferences]
        the PreferenceSet for mechanism.
        If it is not specified, a default is assigned using ``classPreferences`` defined in __init__.py
        (see Description under PreferenceSet for details) [LINK].


    time_scale :  TimeScale : TimeScale.TRIAL
        specifies whether the mechanism is executed on the :keyword:`TIME_STEP` or :keyword:`TRIAL` time scale.
        This must be set to :keyword:`TimeScale.TIME_STEP` for the ``rate`` parameter to have an effect.


    Attributes
    ----------
    variable : value: default
        the input to mechanism's ``function``.

    time_scale :  TimeScale : defaul tTimeScale.TRIAL
        specifies whether the mechanism is executed on the :keyword:`TIME_STEP` or :keyword:`TRIAL` time scale.

    name : str : default Transfer-<index>
        a string used for the name of the mechanism.
        If not is specified, a default is assigned by MechanismRegistry
        (see :doc:`Registry` for conventions used in naming, including for default and duplicate names).[LINK]

    prefs : Optional[PreferenceSet or specification dict : Process.classPreferences]
        the PreferenceSet for mechanism.
        If it is not specified, a default is assigned using ``classPreferences`` defined in __init__.py
        (see Description under PreferenceSet for details) [LINK].

    """

    componentType = "SigmoidLayer"

    classPreferenceLevel = PreferenceLevel.TYPE
    # These will override those specified in TypeDefaultPreferences
    classPreferences = {
        kwPreferenceSetName: 'AdaptiveIntegratorMechanismCustomClassPreferences',
        kpReportOutputPref: PreferenceEntry(True, PreferenceLevel.INSTANCE)}

    # Sets template for variable (input)
    variableClassDefault = [[0]]

    paramClassDefaults = Mechanism_Base.paramClassDefaults.copy()
    paramClassDefaults.update({
        # TIME_SCALE: TimeScale.TRIAL,
        OUTPUT_STATES:[kwPredictionMechanismOutput]
    })

    # Set default input_value to default bias for SigmoidLayer
    paramNames = paramClassDefaults.keys()

    from PsyNeuLink.Components.Functions.Function import Integrator

    @tc.typecheck
    def __init__(self,
                 default_input_value=None,
                 function=Integrator(rate=0.5,
                                     weighting=TIME_AVERAGED),
                 time_scale=TimeScale.TRIAL,
                 params=None,
                 name=None,
                 prefs:is_pref_set=None,
                 context=None):
        """Assign type-level preferences, default input value (SigmoidLayer_DEFAULT_BIAS) and call super.__init__

        :param default_input_value: (value)
        :param params: (dict)
        :param name: (str)
        :param prefs: (PreferenceSet)
        """


        # Assign args to params and functionParams dicts (kwConstants must == arg names)
        params = self._assign_args_to_param_dicts(function=function, params=params)

        # if default_input_value is NotImplemented:
        #     default_input_value = SigmoidLayer_DEFAULT_NET_INPUT

        super(AdaptiveIntegratorMechanism, self).__init__(variable=default_input_value,
                                  params=params,
                                  name=name,
                                  prefs=prefs,
                                  context=self)

        # IMPLEMENT: INITIALIZE LOG ENTRIES, NOW THAT ALL PARTS OF THE MECHANISM HAVE BEEN INSTANTIATED




