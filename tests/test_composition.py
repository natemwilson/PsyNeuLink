import logging

from timeit import timeit

from PsyNeuLink.composition import Composition
from PsyNeuLink.Components.Mechanisms.Mechanism import mechanism
from PsyNeuLink.Components.Projections.MappingProjection import MappingProjection
from PsyNeuLink.Components.Mechanisms.ProcessingMechanisms.TransferMechanism import TransferMechanism

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# All tests are set to run. If you need to skip certain tests,
# see http://doc.pytest.org/en/latest/skipping.html

# Unit tests for each function of the Composition class #######################
# Unit tests for Composition.Composition()
class TestConstructor:
    def test_no_args(self):
        comp = Composition()
        assert isinstance(comp, Composition)

    def test_two_calls_no_args(self):
        comp = Composition()
        assert isinstance(comp, Composition)

        comp_2 = Composition()
        assert isinstance(comp, Composition)


    def test_timing_no_args(self):
        count = 10000
        t = timeit('comp = Composition()', setup='from PsyNeuLink.composition import Composition', number=count)
        print()
        logger.info('completed {0} creation{2} of Composition() in {1:.8f}s'.format(count, t, 's' if count != 1 else ''))

# Unit tests for Composition.add_mechanism
class TestAddMechanism:
    def test_add_once(self):
        comp = Composition()
        comp.add_mechanism(mechanism())

    def test_add_twice(self):
        comp = Composition()
        comp.add_mechanism(mechanism())
        comp.add_mechanism(mechanism())

    def test_add_same_twice(self):
        comp = Composition()
        mech = mechanism()
        comp.add_mechanism(mech)
        comp.add_mechanism(mech)

    def test_timing_stress(self):
        count=100
        t = timeit('comp.add_mechanism(mechanism())',
            setup='''
from PsyNeuLink.composition import Composition
from PsyNeuLink.Components.Mechanisms.Mechanism import mechanism
comp = Composition()
''',
            number=count
        )
        print()
        logger.info('completed {0} addition{2} of a mechanism to a composition in {1:.8f}s'.format(count, t, 's' if count != 1 else ''))

# Unit tests for Composition.add_projection
class TestAddProjection:
    def test_add_once(self):
        comp = Composition()
        A = mechanism()
        B = mechanism()
        comp.add_mechanism(A)
        comp.add_mechanism(B)
        comp.add_projection(A, MappingProjection(), B)

    def test_add_twice(self):
        comp = Composition()
        A = mechanism()
        B = mechanism()
        comp.add_mechanism(A)
        comp.add_mechanism(B)
        comp.add_projection(A, MappingProjection(), B)
        comp.add_projection(A, MappingProjection(), B)

    def test_add_same_twice(self):
        comp = Composition()
        A = mechanism()
        B = mechanism()
        comp.add_mechanism(A)
        comp.add_mechanism(B)
        proj = MappingProjection()
        comp.add_projection(A, proj, B)
        comp.add_projection(A, proj, B)

    def test_timing_stress(self):
        count = 1000
        t = timeit('comp.add_projection(A, MappingProjection(), B)',
            setup='''
from PsyNeuLink.composition import Composition
from PsyNeuLink.Components.Mechanisms.Mechanism import mechanism
from PsyNeuLink.Components.Projections.MappingProjection import MappingProjection
comp = Composition()
A = mechanism()
B = mechanism()
comp.add_mechanism(A)
comp.add_mechanism(B)
''',
            number=count
        )
        print()
        logger.info('completed {0} addition{2} of a mechanism to a composition in {1:.8f}s'.format(count, t, 's' if count != 1 else ''))

'''
# Unit tests for Composition.analyze_graph
if test_analyze_graph:
    print("\n" + "analyze_graph tests:")

    print("Test 1: Empty Call")
    comp = Composition()
    comp.analyze_graph()
    print("passed")

    print("Test 2: Singleton")
    comp = Composition()
    A = mechanism()
    comp.add_mechanism(A)
    comp.analyze_graph()
    assert A in comp.graph.mechanisms
    assert A in comp.origin_mechanisms
    assert A in comp.terminal_mechanisms
    print("passed")

    print("Test 3: Two independent")
    comp = Composition()
    A = mechanism()
    B = mechanism()
    comp.add_mechanism(A)
    comp.add_mechanism(B)
    comp.analyze_graph()
    assert A in comp.origin_mechanisms
    assert B in comp.origin_mechanisms
    assert A in comp.terminal_mechanisms
    assert B in comp.terminal_mechanisms
    print("passed")

    print("Test 4: Two in a row")
    comp = Composition()
    A = mechanism()
    B = mechanism()
    comp.add_mechanism(A)
    comp.add_mechanism(B)
    comp.add_projection(A, MappingProjection(), B)
    comp.analyze_graph()
    assert A in comp.origin_mechanisms
    assert B not in comp.origin_mechanisms
    assert A not in comp.terminal_mechanisms
    assert B in comp.terminal_mechanisms
    print("passed")

    print("Test 5: Two recursive (A)<->(B)")
    comp = Composition()
    A = mechanism()
    B = mechanism()
    comp.add_mechanism(A)
    comp.add_mechanism(B)
    comp.add_projection(A, MappingProjection(), B)
    comp.add_projection(B, MappingProjection(), A)
    comp.analyze_graph()
    assert A not in comp.origin_mechanisms
    assert B not in comp.origin_mechanisms
    assert A not in comp.terminal_mechanisms
    assert B not in comp.terminal_mechanisms
    assert A in comp.cycle_mechanisms
    assert B in comp.recurrent_init_mechanisms
    print("passed")

    print("Test 6: Two origins pointing to recursive pair (A)->(B)<->(C)<-(D)")
    comp = Composition()
    A = mechanism()
    B = mechanism()
    C = mechanism()
    D = mechanism()
    comp.add_mechanism(A)
    comp.add_mechanism(B)
    comp.add_mechanism(C)
    comp.add_mechanism(D)
    comp.add_projection(A, MappingProjection(), B)
    comp.add_projection(C, MappingProjection(), B)
    comp.add_projection(B, MappingProjection(), C)
    comp.add_projection(D, MappingProjection(), C)
    comp.analyze_graph()
    assert A in comp.origin_mechanisms
    assert D in comp.origin_mechanisms
    assert B in comp.cycle_mechanisms
    assert C in comp.recurrent_init_mechanisms
    print("passed")


if test_validate_feed_dict:
    print("\n" + "validate_feed_dict tests:")

    print("Test 1: Origin & Terminal Mechanisms w/ Mapping Projection")
    comp = Composition()
    A = mechanism()
    B = mechanism()
    comp.add_mechanism(A)
    comp.add_mechanism(B)
    comp.add_projection(A, MappingProjection(), B)
    comp.analyze_graph()
    feed_dict_origin = {A: [ [0] ]}
    feed_dict_terminal = {B: [[0] ]}
    comp.validate_feed_dict(feed_dict_origin, comp.origin_mechanisms, "origin")
    comp.validate_feed_dict(feed_dict_terminal, comp.terminal_mechanisms, "terminal")
    print("passed")

    print("Test 2: Empty Feed Dicts")
    comp = Composition()
    A = mechanism()
    B = mechanism()
    comp.add_mechanism(A)
    comp.add_mechanism(B)
    comp.add_projection(A, MappingProjection(), B)
    comp.analyze_graph()
    feed_dict_origin = {}
    feed_dict_terminal = {}
    comp.validate_feed_dict(feed_dict_origin, comp.origin_mechanisms, "origin")
    comp.validate_feed_dict(feed_dict_terminal, comp.terminal_mechanisms, "terminal")
    print("passed")


    print("Test 3: Origin & Terminal Mechanisms w/ Swapped Feed Dicts")
    comp = Composition()
    A = mechanism()
    B = mechanism()
    comp.add_mechanism(A)
    comp.add_mechanism(B)
    comp.add_projection(A, MappingProjection(), B)
    comp.analyze_graph()
    feed_dict_origin = {B: [ [0] ]}
    feed_dict_terminal = {A: [[0] ]}
    try:
        comp.validate_feed_dict(feed_dict_origin, comp.origin_mechanisms, "origin")
    except ValueError:
        print("passed (1/2)")
    try:
        comp.validate_feed_dict(feed_dict_terminal, comp.terminal_mechanisms, "terminal")
    except ValueError:
        print("passed (2/2)")

    print("Test 4: Multiple Origin Mechanisms")
    comp = Composition()
    A = mechanism()
    B = mechanism()
    C = mechanism()
    comp.add_mechanism(A)
    comp.add_mechanism(B)
    comp.add_mechanism(C)
    comp.add_projection(A, MappingProjection(), C)
    comp.add_projection(B, MappingProjection(), C)
    comp.analyze_graph()
    feed_dict_origin = {A: [ [0] ], B: [ [0] ] }
    feed_dict_terminal = {C: [[0] ]}
    comp.validate_feed_dict(feed_dict_origin, comp.origin_mechanisms, "origin")
    comp.validate_feed_dict(feed_dict_terminal, comp.terminal_mechanisms, "terminal")
    print("passed")

    print("Test 5: Multiple Origin Mechanisms, Only 1 in Feed Dict")
    comp = Composition()
    A = mechanism()
    B = mechanism()
    C = mechanism()
    comp.add_mechanism(A)
    comp.add_mechanism(B)
    comp.add_mechanism(C)
    comp.add_projection(A, MappingProjection(), C)
    comp.add_projection(B, MappingProjection(), C)
    comp.analyze_graph()
    feed_dict_origin = {B: [ [0] ] }
    feed_dict_terminal = {C: [[0] ]}
    comp.validate_feed_dict(feed_dict_origin, comp.origin_mechanisms, "origin")
    comp.validate_feed_dict(feed_dict_terminal, comp.terminal_mechanisms, "terminal")
    print("passed")


    print("Test 6: Input State Length 3")
    comp = Composition()
    A = TransferMechanism(default_input_value=[0,1,2])
    B = mechanism()
    comp.add_mechanism(A)
    comp.add_mechanism(B)
    comp.add_projection(A, MappingProjection(), B)
    comp.analyze_graph()
    feed_dict_origin = {A: [ [0,1,2] ] }
    feed_dict_terminal = {B: [[0] ]}
    comp.validate_feed_dict(feed_dict_origin, comp.origin_mechanisms, "origin")
    comp.validate_feed_dict(feed_dict_terminal, comp.terminal_mechanisms, "terminal")
    print("passed")

    print("Test 7: Input State Length 3; Length 2 in Feed Dict")
    comp = Composition()
    A = TransferMechanism(default_input_value=[0,1,2])
    B = mechanism()
    comp.add_mechanism(A)
    comp.add_mechanism(B)
    comp.add_projection(A, MappingProjection(), B)
    comp.analyze_graph()
    feed_dict_origin = {A: [ [0,1] ] }
    feed_dict_terminal = {B: [[0] ]}
    try:
        comp.validate_feed_dict(feed_dict_origin, comp.origin_mechanisms, "origin")
    except ValueError:
        print("passed")

    print("Test 8: Input State Length 2; Length 3 in Feed Dict")
    comp = Composition()
    A = TransferMechanism(default_input_value=[0,1])
    B = mechanism()
    comp.add_mechanism(A)
    comp.add_mechanism(B)
    comp.add_projection(A, MappingProjection(), B)
    comp.analyze_graph()
    feed_dict_origin = {A: [ [0,1,2] ] }
    feed_dict_terminal = {B: [[0] ]}
    try:
        comp.validate_feed_dict(feed_dict_origin, comp.origin_mechanisms, "origin")
    except ValueError:
        print("passed")

    print("Test 9: Feed Dict Includes Mechanisms of the Correct & Incorrect Types")
    comp = Composition()
    A = TransferMechanism(default_input_value=[0])
    B = mechanism()
    comp.add_mechanism(A)
    comp.add_mechanism(B)
    comp.add_projection(A, MappingProjection(), B)
    comp.analyze_graph()
    feed_dict_origin = {A: [ [0] ], B: [ [0] ]}
    try:
        comp.validate_feed_dict(feed_dict_origin, comp.origin_mechanisms, "origin")
    except ValueError:
        print("passed")

    print("Test 10: Input State Length 3, 1 Set of Extra Brackets")
    comp = Composition()
    A = TransferMechanism(default_input_value=[0,1,2])
    B = mechanism()
    comp.add_mechanism(A)
    comp.add_mechanism(B)
    comp.add_projection(A, MappingProjection(), B)
    comp.analyze_graph()
    feed_dict_origin = {A: [ [ [0,1,2] ] ] }
    feed_dict_terminal = {B: [[0] ]}
    comp.validate_feed_dict(feed_dict_origin, comp.origin_mechanisms, "origin")
    comp.validate_feed_dict(feed_dict_terminal, comp.terminal_mechanisms, "terminal")
    print("passed")


    print("Test 11: Input State Length 3, 1 Set of Missing Brackets")
    comp = Composition()
    A = TransferMechanism(default_input_value=[0,1,2])
    B = mechanism()
    comp.add_mechanism(A)
    comp.add_mechanism(B)
    comp.add_projection(A, MappingProjection(), B)
    comp.analyze_graph()
    feed_dict_origin = {A:  [0,1,2] }
    feed_dict_terminal = {B: [[0] ]}
    try:
        comp.validate_feed_dict(feed_dict_origin, comp.origin_mechanisms, "origin")
    except TypeError:
        print("passed")


    print("Test 12: Empty Feed Dict For Empty Type")
    comp = Composition()
    A = TransferMechanism(default_input_value=[0])
    B = mechanism()
    comp.add_mechanism(A)
    comp.add_mechanism(B)
    comp.add_projection(A, MappingProjection(), B)
    comp.analyze_graph()
    feed_dict_origin = {A: [[0]]}
    feed_dict_monitored = {}
    comp.validate_feed_dict(feed_dict_monitored, comp.monitored_mechanisms, "monitored")
    print("passed")

    print("Test 13: Mechanism in Feed Dict For Empty Type")
    comp = Composition()
    A = TransferMechanism(default_input_value=[0])
    B = mechanism()
    comp.add_mechanism(A)
    comp.add_mechanism(B)
    comp.add_projection(A, MappingProjection(), B)
    comp.analyze_graph()
    feed_dict_origin = {A: [[0]]}
    feed_dict_monitored = {B: [[0]]}
    try:
        comp.validate_feed_dict(feed_dict_monitored, comp.monitored_mechanisms, "monitored")
    except ValueError:
        print("passed")

    print("Test 14: One Mechanism")
    comp = Composition()
    A = TransferMechanism(default_input_value=[0])
    comp.add_mechanism(A)
    comp.analyze_graph()
    feed_dict_origin = {A: [[0]]}
    feed_dict_terminal = {A: [[0]]}
    comp.validate_feed_dict(feed_dict_origin, comp.origin_mechanisms, "origin")
    print("passed (1/2)")
    comp.validate_feed_dict(feed_dict_terminal, comp.terminal_mechanisms, "terminal")
    print("passed (2/2)")


    print("Test 15: Multiple Time Steps")
    comp = Composition()
    A = TransferMechanism(default_input_value=[[0,1,2]])
    B = mechanism()
    comp.add_mechanism(A)
    comp.add_mechanism(B)
    comp.add_projection(A, MappingProjection(), B)
    comp.analyze_graph()
    feed_dict_origin = {A: [[0,1,2], [0,1,2]] }
    feed_dict_terminal = {B: [[0]]}
    comp.validate_feed_dict(feed_dict_origin, comp.origin_mechanisms, "origin")
    comp.validate_feed_dict(feed_dict_terminal, comp.terminal_mechanisms, "terminal")
    print("passed")

    print("Test 16: Multiple Time Steps")
    comp = Composition()
    A = TransferMechanism(default_input_value=[[0,1,2]])
    B = mechanism()
    comp.add_mechanism(A)
    comp.add_mechanism(B)
    comp.add_projection(A, MappingProjection(), B)
    comp.analyze_graph()
    feed_dict_origin = {A: [[[0,1,2]], [[0,1,2]]] }
    feed_dict_terminal = {B: [[0]]}
    comp.validate_feed_dict(feed_dict_origin, comp.origin_mechanisms, "origin")
    comp.validate_feed_dict(feed_dict_terminal, comp.terminal_mechanisms, "terminal")
    print("passed")
'''
