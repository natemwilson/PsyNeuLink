# Princeton University licenses this file to You under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may obtain a copy of the License at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.
#
#
# **********************************************  Projection ***********************************************************
#
from PsyNeuLink.Functions.ShellClasses import *
from PsyNeuLink.Functions.Utility import *
from PsyNeuLink.Globals.Registry import register_category
from collections import OrderedDict

ProjectionRegistry = {}

kpProjectionTimeScaleLogEntry = "Projection TimeScale"


class ProjectionError(Exception):
    def __init__(self, error_value):
        self.error_value = error_value

    def __str__(self):
        return repr(self.error_value)

# Projection factory method:
# def projection(name=NotImplemented, params=NotImplemented, context=NotImplemented):
#         """Instantiates default or specified subclass of Projection
#
#         If called w/o arguments or 1st argument=NotImplemented, instantiates default subclass (ParameterState)
#         If called with a name string:
#             - if registered in ProjectionRegistry class dictionary as name of a subclass, instantiates that class
#             - otherwise, uses it as the name for an instantiation of the default subclass, and instantiates that
#         If a params dictionary is included, it is passed to the subclass
#
#         :param name:
#         :param param_defaults:
#         :return:
#         """
#
#         # Call to instantiate a particular subclass, so look up in MechanismRegistry
#         if name in ProjectionRegistry:
#             return ProjectionRegistry[name].mechanismSubclass(params)
#         # Name is not in MechanismRegistry or is not provided, so instantiate default subclass
#         else:
#             # from Functions.Defaults import DefaultProjection
#             return DefaultProjection(name, params)
#

class Projection_Base(Projection):
    """Abstract class definition for Projection category of Function class (default type:  Mapping)

    Description:
        Projections are used as part of a configuration (together with projections) to execute a process
        Each instance must have:
        - a sender: State object from which it gets its input (serves as variable argument of the Function);
            if this is not specified, paramClassDefaults[kwProjectionSender] is used to assign a default
        - a receiver: State object to which it projects;  this MUST be specified
        - an execute method that executes the projection:
            this can be implemented as <class>.function, or specified as a reference to a method in params[kwExecuteMethod]
        - a set of parameters: determine the operation of its execute method
        The default projection type is a Mapping projection

    Subclasses:
        There are two [TBI: three] standard subclasses of Projection:
        - Mapping: uses a function to convey the State from sender to the inputState of a receiver
        - ControlSignal:  takes an allocation as input (sender) and uses it to modulate the controlState of the receiver
        [- TBI: Gating: takes an input signal and uses it to modulate the inputState and/or outputState of the receiver

    Instantiation:
        Projections should NEVER be instantiated by a direct call to the class
           (since there is no obvious default), but rather by calls to the subclass
        Subclasses can be instantiated in one of three ways:
            - call to __init__ with args to subclass for sender, receiver and (optional) params dict:
                - sender (Mechanism or State):
                    this is used if kwProjectionParam is same as default
                    sender.value used as variable for Projection.execute method
                - receiver (Mechanism or State)
                NOTES:
                    if sender and/or receiver is a Mechanism, the appropriate State is inferred as follows:
                        Mapping projection:
                            sender = <Mechanism>.outputState
                            receiver = <Mechanism>.inputState
                        ControlSignal projection:
                            sender = <Mechanism>.outputState
                            receiver = <Mechanism>.paramsCurrent[<param>] IF AND ONLY IF there is a single one
                                        that is a ParameterState;  otherwise, an exception is raised
                - params (dict):
                    + kwProjectionSender:<Mechanism or State class reference or object>:
                        this is populated by __init__ with the default sender state for each subclass
                        it is used if sender arg is not provided (see above)
                        if it is different than the default, it overrides the sender arg even if that is provided
                    + kwProjectionSenderValue:<value>  - use to instantiate ProjectionSender
            - specification dict, that includes params (above), and the following two additional params
                    + kwProjectionType
                    + kwProjectionParams
            - as part of the instantiation of a State (see State);
                the State will be assigned as the projection's receiver
            * Note: the projection will be added to it's sender's State.sendsToProjections attribute

    ProjectionRegistry:
        All Projections are registered in ProjectionRegistry, which maintains a dict for each subclass,
          a count for all instances of that type, and a dictionary of those instances

    Naming:
        Projections can be named explicitly (using the name='<name>' argument).  If the argument is omitted,
        it will be assigned the subclass name with a hyphenated, indexed suffix ('subclass.name-n')

    Class attributes:
        + functionCategory (str): kwProjectionFunctionCategory
        + className (str): kwProjectionFunctionCategory
        + suffix (str): " <className>"
        + registry (dict): ProjectionRegistry
        + classPreference (PreferenceSet): ProjectionPreferenceSet, instantiated in __init__()
        + classPreferenceLevel (PreferenceLevel): PreferenceLevel.CATEGORY
        + variableClassDefault (value): [0]
        + requiredParamClassDefaultTypes = {kwProjectionSender: [str, Mechanism, State]}) # Default sender type
        + paramClassDefaults (dict)
        + paramNames (dict)
        + kwExecuteMethod (Function class or object, or method)

    Class methods:
        None

    Instance attributes:
        + sender (State) - State (belonging to a Mechanims) from which projection receives input
        + receiver (State) - State (belong to Mechanism or Projection) to which projection sends input
        + params (dict) - set currently in effect
        + paramsCurrent (dict) - current value of all params for instance (created and validated in Functions init)
        + paramInstanceDefaults (dict) - defaults for instance (created and validated in Functions init)
        + paramNames (list) - list of keys for the params in paramInstanceDefaults
        + value (value) - output of execute method
        + name (str) - if it is not specified as an arg, a default based on the class is assigned in register_category
        + prefs (PreferenceSet) - if not specified as an arg, default is created by copying ProjectionPreferenceSet

    Instance methods:
        # The following method MUST be overridden by an implementation in the subclass:
        - execute:
            - called by <Projection>reciever.owner.update_states_and_execute()
            - must be implemented by Projection subclass, or an exception is raised
        - add_to(receiver, state, context=NotImplemented):
            - instantiates self as projectoin to specified receiver.state
    """

    color = 0

    functionCategory = kwProjectionFunctionCategory
    className = functionCategory
    suffix = " " + className

    registry = ProjectionRegistry

    classPreferenceLevel = PreferenceLevel.CATEGORY

    variableClassDefault = [0]

    requiredParamClassDefaultTypes = Function.requiredParamClassDefaultTypes.copy()
    requiredParamClassDefaultTypes.update({kwProjectionSender: [str, Mechanism, State]}) # Default sender type

    def __init__(self,
                 receiver,
                 sender=NotImplemented,
                 params=NotImplemented,
                 name=NotImplemented,
                 prefs=NotImplemented,
                 context=NotImplemented):
        """Assign sender, receiver, and execute method and register mechanism with ProjectionRegistry

        This is an abstract class, and can only be called from a subclass;
           it must be called by the subclass with a context value

# DOCUMENT:  MOVE TO ABOVE, UNDER INSTANTIATION
        Initialization arguments:
            - sender (Mechanism, State or dict):
                specifies source of input to projection (default: senderDefault)
            - receiver (Mechanism, State or dict)
                 destination of projection (default: none)
            - params (dict) - dictionary of projection params:
                + kwExecuteMethod:<method>
        - name (str): if it is not specified, a default based on the class is assigned in register_category,
                            of the form: className+n where n is the n'th instantiation of the class
            - prefs (PreferenceSet or specification dict):
                 if it is omitted, a PreferenceSet will be constructed using the classPreferences for the subclass
                 dict entries must have a preference keyPath as key, and a PreferenceEntry or setting as their value
                 (see Description under PreferenceSet for details)
            - context (str): must be a reference to a subclass, or an exception will be raised

        NOTES:
        * Receiver is required, since can't instantiate a Projection without a receiving State
        * If sender and/or receiver is a Mechanism, the appropriate State is inferred as follows:
            Mapping projection:
                sender = <Mechanism>.outputState
                receiver = <Mechanism>.inputState
            ControlSignal projection:
                sender = <Mechanism>.outputState
                receiver = <Mechanism>.paramsCurrent[<param>] IF AND ONLY IF there is a single one
                            that is a ParameterState;  otherwise, an exception is raised
        * instantiate_sender, instantiate_receiver must be called before instantiate_execute_method:
            - validate_params must be called before instantiate_sender, as it validates kwProjectionSender
            - instantatiate_sender may alter self.variable, so it must be called before validate_execute_method
            - instantatiate_receiver must be called before validate_execute_method,
                 as the latter evaluates receiver.value to determine whether to use self.execute or kwExecuteMethod
        * If variable is incompatible with sender's output, it is set to match that and revalidated (instantiate_sender)
        * if kwExecuteMethod is provided but its output is incompatible with receiver value, self.execute is tried
        * registers projection with ProjectionRegistry

        :param sender: (State or dict)
        :param receiver: (State or dict)
        :param param_defaults: (dict)
        :param name: (str)
        :param context: (str)
        :return: None
        """

        if not isinstance(context, Projection_Base):
            raise ProjectionError("Direct call to abstract class Projection() is not allowed; "
                                 "use projection() or one of the following subclasses: {0}".
                                 format(", ".join("{!s}".format(key) for (key) in ProjectionRegistry.keys())))

        # Assign functionType to self.name as default;
        #  will be overridden with instance-indexed name in call to super
        if name is NotImplemented:
            self.name = self.functionType
        # Not needed:  handled by subclass
        # else:
        #     self.name = name

        self.functionName = self.functionType

        register_category(self, Projection_Base, ProjectionRegistry, context=context)

# FIX: 6/23/16 NEEDS ATTENTION *******************************************************A
#      NOTE: SENDER IS NOT YET KNOWN FOR DEFAULT controlSignal
#      WHY IS self.sender IMPLEMENTED BY sender IS NOT??

        self.sender = sender
        self.receiver = receiver

# MODIFIED 6/12/16:  VARIABLE & SENDER ASSIGNMENT MESS:
        # ADD validate_variable, THAT CHECKS FOR SENDER?
        # WHERE DOES DEFAULT SENDER GET INSTANTIATED??
        # VARIABLE ASSIGNMENT SHOULD OCCUR AFTER THAT

# MODIFIED 6/12/16:  ADDED ASSIGNMENT HERE -- BUT SHOULD GET RID OF IT??
        # AS ASSIGNMENT SHOULD BE DONE IN VALIDATE_VARIABLE, OR WHEREVER SENDER IS DETERMINED??
# FIX:  NEED TO KNOW HERE IF SENDER IS SPECIFIED AS A MECHANISM OR STATE
        try:
            variable = sender.value
        except:
            if self.receiver.prefs.verbosePref:
                print("Unable to get value of sender ({0}) for {1};  will assign default ({2})".
                      format(sender, self.name, self.variableClassDefault))
            variable = NotImplemented

# FIX: SHOULDN'T variable_default HERE BE sender.value ??  AT LEAST FOR Mapping?, WHAT ABOUT ControlSignal??
# FIX:  ?LEAVE IT TO VALIDATE_VARIABLE, SINCE SENDER MAY NOT YET HAVE BEEN INSTANTIATED
# MODIFIED 6/12/16:  ADDED ASSIGNMENT ABOVE
#                   (TO HANDLE INSTANTIATION OF DEFAULT ControlSignal SENDER -- BUT WHY ISN'T VALUE ESTABLISHED YET?
        # Validate variable, execute method and params, and assign params to paramsInstanceDefaults
        # Note: pass name of mechanism (to override assignment of functionName in super.__init__)
        super(Projection_Base, self).__init__(variable_default=variable,
                                              param_defaults=params,
                                              name=self.name,
                                              prefs=prefs,
                                              context=context.__class__.__name__)

        self.paramNames = self.paramInstanceDefaults.keys# ()

    def validate_params(self, request_set, target_set=NotImplemented, context=NotImplemented):
        """Validate kwProjectionSender and/or sender arg (current self.sender), and assign one of them as self.sender

        Check:
        - that kwProjectionSender is a Mechanism or State
        - if it is different from paramClassDefaults[kwProjectionSender], use it
        - if it is the same or is invalid, check if sender arg was provided to __init__ and is valid
        - if sender arg is valid use it (if kwProjectionSender can't be used);
        - otherwise use paramClassDefaults[kwProjectionSender]
        - when done, sender is assigned to self.sender

        Note: check here only for sender's type, NOT content (e.g., length, etc.); that is done in instantiate_sender

        :param request_set:
        :param target_set:
        :param context:
        :return:
        """

        super(Projection, self).validate_params(request_set, target_set, context)

        try:
            sender_param = target_set[kwProjectionSender]
        except KeyError:
            # This should never happen, since kwProjectionSender is a required param
            raise ProjectionError("Program error: required param {0} missing in {1}".
                                  format(kwProjectionSender, self.name))

        # kwProjectionSender is either an instance or class of Mechanism or State:
        if (isinstance(sender_param, (Mechanism, State)) or
                (inspect.isclass(sender_param) and
                     (issubclass(sender_param, Mechanism) or issubclass(sender_param, State)))):
            # it is NOT the same as the default, use it
            if sender_param is not self.paramClassDefaults[kwProjectionSender]:
                self.sender = sender_param
            # it IS the same as the default, but sender arg was not provided, so use it (= default):
            elif self.sender is NotImplemented:
                self.sender = sender_param
                if self.prefs.verbosePref:
                    print("Neither {0} nor sender arg was provided for {1} projection to {2}; "
                          "default ({3}) will be used".format(kwProjectionSender,
                                                              self.name,
                                                              self.receiver.owner.name,
                                                              sender_param.__class__.__name__))
            # it IS the same as the default, so check if sender arg (self.sender) is valid
            elif not (isinstance(self.sender, (Mechanism, State, Process)) or
                          (inspect.isclass(self.sender) and
                               (issubclass(self.sender, Mechanism) or issubclass(self.sender, State)))):
                # sender arg (self.sender) is not valid, so use kwProjectionSender (= default)
                self.sender = sender_param
                if self.prefs.verbosePref:
                    print("{0} was not provided for {1} projection to {2}, and sender arg ({3}) is not valid; "
                          "default ({4}) will be used".format(kwProjectionSender,
                                                              self.name,
                                                              self.receiver.owner.name,
                                                              self.sender,
                                                              sender_param.__class__.__name__))

# FIX: IF PROJECTION, PUT HACK HERE TO ACCEPT AND FORGO ANY FURTHER PROCESSING??
            # IS the same as the default, and sender arg was provided, so use sender arg
            else:
                pass
        # kwProjectionSender is not valid, and:
        else:
            # sender arg was not provided, use paramClassDefault
            if self.sender is NotImplemented:
                self.sender = self.paramClassDefaults[kwProjectionSender]
                if self.prefs.verbosePref:
                    print("{0} ({1}) is invalid and sender arg ({2}) was not provided; default {3} will be used".
                          format(kwProjectionSender, sender_param, self.sender,
                                 self.paramClassDefaults[kwProjectionSender]))
            # sender arg is also invalid, so use paramClassDefault
            elif not isinstance(self.sender, (Mechanism, State)):
                self.sender = self.paramClassDefaults[kwProjectionSender]
                if self.prefs.verbosePref:
                    print("Both {0} ({1}) and sender arg ({2}) are both invalid; default {3} will be used".
                          format(kwProjectionSender, sender_param, self.sender,
                                 self.paramClassDefaults[kwProjectionSender]))
            else:
                self.sender = self.paramClassDefaults[kwProjectionSender]
                if self.prefs.verbosePref:
                    print("{0} ({1}) is invalid; sender arg ({2}) will be used".
                          format(kwProjectionSender, sender_param, self.sender))
            if not isinstance(self.paramClassDefaults[kwProjectionSender], (Mechanism, State)):
                raise ProjectionError("Program error: {0} ({1}) and sender arg ({2}) for {3} are both absent or invalid"
                                      " and default (paramClassDefault[{4}]) is also invalid".
                                      format(kwProjectionSender,
                                             # sender_param.__name__,
                                             # self.sender.__name__,
                                             # self.paramClassDefaults[kwProjectionSender].__name__))
                                             sender_param,
                                             self.sender,
                                             self.name,
                                             self.paramClassDefaults[kwProjectionSender]))

    def instantiate_attributes_before_execute_method(self, context=NotImplemented):
        self.instantiate_sender(context=context)

    def instantiate_sender(self, context=NotImplemented):
        """Assign self.sender to outputState of sender and insure compatibility with self.variable

        Assume self.sender has been assigned in validate_params, from either sender arg or kwProjectionSender
        Validate, set self.variable, and assign projection to sender's sendsToProjections attribute

        If self.sender is a Mechanism, re-assign it to <Mechanism>.outputState
        If self.sender is a State class reference, validate that it is a OutputState
        Assign projection to sender's sendsToProjections attribute
        If self.value / self.variable is NotImplemented, set to sender.value

        Notes:
        * ControlSignal initially overrides this method to check if sender is DefaultControlMechanism;
            if so, it assigns a ControlSignal-specific inputState, outputState and ControlSignalChannel to it
        [TBI: * LearningSignal overrides this method to check if sender is kwDefaultSender;
            if so, it instantiates a default MonitoringMechanism and a projection to it from receiver's outputState]

        :param context: (str)
        :return:
        """

        from PsyNeuLink.Functions.States.OutputState import OutputState

        # If sender is a class, instantiate it:
        # - assume it is Mechanism or State (as validated in validate_params)
        # - implement default sender of the corresponding type
        if inspect.isclass(self.sender):
            if issubclass(self.sender, OutputState):
                self.sender = self.paramsCurrent[kwProjectionSender](self.paramsCurrent[kwProjectionSenderValue])
            else:
                raise ProjectionError("Sender ({0}, for {1}) must be a OutputState".
                                      format(self.sender.__class__.__name__, self.name))


        # # If sender is a Mechanism (rather a State), get relevant outputState and assign to self.sender
        if isinstance(self.sender, Mechanism):

            # # IMPLEMENT: HANDLE MULTIPLE SENDER -> RECEIVER MAPPINGS, EACH WITH ITS OWN MATRIX:
            # #            - kwMATRIX NEEDS TO BE A 3D np.array, EACH 3D ITEM OF WHICH IS A 2D WEIGHT MATRIX
            # #            - MAKE SURE len(self.sender.value) == len(self.receiver.inputStates.items())
            # # for i in range (len(self.sender.value)):
            # #            - CHECK EACH MATRIX AND ASSIGN??
            # # FOR NOW, ASSUME SENDER HAS ONLY ONE OUTPUT STATE, AND THAT RECEIVER HAS ONLY ONE INPUT STATE
            self.sender = self.sender.outputState

        # At this point, self.sender should be a OutputState
        if not isinstance(self.sender, OutputState):
            raise ProjectionError("Sender for Mapping projection must be a Mechanism or State")

        # FIX: THIS SHOULD BE HANDLED LIKE receivesFromProjections:  METHOD CALLED ON OWNER OF STATE
        # Assign projection to sender's sendsToProjections list attribute
        self.sender.sendsToProjections.append(self)

        # Validate projection's variable (self.variable) against sender.outputState.value
        if iscompatible(self.variable, self.sender.value):
            # Is compatible, so assign sender.outputState.value to self.variable
            self.variable = self.sender.value

        else:
            # Not compatible, so:
            # - issue warning
            if self.prefs.verbosePref:
                print("The variable ({0}) of {1} projection to {2} is not compatible with output ({3})"
                      " of execute method {4} for sender ({5}); it has been reassigned".
                      format(self.variable,
                             self.name,
                             self.receiver.owner.name,
                             self.sender.value,
                             self.sender.execute.__class__.__name__,
                             self.sender.owner.name))
            # - reassign self.variable to sender.value
            self.assign_defaults(variable=self.sender.value, context=context)

    def instantiate_execute_method(self, context=NotImplemented):
        """Insure that output of execute method is compatible with the receiver's value

        Note:
        - this is called after super.validate_execute_method, self.instantiate_sender and self.instantiate_receiver
        - it overrides super.instantiate_execute_method

        Check if self.execute exists and, if so:
            save it and self.value
        Call super.instantiate_execute_method to instantiate params[kwExecuteMethod] if it is specified
        Check if self.value is compatible with receiver.variable; if it:
            IS compatible, return
            is NOT compatible:
                if self.execute is not implemented, raise exception
                if self.execute is implemented:
                    restore self.execute and check whether it is compatible with receiver.variable;  if it:
                        IS compatible, issue warning (if in VERBOSE mode) and proceed
                        is NOT compatible, raise exception
        Note:  during checks, if receiver.variable is a single numeric item (exposed value or in a list)
               try modifying kwFunctionOutputType of execute method to match receiver's value

        :param request_set:
        :return:
        """

        # Check subclass implementation of self.execute, its output and type and save if it exists
        try:
            self_execute_method = self.execute
        except AttributeError:
            self_execute_method = NotImplemented
            self_execute_output = NotImplemented
            self_execute_type = NotImplemented
        else:
            self_execute_output = self.value

        # Instantiate params[kwExecuteMethod], if it is specified
        super(Projection_Base, self).instantiate_execute_method(context=context)

        # If output of assigned execute method is compatible with receiver's value, return
        if iscompatible(self.value, self.receiver.variable):
            return

        # output of assigned execute method is NOT compatible with receiver's value
        else:
            # If receiver.variable is a single numeric item (exposed value or in a list)
            #   try modifying kwFunctionOutputType of execute method to match receiver's value
            conversion_message = ""
            receiver = self.receiver.variable
            projection_output = self.value
            try:
                if isinstance(receiver, numbers.Number) and len(projection_output) is 1:
                    try:
                        # self.execute.__self__.paramsCurrent[kwFunctionOutputType] = UtilityFunctionOutputType.NUMBER
                        # self.execute.__self__.functionOutputType = UtilityFunctionOutputType.NUMBER
                        self.execute.__self__.functionOutputType = UtilityFunctionOutputType.RAW_NUMBER
                    except UtilityError as error:
                        conversion_message = "; attempted to convert output but "+error.value+" "
                    else:
                        self.value = 0
                        if iscompatible(self.receiver.variable, self.execute()):
                            return
            except TypeError:
                if isinstance(projection_output, numbers.Number) and len(receiver) is 1:
                    try:
                        # self.execute.__self__.paramsCurrent[kwFunctionOutputType] = UtilityFunctionOutputType.LIST
                        # self.execute.__self__.functionOutputType = UtilityFunctionOutputType.LIST
                        self.execute.__self__.functionOutputType = UtilityFunctionOutputType.NP_1D_ARRAY
                    except UtilityError as error:
                        conversion_message = "; attempted to convert output but "+error.value+" "
                    else:
                        self.value = [0]
                        return

            # If self.execute was NOT originally implemented, raise exception
            if self_execute_method is NotImplemented:
                raise ProjectionError("The output type ({0}) of params[kwExecuteMethod] ({1}) for {2} projection "
                                      "to {6} for {3} param of {4} is not compatible with its value ({5}){7}"
                                      "(note: self.execute is not implemented for {2} so can't be used)".
                                      format(type(self.value).__name__,
                                             self.execute.__self__.functionName,
                                             self.name,
                                             self.receiver.name,
                                             self.receiver.owner.name,
                                             type(self.receiver.variable).__name__,
                                             self.receiver.__class__.__name__,
                                             conversion_message))
            # If self.execute WAS originally implemented, but is also incompatible, raise exception:
            elif not iscompatible(self_execute_output, self.receiver.variable):
                raise ProjectionError("The output type ({0}) of self.execute ({1}) for projection {2} "
                          "is not compatible with the value ({3}) of its receiver and"
                          " params[kwExecuteMethod] was not specified{4}".
                          format(type(self.value).__name__,
                                 self.execute.functionName,
                                 self.name,
                                 type(self.receiver.variable).__name__,
                                 conversion_message))
            # self.execute WAS originally implemented and is compatible, so use it
            else:
                if self.prefs.verbosePref:
                    print("The output type ({0}) of params[kwExecuteMethod] ({1}) for projection {2} "
                                          "is not compatible with the value ({3}) of its receiver; "
                                          " default ({4}) will be used".
                                          format(type(self.value).__name__,
                                                 self.execute.functionName,
                                                 self.name,
                                                 type(self.receiver.variable).__name__,
                                                 self_execute_method.functionName))
                self.execute = self_execute_method
                self.update_value()

    def instantiate_attributes_after_execute_method(self, context=NotImplemented):
        self.instantiate_receiver(context=context)

    def instantiate_receiver(self, context=NotImplemented):
        """Call receiver's owner to add projection to its receivesFromProjections list

        Notes:
        * Assume that subclasses implement this method in which they:
          - test whether self.receiver is a Mechanism and, if so, replace with State appropriate for projection
          - calls this method (as super) to assign projection to the Mechanism
        * Constraint that self.value is compatible with receiver.inputState.value
            is evaluated and enforced in instantiate_execute_method, since that may need to be modified (see below)

        IMPLEMENTATION NOTE: since projection is added using Mechanism.add_projection(projection, state) method,
                             could add state specification as arg here, and pass through to add_projection()
                             to request a particular state

        :param context: (str)
        :return:
        """
# FIX: GENEARLIZE THIS (USING Projection.add_to) SO IT CAN BE USED BY MECHANISM AS WELL AS PROJECITON (E.G. LearningSignal)
        if isinstance(self.receiver, State):
            self.receiver.owner.add_projection_to_mechanism(state=self.receiver,
                                                            projection=self,
                                                            context=context)

        # This should be handled by implementation of instantiate_receiver by projection's subclass
        elif isinstance(self.receiver, Mechanism):
            raise ProjectionError("PROGRAM ERROR: receiver for {0} was specified as a Mechanism ({1});"
                                  "this should have been handled by instantiate_receiver for {2}".
                                  format(self.name, self.receiver.name, self.__class__.__name__))

        else:
            raise ProjectionError("Unrecognized receiver specification ({0}) for {1}".format(self.receiver, self.name))

    def is_projection_spec(spec):
        """Evaluate whether spec is a valid Projection specification

        Return true if spec is any of the following:
        + Projection class (or keyword string constant for one):
        + Projection object:
        + specification dict containing:
            + kwProjectionType:<Projection class> - must be a subclass of Projection

        Otherwise, return False

        Returns: (bool)
        """

        if inspect.isclass(spec) and issubclass(spec, Projection):
            return True
        if isinstance(spec, Projection):
            return True
        if isinstance(spec, dict) and kwProjectionType in spec:
            return True
        if inspect.isclass(spec) and (issubclass(spec, Projection)):
            return True
        if isinstance(spec, str) and (kwDefaultMatrix in spec or
                                              kwIdentityMatrix in spec or
                                              kwFullConnectivityMatrix in spec):
            return True
        return False
    
    def add_to(self, receiver, state, context=NotImplemented):
        add_projection_to(receiver=receiver, state=state, projection_spec=self, context=context)
    
def add_projection_to(receiver, state, projection_spec, context=NotImplemented):
    """Assign an "incoming" Projection to an InputState or ParameterState of a receiver Mechanism

    projection_spec can be any valid specification of a projection_spec (see State.instantiate_projections)
    state must be a specification of a InputState or ParameterState
    Specification of InputState can be any of the following:
            - kwInputState - assigns projection_spec to (primary) inputState
            - InputState object
            - index for Mechanism.inputStates OrderedDict
            - name of inputState (i.e., key for Mechanism.inputStates OrderedDict))
            - the keyword kwAddInputState or the name for an inputState to be added
    Specification of ParameterState must be a ParameterState object
    IMPLEMENTATION NOTE:  ADD FULL SET OF ParameterState SPECIFICATIONS
                          CURRENTLY, ASSUMES projection_spec IS AN ALREADY INSTANTIATED PROJECTION

    Args:
        receiver (Mechanism or Projection):
        projection_spec: (Projection, dict, or str)
        state (State subclass):
        context:

    """
    from PsyNeuLink.Functions.States.InputState import InputState
    from PsyNeuLink.Functions.States.ParameterState import ParameterState
    if not isinstance(state, (int, str, InputState, ParameterState)):
        raise ProjectionError("State specification(s) for {0} (as receivers of {1}) contain(s) one or more items"
                             " that is not a name, reference to an inputState or parameterState object, "
                             " or an index (for inputStates)".
                             format(receiver.name, projection_spec))

    # state is State object, so use that
    if isinstance(state, State):
        state.instantiate_projections(projections=projection_spec, context=context)
        return

    # Generic kwInputState is specified, so use (primary) inputState
    elif state is kwInputState:
        receiver.inputState.instantiate_projections(projections=projection_spec, context=context)
        return

    # input_state is index into inputStates OrderedDict, so get corresponding key and assign to input_state
    elif isinstance(state, int):
        try:
            key = list(receiver.inputStates.keys)[state]
        except IndexError:
            raise ProjectionError("Attempt to assign projection_spec ({0}) to inputState {1} of {2} "
                                 "but it has only {3} inputStates".
                                 format(projection_spec.name, state, receiver.name, len(receiver.inputStates)))
        else:
            input_state = key

    # input_state is string (possibly key retrieved above)
    #    so try as key in inputStates OrderedDict (i.e., as name of an inputState)
    if isinstance(state, str):
        try:
            receiver.inputState[state].instantiate_projections(projections=projection_spec, context=context)
        except KeyError:
            pass
        else:
            if receiver.prefs.verbosePref:
                print("Projection_spec {0} added to {1} of {2}".format(projection_spec.name, state, receiver.name))
            # return

    # input_state is either the name for a new inputState or kwAddNewInputState
    if not state is kwAddInputState:
        if receiver.prefs.verbosePref:
            reassign = input("\nAdd new inputState named {0} to {1} (as receiver for {2})? (y/n):".
                             format(input_state, receiver.name, projection_spec.name))
            while reassign != 'y' and reassign != 'n':
                reassign = input("\nAdd {0} to {1}? (y/n):".format(input_state, receiver.name))
            if reassign == 'n':
                raise ProjectionError("Unable to assign projection {0} to receiver {1}".
                                      format(projection_spec.name, receiver.name))

    input_state = receiver.instantiate_mechanism_state(
                                    state_type=InputState,
                                    state_name=input_state,
                                    state_spec=projection_spec.value,
                                    constraint_values=projection_spec.value,
                                    constraint_values_name='Projection_spec value for new inputState',
                                    context=context)
        #  Update inputState and inputStates
    try:
        receiver.inputStates[input_state.name] = input_state
    # No inputState(s) yet, so create them
    except AttributeError:
        receiver.inputStates = OrderedDict({input_state.name:input_state})
        receiver.inputState = list(receiver.inputStates)[0]
    input_state.instantiate_projections(projections=projection_spec, context=context)

# def add_projection_from()
def add_projection_from(sender, state, projection, context=NotImplemented):
    """Assign an "outgoing" Projection from an OutputState of a sender Mechanism

    projection_spec can be any valid specification of a projection_spec (see State.instantiate_projections)
    state must be a specification of an outputState
    Specification of OutputState can be any of the following:
            - kwOutputState - assigns projection_spec to (primary) outputState
            - OutputState object
            - index for Mechanism.outputStates OrderedDict
            - name of outputState (i.e., key for Mechanism.outputStates OrderedDict))
            - the keyword kwAddOutputState or the name for an outputState to be added

    Args:
        sender (Mechanism):
        projection_spec: (Projection, dict, or str)
        state (OutputState, str, or value):
        context:
    """
    from PsyNeuLink.Functions.States.InputState import InputState
    from PsyNeuLink.Functions.States.ParameterState import ParameterState
    if not isinstance(state, (int, str, InputState, ParameterState)):
        raise ProjectionError("State specification(s) for {0} (as receivers of {1}) contain(s) one or more items"
                             " that is not a name, reference to an inputState or parameterState object, "
                             " or an index (for inputStates)".
                             format(sender.name, projection_spec))

    # state is State object, so use that
    if isinstance(state, State):
        state.instantiate_projections(projections=projection_spec, context=context)
        return

    # Generic kwInputState is specified, so use (primary) inputState
    elif state is kwInputState:
        receiver.inputState.instantiate_projections(projections=projection_spec, context=context)
        return

    # input_state is index into inputStates OrderedDict, so get corresponding key and assign to input_state
    elif isinstance(state, int):
        try:
            key = list(receiver.inputStates.keys)[state]
        except IndexError:
            raise ProjectionError("Attempt to assign projection_spec ({0}) to inputState {1} of {2} "
                                 "but it has only {3} inputStates".
                                 format(projection_spec.name, state, receiver.name, len(receiver.inputStates)))
        else:
            input_state = key

    # input_state is string (possibly key retrieved above)
    #    so try as key in inputStates OrderedDict (i.e., as name of an inputState)
    if isinstance(state, str):
        try:
            receiver.inputState[state].instantiate_projections(projections=projection_spec, context=context)
        except KeyError:
            pass
        else:
            if receiver.prefs.verbosePref:
                print("Projection_spec {0} added to {1} of {2}".format(projection_spec.name, state, receiver.name))
            # return

    # input_state is either the name for a new inputState or kwAddNewInputState
    if not state is kwAddInputState:
        if receiver.prefs.verbosePref:
            reassign = input("\nAdd new inputState named {0} to {1} (as receiver for {2})? (y/n):".
                             format(input_state, receiver.name, projection_spec.name))
            while reassign != 'y' and reassign != 'n':
                reassign = input("\nAdd {0} to {1}? (y/n):".format(input_state, receiver.name))
            if reassign == 'n':
                raise ProjectionError("Unable to assign projection {0} to receiver {1}".
                                      format(projection_spec.name, receiver.name))

    input_state = receiver.instantiate_mechanism_state(
                                    state_type=InputState,
                                    state_name=input_state,
                                    state_spec=projection_spec.value,
                                    constraint_values=projection_spec.value,
                                    constraint_values_name='Projection_spec value for new inputState',
                                    context=context)
        #  Update inputState and inputStates
    try:
        receiver.inputStates[input_state.name] = input_state
    # No inputState(s) yet, so create them
    except AttributeError:
        receiver.inputStates = OrderedDict({input_state.name:input_state})
        receiver.inputState = list(receiver.inputStates)[0]
    input_state.instantiate_projections(projections=projection_spec, context=context)