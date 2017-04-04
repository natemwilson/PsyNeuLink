import logging
import pprint

from PsyNeuLink.Components.Mechanisms.ProcessingMechanisms.TransferMechanism import TransferMechanism
from PsyNeuLink.Components.Projections.MappingProjection import MappingProjection
from PsyNeuLink.Components.Functions.Function import Linear
from PsyNeuLink.composition import Composition
from PsyNeuLink.scheduling.Scheduler import Scheduler
from PsyNeuLink.scheduling.condition import *

logger = logging.getLogger(__name__)

def run_trial(scheduler, condition_termination):
    output = []
    for time_step in scheduler.run_trial(condition_termination):
        output.append(time_step)
        for mech in time_step:
            # simulate running the mechanism
            mech.execute()
    return output

class TestScheduler:
    def test_Any_end_before_one_finished(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        for m in [A]:
            comp.add_mechanism(m)
        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, EveryNSteps(1))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = Any(AfterNCalls(A, 10), AtStep(5))
        output = sched.run(termination_conds=termination_conds)

        expected_output = [A for _ in range(5)]
        assert output == expected_output

    def test_All_end_after_one_finished(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        for m in [A]:
            comp.add_mechanism(m)
        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, EveryNSteps(1))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = Any(AfterNCalls(A, 5), AtStep(10))
        output = sched.run(termination_conds=termination_conds)

        expected_output = [A for _ in range(5)]
        assert output == expected_output

    def test_AtStep(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        comp.add_mechanism(A)

        sched = Scheduler(comp)
        sched.condition_set.add_condition(A, AtStep(0))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AtStep(5)
        output = sched.run(termination_conds=termination_conds)
       # output = run_trial(sched, AfterStep(sched, 5))

        expected_output = [A, set(), set(), set(), set()]
        assert output == expected_output

    def test_AtStep_underconstrained(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        C = TransferMechanism(function = Linear(intercept = 1.5), name = 'C')
        for m in [A,B,C]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), B)
        comp.add_projection(B, MappingProjection(), C)

        sched = Scheduler(comp)
        sched.condition_set.add_condition(A, AtStep(0))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AtStep(5)
        output = sched.run(termination_conds=termination_conds)
       # output = run_trial(sched, AfterStep(sched, 5))

        expected_output = [A, set(), set(), set(), set()]
        assert output == expected_output

    def test_AtStep_in_middle(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        comp.add_mechanism(A)

        sched = Scheduler(comp)
        sched.condition_set.add_condition(A, AtStep(2))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AtStep(5)
        output = sched.run(termination_conds=termination_conds)
       # output = run_trial(sched, AfterStep(sched, 5))

        expected_output = [set(), set(), A, set(), set()]
        assert output == expected_output

    def test_AtStep_at_end(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        comp.add_mechanism(A)

        sched = Scheduler(comp)
        sched.condition_set.add_condition(A, AtStep(5))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AtStep(5)
        output = sched.run(termination_conds=termination_conds)
       # output = run_trial(sched, AfterStep(sched, 5))

        expected_output = [set(), set(), set(), set(), set()]
        assert output == expected_output

    def test_AtStep_after_end(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        comp.add_mechanism(A)

        sched = Scheduler(comp)
        sched.condition_set.add_condition(A, AtStep(6))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AtStep(5)
        output = sched.run(termination_conds=termination_conds)
       # output = run_trial(sched, AfterStep(sched, 5))

        expected_output = [set(), set(), set(), set(), set()]
        assert output == expected_output

    def test_AfterStep(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        comp.add_mechanism(A)

        sched = Scheduler(comp)
        sched.condition_set.add_condition(A, AfterStep(0))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AtStep(5)
        output = sched.run(termination_conds=termination_conds)

        expected_output = [set(), A, A, A, A]
        assert output == expected_output

    def test_composite_condition_multi(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        C = TransferMechanism(function = Linear(intercept = 1.5), name = 'C')
        for m in [A,B,C]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), B)
        comp.add_projection(B, MappingProjection(), C)
        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, EveryNSteps(1))
        sched.condition_set.add_condition(B, EveryNCalls(A, 2))
        sched.condition_set.add_condition(C, All(
                Any(
                    AfterStep(7),
                    AfterNCalls(B, 2)
                ),
                Any(
                    AfterStep(3),
                    AfterNCalls(B, 3)
                )
            )
        )

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AfterStep(11)
        output = sched.run(termination_conds=termination_conds)
        # B>A>C: A A B A A B A A C B A C A C B A C A C
        #expected_output = [[A], [A], [A,B], [A], [A,B], [A,C], [A,B,C], [A,C], [A,B,C], [A,C]]
        expected_output = [
            A, A, B, A, A, B, C, A, C, A, B, C
        ]
        assert output == expected_output

    # tests below are copied from old scheduler, need renaming
    def test_1(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        C = TransferMechanism(function = Linear(intercept = 1.5), name = 'C')
        for m in [A,B,C]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), B)
        comp.add_projection(B, MappingProjection(), C)

        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, EveryNSteps(1))
        sched.condition_set.add_condition(B, EveryNCalls(A, 2))
        sched.condition_set.add_condition(C, EveryNCalls(B, 3))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AfterNCalls(C, 4, time_scale=TimeScale.TRIAL)
        output = sched.run(termination_conds=termination_conds)

        expected_output = [
            A, A, B, A, A, B, A, A, B, C,
            A, A, B, A, A, B, A, A, B, C,
            A, A, B, A, A, B, A, A, B, C,
            A, A, B, A, A, B, A, A, B, C,
        ]
        #pprint.pprint(output)
        assert output == expected_output

    def test_1b(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        C = TransferMechanism(function = Linear(intercept = 1.5), name = 'C')
        for m in [A,B,C]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), B)
        comp.add_projection(B, MappingProjection(), C)

        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, EveryNSteps(1))
        sched.condition_set.add_condition(B, Any(EveryNCalls(A, 2), AfterStep(2)))
        sched.condition_set.add_condition(C, EveryNCalls(B, 3))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AfterNCalls(C, 4, time_scale=TimeScale.TRIAL)
        output = sched.run(termination_conds=termination_conds)

        expected_output = [
            A, A, B, A, B, A, B, C,
               A, B, A, B, A, B, C,
               A, B, A, B, A, B, C,
               A, B, A, B, A, B, C,
        ]
        #pprint.pprint(output)
        assert output == expected_output

    def test_2(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        C = TransferMechanism(function = Linear(intercept = 1.5), name = 'C')
        for m in [A,B,C]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), B)
        comp.add_projection(B, MappingProjection(), C)

        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, EveryNSteps(1))
        sched.condition_set.add_condition(B, EveryNCalls(A, 2))
        sched.condition_set.add_condition(C, EveryNCalls(B, 2))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AfterNCalls(C, 1, time_scale=TimeScale.TRIAL)
        output = sched.run(termination_conds=termination_conds)

        expected_output = [A, A, B, A, A, B, C]
        assert output == expected_output

    def test_3(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        C = TransferMechanism(function = Linear(intercept = 1.5), name = 'C')
        for m in [A,B,C]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), B)
        comp.add_projection(B, MappingProjection(), C)

        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, EveryNSteps(1))
        sched.condition_set.add_condition(B, EveryNCalls(A, 2))
        sched.condition_set.add_condition(C, All(AfterNCalls(B, 2), EveryNCalls(B, 1)))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AfterNCalls(C, 4, time_scale=TimeScale.TRIAL)
        output = sched.run(termination_conds=termination_conds)

        expected_output = [
            A, A,B, A, A,B,C, A, A,B,C, A, A,B,C, A, A,B,C
        ]
        #pprint.pprint(output)
        assert output == expected_output

    def test_6(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        C = TransferMechanism(function = Linear(intercept = 1.5), name = 'C')
        for m in [A,B,C]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), B)
        comp.add_projection(B, MappingProjection(), C)

        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, BeforeStep(5))
        sched.condition_set.add_condition(B, AfterNCalls(A, 5))
        sched.condition_set.add_condition(C, AfterNCalls(B, 1))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AfterNCalls(C, 3)
        output = sched.run(termination_conds=termination_conds)

        expected_output = [
            A, A, A, A, A, B, C, B, C, B, C
        ]
        #pprint.pprint(output)
        assert output == expected_output

    def test_6_two_trials(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        C = TransferMechanism(function = Linear(intercept = 1.5), name = 'C')
        for m in [A,B,C]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), B)
        comp.add_projection(B, MappingProjection(), C)

        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, BeforeStep(5))
        sched.condition_set.add_condition(B, AfterNCalls(A, 5))
        sched.condition_set.add_condition(C, AfterNCalls(B, 1))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(2)
        termination_conds[TimeScale.TRIAL] = AfterNCalls(C, 3)
        output = sched.run(termination_conds=termination_conds)

        expected_output = [
            A, A, A, A, A, B, C, B, C, B, C,
            A, A, A, A, A, B, C, B, C, B, C
        ]
        #pprint.pprint(output)
        assert output == expected_output

    def test_7(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        for m in [A, B]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), B)

        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, EveryNSteps(1))
        sched.condition_set.add_condition(B, EveryNCalls(A, 2))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = Any(AfterNCalls(A, 1), AfterNCalls(B, 1))
        output = sched.run(termination_conds=termination_conds)

        expected_output = [A]
        assert output == expected_output

    def test_8(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        for m in [A, B]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), B)

        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, EveryNSteps(1))
        sched.condition_set.add_condition(B, EveryNCalls(A, 2))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = All(AfterNCalls(A, 1), AfterNCalls(B, 1))
        output = sched.run(termination_conds=termination_conds)

        expected_output = [A, A, B]
        assert output == expected_output

    def test_9(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        A.is_finished = True
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        for m in [A, B]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), B)

        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, EveryNSteps(1))
        sched.condition_set.add_condition(B, WhenFinished(A))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AtStep(5)
        output = sched.run(termination_conds=termination_conds)

        expected_output = [A, B, A, B, A]
        assert output == expected_output


    def test_9b(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        A.is_finished = False
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        for m in [A, B]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), B)

        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, EveryNSteps(1))
        sched.condition_set.add_condition(B, WhenFinished(A))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AtStep(5)
        output = sched.run(termination_conds=termination_conds)

        expected_output = [A, A, A, A, A]
        assert output == expected_output

    def test_10(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        A.is_finished = True
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')

        for m in [A, B]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), B)

        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, EveryNSteps(1))
        sched.condition_set.add_condition(B, Any(WhenFinished(A), AfterNCalls(A, 3)))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AtStep(10)
        output = sched.run(termination_conds=termination_conds)

        expected_output = [A, B, A, B, A, B, A, B, A, B]
        assert output == expected_output

    def test_10b(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        A.is_finished = False
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')

        for m in [A, B]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), B)

        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, EveryNSteps(1))
        sched.condition_set.add_condition(B, Any(WhenFinished(A), AfterNCalls(A, 3)))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AtStep(10)
        output = sched.run(termination_conds=termination_conds)

        expected_output = [A, A, A, B, A, B, A, B, A, B]
        assert output == expected_output

    def test_10c(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        A.is_finished = True
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')

        for m in [A, B]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), B)

        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, EveryNSteps(1))
        sched.condition_set.add_condition(B, All(WhenFinished(A), AfterNCalls(A, 3)))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AtStep(10)
        output = sched.run(termination_conds=termination_conds)

        expected_output = [A, A, A, B, A, B, A, B, A, B]
        assert output == expected_output

    def test_10d(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        A.is_finished = False
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')

        for m in [A, B]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), B)

        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, EveryNSteps(1))
        sched.condition_set.add_condition(B, All(WhenFinished(A), AfterNCalls(A, 3)))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AtStep(10)
        output = sched.run(termination_conds=termination_conds)

        expected_output = [A, A, A, A, A, A, A, A, A, A]
        assert output == expected_output

    ########################################
    # tests with linear compositions
    ########################################
    def test_linear_AAB(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        for m in [A, B]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), B)

        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, EveryNSteps(1))
        sched.condition_set.add_condition(B, EveryNCalls(A, 2))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNCalls(B, 2, time_scale=TimeScale.RUN)
        termination_conds[TimeScale.TRIAL] = AfterNCalls(B, 2, time_scale=TimeScale.TRIAL)
        output = sched.run(termination_conds=termination_conds)

        expected_output = [A, A, B, A, A, B]
        assert output == expected_output

    def test_linear_ABB(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        for m in [A, B]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), B)

        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, Any(AtStep(0), EveryNCalls(B, 2)))
        sched.condition_set.add_condition(B, Any(EveryNCalls(A, 1), EveryNCalls(B, 1)))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AfterNCalls(B, 8, time_scale=TimeScale.TRIAL)
        output = sched.run(termination_conds=termination_conds)

        expected_output = [A, B, B, A, B, B, A, B, B, A, B, B]
        assert output == expected_output

    def test_linear_ABBCC(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        C = TransferMechanism(function = Linear(intercept = 1.5), name = 'C')
        for m in [A,B,C]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), B)
        comp.add_projection(B, MappingProjection(), C)

        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, Any(AtStep(0), EveryNCalls(C, 2)))
        sched.condition_set.add_condition(B, Any(JustRan(A), JustRan(B)))
        sched.condition_set.add_condition(C, Any(EveryNCalls(B, 2), JustRan(C)))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AfterNCalls(C, 4, time_scale=TimeScale.TRIAL)
        output = sched.run(termination_conds=termination_conds)

        expected_output = [A, B, B, C, C, A, B, B, C, C]
        assert output == expected_output

    def test_linear_ABCBC(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        C = TransferMechanism(function = Linear(intercept = 1.5), name = 'C')
        for m in [A,B,C]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), B)
        comp.add_projection(B, MappingProjection(), C)

        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, Any(AtStep(0), EveryNCalls(C, 2)))
        sched.condition_set.add_condition(B, Any(EveryNCalls(A, 1), EveryNCalls(C, 1)))
        sched.condition_set.add_condition(C, EveryNCalls(B, 1))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AfterNCalls(C, 4, time_scale=TimeScale.TRIAL)
        output = sched.run(termination_conds=termination_conds)

        expected_output = [A, B, C, B, C, A, B, C, B, C]
        assert output == expected_output

    ########################################
    # tests with small branching compositions
    ########################################

    #   triangle:         A
    #                    / \
    #                   B   C
    def test_triangle_1(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        C = TransferMechanism(function = Linear(intercept = 1.5), name = 'C')
        for m in [A,B,C]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), B)
        comp.add_projection(A, MappingProjection(), C)

        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, EveryNSteps(1))
        sched.condition_set.add_condition(B, EveryNCalls(A, 1))
        sched.condition_set.add_condition(C, EveryNCalls(A, 1))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AfterNCalls(C, 3, time_scale=TimeScale.TRIAL)
        output = sched.run(termination_conds=termination_conds)

        expected_output = [
            A, set([B,C]),
            A, set([B,C]),
            A, set([B,C]),
        ]
        #pprint.pprint(output)
        assert output == expected_output

    def test_triangle_2(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        C = TransferMechanism(function = Linear(intercept = 1.5), name = 'C')
        for m in [A,B,C]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), B)
        comp.add_projection(A, MappingProjection(), C)

        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, EveryNSteps(1))
        sched.condition_set.add_condition(B, EveryNCalls(A, 1))
        sched.condition_set.add_condition(C, EveryNCalls(A, 2))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AfterNCalls(C, 3, time_scale=TimeScale.TRIAL)
        output = sched.run(termination_conds=termination_conds)

        expected_output = [
            A, B,
            A, set([B,C]),
            A, B,
            A, set([B,C]),
            A, B,
            A, set([B,C]),
        ]
        #pprint.pprint(output)
        assert output == expected_output

    def test_triangle_3(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        C = TransferMechanism(function = Linear(intercept = 1.5), name = 'C')
        for m in [A,B,C]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), B)
        comp.add_projection(A, MappingProjection(), C)

        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, EveryNSteps(1))
        sched.condition_set.add_condition(B, EveryNCalls(A, 2))
        sched.condition_set.add_condition(C, EveryNCalls(A, 3))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AfterNCalls(C, 2, time_scale=TimeScale.TRIAL)
        output = sched.run(termination_conds=termination_conds)

        expected_output = [
            A, A, B, A, C, A, B, A, A, set([B,C])
        ]
        #pprint.pprint(output)
        assert output == expected_output

    # this is test 11 of original constraint_scheduler.py
    def test_triangle_4(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        A.is_finished = True
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        C = TransferMechanism(function = Linear(intercept = 1.5), name = 'C')

        for m in [A, B, C]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), B)
        comp.add_projection(A, MappingProjection(), C)

        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, EveryNSteps(1))
        sched.condition_set.add_condition(B, EveryNCalls(A, 2))
        sched.condition_set.add_condition(C, All(WhenFinished(A), AfterNCalls(B, 3)))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AfterNCalls(C, 1)
        output = sched.run(termination_conds=termination_conds)

        expected_output = [A, A, B, A, A, B, A, A, set([B,C])]
        #pprint.pprint(output)
        assert output == expected_output

    #   inverted triangle:           A   B
    #                                 \ /
    #                                  C

    # this is test 4 of original constraint_scheduler.py
    # this test has an implicit priority set of A<B !
    def test_invtriangle_1(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        C = TransferMechanism(function = Linear(intercept = 1.5), name = 'C')
        for m in [A,B,C]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), C)
        comp.add_projection(B, MappingProjection(), C)

        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, EveryNSteps(1))
        sched.condition_set.add_condition(B, EveryNCalls(A, 2))
        sched.condition_set.add_condition(C, Any(AfterNCalls(A, 3), AfterNCalls(B, 3)))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AfterNCalls(C, 4, time_scale=TimeScale.TRIAL)
        output = sched.run(termination_conds=termination_conds)

        expected_output = [
            A, set([A,B]), A, C, set([A,B]), C, A, C, set([A,B]), C
        ]
        #pprint.pprint(output)
        assert output == expected_output

    # this is test 5 of original constraint_scheduler.py
    # this test has an implicit priority set of A<B !
    def test_invtriangle_2(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        C = TransferMechanism(function = Linear(intercept = 1.5), name = 'C')
        for m in [A,B,C]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), C)
        comp.add_projection(B, MappingProjection(), C)

        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, EveryNSteps(1))
        sched.condition_set.add_condition(B, EveryNCalls(A, 2))
        sched.condition_set.add_condition(C, All(AfterNCalls(A, 3), AfterNCalls(B, 3)))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AfterNCalls(C, 2, time_scale=TimeScale.TRIAL)
        output = sched.run(termination_conds=termination_conds)

        expected_output = [
            A, set([A,B]), A, set([A,B]), A, set([A,B]), C, A, C
        ]
        assert output == expected_output


    #   checkmark:                   A
    #                                 \
    #                                  B   C
    #                                   \ /
    #                                    D
    # testing toposort
    def test_checkmark_1(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        C = TransferMechanism(function = Linear(intercept = 1.5), name = 'C')
        D = TransferMechanism(function = Linear(intercept = .5), name = 'D')
        for m in [A,B,C,D]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), B)
        comp.add_projection(B, MappingProjection(), D)
        comp.add_projection(C, MappingProjection(), D)

        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, Always())
        sched.condition_set.add_condition(B, Always())
        sched.condition_set.add_condition(C, Always())
        sched.condition_set.add_condition(D, Always())

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AfterNCalls(D, 1, time_scale=TimeScale.TRIAL)
        output = sched.run(termination_conds=termination_conds)

        expected_output = [
            set([A, C]), B, D
        ]
        assert output == expected_output

    def test_checkmark_2(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        C = TransferMechanism(function = Linear(intercept = 1.5), name = 'C')
        D = TransferMechanism(function = Linear(intercept = .5), name = 'D')
        for m in [A,B,C,D]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), B)
        comp.add_projection(B, MappingProjection(), D)
        comp.add_projection(C, MappingProjection(), D)

        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, EveryNSteps(1))
        sched.condition_set.add_condition(B, EveryNCalls(A, 2))
        sched.condition_set.add_condition(C, EveryNSteps(2))
        sched.condition_set.add_condition(D, All(EveryNCalls(B, 2), EveryNCalls(C, 2)))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AfterNCalls(D, 1, time_scale=TimeScale.TRIAL)
        output = sched.run(termination_conds=termination_conds)

        expected_output = [
            A, set([A, C]), B, A, set([A, C]), B, D
        ]
        assert output == expected_output