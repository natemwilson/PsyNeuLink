# Princeton University licenses this file to You under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may obtain a copy of the License at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.
#
#
# **************************************************  Main *************************************************************
#
#
from enum import Enum
from enum import IntEnum
from enum import EnumMeta
from collections import namedtuple
import numbers
import numpy as np
from random import random

from Globals.Keywords import *
from Globals.TimeScale import *
from Globals.Defaults import *

"""Contents:

KVO:
observe_value_at_keypath(keypath, old_value, new_value)

COMPARISON:
def iscompatible(candidate, reference=NotImplemented, **kargs)

ENUM:
Autonumber
"""

class MainError(Exception):
    def __init__(self, error_value):
        self.error_value = error_value

    def __str__(self):
        return repr(self.error_value)


class ModulationOperation(Enum):
    DISABLED = 0
    ADD = lambda runtime, default : runtime + default
    MULTIPLY = lambda runtime, default : runtime * default
    OVERRIDE = lambda runtime, default : runtime

def get_modulationOperation_name(operation):
        x = operation(1,2)
        if x is 1:
            return 'ModulationOperation.OVERRIDE'
        elif x is 2:
            return 'ModulationOperation.MULTIPLY'
        elif x is 3:
            return 'ModulationOperation.ADD'



class AutoNumber(IntEnum):
    """Autonumbers IntEnum type

    First item in list of declarations is numbered 0;
    Others incremented by 1

    Sample:

        class NumberedList(AutoNumber):
            FIRST_ITEM = ()
            SECOND_ITEM = ()

        >>>NumberedList.FIRST_ITEM.value
         0
        >>>NumberedList.SECOND_ITEM.value
         1

    Adapted from AutoNumber example for Enum at https://docs.python.org/3/library/enum.html#enum.IntEnum:
    Notes:
    * Start of numbering changed to 0 (from 1 in example)
    * obj based on int rather than object
    """
    def __new__(cls):
        # Original example:
        # value = len(cls.__members__) + 1
        # obj = object.__new__(cls)
        value = len(cls.__members__)
        obj = int.__new__(cls)
        obj._value_ = value
        return obj


# ************************************** GLOBAL STRUCTURES AND CONSTANTS ***********************************************

TEST_CONDTION = False

# ********************************************* KVO ********************************************************************

class classProperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()

def observe_value_at_keypath(keypath, old_value, new_value):
    print("KVO keypath: {0};  old value: {1};  new value: {2}".format(keypath, old_value, new_value))

kwCompatibilityType = "type"
kwCompatibilityLength = "length"
kwCompatibilityNumeric = "numeric"

#   IMPLEMENT SUPPORT OF *LIST* OF TYPES IN kwCompatibilityType (see Function.__init__ FOR EXAMPLE)
def iscompatible(candidate, reference=NotImplemented, **kargs):
    """Check if candidate matches reference or, if that is omitted, it matches type, length and/or numeric specification

    If kargs is omitted, candidate and reference must match in type and length
    If reference and kargs are omitted, candidate must be a list of numbers (of any length)
    If reference is omitted, candidate must match specs in kargs

    kargs is an optional dictionary with the following entries:
        kwCompatibilityType ("type"):<type> (default: list):  (spec local_variable: match_type)
            - if reference is provided, candidate's type must match or be subclass of reference,
                irrespective of whether kwCompatibilityType is specified or absent;  however, if:
                + kwCompatibilityType is absent, enums are treated as numbers (of which they are a subclass)
                + kwCompatibilityType = enum, then candidate must be an enum if reference is one
            - if reference is absent:
                if kwCompatibilityType is also absent:
                    if kwCompatibilityNumeric is True, all elements of candidate must be numbers
                    if kwCompatibilityNumeric is False, candidate can contain any type
                if kwCompatibilityType is specified, candidate's type must match or be subclass of specified type
            - for iterables, if kwNumeric is False, candidate can have multiple types but
                if a reference is provided, then the corresponding items must have the same type
        kwCompatibilityLength ("length"):<int>  (default: 0):    (spec local_variable: match_length)
            - if kwCompatibilityLength is absent:
                if reference is absent, candidate can be of any length
                if reference is provided, candidate must match reference length
            - if kwCompatibilityLength = 0:
                candidate can be any length, irrespective of the reference or its length
            - if kwCompatibilityLength > 0:
                if reference is provided, candidate must be same length as reference
                if reference is omitted, length of candidate must equal value of kwLength
            Note: kwCompatibility < 0 is illegal;  it will generate a warning and be set to 0
        kwCompatibilityNumeric ("number": <bool> (default: True)  (spec local_variable: number_only)
            If kwCompatibilityNumeric is True, candidate must be either numeric or a list or tuple of numeric types
            If kwCompatibilityNumberic is False, candidate can be strings, lists or tuples of strings, or dicts
                Note: if the candidate is a dict, the number of entries (lengths) are compared, but not their contents

    :param candidate: (value)
    :param reference:  (value)
    :param args: (dict)
    :return:
    """

    # If the two are equal, can settle it right here
    try:
        if candidate == reference:
            return True
    except ValueError:
        # raise MainError("Could not compare {0} and {1}".format(candidate, reference))
        pass

    # If args not provided, assign to default values
    # if not specified in args, use these:
    #     args[kwCompatibilityType] = list
    #     args[kwCompatibilityLength] = 1
    #     args[kwCompatibilityNumeric] = True
    try:
        kargs[kwCompatibilityType]
    except KeyError:
        kargs[kwCompatibilityType] = list
    try:
        kargs[kwCompatibilityLength]
    except KeyError:
        kargs[kwCompatibilityLength] = 1
    try:
        # number_only = kargs[kwCompatibilityNumeric]
        kargs[kwCompatibilityNumeric]
    except KeyError:
        kargs[kwCompatibilityNumeric] = True
        # number_only = True


    # If reference is not provided, assign local_variables to arg values (provided or default)
    if reference is NotImplemented:
        match_type = kargs[kwCompatibilityType]
        match_length = kargs[kwCompatibilityLength]
        number_only = kargs[kwCompatibilityNumeric]
    # If reference is provided, assign specification local_variables to reference-based values
    else:
        match_type = type(reference)
        # If length specification is non-zero (i.e., use length) and reference is an object for which len is defined:
        if kargs[kwCompatibilityLength] and isinstance(reference, (list, tuple, dict)):
            match_length = len(reference)
        else:
            match_length = 0
        # If reference is not a number, then don't require the candidate to be one
        if not isinstance(reference, numbers.Number):
            number_only = False
        else:
            number_only = kargs[kwCompatibilityNumeric]

    if match_length < 0:
        # if settings & Settings.VERBOSE:
        print("\niscompatible({0}, {1}): length argument must be non-negative; it has been set to 0\n".
              format(candidate, kargs, match_length))
        match_length = 0

    # IMPLEMENTATION NOTE:
    #   modified to allow numeric type mismatches (e.g., int and float;
    #   should be added as option in future (i.e., to disallow it)
    # if isinstance(candidate, match_type):
    if (isinstance(candidate, match_type) or
        # MODIFIED 6/7/16 TO ALLOW ndarray AND list TO MATCH;
            (isinstance(candidate, (list, np.ndarray)) and
                 (issubclass(match_type, list) or issubclass(match_type, np.ndarray))) or
        # END MODIFIED 6/7/16
            (isinstance(candidate, numbers.Number) and issubclass(match_type,numbers.Number))):

        # Check compatibility of enum's
        # IMPLEMENTATION NOTE: THE FIRST VERSION BELOW SOUGHT TO CHECK COMPATIBILTY OF ENUM VALUE;  NEEDS WORK
        # if (kargs[kwCompatibilityType] is Enum and
        #         (isinstance(candidate, Enum) or isinstance(match_type, (Enum, IntEnum, EnumMeta)))):
        #     # If either the candidate enum's label is not in the reference's Enum class
        #     #    or its value is different, then return with fail
        #     try:
        #         match_type.__dict__['_member_names_']
        #     except:
        #         pass
        #     if not (candidate.name in match_type.__dict__['_member_names_'] and
        #                 candidate.value is match_type.__dict__['_member_map_'][candidate.name].value):
        #         return False
        # This version simply enforces the constraint that, if either is an enum of some sort, then both must be
        if (kargs[kwCompatibilityType] is Enum and
                (isinstance(candidate, Enum) != isinstance(match_type, (Enum, IntEnum, EnumMeta)))
            ):
            return False

        if isinstance(candidate, numbers.Number):
            return True
        if number_only:
        # MODIFIED 6/7/16 TO ALLOW ndarray AND list TO MATCH;
            # if not isinstance(candidate, list) and not isinstance(candidate, tuple):
            if not isinstance(candidate, (list, tuple, np.ndarray)):
        # END MODIFIED 6/7/16
                return False
            if (not all(isinstance(elem, numbers.Number) for elem in candidate) or
                    not all(isinstance(elem, numbers.Number) for elem in candidate)):
                return False
        if isinstance(candidate, (list, tuple, dict, np.ndarray)):
            if not match_length:
                return True
            else:
                if len(candidate) == match_length:
                    # No reference,so item by item comparison is not relevant
                    if reference is NotImplemented:
                        return True
                    # If reference was provided, compare element by element
                    elif all(isinstance(c, type(r)) for c, r in zip(candidate,reference)):
                        return True
                    else:
                        return False
                else:
                    return False
        else:
            return True
    else:
        return False

def merge_param_dicts(source, specific, general):
    """Search source for specific and general, merge specific with general, and return merged

    Arguments:
    - source (dict): container dict; its entries are searched for specific and general dicts
    - specific (dict or str): if str, will use as key to look for entry dict in source, and check that it is a dict
    - general (dict or str): if str, will use as key to look for entry dict in source, and check that it is a dict

    Description:
    - searches source dict for specific and general dicts
    - if both are found, merges them, with entries from specific overwriting any duplicates in general
    - if only one is found, returns just that dict
    - if neither are found, returns empty dict

    :param source: (dict)
    :param specific: (dict or str)
    :param general: (dict or str)
    :return merged: (dict)
    """

    # Validate source as dict
    if source is NotImplemented:
        return
    if not isinstance(source, dict):
        raise MainError("merge_param_dicts: source {0} must be a dict".format(source))

    # Get specific and make sure it is a dict
    if isinstance(specific, str):
        try:
            specific = source[specific]
        except (KeyError, TypeError):
            specific = {}
    if not isinstance(specific, dict):
        raise MainError("merge_param_dicts: specific {0} must be dict or the name of one in {1}".
                        format(specific, source))

    # Get general and make sure it is a dict
    if isinstance(general, str):
        try:
            general = source[general]
        except (KeyError, TypeError):
            general = {}
    if not isinstance(general, dict):
        raise MainError("merge_param_dicts: general {0} must be dict or the name of one in {1}".
                        format(general, source))

    return general.update(source)

def multi_getattr(obj, attr, default = None):
    """
    Get a named attribute from an object; multi_getattr(x, 'a.b.c.d') is
    equivalent to x.a.b.c.d. When a default argument is given, it is
    returned when any attribute in the chain doesn't exist; without
    it, an exception is raised when a missing attribute is encountered.

    """
    attributes = attr.split(".")
    for i in attributes:
        try:
            obj = getattr(obj, i)
        except AttributeError:
            if default:
                return default
            else:
                raise
    return obj

# # Example usage
# obj  = [1,2,3]
# attr = "append.__doc__.capitalize.__doc__"

# http://pythoncentral.io/how-to-get-an-attribute-from-an-object-in-python/
# getattr also accepts modules as arguments.

# # http://code.activestate.com/recipes/577346-getattr-with-arbitrary-depth/
# multi_getattr(obj, attr) #Will return the docstring for the
#                          #capitalize method of the builtin string
#                          #object


#region NUMPY ARRAY METHODS ******************************************************************************************

def np_array_less_than_2d(array):
    if not isinstance(array, np.ndarray):
        raise MainError("Argument to np_array_less_than_2d() ({0}) must be an np.ndarray".format(array))
    if array.ndim <= 1:
        return True
    else:
        return False

def convert_to_np_array(value, dimension):
    """Convert value to np.array if it is not already

    Check whether value is already an np.ndarray and whether it has non-numeric elements

    Return np.array of specified dimension

    :param value:
    :return:
    """
    if dimension is 1:
        value = np.atleast_1d(value)
    elif dimension is 2:
        value = np.atleast_2d(value)
    else:
        raise MainError("dimensions param ({0}) must be 1 or 2".format(dimension))
    if 'U' in repr(value.dtype):
        raise MainError("{0} has non-numeric entries".format(value))
    return value

def get_value_from_array(array):
    """Extract numeric value from array, preserving numeric type
    :param array:
    :return:
    """

#endregion