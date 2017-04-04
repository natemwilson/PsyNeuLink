import logging

from PsyNeuLink import Component
from PsyNeuLink.Components.Mechanisms.Mechanism import Mechanism
#from PsyNeuLink.scheduling.Scheduler import Scheduler
from PsyNeuLink.Globals.TimeScale import TimeScale

logger = logging.getLogger(__name__)

class ConditionError(Exception):
     def __init__(self, error_value):
         self.error_value = error_value

     def __str__(self):
         return repr(self.error_value)

class ConditionSet(object):
    def __init__(self, scheduler=None, conditions={}):
        '''
        :param self:
        :param scheduler: a :keyword:`Scheduler` that these conditions are associated with, which maintains any state necessary for these conditions
        :param conditions: a :keyword:`dict` mapping :keyword:`Component`s to :keyword:`iterable`s of :keyword:`Condition`s, can be added later with :keyword:`add_condition`
        '''
        self.scheduler = scheduler
        # even though conditions may be added in arbitrary iterables, they are stored internally as dicts of sets
        self.conditions = conditions

    def __contains__(self, item):
        return item in self.conditions

    def add_condition(self, owner, condition):
        '''
        :param: self:
        :param owner: the :keyword:`Component` that is dependent on the :param conditions:
        :param conditions: a :keyword:`Condition` (including All or Any)
        '''
        logger.debug('add_condition: Setting scheduler of {0}, (owner {2}) to self.scheduler ({1})'.format(condition, self.scheduler, owner))
        condition.owner = owner
        condition.scheduler = self.scheduler
        self.conditions[owner] = condition

    def add_condition_set(self, conditions):
        '''
        :param: self:
        :param conditions: a :keyword:`dict` mapping :keyword:`Component`s to :keyword:`Condition`s, can be added later with :keyword:`add_condition`
        '''
        for owner in conditions:
            self.conditions[owner] = conditions[owner]

class Condition(object):
    def __init__(self, dependencies, func, *args, **kwargs):
        '''
        :param self:
        :param dependencies: one or more PNL objects over which func is evaluated to determine satisfaction of the :keyword:`Condition`
            user must ensure that dependencies are suitable as func parameters
        :param func: parameters over which func is evaluated to determine satisfaction of the :keyword:`Condition`
        :param args: additional formal arguments passed to func
        :param kwargs: additional keyword arguments passed to func
        '''
        self.dependencies = dependencies
        self.func = func
        self.args = args
        self.kwargs = kwargs

        self._scheduler = None
        self._owner = None
        #logger.debug('{1} dependencies: {0}'.format(dependencies, type(self).__name__))

    @property
    def scheduler(self):
        return self._scheduler

    @scheduler.setter
    def scheduler(self, value):
        logger.debug('Condition ({0}) setting scheduler to {1}'.format(type(self).__name__, value))
        self._scheduler = value

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, value):
        logger.debug('Condition ({0}) setting owner to {1}'.format(type(self).__name__, value))
        self._owner = value

    def is_satisfied(self):
        has_args = len(self.args) > 0
        has_kwargs = len(self.kwargs) > 0

        if has_args and has_kwargs:
            return self.func(self.dependencies, *self.args, **self.kwargs)
        if has_args:
            return self.func(self.dependencies, *self.args)
        if has_kwargs:
            return self.func(self.dependencies, **self.kwargs)
        return self.func(self.dependencies)

# TODO: create this class to subclass All and Any from
#class CompositeCondition(Condition):
    #def

class All(Condition):
    def __init__(self, *args):
        '''
        :param self:
        :param args: one or more :keyword:`Condition`s, all of which must be satisfied to satisfy this composite condition
            to initialize with a list (for example),
                conditions = [AfterNCalls(mechanism, 5) for mechanism in mechanism_list]
            unpack the list to supply its members as args
                composite_condition = All(*conditions)
        '''
        super().__init__(args, self.satis)

    @Condition.scheduler.setter
    def scheduler(self, value):
        for cond in self.dependencies:
            logger.debug('schedule setter: Setting scheduler of {0} to ({1})'.format(cond, value))
            if cond.scheduler is None:
                cond.scheduler = value

    @Condition.owner.setter
    def owner(self, value):
        for cond in self.dependencies:
            logger.debug('owner setter: Setting owner of {0} to ({1})'.format(cond, value))
            if cond.owner is None:
                cond.owner = value

    def satis(self, conds):
        for cond in conds:
            if not cond.is_satisfied():
                return False
        return True

class Any(Condition):
    def __init__(self, *args):
        '''
        :param self:
        :param args: one or more :keyword:`Condition`s, any of which must be satisfied to satisfy this composite condition
            to initialize with a list (for example),
                conditions = [AfterNCalls(mechanism, 5) for mechanism in mechanism_list]
            unpack the list to supply its members as args
                composite_condition = All(*conditions)
        '''
        super().__init__(args, self.satis)

    @Condition.scheduler.setter
    def scheduler(self, value):
        logger.debug('Any setter args: {0}'.format(self.dependencies))
        for cond in self.dependencies:
            logger.debug('schedule setter: Setting scheduler of {0} to ({1})'.format(cond, value))
            if cond.scheduler is None:
                cond.scheduler = value

    @Condition.owner.setter
    def owner(self, value):
        for cond in self.dependencies:
            logger.debug('owner setter: Setting owner of {0} to ({1})'.format(cond, value))
            if cond.owner is None:
                cond.owner = value

    def satis(self, conds):
        for cond in conds:
            if cond.is_satisfied():
                return True
        return False

######################################################################
# Included Conditions
######################################################################
class Always(Condition):
    def __init__(self):
        super().__init__(True, lambda x: x)

class Never(Condition):
    def __init__(self):
        super().__init__(False, lambda x: x)

class AtStep(Condition):
    def __init__(self, n, time_scale=TimeScale.TRIAL):
        def func(n):
            if self.scheduler is None:
                raise ConditionError('{0}: self.scheduler is None - scheduler must be assigned'.format(type(self).__name__))
            try:
                return self.scheduler.counts_current[time_scale][self.scheduler] == n
            except KeyError as e:
                raise ConditionError('{0}: {1}, is time_scale set correctly? Currently: {2}'.format(type(self).__name__, e, time_scale))
        super().__init__(n, func)

class AfterStep(Condition):
    def __init__(self, n, time_scale=TimeScale.TRIAL):
        def func(n, time_scale):
            if self.scheduler is None:
                raise ConditionError('{0}: self.scheduler is None - scheduler must be assigned'.format(type(self).__name__))
            return self.scheduler.counts_current[time_scale][self.scheduler] >= n+1
        super().__init__(n, func, time_scale)

class AfterNCalls(Condition):
    def __init__(self, dependency, n, time_scale=TimeScale.TRIAL):
        def func(dependency, n):
            if self.scheduler is None:
                raise ConditionError('{0}: self.scheduler is None - scheduler must be assigned'.format(type(self).__name__))
            num_calls = self.scheduler.counts_current[time_scale][dependency]
            logger.debug('{0} has reached {1} num_calls in {2}'.format(dependency, num_calls, time_scale.name))
            return num_calls >= n
        super().__init__(dependency, func, n)

class AfterNCallsCombined(Condition):
    def __init__(self, dependency_list, n, time_scale=TimeScale.TRIAL):
        def func(dependency_list, n):
            if self.scheduler is None:
                raise ConditionError('{0}: self.scheduler is None - scheduler must be assigned'.format(type(self).__name__))
            count_sum = 0
            for d in dependency_list:
                count_sum += self.scheduler.counts_current[time_scale][d]
                logger.debug('{0} has reached {1} num_calls in {2}'.format(d, self.scheduler.counts_current[time_scale][d], time_scale.name))
            return count_sum >= n
        super().__init__(dependency_list, func, n)

class AfterNTrials(Condition):
    def __init__(self, n):
        def func(n):
            if self.scheduler is None:
                raise ConditionError('{0}: self.scheduler is None - scheduler must be assigned'.format(type(self).__name__))
            return self.scheduler.counts_total[TimeScale.TRIAL] >= n
        super().__init__(n, func)

class BeforeStep(Condition):
    def __init__(self, n, time_scale=TimeScale.TRIAL):
        def func(n, time_scale):
            if self.scheduler is None:
                raise ConditionError('{0}: self.scheduler is None - scheduler must be assigned'.format(type(self).__name__))
            return self.scheduler.counts_current[time_scale][self.scheduler] <= n
        super().__init__(n, func, time_scale)

class EveryNSteps(Condition):
    def __init__(self, n, time_scale=TimeScale.TRIAL):
        def func(n, time_scale):
            if self.scheduler is None:
                raise ConditionError('{0}: self.scheduler is None - scheduler must be assigned'.format(type(self).__name__))
            return self.scheduler.counts_current[time_scale][self.scheduler] % n == 0
        super().__init__(n, func, time_scale)

class EveryNCalls(Condition):
    def __init__(self, dependency, n):
        def func(dependency, n):
            if self.scheduler is None:
                raise ConditionError('{0}: self.scheduler is None - scheduler must be assigned'.format(type(self).__name__))
            num_calls = self.scheduler.counts_useable[dependency][self.owner]
            logger.debug('{0} has reached {1} num_calls'.format(dependency, num_calls))
            return num_calls >= n
        super().__init__(dependency, func, n)

class JustRan(Condition):
    def __init__(self, dependency):
        def func(dependency):
            if self.scheduler is None:
                raise ConditionError('{0}: self.scheduler is None - scheduler must be assigned'.format(type(self).__name__))
            logger.debug('checking if {0} in previous execution step set'.format(dependency))
            if isinstance(self.scheduler.execution_queue[-1], set):
                return dependency in self.scheduler.execution_queue[-1]
            else:
                return dependency == self.scheduler.execution_queue[-1]
        super().__init__(dependency, func)

class WhenFinished(Condition):
    def __init__(self, dependency):
        def func(dependency):
            if isinstance(dependency, Mechanism):
                return dependency.is_finished
            else:
                raise ConditionError('WhenFinished: Unsupported dependency type: {0}'.format(type(dependency)))

        super().__init__(dependency, func)

class WhenFinishedAny(Condition):
    def __init__(self, *dependencies):
        def func(_none, *dependencies):
            for d in dependencies:
                if isinstance(d, Mechanism):
                    if d.is_finished:
                        return True
                else:
                    raise ConditionError('WhenFinished: Unsupported dependency type: {0}'.format(type(d)))
            return False

        super().__init__(None, *dependencies, func)

class WhenFinishedAll(Condition):
    def __init__(self, *dependencies):
        def func(_none, *dependencies):
            for d in dependencies:
                if isinstance(d, Mechanism):
                    if not d.is_finished:
                        return False
                else:
                    raise rConditionError('WhenFinished: Unsupported dependency type: {0}'.format(type(d)))
            return True

        super().__init__(None, func, *dependencies)
