import logging

from PsyNeuLink.Globals.TimeScale import TimeScale

#only for testing purposes in main
from PsyNeuLink.scheduling.condition import *
from PsyNeuLink.composition import Composition
from PsyNeuLink.Components.Mechanisms.ProcessingMechanisms.TransferMechanism import TransferMechanism
from PsyNeuLink.Components.Projections.MappingProjection import MappingProjection
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

        self.counts_useable = {vert.mechanism: {vert.mechanism: 0 for vert in self.composition.graph.vertices} for vert in self.composition.graph.vertices}

    def _reset(self, time_scale):
        for count in self.counts[time_scale]:
            self.counts[time_scale][count] = 0

    def run(self, termination_conds):
        '''
        :param self:
        :param termination_conds: (dict) - a mapping from :keyword:`TimeScale`s to :keyword:`Condition`s that when met terminate the execution of the specified :keyword:`TimeScale`
        '''
        for tc in termination_conds:
            if termination_conds[tc] is None:
                if tc in [TimeScale.RUN, TimeScale.TRIAL]:
                    raise SchedulerError('Must specify a {0} termination Condition (termination_conds[{0}]'.format(tc))
            else:
                if termination_conds[tc].scheduler is None:
                    logger.debug('Setting scheduler of {0} to self ({1})'.format(termination_conds[tc], self))
                    termination_conds[tc].scheduler = self

        self.counts[TimeScale.RUN] = {vert.mechanism: 0 for vert in self.composition.graph.vertices}
        self.counts[TimeScale.RUN][self] = 0
        execution_queue = []

        logger.debug('runterm: {0}'.format(termination_conds[TimeScale.RUN]))
        while not termination_conds[TimeScale.RUN].is_satisfied():
            self.counts[TimeScale.TRIAL] = {vert.mechanism: 0 for vert in self.composition.graph.vertices}
            self.counts[TimeScale.TRIAL][self] = 0
            logger.debug('run, itercount {0}'.format(self.counts[TimeScale.RUN][self]))
            # counts_useable is a dictionary intended to store the number of available "instances" of a certain mechanism that
            # are available to expend in order to satisfy conditions such as "run B every two times A runs"
            # specifically, counts_useable[a][b] = n indicates that there are n uses of a that are available for b to expend
            # so, in the previous example B would check to see if counts_useable[A][B] is 2, in which case B can run
            self.counts_useable = {vert.mechanism: {vert.mechanism: 0 for vert in self.composition.graph.vertices} for vert in self.composition.graph.vertices}

            while not termination_conds[TimeScale.TRIAL].is_satisfied() and not termination_conds[TimeScale.RUN].is_satisfied():
                # this queue is used to determine which components to run next, and roughly uses a BFS
                # add source nodes into the consideration queue to start
                consideration_queue = [vert.mechanism for vert in self.composition.graph.vertices if len(self.composition.graph.get_incoming(vert.mechanism)) == 0]
                next_consideration_queue = []

                while len(consideration_queue) > 0:
                    logger.debug('trial, itercount {0}, consideration_queue {1}'.format(self.counts[TimeScale.TRIAL][self], ' '.join([str(x) for x in consideration_queue])))
                    for current_mech in consideration_queue:
                        for m in self.counts_useable:
                            logger.debug('Counts of {0} useable by'.format(m))
                            for m2 in self.counts_useable[m]:
                                logger.debug('\t{0}: {1}'.format(m2, self.counts_useable[m][m2]))
                        if self.condition_set.conditions[current_mech].is_satisfied():
                            execution_queue.append(current_mech)
                            self.counts[TimeScale.RUN][current_mech] += 1
                            self.counts[TimeScale.TRIAL][current_mech] += 1

                            # current_mech's mechanism is added to the execution queue, so we now need to
                            # reset all of the counts useable by current_mech's mechanism to 0
                            for m in self.counts_useable:
                                self.counts_useable[m][current_mech] = 0
                        # and increment all of the counts of current_mech's mechanism useable by other
                        # mechanisms by 1
                        for m in self.counts_useable:
                            self.counts_useable[current_mech][m] += 1
                        # priorities could be used here, or alternatively using sets and checking for
                        # parallelization
                        logger.debug('adding children of {0}: {1} to consideration'.format(current_mech, [str(c) for c in self.composition.graph.get_children(current_mech)]))
                        for child in self.composition.graph.get_children(current_mech):
                            next_consideration_queue.append(child)

                    consideration_queue = next_consideration_queue
                    next_consideration_queue = []
                    logger.debug(consideration_queue)
                    self.counts[TimeScale.TRIAL][self] += 1
                    self.counts[TimeScale.RUN][self] += 1

                # can execute the execution_queue here
                logger.info(' '.join([str(x) for x in execution_queue]))

        return execution_queue

def main():
    comp = Composition()
    A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
    B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
    for m in [A, B]:
        comp.add_mechanism(m)
    comp.add_projection(A, MappingProjection(), B)

    sched = Scheduler(comp)

    sched.condition_set.add_condition(A, Any(AtStep(0), EveryNCalls(B, 1)))
    sched.condition_set.add_condition(B, EveryNCalls(A, 2))
    logger.debug('condition set sched: {0}'.format(sched.condition_set.scheduler))

    logger.debug('Pre run')
    termination_conds = {ts: None for ts in TimeScale}
    termination_conds[TimeScale.RUN] = AfterNCalls(B, 2, time_scale=TimeScale.RUN)
    termination_conds[TimeScale.TRIAL] = AfterNCalls(B, 2, time_scale=TimeScale.TRIAL)
    sched.run(termination_conds=termination_conds)
    logger.debug('Post run')

if __name__ == '__main__':
    main()

