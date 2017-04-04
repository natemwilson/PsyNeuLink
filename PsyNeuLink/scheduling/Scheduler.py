import logging

from toposort import toposort

from PsyNeuLink.Globals.TimeScale import TimeScale
from PsyNeuLink.scheduling.condition import ConditionSet, Never

logger = logging.getLogger(__name__)

class SchedulerError(Exception):
     def __init__(self, error_value):
         self.error_value = error_value

     def __str__(self):
         return repr(self.error_value)

class Scheduler(object):
    def __init__(self, composition, condition_set=None, priorities={}):
        '''
        :param self:
        :param composition: (Composition) - the Composition this scheduler is scheduling for
        :param priorities: (dict) - a dictionary mapping each :keyword:`Component` to its priority, where lower values for priority indicate a higher priority
        :param condition_set: (ConditionSet) - a :keyword:`ConditionSet` to be scheduled
        '''
        self.composition = composition
        self.condition_set = condition_set if condition_set is not None else ConditionSet(scheduler=self)
        self.priorities = priorities
        # used for JustRan condition
        self.execution_queue = []
        self.consideration_queue = []

        self._init_consideration_queue()
        self._init_counts()

    def _init_consideration_queue(self):
        dependencies = {}
        for vert in self.composition.graph.vertices:
            dependencies[vert.mechanism] = set()
            for parent in self.composition.graph.get_parents(vert.mechanism):
                dependencies[vert.mechanism].add(parent)

        self.consideration_queue = list(toposort(dependencies))
        logger.debug('Consideration queue: {0}'.format(self.consideration_queue))

    def _init_counts(self):
        # stores the total number of TimeScales that have occurred during the lifetime of this scheduler
        self.counts_total = {ts: 0 for ts in TimeScale}
        # stores the number of occurrences of a mechanism or the scheduler through the time scale's loop
        # i.e. the number of trials in a run, or the number of time steps in a trial, or the number of times mech has occurred in a trial
        self.counts_current = {ts: None for ts in TimeScale}
        # counts_useable is a dictionary intended to store the number of available "instances" of a certain mechanism that
        # are available to expend in order to satisfy conditions such as "run B every two times A runs"
        # specifically, counts_useable[a][b] = n indicates that there are n uses of a that are available for b to expend
        # so, in the previous example B would check to see if counts_useable[A][B] is 2, in which case B can run
        self.counts_useable = {vert.mechanism: {vert.mechanism: 0 for vert in self.composition.graph.vertices} for vert in self.composition.graph.vertices}

        for ts in TimeScale:
            self.counts_current[ts] = {vert.mechanism: 0 for vert in self.composition.graph.vertices}
            self.counts_current[ts][self] = 0

    def _reset_count(self, count, time_scale):
        for c in count[time_scale]:
            count[time_scale][c] = 0

    ################################################################################
    # Validation methods
    #   to provide the user with info if they do something odd
    ################################################################################
    def _validate_run_state(self, termination_conds):
        self._validate_condition_set()
        self._validate_termination(termination_conds)

    def _validate_condition_set(self):
        unspecified_mechs = []
        for vert in self.composition.graph.vertices:
            if vert.mechanism not in self.condition_set:
                self.condition_set.add_condition(vert.mechanism, Never())
                unspecified_mechs.append(vert.mechanism)
        if len(unspecified_mechs) > 0:
            logger.warning('These mechanisms have no Conditions specified, and will NOT be scheduled: {0}'.format(unspecified_mechs))

    def _validate_termination(self, termination_conds):
        for tc in termination_conds:
            if termination_conds[tc] is None:
                if tc in [TimeScale.RUN, TimeScale.TRIAL]:
                    raise SchedulerError('Must specify a {0} termination Condition (termination_conds[{0}]'.format(tc))
            else:
                if termination_conds[tc].scheduler is None:
                    logger.debug('Setting scheduler of {0} to self ({1})'.format(termination_conds[tc], self))
                    termination_conds[tc].scheduler = self

    ################################################################################
    # Run methods
    ################################################################################
    def run(self, termination_conds):
        '''
        :param self:
        :param termination_conds: (dict) - a mapping from :keyword:`TimeScale`s to :keyword:`Condition`s that when met terminate the execution of the specified :keyword:`TimeScale`
        '''
        self._validate_run_state(termination_conds)

        def has_reached_termination(self, time_scale=None):
            term = True
            if time_scale is None:
                for ts in termination_conds:
                    term = term and termination_conds[ts].is_satisfied()
            else:
                term = term and termination_conds[time_scale].is_satisfied()

            return term

        execution_queue = []
        logger.debug('runterm: {0}'.format(termination_conds[TimeScale.RUN]))

        self._reset_count(self.counts_current, TimeScale.RUN)
        while not termination_conds[TimeScale.RUN].is_satisfied():
            logger.debug('run, num trials in run: {0}'.format(self.counts_current[TimeScale.RUN][self]))

            self.counts_useable = {vert.mechanism: {vert.mechanism: 0 for vert in self.composition.graph.vertices} for vert in self.composition.graph.vertices}
            self._reset_count(self.counts_current, TimeScale.TRIAL)
            while not termination_conds[TimeScale.TRIAL].is_satisfied() and not termination_conds[TimeScale.RUN].is_satisfied():
                self._reset_count(self.counts_current, TimeScale.PASS)
                execution_queue_has_changed = False

                cur_index_consideration_queue = 0

                while (
                        cur_index_consideration_queue < len(self.consideration_queue)
                        and not termination_conds[TimeScale.TRIAL].is_satisfied()
                        and not termination_conds[TimeScale.RUN].is_satisfied()
                        ):
                    cur_time_step_exec = set()
                    cur_consideration_set = self.consideration_queue[cur_index_consideration_queue]
                    logger.debug('trial, itercount {0}, consideration_queue {1}'.format(self.counts_current[TimeScale.TRIAL][self], ' '.join([str(x) for x in cur_consideration_set])))

                    # do-while, on cur_consideration_set_has_changed
                    while True:
                        cur_consideration_set_has_changed = False
                        for current_mech in cur_consideration_set:
                            logger.debug('cur time_step exec: {0}'.format(cur_time_step_exec))
                            for m in self.counts_useable:
                                logger.debug('Counts of {0} useable by'.format(m))
                                for m2 in self.counts_useable[m]:
                                    logger.debug('\t{0}: {1}'.format(m2, self.counts_useable[m][m2]))

                            if self.condition_set.conditions[current_mech].is_satisfied():
                                if current_mech not in cur_time_step_exec:
                                    logger.debug('adding {0} to execution list'.format(current_mech))
                                    logger.debug('cur time_step exec pre add: {0}'.format(cur_time_step_exec))
                                    cur_time_step_exec.add(current_mech)
                                    logger.debug('cur time_step exec post add: {0}'.format(cur_time_step_exec))
                                    execution_queue_has_changed = True
                                    cur_consideration_set_has_changed = True

                                    for ts in TimeScale:
                                        self.counts_current[ts][current_mech] += 1

                                    # current_mech's mechanism is added to the execution queue, so we now need to
                                    # reset all of the counts useable by current_mech's mechanism to 0
                                    for m in self.counts_useable:
                                        self.counts_useable[m][current_mech] = 0
                                    # and increment all of the counts of current_mech's mechanism useable by other
                                    # mechanisms by 1
                                    for m in self.counts_useable:
                                        self.counts_useable[current_mech][m] += 1
                        # do-while condition
                        if not cur_consideration_set_has_changed:
                            break

                    if len(cur_time_step_exec) >= 1:
                        if len(cur_time_step_exec) > 1:
                            self.execution_queue.append(cur_time_step_exec)
                        else:
                            self.execution_queue.append(cur_time_step_exec.pop())
                        for ts in TimeScale:
                            self.counts_current[ts][self] += 1

                    cur_index_consideration_queue += 1

                if not execution_queue_has_changed:
                    self.execution_queue.append(set())
                    for ts in TimeScale:
                        self.counts_current[ts][self] += 1

                # can execute the execution_queue here
                logger.info(' '.join([str(x) for x in self.execution_queue]))
                self.counts_total[TimeScale.PASS] += 1

            self.counts_total[TimeScale.TRIAL] += 1

        self.counts_total[TimeScale.RUN] += 1
        return self.execution_queue
