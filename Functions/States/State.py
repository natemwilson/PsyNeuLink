# Princeton University licenses this file to You under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may obtain a copy of the License at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.
#
#
#  *********************************************  State ********************************************************
#
#
from Functions.ShellClasses import *
from Functions.Utility import *
from Globals.Registry import  register_category
from collections import OrderedDict
import numpy as np

StateRegistry = {}

class StateError(Exception):
    def __init__(self, error_value):
        self.error_value = error_value

    def __str__(self):
        return repr(self.error_value)


# State factory method:
# def state(name=NotImplemented, params=NotImplemented, context=NotImplemented):
#         """Instantiates default or specified subclass of State
#
#        If called w/o arguments or 1st argument=NotImplemented, instantiates default subclass (ParameterState)
#         If called with a name string:
#             - if registered in StateRegistry class dictionary as name of a subclass, instantiates that class
#             - otherwise, uses it as the name for an instantiation of the default subclass, and instantiates that
#         If a params dictionary is included, it is passed to the subclass
#
#         :param name:
#         :param param_defaults:
#         :return:
#         """
#
#         # Call to instantiate a particular subclass, so look up in MechanismRegistry
#         if name in StateRegistry:
#             return StateRegistry[name].mechanismSubclass(params)
#         # Name is not in MechanismRegistry or is not provided, so instantiate default subclass
#         else:
#             # from Functions.Defaults import DefaultState
#             return DefaultState(name, params)

# DOCUMENT:  INSTANTATION CREATES AN ATTIRBUTE ON THE OWNER MECHANISM WITH THE STATE'S NAME + kwValueSuffix
#            THAT IS UPDATED BY THE STATE'S value setter METHOD (USED BY LOGGING OF MECHANISM ENTRIES)
class State_Base(State):
    """Implement abstract class for State category of class types that compute and represent mechanism states

    Description:
        Represents and updates the state of an input, output or parameter of a mechanism
            - receives inputs from projections (self.receivesFromProjections, kwStateProjections)
            - combines inputs from all projections (mapping and/or control) and uses this as variable of
                execute method to update the value attribute
        Value attribute:
             - is updated by the execute method
             - can be used as sender (input) to one or more projections
             - can be accessed by KVO
        Constraints:
            - value must be compatible with variable of execute method
            - value must be compatible with receiver.value for all projections it receives

    Subclasses:
        Must implement:
            functionType
            ParamClassDefaults with:
                + kwExecuteMethod (or <subclass>.execute
                + kwExecuteMethodParams (optional)
                + kwProjectionType - specifies type of projection to use for instantiation of default subclass
        Standard subclasses and constraints:
            InputState - used as input state for Mechanism;  additional constraint:
                - value must be compatible with variable of owner's execute method
            OutputState - used as output state for Mechanism;  additional constraint:
                - value must be compatible with the output of the ownerMechanism's execute method
            MechanismsParameterState - used as state for Mechanism parameter;  additional constraint:
                - output of execute method must be compatible with the parameter's value

    Instantiation:
        States should NEVER be instantiated by a direct call to the class
           (since there is no obvious default), but rather by calls to the subclass
        Subclasses can be instantiated in one of two ways:
            - call to __init__ with args to subclass with args for ownerMechanism, value and params:
            - as part of the instantiation of a Mechanism (see Mechanism.intantiate_mechanism_state for details)

    Initialization arguments:
        - value (value) - establishes type of value attribute and initializes it (default: [0])
        - ownerMechanism(Mechanism) - assigns state to mechanism (default: NotImplemented)
        - params (dict):  (if absent, default state is implemented)
            + kwExecuteMethod (method)         |  Implemented in subclasses; used in update_state()
            + kwExecuteMethodParams (dict) |
            + kwStateProjections:<projection specification or list of ones>
                if absent, no projections will be created
                projection specification can be: (see Projection for details)
                    + Projection object
                    + Projection class
                    + specification dict
                    + a list containing any or all of the above
                    if dict, must contain entries specifying a projection:
                        + kwProjectionType:<Projection class>: must be a subclass of Projection
                        + kwProjectionParams:<dict>? - must be dict of params for kwProjectionType
        - name (str): if it is not specified, a default based on the class is assigned in register_category,
                            of the form: className+n where n is the n'th instantiation of the class
        - prefs (PreferenceSet or specification dict):
             if it is omitted, a PreferenceSet will be constructed using the classPreferences for the subclass
             dict entries must have a preference keyPath as their key, and a PreferenceEntry or setting as their value
             (see Description under PreferenceSet for details)
        - context (str): must be a reference to a subclass, or an exception will be raised

    StateRegistry:
        All States are registered in StateRegistry, which maintains a dict for each subclass,
          a count for all instances of that type, and a dictionary of those instances

    Naming:
        States can be named explicitly (using the name='<name>' argument).  If the argument is omitted,
        it will be assigned the subclass name with a hyphenated, indexed suffix ('subclass.name-n')

    Execution:


    Class attributes:
        + functionCategory = kwStateFunctionCategory
        + className = kwState
        + suffix
        + registry (dict): StateRegistry
        + classPreference (PreferenceSet): StatePreferenceSet, instantiated in __init__()
        + classPreferenceLevel (PreferenceLevel): PreferenceLevel.CATEGORY
        + variableClassDefault (value): [0]
        + requiredParamClassDefaultTypes = {kwExecuteMethodParams : [dict],    # Subclass execute method params
                                           kwProjectionType: [str, Projection]})   # Default projection type
        + paramClassDefaults (dict): {kwStateProjections: []}             # Projections to States
        + paramNames (dict)
        + ownerMechanism (Mechansim)
        + kwExecuteMethod (Function class or object, or method)

    Class methods:
        • set_value(value) -
            validates and assigns value, and updates observers
            returns None
        • update_state(context) -
            updates self.value by combining all projections and using them to compute new value
            return None

    Instance attributes:
        + ownerMechanism (Mechanism): object to which State belongs
        + value (value): current value of the State (updated by update_state method)
        + baseValue (value): value with which it was initialized (e.g., from params in call to __init__)
        + receivesFromProjections (list): list of projections for which State is a receiver
        + sendsToProjections (list): list of projections for which State is a sender
        + params (dict)
        + value (value - output of execute method
        + name (str) - if it is not specified as an arg, a default based on the class is assigned in register_category
        + prefs (PreferenceSet) - if not specified as an arg, default is created by copying StatePreferenceSet

    Instance methods:
        none
    """

    #region CLASS ATTRIBUTES

    kpState = "State"
    functionCategory = kwStateFunctionCategory
    className = kwState
    suffix = " " + className

    registry = StateRegistry

    classPreferenceLevel = PreferenceLevel.CATEGORY

    variableClassDefault = [0]

    requiredParamClassDefaultTypes = Function.requiredParamClassDefaultTypes.copy()
    requiredParamClassDefaultTypes.update({kwExecuteMethodParams : [dict],
                                           kwProjectionType: [str, Projection]})   # Default projection type
    paramClassDefaults = Function.paramClassDefaults.copy()
    paramClassDefaults.update({kwStateProjections: []})
    paramNames = paramClassDefaults.keys()

    #endregion

    def __init__(self,
                 owner_mechanism,
                 value=NotImplemented,
                 params=NotImplemented,
                 name=NotImplemented,
                 prefs=NotImplemented,
                 context=NotImplemented,
                 **kargs):
        """Initialize subclass that computes and represents the value of a particular state of a mechanism

        This is used by subclasses to implement the input, output, and parameter states of a Mechanism

        Arguments:
            - ownerMechanism (Mechanism):
                 mechanism with which state is associated (default: NotImplemented)
                 this argument is required, as can't instantiate a State without an owning Mechanism
            - value (value): value of the state:
                must be list or tuple of numbers, or a number (in which case it will be converted to a single-item list)
                must match input and output of state's update function, and any sending or receiving projections
            - params (dict):
                + if absent, implements default State determined by kwProjectionType param
                + if dict, can have the following entries:
                    + kwStateProjections:<Projection object, Projection class, dict, or list of either or both>
                        if absent, no projections will be created
                        if dict, must contain entries specifying a projection:
                            + kwProjectionType:<Projection class> - must be a subclass of Projection
                            + kwProjectionParams:<dict> - must be dict of params for kwProjectionType
            - name (str): string with name of state (default: name of ownerMechanism + suffix + instanceIndex)
            - prefs (dict): dictionary containing system preferences (default: Prefs.DEFAULTS)
            - context (str)
            - **kargs (dict): dictionary of arguments using the following keywords for each of the above kargs:
                + kwStateValue = value
                + kwStateParams = params
                + kwStateName = name
                + kwStatePrefs = prefs
                + kwStateContext = context
                NOTES:
                    * these are used for dictionary specification of a State in param declarations
                    * they take precedence over arguments specified directly in the call to __init__()

        :param ownerMechanism: (Mechanism)
        :param value: (value)
        :param params: (dict)
        :param name: (str)
        :param prefs: (dict)
        :return:
        """
        if kargs:
            try:
                value = kargs[kwStateValue]
            except (KeyError, NameError):
                pass
            try:
                params = kargs[kwStateParams]
            except (KeyError, NameError):
                pass
            try:
                name = kargs[kwStateName]
            except (KeyError, NameError):
                pass
            try:
                prefs = kargs[kwStatePrefs]
            except (KeyError, NameError):
                pass
            try:
                context = kargs[kwStateContext]
            except (KeyError, NameError):
                pass

        if not isinstance(context, State_Base):
            raise StateError("Direct call to abstract class State() is not allowed; "
                                      "use state() or one of the following subclasses: {0}".
                                      format(", ".join("{!s}".format(key) for (key) in StateRegistry.keys())))

        # FROM MECHANISM:
        # Note: pass name of mechanism (to override assignment of functionName in super.__init__)

        # Assign functionType to self.name as default;
        #  will be overridden with instance-indexed name in call to super
        if name is NotImplemented:
            self.name = self.functionType
        # Not needed:  handled by subclass
        # else:
        #     self.name = name

        self.functionName = self.functionType

        register_category(self, State_Base, StateRegistry, context=context)

        #region VALIDATE ownerMechanism
        if isinstance(owner_mechanism, Mechanism):
            self.ownerMechanism = owner_mechanism
        else:
            raise StateError("ownerMechanism argument ({0}) for {1} must be a mechanism".
                                      format(owner_mechanism, self.name))
        #endregion

        self.receivesFromProjections = []
        self.sendsToProjections = []

        # VALIDATE VARIABLE, PARAMS, AND INSTANTIATE EXECUTE METHOD
        super(State_Base, self).__init__(variable_default=value,
                                                  param_defaults=params,
                                                  name=name,
                                                  prefs=prefs,
                                                  context=context.__class__.__name__)

        # INSTANTIATE PROJECTIONS SPECIFIED IN PARAMS
        try:
            projections = self.paramsCurrent[kwStateProjections]
        except KeyError:
            # No projections specified, so none will be created here
            # IMPLEMENTATION NOTE:  This is where a default projection would be implemented
            #                       if params = NotImplemented or there is no param[kwStateProjections]
            pass
        else:
            # MODIFIED 6/23/16  ADDED 'if projections' STATEMENT
            if projections:
                self.instantiate_projections(projections=projections, context=context)

# # FIX LOG: EITHER GET RID OF THIS NOW THAT @property HAS BEEN IMPLEMENTED, OR AT LEAST INTEGRATE WITH IT
#         # add state to KVO observer dict
#         self.observers = {self.kpState: []}
#
# # FIX: WHY IS THIS COMMENTED OUT?  IS IT HANDLED BY SUBCLASSES??
    # def register_category(self):
    #     register_mechanism_state_subclass(self)

    def validate_variable(self, variable, context=NotImplemented):
        """Validate variable and assign validated values to self.variable

        Sets self.baseValue = self.value = self.variable = variable
        Insures that it is a number of list or tuple of numbers

        This overrides the class method, to perform more detailed type checking
        See explanation in class method.
        Note:  this method (or the class version) is called only if the parameter_validation attribute is True

        :param variable: (anything but a dict) - variable to be validated:
        :param context: (str)
        :return none:
        """

        super(State,self).validate_variable(variable, context)

        if context is NotImplemented:
            context = kwAssign + ' Base Value'
        else:
            context = context + kwAssign + ' Base Value'

        self.baseValue = self.variable


    def validate_params(self, request_set, target_set=NotImplemented, context=NotImplemented):
        """validate projection specification(s)

        Call super (Function.validate_params()
        Validate following params:
            + kwStateProjections:  <entry or list of entries>; each entry must be one of the following:
                + Projection object
                + Projection class
                + specification dict, with the following entries:
                    + kwProjectionType:<Projection class> - must be a subclass of Projection
                    + kwProjectionParams:<dict> - must be dict of params for kwProjectionType
            # IMPLEMENTATION NOTE: TBI - When learning projection is implemented
            # + kwExecuteMethodParams:  <dict>, every entry of which must be one of the following:
            #     ParameterState, projection, ParamValueProjection tuple or value

        :param request_set:
        :param target_set:
        :param context:
        :return:
        """

        # Check params[kwStateProjections] before calling validate_param:
        # - if projection specification is an object or class reference, needs to be wrapped in a list
        try:
            projections = target_set[kwStateProjections]
        except KeyError:
            # If no projections, ignore (none will be created)
            projections = None
        else:
            # If specification is not a list, wrap it in one:
            # - to be consistent with paramClassDefaults
            # - for consistency of treatment below
            if not isinstance(projections, list):
                projections = [projections]

        super(State, self).validate_params(request_set, target_set, context=context)

        if projections:
            # Validate projection specs in list
            from Functions.Projections import Projection
            for projection in projections:
                try:
                    issubclass(projection, Projection)
                except TypeError:
                    if (isinstance(projection, Projection) or iscompatible(projection. dict)):
                        continue
                    else:
                        if self.prefs.verbosePref:
                            print("{0} in {1} is not a projection, projection type, or specification dict; "
                                  "{2} will be used to create default {3} for {4}".
                                format(projection,
                                       self.__class__.__name__,
                                       target_set[kwProjectionType],
                                       self.ownerMechanism.name))


    def instantiate_execute_method(self, context=NotImplemented):
        """Insure that output of execute method (self.value) is compatible with its input (self.variable)

        This constraint reflects the function of State execute methods:
            they simply update the value of the State;
            accordingly, their variable and value must be compatible

        :param context:
        :return:
        """

        super().instantiate_execute_method(context=context)

        # Insure that output of execute method (self.value) is compatible with its input (self.variable)
        if not iscompatible(self.variable, self.value):
            raise StateError("Output ({0}: {1}) of execute function ({2}) for {3} {4} of {5}"
                                      " must be the same format as its input ({6}: {7})".
                                      format(type(self.value).__name__,
                                             self.value,
                                             self.execute.__self__.functionName,
                                             self.name,
                                             self.__class__.__name__,
                                             self.ownerMechanism.name,
                                             self.variable.__class__.__name__,
                                             self.variable))

    def instantiate_projections(self, projections, context=NotImplemented):
        """Instantiate projections for a state and assign them to self.receivesFromProjections

        For each projection spec in kwStateProjections, check that it is one or a list of any of the following:
        + Projection class (or keyword string constant for one):
            implements default projection for projection class
        + Projection object:
            checks that receiver is self
            checks that projection execute method output is compatible with self.value
        + specification dict:
            checks that projection execute method output is compatible with self.value
            implements projection
            dict must contain:
                + kwProjectionType:<Projection class> - must be a subclass of Projection
                + kwProjectionParams:<dict> - must be dict of params for kwProjectionType
        If any of the conditions above fail:
            a default projection is instantiated using self.paramsCurrent[kwProjectionType]
        Each projection in the list is added to self.receivesFromProjections
        If kwMStateProjections is absent or empty, no projections are created

        :param context: (str)
        :return state: (State)
        """

        from Functions.Projections.Projection import Projection_Base
        # If specification is not a list, wrap it in one for consistency of treatment below
        # (since specification can be a list, so easier to treat any as a list)
        from Functions.States.ParameterState import ParameterState
        projection_list = projections
        if not isinstance(projection_list, list):
            projection_list = [projection_list]

        object_name_string = self.name
        item_prefix_string = ""
        item_suffix_string = " for " + object_name_string
        default_string = ""
        kwDefault = "default "

        default_projection_type = self.paramsCurrent[kwProjectionType]

        # Instantiate each projection specification in the projection_list, and
        # - insure it is in self.receivesFromProjections
        # - insure the output of its execute method is compatible with self.value
        for projection_spec in projection_list:

            # If there is more than one projection specified, construct messages for use in case of failure
            if len(projection_list) > 1:
                item_prefix_string = "Item {0} of projection list for {1}: ".\
                    format(projection_list.index(projection_spec)+1, object_name_string)
                item_suffix_string = ""

# FIX: FROM HERE TO BOTTOM OF METHOD SHOULD ALL BE HANDLED IN __init__() FOR PROJECTION
            projection_object = None # flags whether projection object has been instantiated; doesn't store object
            projection_type = None   # stores type of projection to instantiate
            projection_params = {}

            # INSTANTIATE PROJECTION
            # If projection_spec is a Projection object:
            # - call check_projection_receiver() to check that receiver is self; if not, it:
            #     returns object with receiver reassigned to self if chosen by user
            #     else, returns new (default) kwProjectionType object with self as receiver
            #     note: in that case, projection will be in self.receivesFromProjections list
            if isinstance(projection_spec, Projection_Base):
                projection_object, default_class_name = self.check_projection_receiver(projection_spec=projection_spec,
                                                                                       messages=[item_prefix_string,
                                                                                                 item_suffix_string,
                                                                                                 object_name_string],
                                                                                       context=self)
                # If projection's name has not been assigned, base it on State's name:
                if default_class_name:
                    # projection_object.name = projection_object.name.replace(default_class_name, self.name)
                    projection_object.name = self.name + '_' + projection_object.name
                    # Used for error message
                    default_string = kwDefault
# FIX:  REPLACE DEFAULT NAME (RETURNED AS DEFAULT) PROJECTION NAME WITH State'S NAME, LEAVING INDEXED SUFFIX INTACT

            # If projection_spec is a dict:
            # - get projection_type
            # - get projection_params
            # Note: this gets projection_type but does NOT not instantiate projection; so,
            #       projection is NOT yet in self.receivesFromProjections list
            elif isinstance(projection_spec, dict):
                # Get projection type from specification dict
                try:
                    projection_type = projection_spec[kwProjectionType]
                except KeyError:
                    projection_type = default_projection_type
                    default_string = kwDefault
                    if self.prefs.verbosePref:
                        print("{0}{1} not specified in {2} params{3}; default {4} will be assigned".
                              format(item_prefix_string,
                                     kwProjectionType,
                                     kwStateProjections,
                                     item_suffix_string,
                                     default_projection_type.__class__.__name__))
                else:
                    # IMPLEMENTATION NOTE:  can add more informative reporting here about reason for failure
                    projection_type, error_str = self.parse_projection_ref(projection_spec=projection_type,
                                                                           context=self)
                    if error_str:
                        print("{0}{1} {2}; default {4} will be assigned".
                              format(item_prefix_string,
                                     kwProjectionType,
                                     error_str,
                                     kwStateProjections,
                                     item_suffix_string,
                                     default_projection_type.__class__.__name__))

                # Get projection params from specification dict
                try:
                    projection_params = projection_spec[kwProjectionParams]
                except KeyError:
                    if self.prefs.verbosePref:
                        print("{0}{1} not specified in {2} params{3}; default {4} will be assigned".
                              format(item_prefix_string,
                                     kwProjectionParams,
                                     kwStateProjections, object_name_string,
                                     item_suffix_string,
                                     default_projection_type.__class__.__name__))

            # Check if projection_spec is class ref or keyword string constant for one
            # Note: this gets projection_type but does NOT not instantiate projection; so,
            #       projection is NOT yet in self.receivesFromProjections list
            else:
                projection_type, err_str = self.parse_projection_ref(projection_spec=projection_spec,context=self)
                if err_str:
                    print("{0}{1} {2}; default {4} will be assigned".
                          format(item_prefix_string,
                                 kwProjectionType,
                                 err_str,
                                 kwStateProjections,
                                 item_suffix_string,
                                 default_projection_type.__class__.__name__))

            # If neither projection_object nor projection_type have been assigned, assign default type
            # Note: this gets projection_type but does NOT not instantiate projection; so,
            #       projection is NOT yet in self.receivesFromProjections list
            if not projection_object and not projection_type:
                    projection_type = default_projection_type
                    default_string = kwDefault
                    if self.prefs.verbosePref:
                        print("{0}{1} is not a Projection object or specification for one{2}; "
                              "default {3} will be assigned".
                              format(item_prefix_string,
                                     projection_spec.name,
                                     item_suffix_string,
                                     default_projection_type.__class__.__name__))

            # If projection_object has not been assigned, instantiate projection_type
            # Note: this automatically assigns projection to self.receivesFromProjections and
            #       to it's sender's sendsToProjections list:
            #           when a projection is instantiated, it assigns itself to:
            #               its receiver's .receivesFromProjections attribute (in Projection.instantiate_receiver)
            #               its sender's .sendsToProjections list attribute (in Projection.instantiate_sender)
            if not projection_object:
                projection_spec = projection_type(receiver=self,
                                                  name=self.name+'_'+projection_type.className,
                                                  params=projection_params,
                                                         context=context)

            # Check that output of projection's execute method (projection_spec.value is compatible with
            #    variable of State to which it projects;  if it is not, raise exception:
            # The buck stops here; otherwise there would be an unmanageable regress of reassigning
            #    projections, requiring reassignment or modification of sender outputState, etc.
            if not iscompatible(self.variable, projection_spec.value):
                raise StateError("{0}Output ({1}) of execute method for {2}{3} "
                                          "is not compatible with value ({4}){5}".
                      format(item_prefix_string,
                             projection_spec.value,
                             default_string,
                             projection_spec.name,
                             self.value,
                             item_suffix_string))

            # If projection is valid, assign to State's receivesFromProjections list
            else:
                # This is needed to avoid duplicates, since instantiation of projection (e.g., of ControlSignal)
                #    may have already called this method and assigned projection to self.receivesFromProjections list
                if not projection_spec in self.receivesFromProjections:
                    self.receivesFromProjections.append(projection_spec)

    def check_projection_receiver(self, projection_spec, messages=NotImplemented, context=NotImplemented):
        """Check whether Projection object belongs to State and if not return default Projection object

        Arguments:
        - projection_spec (Projection object)
        - message (list): list of three strings - prefix and suffix for error/warning message, and State name
        - context (object): ref to State object; used to identify kwProjectionType and name

        Returns: tuple (Projection object, str); second value is name of default projection, else None

        :param self:
        :param projection_spec: (Projection object)
        :param messages: (list)
        :param context: (State object)
        :return: (tuple) Projection object, str) - second value is false if default was returned
        """

        prefix = 0
        suffix = 1
        name = 2
        if messages is NotImplemented:
            messages = ["","","",context.__class__.__name__]
        message = "{0}{1} is a projection of the correct type for {2}, but its receiver is not assigned to {3}." \
                  " \nReassign (r) or use default (d)?:".\
            format(messages[prefix], projection_spec.name, projection_spec.receiver.name, messages[suffix])

        if projection_spec.receiver is not self:
            reassign = input(message)
            while reassign != 'r' and reassign != 'd':
                reassign = input("Reassign {0} to {1} or use default (r/d)?:".
                                 format(projection_spec.name, messages[name]))
            # User chose to reassign, so return projection object with State as its receiver
            if reassign == 'r':
                projection_spec.receiver = self
                # IMPLEMENTATION NOTE: allow this, since it is being carried out by State itself
                self.receivesFromProjections.append(projection_spec)
                if self.prefs.verbosePref:
                    print("{0} reassigned to {1}".format(projection_spec.name, messages[name]))
                return (projection_spec, None)
            # User chose to assign default, so return default projection object
            elif reassign == 'd':
                print("Default {0} will be used for {1}".
                      format(projection_spec.name, messages[name]))
                return (self.paramsCurrent[kwProjectionType](receiver=self),
                        self.paramsCurrent[kwProjectionType].className)
                #     print("{0} reassigned to {1}".format(projection_spec.name, messages[name]))
            else:
                raise StateError("Program error:  reassign should be r or d")

        return (projection_spec, None)

    def parse_projection_ref(self,
                             projection_spec,
                             # messages=NotImplemented,
                             context=NotImplemented):
        """Take projection ref and return ref to corresponding type or, if invalid, to  default for context

        Arguments:
        - projection_spec (Projection subclass or str):  str must be a keyword constant for a Projection subclass
        - context (str):

        Returns tuple: (Projection subclass or None, error string)

        :param projection_spec: (Projection subclass or str)
        :param messages: (list)
        :param context: (State object)
        :return: (Projection subclass, string)
        """
        try:
            # Try projection spec as class ref
            is_projection_class = issubclass(projection_spec, Projection)
        except TypeError:
            # Try projection spec as keyword string constant
            if isinstance(projection_spec, str):
                try:
                    from Functions.Projections.Projection import ProjectionRegistry
                    projection_spec = ProjectionRegistry[projection_spec].subclass
                except KeyError:
                    # projection_spec was not a recognized key
                    return (None, "not found in ProjectionRegistry")
                # projection_spec was legitimate keyword
                else:
                    return (projection_spec, None)
            # projection_spec was neither a class reference nor a keyword
            else:
                return (None, "neither a class reference nor a keyword")
        else:
            # projection_spec was a legitimate class
            if is_projection_class:
                return (projection_spec, None)
            # projection_spec was class but not Projection
            else:
                return (None, "not a Projection subclass")

# # FIX: NO LONGER USED;  SUPERCEDED BY value setter METHOD ABOVE.  INCOROPRATE VALIDATION THERE??
#     def add_observer_for_keypath(self, object, keypath):
#         self.observers[keypath].append(object)
#
# # IMPLEMENTATION NOTE:  USE DECORATOR TO MAKE SURE THIS IS CALLED WHENEVER state.value IS ASSIGNED
#     def set_value(self, new_value):
#         """Validate value, assign it, and update any observers
#
#         Uses valueClassDefault as the template for validating new_value
#         :param new_value:
#         :return:
#         """
#
#         # Validate new_value
#         if self.prefs.paramValidationPref:
#             if not isinstance(new_value, self.variableInstanceDefault):
#                 raise StateError("Value {0} of {1} must be of type {2}".
#                                      format(new_value, self.name, self.variableInstanceDefault))
#             # Check that each element is a number
#             for element in new_value:
#                 if not isinstance(element, numbers.Number):
#                     raise StateError("Item {0} ({1}) in value of {2} is not a number".
#                                          format(new_value.index(element), element, self.name))
#
#         old_value = self.value
#
#         # Set value
#         self.value = new_value
#
#         # Update observers
#         if self.observers:
#         # if len(self.observers[self.kpState]):
#             for observer in self.observers[self.kpState]:
#                 observer.observe_value_at_keypath(self.kpState, old_value, new_value)
#
    def update(self, params=NotImplemented, time_scale=TimeScale.TRIAL, context=NotImplemented):
        """Execute function for each projection, combine them, and assign result to value

        Updates self.value by calling self.receivesFromProjections and LinearCombination function with kwLinearCombinationOperation

    Arguments:
    - context (str)

    :param context: (str)
    :return: None
    """

        #region FLAG FORMAT OF INPUT
        if isinstance(self.value, numbers.Number):
            # Treat as single real value
            value_is_number = True
        else:
            # Treat as vector (list or np.array)
            value_is_number = False
        #endregion

        #region AGGREGATE INPUT FROM PROJECTIONS

        #region Initialize aggregation
        from Functions.Utility import kwLinearCombinationInitializer
        combined_values = kwLinearCombinationInitializer
        #endregion

        #region Get type-specific params from kwProjectionParams
        mapping_params = merge_param_dicts(params, kwMappingParams, kwProjectionParams)
        control_signal_params = merge_param_dicts(params, kwControlSignalParams, kwProjectionParams)
        #endregion

        #region Get params for each projection, pass them to it, and get its value
        projection_value_list = []
        for projection in self.receivesFromProjections:

            # Merge with relevant projection type-specific params
            from Functions.Projections.Mapping import Mapping
            from Functions.Projections.ControlSignal import ControlSignal
            if isinstance(projection, Mapping):
                projection_params = merge_param_dicts(params, projection.name, mapping_params, )
            elif isinstance(projection, ControlSignal):
                projection_params = merge_param_dicts(params, projection.name, control_signal_params)
            if not projection_params:
                projection_params = NotImplemented

            # Update projection and get value
            projection_value = projection.update(projection_params, context=context)

            # If value is number, put in list (for aggregation below)
            # if value_is_number:
            #     projection_value = [projection_value]

            # Add projection_value to list (for aggregation below)
            projection_value_list.append(projection_value)

        #endregion
        #region Aggregate projection values

        # If there were projections:
        if projection_value_list:
            try:
                # pass only execute_method params
                execute_method_params = params[kwExecuteMethodParams]
            except (KeyError, TypeError):
                execute_method_params = NotImplemented

            # Combine projection values
            combined_values = self.execute(variable=projection_value_list,
                                           params=execute_method_params,
                                           context=context)

            # If self.value is a number, convert combined_values back to number
            if value_is_number and combined_values:
                combined_values = combined_values[0]

        # There were no projections
        else:
            # mark combined_values as none, so that (after being assigned to self.value)
            #    it is ignored in execute method (i.e., not combined with baseValue)
            combined_values = None
        #endregion

        #region ASSIGN STATE VALUE
        context = context + kwAggregate + ' Projection Inputs'
        self.value = combined_values
        #endregion

    @property
    def ownerMechanism(self):
        return self._ownerMechanism

    @ownerMechanism.setter
    def ownerMechanism(self, assignment):
        self._ownerMechanism = assignment

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, assignment):

        self._value = assignment

        # Store value in log if specified
        # Get logPref
        if self.prefs:
            log_pref = self.prefs.logPref

        # Get context
        try:
            curr_frame = inspect.currentframe()
            prev_frame = inspect.getouterframes(curr_frame, 2)
            context = inspect.getargvalues(prev_frame[1][0]).locals['context']
        except KeyError:
            context = ""

        # If context is consistent with log_pref, record value to log
        if (log_pref is LogLevel.ALL_ASSIGNMENTS or
                (log_pref is LogLevel.EXECUTION and kwExecuting in context) or
                (log_pref is LogLevel.VALUE_ASSIGNMENT and (kwExecuting in context and kwAssign in context))):
            self.ownerMechanism.log.entries[self.name] = LogEntry(CurrentTime(), context, assignment)
            # self.ownerMechanism.log.entries[self.name] = LogEntry(CentralClock, context, assignment)

    @property
    def baseValue(self):
        return self._baseValue

    @baseValue.setter
    def baseValue(self, item):
        self._baseValue = item

    @property
    def projections(self):
        return self._projections

    @projections.setter
    def projections(self, assignment):
        self._projections = assignment

    # @property
    # def receivesFromProjections(self):
    #     return self._receivesFromProjections
    #
    # @receivesFromProjections.setter
    # def receivesFromProjections(self, assignment):
    #     self._receivesFromProjections = assignment

# **************************************************************************************

# Module functions:
#
# • instantiate_mechanism_state_list(state_type,
#                                    state_param_identifier,
#                                    constraint_values,
#                                    constraint_values_name,
#                                    context)
#     instantiates states of type specified from list in paramsCurrent specified by state_param_identifier;
#     passes state_type and constraints to State.instantiate_mechanism_state
#         for instantiating each individual state
#
# • instantiate_mechanism_state(owner,
#                               state_type
#                               state_name,
#                               state_spec,
#                               constraint_values,
#                               constraint_values_name,
#                               constraint_index,
#                               context):
#     instantiates state of type specified by state_type and state_spec, using constraints

def instantiate_mechanism_state_list(
                        owner,
                        state_list,              # list of State specs, (state_spec, params) tuples, or None
                        state_type,              # StateType subclass
                        state_param_identifier,  # used to specify state_type state(s) in params[]
                        constraint_values,       # value(s) used as default for state and to check compatibility
                        constraint_values_name,  # name of constraint_values type (e.g. variable, output...)
                        context=NotImplemented):
    """Instantiate and return an OrderedDictionary of States specified in state_list

    Arguments:
    - state_type (class): State class to be instantiated
    - state_list (list): List of State specifications (generally from owner.paramsCurrent[kw<State>]),
                         (state_spec, params_dict) tuple(s), or None
                         if None, instantiate a default using constraint_values as state_spec
    - state_param_identifier (str): kw used to identify set of states in params;  must be one of:
        - kwInputState
        - kwOutputState
    - constraint_values (2D np.array): set of 1D np.ndarrays used as default values and
        for compatibility testing in instantiation of state(s):
        - kwInputState: self.variable
        - kwOutputState: self.value
        ?? ** Note:
        * this is ignored if param turns out to be a dict (entry value used instead)
    - constraint_values_name (str):  passed to State.instantiate_mechanism_state(), used in error messages
    - context (str)

    If state_list is None:
        - instantiate a default State using constraint_values,
        - place as the single entry in the OrderedDict
    Otherwise, if state_list is:
        - a single value:
            instantiate it (if necessary) and place as the single entry in an OrderedDict
        - a list:
            instantiate each item (if necessary) and place in an OrderedDict
        - an OrderedDict:
            instantiate each entry value (if necessary)
    In each case, generate an OrderedDict with one or more entries, assigning:
        the key for each entry the name of the outputState if provided,
            otherwise, use kwMechanism<state_type>States-n (incrementing n for each additional entry)
        the state value for each entry to the corresponding item of the mechanism's state_type state's value
        the dict to both self.<state_type>States and paramsCurrent[kwMechanism<state_type>States]
        self.<state_type>State to self.<state_type>States[0] (the first entry of the dict)
    Notes:
        * if there is only one state, but the value of the mechanism's state_type has more than one item:
            assign it to the sole state, which is assumed to have a multi-item value
        * if there is more than one state:
            the number of states must match length of mechanisms state_type value or an exception is raised

    :param state_type:
    :param state_param_identifier:
    :param constraint_values:
    :param constraint_values_name:
    :param context:
    :return:
    """

    state_entries = state_list

    # If kwMechanism<*>States is None, instantiate a default state_type using constraint_values
    if not state_entries:
        # assign constraint_values as single item in a list, to be used as state_spec below
        state_entries = constraint_values

        # issue warning if in VERBOSE mode:
        if owner.prefs.verbosePref:
            print("No {0} specified for {1}; default will be created using {2} of execute method ({3})"
                  " as its value".format(state_param_identifier,
                                         owner.__class__.__name__,
                                         constraint_values_name,
                                         constraint_values))

    # kwMechanism<*>States should now be either a list (possibly constructed in validate_params) or an OrderedDict:
    if isinstance(state_entries, (list, OrderedDict, np.ndarray)):

        # VALIDATE THAT NUMBER OF STATES IS COMPATIBLE WITH NUMBER OF CONSTRAINT VALUES
        num_states = len(state_entries)

        # Check that constraint_values is an indexable object, the items of which are the constraints for each state
        # Notes
        # * generally, this will be a list or an np.ndarray (either >= 2D np.array or with a dtype=object)
        # * for OutputStates, this should correspond to its value
        try:
            # Insure that constraint_values is an indexible item (list, >=2D np.darray, or otherwise)
            num_constraint_items = len(constraint_values)
        except:
            raise StateError("PROGRAM ERROR: constraint_values ({0}) for {1} of {2}"
                                 " must be an indexable object (e.g., list or np.ndarray)".
                                 format(constraint_values, constraint_values_name, state_type.__name__))

        # # If there is only one state, assign full constraint_values to sole state
        # #    but only do this if number of constraints is > 1, as need to leave solo exposed value intact
        # if num_states == 1 and num_constraint_items > 1:
        #     state_constraint_value = [constraint_values]

        # If number of states exceeds number of items in constraint_values, raise exception
        if num_states > num_constraint_items:
            raise StateError("There are too many {0} specified ({1}) in {2} "
                                 "for the number of values ({3}) in the {4} of its execute method".
                                 format(state_param_identifier,
                                        num_states,
                                        owner.__class__.__name__,
                                        num_constraint_items,
                                        constraint_values_name))

        # If number of states is less than number of items in constraint_values, raise exception
        elif num_states < num_constraint_items:
            raise StateError("There are fewer {0} specified ({1}) than the number of values ({2}) "
                                 "in the {3} of the execute method for {4}".
                                 format(state_param_identifier,
                                        num_states,
                                        num_constraint_items,
                                        constraint_values_name,
                                        owner.name))

        # INSTANTIATE EACH STATE

        # Iterate through list or state_dict:
        # - instantiate each item or entry as state_type State
        # - get name, and use as key to assign as entry in self.<*>states
        states = OrderedDict()

        # Instantiate state for entry in list or dict
        # Note: if state_entries is a list, state_spec is the item, and key is its index in the list
        for key, state_spec in state_entries if isinstance(state_entries, dict) else enumerate(state_entries):
            state_name = ""

            # State_entries is already an OrderedDict, so use:
            # - entry key as state's name
            # - entry value as state_spec
            if isinstance(key, str):
                state_name = key
                state_constraint_value = constraint_values
                # Note: state_spec has already been assigned to entry value by enumeration above
                state_params = None

            # State_entries is a list
            else:
                if isinstance(state_spec, tuple):
                    if not len(state_spec) == 2:
                        raise StateError("List of {}s to instantiate for {} has tuple with more than 2 items:"
                                                  " {}".format(state_type.__name__, owner.name, state_spec))

                    state_spec, state_params = state_spec
                    if not (isinstance(state_params, dict) or state_params is None):
                        raise StateError("In list of {}s to instantiate for {}, second item of tuple "
                                                  "({}) must be a params dict or None:".
                                                  format(state_type.__name__, owner.name, state_params))
                else:
                    state_params = None

                # If state_spec is a string, then use:
                # - string as the name for a default state
                # - key (index in list) to get corresponding value from constraint_values as state_spec
                # - assign same item of constraint_values as the constraint
                if isinstance(state_spec, str):
                    # Use state_spec as state_name if it has not yet been used
                    if not state_name is state_spec and not state_name in states:
                        state_name = state_spec
                    # Add index suffix to name if it is already been used
                    # Note: avoid any chance of duplicate names (will cause current state to overwrite previous one)
                    else:
                        state_name = state_spec + '-' + str(key)
                    state_spec = constraint_values[key]
                    state_constraint_value = constraint_values[key]

                # If state_spec is NOT a string, then:
                # - use default name (which is incremented for each instance in register_categories)
                # - use item as state_spec (i.e., assume it is a specification for a State)
                #   Note:  still need to get indexed element of constraint_values,
                #          since it was passed in as a 2D array (one for each state)
                else:
                    # If only one state, don't add index suffix
                    if num_states == 1:
                        state_name = 'Default' + state_param_identifier[:-1]
                    # Add incremented index suffix for each state name
                    else:
                        state_name = 'Default' + state_param_identifier[:-1] + "-" + str(key+1)
                    # Note: state_spec has already been assigned to item in state_entries list by enumeration above
                    state_constraint_value = constraint_values[key]

            state = instantiate_mechanism_state(owner=owner,
                                                state_type=state_type,
                                                state_name=state_name,
                                                state_spec=state_spec,
                                                state_params=state_params,
                                                constraint_values=state_constraint_value,
                                                constraint_values_name=constraint_values_name,
                                                context=context)

            # Get name of state, and use as key to assign to states OrderedDict
            states[state.name] = state
        return states

    else:
        # This shouldn't happen, as kwMechanism<*>States was validated to be one of the above in validate_params
        raise StateError("Program error: {0} for is not a recognized {1} specification for {2}; "
                                  "it should have been converted to a list in Mechanism.validate_params)".
                                  format(state_entries, state_param_identifier, owner.__class__.__name__))


def instantiate_mechanism_state(owner,
                                state_type,            # State subclass
                                state_name,            # Name used to refer to subclass in prompts
                                state_spec,            # State subclass, object, spec dict or value
                                state_params,                # params for state
                                constraint_values,     # Value used to check compatibility
                                constraint_values_name,# Name of constraint_values's type (e.g. variable, output...)
                                context=NotImplemented):
    """Instantiate a State of specified type, with a value that is compatible with constraint_values

    Constraint value must be a number or a list or tuple of numbers
    (since it is used as the variable for instantiating the requested state)

    If state_spec is a:
    + State class:
        implements default using constraint_values
    + State object:
        checks ownerMechanism is owner (if not, user is given options in check_mechanism_state_ownership)
        checks compatibility of value with constraint_values
    + Projection object:
        assigns constraint_values to value
        assigns projection to kwStateParams{kwStateProjections:<projection>}
    + Projection class (or keyword string constant for one):
        assigns constraint_values to value
        assigns projection class spec to kwStateParams{kwStateProjections:<projection>}
    + specification dict for State (see XXX for context):
        check compatibility of kwStateValue with constraint_values
    + ParamValueProjection tuple: (only allowed for ParameterState spec)
        assigns ParamValueProjection.value to state_spec
        assigns ParamValueProjection.projection to kwStateParams{kwStateProjections:<projection>}
    + 2-item tuple: (only allowed for ParameterState spec)
        assigns first item to state_spec
        assigns second item to kwStateParams{kwStateProjections:<projection>}
    + value:
        checks compatibility with constraint_values
    If any of the conditions above fail:
        a default State of specified type is instantiated using constraint_values as value

    If state_params is specified, include with instantiation of state

    :param context: (str)
    :return state: (State)
    """

# IMPLEMENTATION NOTE: CONSIDER MOVING MUCH IF NOT ALL OF THIS TO State.__init__()

    #region VALIDATE ARGS
    if not inspect.isclass(state_type) or not issubclass(state_type, State):
        raise StateError("state_type arg ({0}) to instantiate_mechanism_state "
                             "must be a State subclass".format(state_type))
    if not isinstance(state_name, str):
        raise StateError("state_name arg ({0}) to instantiate_mechanism_state must be a string".
                             format(state_name))
    if not isinstance(constraint_values_name, str):
        raise StateError("constraint_values_name arg ({0}) to instantiate_mechanism_state must be a string".
                             format(constraint_values_name))
    #endregion

    # Assume state is specified as a value, so set state_value to it; if otherwise, will be overridden below
    state_value = state_spec

    # # MODIFIED 7/31/16 OLD:
    # state_params = {}
    # MODIFIED 7/31/16 NEW:
    if state_params is None:
        state_params = {}
    # MODIFIED 7/31/16 END

    # Used locally to report type of specification for State
    #  if value is not compatible with constraint_values
    spec_type = None

    #region CHECK FORMAT OF constraint_values AND CONVERT TO SIMPLE VALUE
    # If constraint_values is a class:
    if inspect.isclass(constraint_values):
        # If constraint_values is a State class, set to variableClassDefault:
        if issubclass(constraint_values, State):
            constraint_values = state_spec.variableClassDefault
        # If constraint_values is a Projection, set to output of execute method:
        if issubclass(constraint_values, Projection):
            constraint_values = constraint_values.value
    # If constraint_values is a State object, set to value:
    elif isinstance(constraint_values, state_type):
        constraint_values = constraint_values.value
    # If constraint_values is a specification dict, presumably it is for a State:
    elif isinstance(constraint_values, dict):
        constraint_values = constraint_values[kwStateValue]
    # If constraint_values is a ParamValueProjection tuple, set to ParamValueProjection.value:
    elif isinstance(constraint_values, ParamValueProjection):
        constraint_values = constraint_values.value
    # Otherwise, assumed to be a value

    # # MODIFIED 6/14/16: QQQ - WHY DOESN'T THIS WORK HERE?? (DONE BELOW, JUST BEFORE CALLING state = state_type(<>)
    # # CONVERT CONSTRAINT_VALUES TO NP ARRAY AS ACTUAL STATE VALUES WILL BE SO CONVERTED (WHERE ??)
    # #  Convert constraint_values to np.array as actual state value is converted
    # constraint_values = convert_to_np_array(constraint_values,1)
    # # MODIFIED END

    #endregion

    #region CHECK COMPATIBILITY OF state_spec WITH constraint_values

    # State subclass
    # If state_spec is a subclass:
    # - instantiate default using constraint_values as value
    if inspect.isclass(state_spec) and issubclass(state_spec, state_type):
        state_value = constraint_values

    # State object
    # If state_spec is a State object:
    # - check that its value attribute matches the constraint_values
    # - check that its ownerMechanism = owner
    # - if either fails, assign default
    # from Functions.States.State import OutputState
    if isinstance(state_spec, state_type):
        # Check that State's value is compatible with Mechanism's variable
        if iscompatible(state_spec.value, constraint_values):
            # Check that Mechanism is State's owner;  if it is not, user is given options
            state =  owner.check_mechanism_state_ownership(state_name, state_spec)
            if state:
                return
            else:
                # State was rejected, and assignment of default selected
                state = constraint_values
        else:
            # State's value doesn't match constraint_values, so assign default
            state = constraint_values
            spec_type = state_name

    # Specification dict
    # If state_spec is a specification dict:
    # - check that kwStateValue matches constraint_values and assign to state_value
    # - add/assign kwState params to state_params
    if isinstance(state_spec, dict):
        try:
            state_value =  state_spec[kwStateValue]
        except KeyError:
            state_value = constraint_values
            if owner.prefs.verbosePref:
                print("{0} missing from inputState specification dict for {1};  default ({2}) will be used".
                                     format(kwStateValue, owner.name, constraint_values))
        if not iscompatible(state_value, constraint_values):
            state_value = constraint_values
            spec_type = kwStateValue

        # # MODIFIED 7/31/16 OLD:
        # try:
        #     state_params = state_spec[kwStateParams]
        # except KeyError:
        #     state_params = {}

        # MODIFIED 7/31/16 NEW:
        # Add state_spec[kwStateParams] to state_params
        try:
            state_params.update(state_spec[kwStateParams])
        # state_spec[kwStateParams] was not specified
        except KeyError:
                pass
        # MODIFIED END

    # ParamValueProjection
    # If state_type is ParameterState and state_spec is a ParamValueProjection tuple:
    # - check that ParamValueProjection.value matches constraint_values and assign to state_value
    # - assign ParamValueProjection.projection to kwStateParams:{kwStateProjections:<projection>}
    # Note: validity of projection specification or compatiblity of projection's variable or execute method output
    #       with state value is handled in State.instantiate_projections
    if isinstance(state_spec, ParamValueProjection):
        from Functions.States.ParameterState import ParameterState
        if not issubclass(state_type, ParameterState):
            raise StateError("ParamValueProjection ({0}) not permitted as specification for {1} (in {2})".
                                 format(state_spec, state_type.__name__, owner.name))
        state_value =  state_spec.value
        if not iscompatible(state_value, constraint_values):
            state_value = constraint_values
            spec_type = 'ParamValueProjection'
        # MODIFIED 7/31/16 OLD:
        # state_params = {kwStateProjections:[state_spec.projection]}
        # MODIFIED 7/31/16 NEW:
        state_params.update({kwStateProjections:[state_spec.projection]})

    # 2-item tuple (param_value, projection_spec) [convenience notation for projection to parameterState]:
    # If state_type is ParameterState, and state_spec is a tuple with two items, the second of which is a
    #    projection specification (kwControlSignal or kwMapping)), allow it (though should use ParamValueProjection)
    # - check that first item matches constraint_values and assign to state_value
    # - assign second item as projection to kwStateParams:{kwStateProjections:<projection>}
    # Note: validity of projection specification or compatibility of projection's variable or execute method output
    #       with state value is handled in State.instantiate_projections
    # IMPLEMENTATION NOTE:
    #    - need to do some checking on state_spec[1] to see if it is a projection
    #      since it could just be a numeric tuple used for the variable of a state;
    #      could check string against ProjectionRegistry (as done in parse_projection_ref in State)
    if (isinstance(state_spec, tuple) and len(state_spec) is 2 and
            (state_spec[1] is kwControlSignal or
                     state_spec[1] is kwMapping or
                 isinstance(state_spec[1], Projection) or
                 inspect.isclass(state_spec[1] and issubclass(state_spec[1], Projection))
             )):
        from Functions.States.ParameterState import ParameterState
        if not issubclass(state_type, ParameterState):
            raise StateError("Tuple with projection spec ({0}) not permitted as specification "
                                      "for {1} (in {2})".format(state_spec, state_type.__name__, owner.name))
        state_value =  state_spec[0]
        constraint_values = state_value
        # if not iscompatible(state_value, constraint_values):
        #     state_value = constraint_values
        #     spec_type = 'ParamValueProjection'
        # MODIFIED 7/31/16 OLD:
        state_params = {kwStateProjections:[state_spec[1]]}
        # MODIFIED 7/31/16 NEW:
        state_params.update({kwStateProjections:[state_spec[1]]})

    # Projection
    # If state_spec is a Projection object or Projection class
    # - assign constraint_values to state_value
    # - assign ParamValueProjection.projection to kwStateParams:{kwStateProjections:<projection>}
    # Note: validity of projection specification or compatibility of projection's variable or execute method output
    #       with state value is handled in State.instantiate_projections
    try:
        issubclass(state_spec, Projection)
    except TypeError:
        if isinstance(state_spec, (Projection, str)):
            state_value =  constraint_values
            # # MODIFIED 7/31/16 OLD:
            # state_params = {kwStateProjections:{kwProjectionType:state_spec}}
            # MODIFIED 7/31/16 NEW:
            state_params.update({kwStateProjections:{kwProjectionType:state_spec}})
    else:
        state_value =  constraint_values
        # # MODIFIED 7/31/16 OLD:
        # state_params = {kwStateProjections:state_spec}
        # MODIFIED 7/31/16 NEW:
        state_params.update({kwStateProjections:state_spec})

    # FIX:  WHEN THERE ARE MULTIPLE STATES, LENGTH OF constraint_values GROWS AND MISMATCHES state_value
    # IMPLEMENT:  NEED TO CHECK FOR ITEM OF constraint_values AND CHECK COMPATIBLITY AGAINST THAT
    #         # Do one last check for compatibility of value with constraint_values (in case state_spec was a value)
    if not iscompatible(state_value, constraint_values):
        # FIX:  IMPLEMENT TEST OF constraint_index HERE 5/26/16
        # pass
        state_value = constraint_values
        spec_type = state_name

    # WARN IF DEFAULT (constraint_values) HAS BEEN ASSIGNED
    # spec_type has been assigned, so iscompatible() failed above and constraint value was assigned
    if spec_type:
        if owner.prefs.verbosePref:
            print("Value ({0}) of {1} (type: {2}) is not compatible with {3} ({4}) of {6};"
                  " default {4} will be created using {5}".
                  format(state_value,
                         state_name,
                         spec_type,
                         constraint_values_name,
                         constraint_values.__class__.__name__,
                         constraint_values,
                         owner.__class__.__name__))
    #endregion

    #region INSTANTIATE STATE:
    # Instantiate new State
    # Note: this will be either a default State instantiated using constraint_values as its value
    #       or one determined by a specification dict, depending on which of the following obtained above:
    # - state_spec was a ParamValueProjection tuple
    # - state_spec was a specification dict
    # - state_spec was a value
    # - value of specified State was incompatible with constraint_values
    # - owner of State was not owner and user chose to implement default
    # IMPLEMENTATION NOTE:
    # - setting prefs=NotImplemented causes TypeDefaultPreferences to be assigned (from FunctionPreferenceSet)
    # - alternative would be prefs=owner.prefs, causing state to inherit the prefs of its ownerMechanism;

    #  Convert constraint_values to np.array to match state_value (which, as output of execute method, will be one)
    constraint_values = convert_to_np_array(constraint_values,1)

    # Implement default State
    state = state_type(owner_mechanism=owner,
                       reference_value=constraint_values,
                       value=state_value,
                       name=state_name,
                       params=state_params,
                       prefs=NotImplemented,
                       context=context)

# FIX LOG: ADD NAME TO LIST OF MECHANISM'S VALUE ATTRIBUTES FOR USE BY LOGGING ENTRIES
    # This is done here to register name with Mechanism's stateValues[] list
    # It must be consistent with value setter method in State
# FIX LOG: MOVE THIS TO MECHANISM STATE __init__ (WHERE IT CAN BE KEPT CONSISTENT WITH setter METHOD??
#      OR MAYBE JUST REGISTER THE NAME, WITHOUT SETTING THE
    setattr(owner, state.name+'.value', state.value)

    #endregion

    return state

def check_mechanism_parameter_state_value(owner, param_name, value):
    """Check that parameter value (<ParameterState>.value) is compatible with value in paramClassDefault

    :param param_name: (str)
    :param value: (value)
    :return: (value)
    """
    default_value = owner.paramClassDefaults[param_name]
    if iscompatible(value, default_value):
        return value
    else:
        if owner.prefs.verbosePref:
            print("Format is incorrect for value ({0}) of {1} in {2};  default ({3}) will be used.".
                  format(value, param_name, owner.name, default_value))
        return default_value

def check_mechanism_state_ownership(owner, param_name, mechanism_state):
    """Check whether State's owner is owner and if not offer options how to handle it

    If State's owner is not owner, options offered to:
    - reassign it to owner
    - make a copy and assign to owner
    - return None => caller should assign default

    :param param_name: (str)
    :param mechanism_state: (State)
    :param context: (str)
    :return: (State or None)
    """

    if mechanism_state.ownerMechanism != owner:
        reassign = input("\nState {0}, assigned to {1} in {2}, already belongs to {3}"
                         " You can choose to reassign it (r), copy it (c), or assign default (d):".
                         format(mechanism_state.name, param_name, owner.name,
                                mechanism_state.ownerMechanism.name))
        while reassign != 'r' and reassign != 'c' and reassign != 'd':
            reassign = input("\nReassign (r), copy (c), or default (d):".
                             format(mechanism_state.name, param_name, owner.name,
                                    mechanism_state.ownerMechanism.name))

            if reassign == 'r':
                while reassign != 'y' and reassign != 'n':
                    reassign = input("\nYou are certain you want to reassign it {0}? (y/n):".
                                     format(param_name))
                if reassign == 'y':
                    # Note: assumed that parameters have already been checked for compatibility with assignment
                    return mechanism_state

        # Make copy of state
        if reassign == 'c':
            import copy
            mechanism_state = copy.deepcopy(mechanism_state)

        # Assign owner to chosen state
        mechanism_state.ownerMechanism = owner
    return mechanism_state
