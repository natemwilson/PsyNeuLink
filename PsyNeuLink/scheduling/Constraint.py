from PsyNeuLink import Component
from PsyNeuLink.scheduling.condition import BeginImmediately, RepeatAlways, EndAfterNCalls

class Constraint(object):
    ########
    # Helper class for scheduling
    # Contains an owner (the Component which owns this constraint), dependencies (list of all Components
    # the owner depends on with respect to *this* constraint), and the condition (of this constraint)
    # Contains a method 'is_satisfied' which checks dependencies against the condition and returns a boolean
    ########
    def __init__(
        self, 
        owner,
        dependencies=(),
        condition_activation=BeginImmediately(), 
        condition_repeat=RepeatAlways(),
        condition_termination=None,
        time_scales = None
    ):
        self.owner = owner # Component that falls under this constraint
        if isinstance(dependencies, Component):
            self.dependencies = (dependencies,)
        else:
            self.dependencies = dependencies # Tuple of Components on which this constraint depends

        self.condition_activation = condition_activation
        self.condition_repeat = condition_repeat
        self.condition_termination = condition_termination

    def __repr__(self):
        return '{0}(owner={1}, dependencies={2}, activate={3}, repeat={4}, terminate={5}, at {6})'.format(
            self.__class__.__name__,
            self.owner,
            self.dependencies,
            self.condition_activation.__class__.__name__,
            self.condition_repeat.__class__.__name__,
            self.condition_termination.__class__.__name__,
            hex(id(self))
        )
    __str__ = __repr__
