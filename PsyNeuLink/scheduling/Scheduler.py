class Scheduler(object):
    def __init__(self, components={}, constraints={}):
        '''
        :param self:
        :param components: (dict) - a dictionary mapping each component to its priority
        :param constraints: (set) - a dictionary mapping each component to the set of :keyword:`Constraint`s of which it is owner
        '''
        self.components = components
        self.constraints = constraints

    def run_time_step(self):
        #######
        # Resets all mechanisms in the Scheduler for this time_step
        # Initializes a firing queue, then continuously executes mechanisms and updates queue according to any
        # constraints that were satisfied by the previous execution
        #######
        def update_dependent_vars(variable):
            #######
            # Takes in the ScheduleVariable of the mechanism that *just* ran
            # Loops through all of the constraints that depend on this mechanism
            # Returns a list ('change_list') of all of the ScheduleVariables (mechanisms) that own a constraint which
            # was satisfied by this mechanism's run
            #######

            change_list = []

            for con_set in variable.dependent_constraint_sets:
                for con in con_set:
                    if isinstance(con.owner, Scheduler):        # special case where the constraint is on the Scheduler
                        if con.is_satisfied():                  # If the constraint is satisfied, end trial
                            self.trial_terminated = True

                    elif con_set not in con.owner.filled_constraint_sets: # typical case where the constraint is on a ScheduleVariable
                        if con.owner.evaluate_constraint_set(con_set) and con.owner not in change_list:  # If the constraint set is satisfied, pass owner to change list
                            change_list.append(con.owner)
                    change_list.sort(key=lambda x:x.priority)   # sort change list according to priority

            return change_list

        def update_firing_queue(firing_queue, change_list):
            ######
            # Takes in the current firing queue & list of schedule variables that own a recently satisfied constraint
            # Any ScheduleVariable with no remaining constraints is added to the firing queue
            ######

            for var in change_list:
                if len(var.filled_constraint_sets) == len(var.own_constraint_sets):
                    firing_queue.append(var)
            return firing_queue

        # reset all mechanisms for this time step
        for var in self.var_list:
            var.new_time_step()
        # initialize firing queue by adding clock
        firing_queue = [self.clock]
        for var in firing_queue:

            yield var

            if (var is not self.clock):
                print(var.component.name, end='')

            change_list = update_dependent_vars(var)
            firing_queue = update_firing_queue(firing_queue, change_list)
        print('', end=' ')


    def run_trial(self):
        ######
        # Resets all mechanisms, then calls self.run_time_step() until the terminal mechanism runs
        ######

        for var in self.var_list:
            var.new_trial()
        self.trial_terminated = False
        while (not self.trial_terminated):
            for var in self.run_time_step():
                yield var.component
            print()



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

