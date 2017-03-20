class Trial(object):
    def __init__(self, composition=None, constraints={}, terminal_condition=None):
        '''
        :param self:
        :param composition: (:keyword:`Composition`) - the :keyword:`Composition` on which the trial is run
        :param constraints: (set) - a dictionary mapping each component to the set of :keyword:`Constraint`s of which it is owner.
        Alternatively, the set of :keyword:`Constraint`s
        '''
        self.composition = composition

        if isinstance(constraints, set):
            self.constraints = {x: set() for x in components}
            for c in constraints:
                self.constraints[c.owner].add(c)
