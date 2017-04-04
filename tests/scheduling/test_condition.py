import logging
import pprint

from PsyNeuLink.Components.Mechanisms.ProcessingMechanisms.TransferMechanism import TransferMechanism
from PsyNeuLink.Components.Projections.MappingProjection import MappingProjection
from PsyNeuLink.Components.Functions.Function import Linear
from PsyNeuLink.composition import Composition
from PsyNeuLink.scheduling.Scheduler import Scheduler
from PsyNeuLink.scheduling.condition import *

logger = logging.getLogger(__name__)

class TestCondition:
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

    def test_WhenFinishedAll_1(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        A.is_finished = True
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        B.is_finished = True
        C = TransferMechanism(function = Linear(intercept = 1.5), name = 'C')
        for m in [A,B,C]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), C)
        comp.add_projection(B, MappingProjection(), C)
        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, EveryNSteps(1))
        sched.condition_set.add_condition(B, EveryNSteps(1))
        sched.condition_set.add_condition(C, WhenFinishedAll(A, B))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AfterNCalls(C, 1)
        output = sched.run(termination_conds=termination_conds)
        expected_output = [
            set([A, B]), C
        ]
        assert output == expected_output

    def test_WhenFinishedAll_2(self):
        comp = Composition()
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        A.is_finished = False
        B = TransferMechanism(function = Linear(intercept = 4.0), name = 'B')
        B.is_finished = True
        C = TransferMechanism(function = Linear(intercept = 1.5), name = 'C')
        for m in [A,B,C]:
            comp.add_mechanism(m)
        comp.add_projection(A, MappingProjection(), C)
        comp.add_projection(B, MappingProjection(), C)
        sched = Scheduler(comp)

        sched.condition_set.add_condition(A, EveryNSteps(1))
        sched.condition_set.add_condition(B, EveryNSteps(1))
        sched.condition_set.add_condition(C, WhenFinishedAll(A, B))

        termination_conds = {ts: None for ts in TimeScale}
        termination_conds[TimeScale.RUN] = AfterNTrials(1)
        termination_conds[TimeScale.TRIAL] = AfterNCalls(A, 5)
        output = sched.run(termination_conds=termination_conds)
        expected_output = [
            set([A, B]), set([A, B]), set([A, B]), set([A, B]), set([A, B]),
        ]
        assert output == expected_output
