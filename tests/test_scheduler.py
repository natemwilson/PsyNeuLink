import logging
import pprint

from PsyNeuLink.Components.Mechanisms.ProcessingMechanisms.TransferMechanism import TransferMechanism
from PsyNeuLink.Components.Projections.MappingProjection import MappingProjection
from PsyNeuLink.Components.Functions.Function import Linear
from PsyNeuLink.composition import Composition
from PsyNeuLink.scheduling.Scheduler import Scheduler
from PsyNeuLink.scheduling.Constraint import Constraint
from PsyNeuLink.scheduling.condition import Immediately, Always, AfterNCalls, WhenTerminated, CompositeConditionAny, CompositeConditionAll, Never, EveryNCalls

logger = logging.getLogger(__name__)

# used to determine whether expected test output is identical to received output
def pytest_assertrepr(op, output, expected_output):
    message_fail = ['Time Step output matching:',
        'Actual Output:\n{0}\nExpected Output:\n{1}'.format(
            pprint.pformat(output),
            pprint.pformat(expected_output)
            )
    ]
    if len(output) != len(expected_output):
        return message_fail
    for time_step in range(len(output)):
        if output[time_step] != expected_output[time_step]:
            pprint.pprint(output)
            pprint.pprint(expected_output)
            return message_fail

def run_trial(scheduler, condition_termination):
    output = []
    for time_step in scheduler.run_trial(condition_termination):
        output.append(time_step)
        for mech in time_step:
            # simulate running the mechanism
            mech.execute()
    return output

class TestScheduler:
    def test_AfterNCalls_scheduler(self):
        sched = Scheduler({}, set())
        output = run_trial(sched, AfterNCalls(sched, 5))

        expected_output = [set() for _ in range(5)]
        assert output == expected_output

    def test_CompositeConditionAny_end_before_one_finished(self):
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        c = Constraint(A,
            condition_activation=Immediately(),
            condition_repeat=Always(),
            condition_termination=AfterNCalls(A, 10)
        )
        sched = Scheduler({A: 1}, set([c]))
        output = run_trial(sched, CompositeConditionAny(WhenTerminated(sched), AfterNCalls(sched, 5)))

        expected_output = [set([A]) for _ in range(5)]
        assert output == expected_output

    def test_CompositeConditionAll_end_after_one_finished(self):
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        c = Constraint(A,
            condition_activation=Immediately(),
            condition_repeat=Always(),
            condition_termination=AfterNCalls(A, 5)
        )
        sched = Scheduler({A: 1}, set([c]))
        output = run_trial(sched, CompositeConditionAll(WhenTerminated(sched), AfterNCalls(sched, 10)))

        expected_output = [set([A]) for _ in range(5)]
        expected_output.extend([set() for _ in range(5)])
        assert output == expected_output

    # tests below are copied from old scheduler, need renaming
    def test_1(self):
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        C = TransferMechanism(function = Linear(intercept = 1.5), name = 'C')

        c1 = Constraint(A)     # implicit Immediately, Always, Never
        c2 = Constraint(B, condition_repeat=EveryNCalls(A, 2, owner=B))
        c3 = Constraint(C, condition_repeat=EveryNCalls(B, 3, owner=C))
        sched = Scheduler({A: 1, B: 2, C: 3}, set([c1, c2, c3]))
        output = run_trial(sched, AfterNCalls(C, 4))

        #import pprint
        #pprint.pprint(output)

        # A  A  A,B  A  A,B  A  A,B  A,C
        #       A,B  A  A,B  A  A,B  A,C
        #       A,B  A  A,B  A  A,B  A,C
        #       A,B  A  A,B  A  A,B  A,C
        expected_output = [[A], [A],
            [A,B], [A], [A,B], [A], [A,B], [A,C],
            [A,B], [A], [A,B], [A], [A,B], [A,C],
            [A,B], [A], [A,B], [A], [A,B], [A,C],
            [A,B], [A], [A,B], [A], [A,B], [A,C],
        ]
        expected_output = [set(x) for x in expected_output]
        #pprint.pprint(expected_output)
        assert output == expected_output

    def test_2(self):
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        C = TransferMechanism(function = Linear(intercept = 1.5), name = 'C')

        c1 = Constraint(A)     # implicit Immediately, Always, Never
        c2 = Constraint(B, condition_repeat=EveryNCalls(A, 2, owner=B))
        c3 = Constraint(C, condition_repeat=EveryNCalls(B, 2, owner=C))
        sched = Scheduler({A: 1, B: 2, C: 3}, set([c1, c2, c3]))
        output = run_trial(sched, AfterNCalls(C, 1))

        expected_output = [[A], [A], [A,B], [A], [A,B], [A,C]]
        expected_output = [set(x) for x in expected_output]
        assert output == expected_output

    def test_3(self):
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        C = TransferMechanism(function = Linear(intercept = 1.5), name = 'C')

        c1 = Constraint(A)     # implicit Immediately, Always, Never
        c2 = Constraint(B, condition_repeat=EveryNCalls(A, 2, owner=B))
        c3 = Constraint(C, condition_activation=AfterNCalls(B, 2), condition_repeat=EveryNCalls(B, 1, owner=C))
        sched = Scheduler({A: 1, B: 2, C: 3}, set([c1, c2, c3]))
        output = run_trial(sched, AfterNCalls(sched, 10))

        expected_output = [[A], [A], [A,B], [A], [A,B], [A,C], [A,B], [A,C], [A,B], [A,C]]
        expected_output = [set(x) for x in expected_output]
        assert output == expected_output

    def test_4(self):
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        C = TransferMechanism(function = Linear(intercept = 1.5), name = 'C')

        c1 = Constraint(A)     # implicit Immediately, Always, Never
        c2 = Constraint(B, condition_repeat=EveryNCalls(A, 2, owner=B))
        c3 = Constraint(C, condition_activation=CompositeConditionAny(AfterNCalls(A, 3), AfterNCalls(B, 3)))
        sched = Scheduler({A: 1, B: 2, C: 3}, set([c1, c2, c3]))
        output = run_trial(sched, AfterNCalls(sched, 10))

        expected_output = [[A], [A], [A,B], [A,C], [A,B,C], [A,C], [A,B,C], [A,C], [A,B,C], [A,C]]
        expected_output = [set(x) for x in expected_output]
        assert output == expected_output
