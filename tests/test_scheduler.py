import logging

from PsyNeuLink.Components.Mechanisms.ProcessingMechanisms.TransferMechanism import TransferMechanism
from PsyNeuLink.Components.Functions.Function import Linear
from PsyNeuLink.composition import Composition
from PsyNeuLink.scheduling.Scheduler import Scheduler
from PsyNeuLink.scheduling.Constraint import Constraint
from PsyNeuLink.scheduling.condition import BeginImmediately, RepeatAlways, EndAfterNCalls, EndWhenAllTerminated, CompositeConditionAny

logger = logging.getLogger(__name__)

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

    def test_A_every_step(self):
        A = TransferMechanism(function = Linear(slope=5.0, intercept = 2.0), name = 'A')
        c = Constraint(A, 
            condition_activation=BeginImmediately(),
            condition_repeat=RepeatAlways(),
            condition_termination=EndAfterNCalls(A, 10)
        )
        sched = Scheduler({A: 1}, set([c]))
        output = []
        for time_step in sched.run_trial(CompositeConditionAny(EndWhenAllTerminated(sched), EndAfterNCalls(sched, 20))):
            output.append(time_step)
            for mech in time_step:
                # simulate running the mechanism
                mech.execute()
                #logger.debug('{0}, {1}, {2}'.format(e, e is A, e == A))
