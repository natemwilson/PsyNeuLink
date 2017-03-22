class Constraint(object):
    ########
    # Helper class for scheduling
    # Contains an owner (the Component which owns this constraint), dependencies (list of all Components
    # the owner depends on with respect to *this* constraint), and the condition (of this constraint)
    # Contains a method 'is_satisfied' which checks dependencies against the condition and returns a boolean
    ########
    def __init__(self, owner, condition_activation=ConditionBeginImmediately(), condition_repeat, condition_termination, time_scales = None):
        self.owner = owner # Component that falls under this constraint
        if isinstance(dependencies, Component):
            self.dependencies = (dependencies,)
        else:
            self.dependencies = dependencies # Tuple of Components on which this constraint depends

        self.condition_activation = condition_activation
        self.condition_repeat = condition_repeat
        self.condition_termination = condition_termination
        