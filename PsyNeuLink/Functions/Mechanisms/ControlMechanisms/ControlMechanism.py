# Princeton University licenses this file to You under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may obtain a copy of the License at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.
#
#
# **************************************  ControlMechanism ************************************************
#

# IMPLEMENTATION NOTE: COPIED FROM DefaultProcessingMechanism;
#                      ADD IN GENERIC CONTROL STUFF FROM DefaultControlMechanism

from collections import OrderedDict

from PsyNeuLink.Functions.Mechanisms.Mechanism import Mechanism_Base
from PsyNeuLink.Functions.ShellClasses import *


ControlMechanismRegistry = {}


class ControlMechanismError(Exception):
    def __init__(self, error_value):
        self.error_value = error_value


class ControlMechanism_Base(Mechanism_Base):
    """Abstract class for control mechanism subclasses

    Description:
# DOCUMENTATION NEEDED:
    .instantiate_control_signal_projection INSTANTIATES OUTPUT STATE FOR EACH CONTROL SIGNAL ASSIGNED TO THE INSTANCE
    .EXECUTE MUST BE OVERRIDDEN BY SUBCLASS
    WHETHER AND HOW MONITORING INPUT STATES ARE INSTANTIATED IS UP TO THE SUBCLASS

# PROTOCOL FOR ASSIGNING DefaultController (defined in Functions.__init__.py)
#    Initial assignment is to SystemDefaultCcontroller (instantiated and assigned in Functions.__init__.py)
#    When any other ControlMechanism is instantiated, if its params[kwMakeDefaultController] == True
#        then its take_over_as_default_controller method is called in instantiate_attributes_after_function()
#        which moves all ControlSignal Projections from DefaultController to itself, and deletes them there
# params[kwMontioredStates]: Determines which states will be monitored.
#        can be a list of Mechanisms, OutputStates, a MonitoredOutputStatesOption, or a combination
#        if MonitoredOutputStates appears alone, it will be used to determine how states are assigned from system.graph by default
#        TBI: if it appears in a tuple with a Mechanism, or in the Mechamism's params list, it applied to just that mechanism
        + kwMonitoredOutputStates (list): (default: PRIMARY_OUTPUT_STATES)
            specifies the outputStates of the terminal mechanisms in the System to be monitored by ControlMechanism
            this specification overrides any in System.params[], but can be overridden by Mechanism.params[]
            each item must be one of the following:
                + Mechanism or OutputState (object)
                + Mechanism or OutputState name (str)
                + (Mechanism or OutputState specification, exponent, weight) (tuple):
                    + mechanism or outputState specification (Mechanism, OutputState, or str):
                        referenceto Mechanism or OutputState object or the name of one
                        if a Mechanism ref, exponent and weight will apply to all outputStates of that mechanism
                    + exponent (int):  will be used to exponentiate outState.value when computing EVC
                    + weight (int): will be used to multiplicative weight outState.value when computing EVC
                + MonitoredOutputStatesOption (AutoNumber enum):
                    + PRIMARY_OUTPUT_STATES:  monitor only the primary (first) outputState of the Mechanism
                    + ALL_OUTPUT_STATES:  monitor all of the outputStates of the Mechanism
                    Notes:
                    * this option applies to any mechanisms specified in the list for which no outputStates are listed;
                    * it is overridden for any mechanism for which outputStates are explicitly listed

    Class attributes:
        + functionType (str): System Default Mechanism
        + paramClassDefaults (dict):
            # + kwInputStateValue: [0]
            # + kwOutputStateValue: [1]
            + kwFunction: Linear
            + kwFunctionParams:{kwSlope:1, kwIntercept:0}

    Instance methods:
    - validate_params(request_set, target_set, context):
    - validate_monitoredstates_spec(state_spec, context):
    - instantiate_attributes_before_function(context):
    - instantiate_attributes_after_function(context):
    - take_over_as_default_controller(context):
    - instantiate_control_signal_projection(projection, context):
        adds outputState, and assigns as sender of to requesting ControlSignal Projection
    - execute(time_scale, runtime_params, context):
    - inspect(): prints monitored OutputStates and mechanism parameters controlled

    Instance attributes:
    - allocationPolicy (np.arry): controlSignal intensity for controlSignals associated with each outputState
    - controlSignalCosts (np.array):  current cost for controlSignals associated with each outputState
    """

    functionType = "ControlMechanism"

    initMethod = INIT_FUNCTION_METHOD_ONLY


    classPreferenceLevel = PreferenceLevel.TYPE
    # Any preferences specified below will override those specified in TypeDefaultPreferences
    # Note: only need to specify setting;  level will be assigned to TYPE automatically
    # classPreferences = {
    #     kwPreferenceSetName: 'ControlMechanismClassPreferences',
    #     kp<pref>: <setting>...}

    # variableClassDefault = defaultControlAllocation
    # This must be a list, as there may be more than one (e.g., one per controlSignal)
    variableClassDefault = [defaultControlAllocation]

    from PsyNeuLink.Functions.Utility import Linear
    paramClassDefaults = Mechanism_Base.paramClassDefaults.copy()
    paramClassDefaults.update({
        kwFunction:Linear,
        kwFunctionParams:{Linear.kwSlope:1, Linear.kwIntercept:0},
        kwControlSignalProjections: None
    })

    def __init__(self,
                 default_input_value=NotImplemented,
                 params=NotImplemented,
                 name=NotImplemented,
                 prefs=NotImplemented,
                 context=NotImplemented):
        """Abstract class for system control mechanisms

        :param default_input_value: (value)
        :param params: (dict)
        :param name: (str)
        :param prefs: (PreferenceSet)
        """

        # Assign functionType to self.name as default;
        #  will be overridden with instance-indexed name in call to super
        if name is NotImplemented:
            self.name = self.functionType

        self.functionName = self.functionType
        # self.controlSignalChannels = OrderedDict()
        self.system = None

        super(ControlMechanism_Base, self).__init__(variable=default_input_value,
                                                          params=params,
                                                          name=name,
                                                          prefs=prefs,
                                                          context=self)

    def validate_params(self, request_set, target_set=NotImplemented, context=NotImplemented):
        """Validate kwSystem, kwMonitoredOutputStates and kwFunctionParams

        If kwSystem is not specified:
        - OK if controller is DefaultControlMechanism
        - otherwise, raise an exception
        Check that all items in kwMonitoredOutputStates are Mechanisms or OutputStates for Mechanisms in self.system
        Check that len(kwWeights) = len(kwMonitoredOutputStates)
        """

        # DefaultController does not require a system specification
        #    (it simply passes the defaultControlAllocation for default ConrolSignal Projections)
        from PsyNeuLink.Functions.Mechanisms.ControlMechanisms.DefaultControlMechanism import DefaultControlMechanism
        if isinstance(self,DefaultControlMechanism):
            pass

        # For all other ControlMechanisms, validate System specification
        elif not isinstance(request_set[kwSystem], System):
            raise ControlMechanismError("A system must be specified in the kwSystem param to instantiate {0}".
                                              format(self.name))
        self.paramClassDefaults[kwSystem] = request_set[kwSystem]

        super(ControlMechanism_Base, self).validate_params(request_set=request_set,
                                                                 target_set=target_set,
                                                                 context=context)

    def validate_monitored_state_spec(self, state_spec, context=NotImplemented):
        """Validate specified outputstate is for a Mechanism in the System

        Called by both self.validate_params() and self.add_monitored_state() (in ControlMechanism)
        """
        super(ControlMechanism_Base, self).validate_monitored_state(state_spec=state_spec, context=context)

        # Get outputState's owner
        from PsyNeuLink.Functions.States.OutputState import OutputState
        if isinstance(state_spec, OutputState):
            state_spec = state_spec.owner

        # Confirm it is a mechanism in the system
        if not state_spec in self.system.mechanisms:
            raise ControlMechanismError("Request for controller in {0} to monitor the outputState(s) of "
                                              "a mechanism ({1}) that is not in {2}".
                                              format(self.system.name, state_spec.name, self.system.name))

        # Warn if it is not a terminalMechanism
        if not state_spec in self.system.terminalMechanisms.mechanisms:
            if self.prefs.verbosePref:
                print("Request for controller in {0} to monitor the outputState(s) of a mechanism ({1}) that is not"
                      " a terminal mechanism in {2}".format(self.system.name, state_spec.name, self.system.name))

    def instantiate_attributes_before_function(self, context=NotImplemented):
        """Instantiate self.system

        Assign self.system
        """
        self.system = self.paramsCurrent[kwSystem]
        super().instantiate_attributes_before_function(context=context)

    def instantiate_monitored_output_states(self, context=NotImplemented):
        raise ControlMechanismError("{0} (subclass of {1}) must implement instantiate_monitored_output_states".
                                          format(self.__class__.__name__,
                                                 self.__class__.__bases__[0].__name__))

    def instantiate_control_mechanism_input_state(self, input_state_name, input_state_value, context=NotImplemented):
        """Instantiate inputState for ControlMechanism

        Extend self.variable by one item to accommodate new inputState
        Instantiate an inputState using input_state_name and input_state_value
        Update self.inputState and self.inputStates

        Args:
            input_state_name (str):
            input_state_value (2D np.array):
            context:

        Returns:
            input_state (InputState):

        """
        # Extend self.variable to accommodate new inputState
        if self.variable is None:
            self.variable = np.atleast_2d(input_state_value)
        else:
            self.variable = np.append(self.variable, np.atleast_2d(input_state_value), 0)
        variable_item_index = self.variable.size-1

        # Instantiate inputState
        from PsyNeuLink.Functions.States.State import instantiate_state
        from PsyNeuLink.Functions.States.InputState import InputState
        input_state = instantiate_state(owner=self,
                                                  state_type=InputState,
                                                  state_name=input_state_name,
                                                  state_spec=defaultControlAllocation,
                                                  state_params=None,
                                                  constraint_value=np.array(self.variable[variable_item_index]),
                                                  constraint_value_name='Default control allocation',
                                                  context=context)

        #  Update inputState and inputStates
        try:
            self.inputStates[input_state_name] = input_state
        except AttributeError:
            self.inputStates = OrderedDict({input_state_name:input_state})
            self.inputState = list(self.inputStates.values())[0]
        return input_state

    def instantiate_attributes_after_function(self, context=NotImplemented):
        """Take over as default controller (if specified) and implement any specified ControlSignal projections

        """

        try:
            # If specified as DefaultController, reassign ControlSignal projections from DefaultController
            if self.paramsCurrent[kwMakeDefaultController]:
                self.take_over_as_default_controller(context=context)
        except KeyError:
            pass

        # If controlSignal projections were specified, implement them
        try:
            if self.paramsCurrent[kwControlSignalProjections]:
                for key, projection in self.paramsCurrent[kwControlSignalProjections].items():
                    self.instantiate_control_signal_projection(projection, context=self.name)
        except:
            pass

    def take_over_as_default_controller(self, context=NotImplemented):

        from PsyNeuLink.Functions import DefaultController

        # Iterate through old controller's outputStates
        to_be_deleted_outputStates = []
        for outputState in DefaultController.outputStates:

            # Iterate through projections sent for outputState
            for projection in DefaultController.outputStates[outputState].sendsToProjections:

                # Move ControlSignal projection to self (by creating new outputState)
                # IMPLEMENTATION NOTE: Method 1 -- Move old ControlSignal Projection to self
                #    Easier to implement
                #    - call instantiate_control_signal_projection directly here (which takes projection as arg)
                #        instead of instantiating a new ControlSignal Projection (more efficient, keeps any settings);
                #    - however, this bypasses call to Projection.instantiate_sender()
                #        which calls Mechanism.sendsToProjections.append(),
                #        so need to do that in instantiate_control_signal_projection
                #    - this is OK, as it is case of a Mechanism managing its *own* projections list (vs. "outsider")
                self.instantiate_control_signal_projection(projection, context=context)

                # # IMPLEMENTATION NOTE: Method 2 - Instantiate new ControlSignal Projection
                # #    Cleaner, but less efficient and ?? may lose original params/settings for ControlSignal
                # # TBI: Implement and then use Mechanism.add_project_from_mechanism()
                # self.add_projection_from_mechanism(projection, new_output_state, context=context)

                # Remove corresponding projection from old controller
                DefaultController.outputStates[outputState].sendsToProjections.remove(projection)

            # Current controller's outputState has no projections left (after removal(s) above)
            if not DefaultController.outputStates[outputState].sendsToProjections:
                # If this is the old controller's primary outputState, set it to None
                if DefaultController.outputState is DefaultController.outputStates[outputState]:
                    DefaultController.outputState = None
                # Delete outputState from old controller's outputState dict
                to_be_deleted_outputStates.append(DefaultController.outputStates[outputState])
        for item in to_be_deleted_outputStates:
            del DefaultController.outputStates[item.name]

    def instantiate_control_signal_projection(self, projection, context=NotImplemented):
        """Add outputState and assign as sender to requesting controlSignal projection

        Updates allocationPolicy and controlSignalCosts attributes to accomodate instantiated projection

        Args:
            projection:
            context:

        Returns state: (OutputState)

        """

        from PsyNeuLink.Functions.Projections.ControlSignal import ControlSignal
        if not isinstance(projection, ControlSignal):
            raise ControlMechanismError("PROGRAM ERROR: Attempt to assign {0}, "
                                              "that is not a ControlSignal Projection, to outputState of {1}".
                                              format(projection, self.name))

        output_name = projection.receiver.name + '_ControlSignal' + '_Output'

        #  Update self.value by evaluating function
        self.update_value(context=context)
        # IMPLEMENTATION NOTE: THIS ASSUMED THAT self.value IS AN ARRAY OF OUTPUT STATE VALUES, BUT IT IS NOT
        #                      RATHER, IT IS THE OUTPUT OF THE EXECUTE METHOD (= EVC OF monitoredOutputStates)
        #                      SO SHOULD ALWAYS HAVE LEN = 1 (INDEX = 0)
        #                      self.allocationPolicy STORES THE outputState.value(s)
        output_item_index = len(self.value)-1
        output_value = self.value[output_item_index]

        # Instantiate outputState for self as sender of ControlSignal
        from PsyNeuLink.Functions.States.State import instantiate_state
        from PsyNeuLink.Functions.States.OutputState import OutputState
        state = instantiate_state(owner=self,
                                            state_type=OutputState,
                                            state_name=output_name,
                                            state_spec=defaultControlAllocation,
                                            state_params=None,
                                            constraint_value=output_value,
                                            constraint_value_name='Default control allocation',
                                            # constraint_index=output_item_index,
                                            context=context)

        projection.sender = state

        # Update allocationPolicy to accommodate instantiated projection and add output_value
        try:
            self.allocationPolicy = np.append(self.self.allocationPolicy, np.atleast_2d(output_value, 0))
        except AttributeError:
            self.allocationPolicy = np.atleast_2d(output_value)

        # Update self.outputState and self.outputStates
        try:
            self.outputStates[output_name] = state
        except AttributeError:
            self.outputStates = OrderedDict({output_name:state})
            self.outputState = self.outputStates[output_name]

        # Add projection to list of outgoing projections
        state.sendsToProjections.append(projection)

        # Update controlSignalCosts to accommodate instantiated projection
        try:
            self.controlSignalCosts = np.append(self.controlSignalCosts, np.empty((1,1)),axis=0)
        except AttributeError:
            self.controlSignalCosts = np.empty((1,1))

        return state

    def __execute__(self, time_scale=TimeScale.TRIAL, runtime_params=NotImplemented, context=NotImplemented):
        """Updates controlSignals based on inputs

        Must be overriden by subclass
        """
        raise ControlMechanismError("{0} must implement execute() method".format(self.__class__.__name__))

    def inspect(self):

        print ("\n---------------------------------------------------------")

        print ("\n{0}".format(self.name))
        print("\n\tMonitoring the following mechanism outputStates:")
        for state_name, state in list(self.inputStates.items()):
            for projection in state.receivesFromProjections:
                monitored_state = projection.sender
                monitored_state_mech = projection.sender.owner
                monitored_state_index = self.monitoredOutputStates.index(monitored_state)
                exponent = self.paramsCurrent[kwFunctionParams][kwExponents][monitored_state_index]
                weight = self.paramsCurrent[kwFunctionParams][kwWeights][monitored_state_index]
                print ("\t\t{0}: {1} (exp: {2}; wt: {3})".
                       format(monitored_state_mech.name, monitored_state.name, exponent, weight))

        print ("\n\tControlling the following mechanism parameters:".format(self.name))
        for state_name, state in list(self.outputStates.items()):
            for projection in state.sendsToProjections:
                print ("\t\t{0}: {1}".format(projection.receiver.owner.name, projection.receiver.name))

        print ("\n---------------------------------------------------------")