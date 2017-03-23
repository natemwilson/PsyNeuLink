import logging
logger = logging.getLogger(__name__)

class Scheduler(object):
    def __init__(self, components={}, constraints=set()):
        '''
        :param self:
        :param components: (dict) - a dictionary mapping each component to its priority
        :param constraints: (set) - a dictionary mapping each component to the set of :keyword:`Constraint`s of which it is owner
        '''
        self.components = components
        self.constraints = constraints
        #self.constraints_dict = {x: set() for x in components}
        self.constraints_inactive = constraints
        self.constraints_active = set()
        self.constraints_terminated = set()

        self.current_time_step = 0

        #for c in constraints:
        #    self.constraints_dict[c.owner].add(c)

    def run_time_step(self):
        #######
        # Resets all mechanisms in the Scheduler for this time_step
        # Initializes a firing queue, then continuously executes mechanisms and updates queue according to any
        # constraints that were satisfied by the previous execution
        #######

        self.current_time_step += 1
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
                    firing_queue.add(comp)

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


def main():
    from PsyNeuLink.Components.Mechanisms.ProcessingMechanisms.TransferMechanism import TransferMechanism
    from PsyNeuLink.Components.Functions.Function import Linear
    from PsyNeuLink.composition import Composition
    comp = Composition()
    A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
    B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
    C = TransferMechanism(function = Linear(intercept = 1.5), name = 'C')
    Clock = TransferMechanism(function = Linear(), name = 'Clock')
    T = TransferMechanism(function = Linear(), name = 'Terminal')

    comp.add_mechanism(A)
    comp.add_mechanism(B)
    comp.add_mechanism(C)
    comp.add_mechanism(T)
    comp.add_projection(A, MappingProjection(), B)
    comp.add_projection(B, MappingProjection(), C)
    comp.add_projection(C, MappingProjection(), T)
    comp.analyze_graph()

    sched = Scheduler()

    sched.set_clock(Clock)
    sched.add_vars([(A, 1), (B, 2), (C, 3), (T, 0)])

    test_constraints_dict = {
        # every_n
         "Test 1": [[(A, (Clock,), every_n_calls(1))],
           [(B, (A,), every_n_calls(2))],
           [(C, (B,), every_n_calls(3))],
           [(T, (C,), every_n_calls(4))],
           [(sched, (T,), terminal())]],

        # Test 1 Expected Output: A AB A AB A ABC A AB A AB A ABC A AB A AB A ABC A AB A AB A ABCT

        "Test 1b": [[(A, (Clock,), every_n_calls(1))],
                   [(B, (A,), every_n_calls(2)),(B, (Clock,), after_n_calls(2))],
                   [(C, (B,), every_n_calls(3))],
                   [(T, (C,), every_n_calls(4))],
                   [(sched, (T,), terminal())]],

        # Test 1b Expected Output: A AB AB ABC AB AB ABC AB AB ABC AB AB ABCT

        "Test 1c": [[(A, (Clock,), every_n_calls(1))],
                   [(B, (A,), every_n_calls(2)),(B, (Clock,), after_n_calls(5))],
                   [(C, (B,), every_n_calls(3))],
                   [(T, (C,), every_n_calls(4))],
                   [(sched, (T,), terminal())]],

        # Test 1c Expected Output: A AB AB ABC AB AB ABC AB AB ABC AB AB ABCT

        # after_n where C begins after 2 runs of B; C is terminal
         "Test 2": [[(A, (Clock,), every_n_calls(1))],
                    [(B, (A,), every_n_calls(2))],
                    [(C, (B,), after_n_calls(2))],
                    [(sched, (C,), terminal())]],

        #Test 2 Expected Output: A AB A ABC

        # after_n where C begins after 2 runs of B; runs for 10 time steps
        "Test 3": [[(A, (Clock,), every_n_calls(1))],
                   [(B, (A,), every_n_calls(2))],
                   [(C, (B,), after_n_calls(2))],
                   [(sched, (Clock,), num_time_steps(10))]],

        # Test 3 Expected Output: A AB A ABC A ABC A ABC A ABC
        # Note -- after_n means that C will run *each* time B runs after B has run n times

        # after_n where C begins after 3 runs of B OR A; runs for 10 time steps
        "Test 4": [[(A, (Clock,), every_n_calls(1))],
                   [(B, (A,), every_n_calls(2))],
                   [(C, (B, A), after_n_calls(3, op="OR"))],
                   [(sched, (Clock,), num_time_steps(10))]],

        # Test 4 Expected Output: A AB AC ABC AC ABC AC ABC AC ABC

        "Test 4b": [[(A, (Clock,), every_n_calls(1))],
                   [(B, (A,), every_n_calls(2))],
                   [(C, (B,), after_n_calls(3)), (C, (A,), after_n_calls(3))],
                   [(sched, (Clock,), num_time_steps(10))]],

        # Test 4b Expected Output: A AB AC ABC AC ABC AC ABC AC ABC

        # after_n where C begins after 2 runs of B AND A; runs for 10 time steps
        "Test 5": [[(A, (Clock,), every_n_calls(1))],
                    [(B, (A,), every_n_calls(2))],
                    [(C, (B,A), after_n_calls(3))],
                    [(sched, (Clock,), num_time_steps(10))]],

        # Test 5 Expected Output: A AB A AB A ABC AC ABC AC ABC


        # first n where A depends on the clock
        "Test 6": [[(A, (Clock,), first_n_calls(5))],
                   [(B, (A,), after_n_calls(5))],
                   [(C, (B,), after_n_calls(1))],
                   [(sched, (Clock,), num_time_steps(10))]],

        # Test 6 Expected Output: A A A A ABC -- -- -- -- --

        # terminal where trial ends when A OR B runs
        "Test 7": [[(A, (Clock,), every_n_calls(1))],
                   [(B, (A,), every_n_calls(2))],
                   [(sched, (A,B), terminal(op="OR"))]],

        # Test 7 Expected Output: A

        # terminal where trial ends when A AND B have run
        "Test 8": [[(A, (Clock,), every_n_calls(1))],
                   [(B, (A,), every_n_calls(2))],
                   [(sched, (A, B), terminal())]],

        # Test 8 Expected Output: A AB

        # if_finished where B runs when A is done
        "Test 9": [[(A, (Clock,), every_n_calls(1))],
                   [(B, (A,), if_finished())],
                   [(sched, (Clock,), num_time_steps(5))]],

        # Test 9 Expected Output: AB AB AB AB AB

        # if_finished where B runs when A is done or A has run n times
        "Test 10": [[(A, (Clock,), every_n_calls(1))],
                   [(B, (A,), if_finished()), (B, (A,), after_n_calls(3))],
                   [(sched, (Clock,), num_time_steps(5))]],

        # Test 10 Expected Output: AB AB AB AB AB

        # if_finished where C runs when A is and B has run n times
        "Test 11": [[(A, (Clock,), every_n_calls(1))],
                    [(B, (A,), every_n_calls(2))],
                    [(C, (A,), if_finished())],
                    [(C, (B,), after_n_calls(3))],
                    [(sched, (C), terminal())]],

        # Test 11 Expected Output: A AB A AB A ABC
    }

    # Set mechanism A to finished for testing
    A.is_finished = True

    print('=================================')

    for test in sorted(test_constraints_dict.keys()):
        sched = Scheduler()
        sched.set_clock(Clock)
        sched.add_vars([(A, 1), (B, 2), (C, 3), (T, 0)])
        # for now it is unnecessary to change terminal conditions in test cases
        # in between runs because the only requirement for the condition to
        # function properly is that sched (or its previous dicarded instance
        # is a Scheduler()
        print('--- RUNNING {0} ---'.format(test))
        sched.add_constraints(test_constraints_dict[test])

        for var in sched.var_list:
            var.component.new_trial()

        comp.run(sched)

        print('=================================')

if __name__ == '__main__':
    main()

