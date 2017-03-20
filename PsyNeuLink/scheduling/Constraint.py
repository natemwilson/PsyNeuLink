class Constraint(object):
    ########
    # Helper class for scheduling
    # Contains an owner (the Component which owns this constraint), dependencies (list of all Components
    # the owner depends on with respect to *this* constraint), and the condition (of this constraint)
    # Contains a method 'is_satisfied' which checks dependencies against the condition and returns a boolean
    ########
    def __init__(self, owner, dependencies, condition, time_scales = None):
        self.owner = owner # Component that falls under this constraint
        if isinstance(dependencies, Component):
            self.dependencies = (dependencies,)
        else:
            self.dependencies = dependencies # Tuple of Components on which this constraint depends

        self.condition = condition # Condition to be evaluated

    def is_satisfied(self):
        return self.condition(self.dependencies) #Checks dependencies against condition; returns True if ALL satisfied
