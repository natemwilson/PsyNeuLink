import logging

from PsyNeuLink.Components.Mechanisms.ProcessingMechanisms.TransferMechanism import TransferMechanism
from PsyNeuLink.Components.Functions.Function import Linear
from PsyNeuLink.composition import Composition
from PsyNeuLink.scheduling.Scheduler import Scheduler
from PsyNeuLink.scheduling.Constraint import Constraint
from PsyNeuLink.scheduling.condition import BeginImmediately, RepeatAlways, EndAfterNCalls, EndWhenAllTerminated, CompositeConditionAny, CompositeConditionAll

logger = logging.getLogger(__name__)

# used to determine whether expected test output is identical to received output
def schedule_outputs_are_equivalent(a, b):
    if len(a) != len(b):
        return False
    for time_step in range(len(a)):
        if a[time_step] != b[time_step]:
            return False
    return True

class TestScheduler:
    def init(self):
        self.comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        C = TransferMechanism(function = Linear(intercept = 1.5), name = 'C')

        comp.add_mechanism(A)
        comp.add_mechanism(B)
        comp.add_mechanism(C)
        comp.add_projection(A, MappingProjection(), B)
        comp.add_projection(B, MappingProjection(), C)
        comp.analyze_graph()

    def test_compositeAny_end_before_one_finished(self):
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        c = Constraint(A, 
            condition_activation=BeginImmediately(),
            condition_repeat=RepeatAlways(),
            condition_termination=EndAfterNCalls(A, 10)
        )
        sched = Scheduler({A: 1}, set([c]))
        output = []
        for time_step in sched.run_trial(CompositeConditionAny(EndWhenAllTerminated(sched), EndAfterNCalls(sched, 5))):
            output.append(time_step)
            for mech in time_step:
                # simulate running the mechanism
                mech.execute()

        expected_output = [set([A]) for _ in range(5)]
        assert(schedule_outputs_are_equivalent(output, expected_output))

    def test_compositeAll_end_after_one_finished(self):
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        c = Constraint(A,
            condition_activation=BeginImmediately(),
            condition_repeat=RepeatAlways(),
            condition_termination=EndAfterNCalls(A, 5)
        )
        sched = Scheduler({A: 1}, set([c]))
        output = []
        for time_step in sched.run_trial(CompositeConditionAll(EndWhenAllTerminated(sched), EndAfterNCalls(sched, 10))):
            output.append(time_step)
            for mech in time_step:
                # simulate running the mechanism
                mech.execute()

        expected_output = [set([A]) for _ in range(5)]
        expected_output.extend([set() for _ in range(5)])
        assert(schedule_outputs_are_equivalent(output, expected_output))
