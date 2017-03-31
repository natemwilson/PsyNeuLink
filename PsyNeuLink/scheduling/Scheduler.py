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

        self.counts = {ts: 0 for ts in TimeScale}

    def add_constraints(self, constraints):
        self.constraints_inactive.update(set(constraints))

    def run_time_step(self):
        #######
        # Resets all mechanisms in the Scheduler for this time_step
        # Initializes a firing queue, then continuously executes mechanisms and updates queue according to any
        # constraints that were satisfied by the previous execution
        #######

        logger.debug('Current time step: {0}'.format(self.current_time_step))
        # reset all mechanisms for this time step
        for comp in self.components:
            comp.new_time_step()

        firing_queue = set()
        for cons in list(self.constraints_inactive):
            if cons.condition_activation.is_satisfied():
                logger.debug('Activating {0}'.format(cons))
                self.constraints_active.add(cons)
                self.constraints_inactive.remove(cons)
        for cons in list(self.constraints_active):
            if cons.condition_termination.is_satisfied():
                logger.debug('Terminating {0}'.format(cons))
                self.constraints_terminated.add(cons)
                self.constraints_active.remove(cons)
            else:
                if cons.condition_repeat.is_satisfied():
                    firing_queue.add(cons.owner)

        self.current_time_step += 1
        #return self.prioritize_queue(firing_queue)
        return firing_queue

    def run_trial(self, condition_termination):
        ######
        # Resets all mechanisms, then calls self.run_time_step() until the terminal mechanism runs
        ######

        for c in self.components:
            c.new_trial()
        while not condition_termination.is_satisfied():
            yield self.run_time_step()

        logger.debug('Exit run_trial')

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

        self.counts[TimeScale.RUN] = {vert.mechanism: 0 for vert in self.composition.graph.vertices}
        self.counts[TimeScale.RUN][self] = 0
        execution_queue = []

        while not run_termination_cond:
            self.counts[TimeScale.TRIAL] = {vert.mechanism: 0 for vert in self.composition.graph.vertices}
            self.counts[TimeScale.TRIAL][self] = 0
            # counts_useable is a dictionary intended to store the number of available "instances" of a certain mechanism that
            # are available to expend in order to satisfy conditions such as "run B every two times A runs"
            # specifically, counts_useable[a][b] = n indicates that there are n uses of a that are available for b to expend
            # so, in the previous example B would check to see if counts_useable[A][B] is 2, in which case B can run
            counts_useable = {vert.mechanism: {vert.mechanism: 0 for vert in self.composition.graph.vertices} for vert in self.composition.graph.vertices}

            # this queue is used to determine which components to run next, and roughly uses a BFS
            # add source nodes into the consideration queue to start
            consideration_queue = [vert for vert in self.composition.graph.vertices if len(self.graph.get_incoming(vert)) == 0]
            next_consideration_queue = []

            while not trial_termination_cond:
                for current_vert in consideration_queue:
                    if self.condition_set[current_vert.mechanism].is_satisfied():
                        execution_queue.append(current_vert.mechanism)
                        self.counts_run[current_vert.mechanism] += 1
                        self.counts_trial[current_vert.mechanism] += 1

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

            # can execute the execution_queue here
            logger.debug(' '.join(execution_queue))

            consideration_queue = next_consideration_queue

        return execution_queue

def main():
    comp = Composition()
    A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
    comp.add_mechanism(A)
    sched = Scheduler(comp)

    sched.condition_set.add_condition(A, Always())

    sched.run(run_termination_cond=AfterNCalls(A, 10), trial_termination_cond=AfterNCalls(A, 5))


if __name__ == '__main__':
    main()

