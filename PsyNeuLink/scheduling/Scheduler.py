import logging

from PsyNeuLink.Globals.TimeScale import TimeScale

#only for testing purposes in main
from PsyNeuLink.scheduling.condition import *
from PsyNeuLink.composition import Composition
from PsyNeuLink.Components.Mechanisms.ProcessingMechanisms.TransferMechanism import TransferMechanism
from PsyNeuLink.Components.Functions.Function import Linear

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

        self.counts = {ts: {} for ts in TimeScale}
        self.counts[TimeScale.RUN] = {vert.mechanism: 0 for vert in self.composition.graph.vertices}
        self.counts[TimeScale.RUN][self] = 0
        self.counts[TimeScale.TRIAL] = {vert.mechanism: 0 for vert in self.composition.graph.vertices}
        self.counts[TimeScale.TRIAL][self] = 0

    def _reset(self, time_scale):
        for count in self.counts[time_scale]:
            self.counts[time_scale][count] = 0

    def run(self, run_termination_cond=None, trial_termination_cond=None):
        '''
        :param self:
        :param run_termination_cond: (:keyword:`Condition`) - the :keyword:`Condition` that when met terminates the run
        :param trial_termination_cond: (:keyword:`Condition`) - the :keyword:`Condition` that when met terminates each trial
        '''
        if run_termination_cond is None:
            raise SchedulerError('Must specify a run termination Condition (run_termination_cond)')
        elif not isinstance(run_termination_cond, Condition):
            raise SchedulerError('Run termination condition (run_termination_cond) must be a Condition object')

        if trial_termination_cond is None:
            raise SchedulerError('Must specify a trial termination Condition (trial_termination_cond)')
        elif not isinstance(trial_termination_cond, Condition):
            raise SchedulerError('Trial termination condition (trial_termination_cond) must be a Condition object')

        if run_termination_cond.scheduler is None:
            logger.debug('Setting scheduler of {0} to self ({1})'.format(run_termination_cond, self))
            run_termination_cond.scheduler = self

        if trial_termination_cond.scheduler is None:
            logger.debug('Setting scheduler of {0} to self ({1})'.format(trial_termination_cond, self))
            trial_termination_cond.scheduler = self

        self.counts[TimeScale.RUN] = {vert.mechanism: 0 for vert in self.composition.graph.vertices}
        self.counts[TimeScale.RUN][self] = 0
        execution_queue = []

        logger.debug('runterm: {0}'.format(run_termination_cond))

        while not run_termination_cond.is_satisfied():
            self.counts[TimeScale.TRIAL] = {vert.mechanism: 0 for vert in self.composition.graph.vertices}
            self.counts[TimeScale.TRIAL][self] = 0
            # counts_useable is a dictionary intended to store the number of available "instances" of a certain mechanism that
            # are available to expend in order to satisfy conditions such as "run B every two times A runs"
            # specifically, counts_useable[a][b] = n indicates that there are n uses of a that are available for b to expend
            # so, in the previous example B would check to see if counts_useable[A][B] is 2, in which case B can run
            counts_useable = {vert.mechanism: {vert.mechanism: 0 for vert in self.composition.graph.vertices} for vert in self.composition.graph.vertices}

            # this queue is used to determine which components to run next, and roughly uses a BFS
            # add source nodes into the consideration queue to start
            consideration_queue = [vert for vert in self.composition.graph.vertices if len(self.composition.graph.get_incoming(vert.mechanism)) == 0]
            next_consideration_queue = []

            logger.debug('run')

            while not trial_termination_cond.is_satisfied():
                logger.debug('trial')
                for current_vert in consideration_queue:
                    if self.condition_set.conditions[current_vert.mechanism].is_satisfied():
                        execution_queue.append(current_vert.mechanism)
                        self.counts[TimeScale.RUN][current_vert.mechanism] += 1
                        self.counts[TimeScale.TRIAL][current_vert.mechanism] += 1

                        # current_vert's mechanism is added to the execution queue, so we now need to
                        # reset all of the counts useable by current_vert's mechanism to 0
                        for m in counts_useable:
                            counts_useable[m][current_vert.mechanism] = 0
                        # and increment all of the counts of current_vert's mechanism useable by other
                        # mechanisms by 1
                        for m in counts_useable:
                            counts_useable[current_vert.mechanism][m] += 1
                    # priorities could be used here, or alternatively using sets and checking for
                    # parallelization
                    for child in self.composition.graph.get_outgoing(current_vert.mechanism):
                        next_consideration_queue.append(child)

                self.counts[TimeScale.TRIAL][self] += 1

            # can execute the execution_queue here
            logger.debug(' '.join([str(x) for x in execution_queue]))

            consideration_queue = next_consideration_queue
            self.counts[TimeScale.RUN][self] += 1

        return execution_queue

def main():
    comp = Composition()
    A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
    B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
    for m in [A, B]:
        comp.add_mechanism(m)
    sched = Scheduler(comp)

    sched.condition_set.add_condition(A, Any(AtStep(1), AfterNCalls(B, 3)))
    sched.condition_set.add_condition(B, AfterNCalls(A, 1))
    logger.debug('condition set sched: {0}'.format(sched.condition_set.scheduler))

    logger.debug('Pre run')
    sched.run(run_termination_cond=AfterNCalls(A, 3, time_scale=TimeScale.RUN), trial_termination_cond=AfterNCalls(B, 2, time_scale=TimeScale.TRIAL))
    logger.debug('Post run')

if __name__ == '__main__':
    main()

