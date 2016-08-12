import numpy as np
import unittest

# For keeping self contained only
import sys
import os
PycQEDdir = (os.path.abspath('../../../..'))
sys.path.append(PycQEDdir)

from modules.measurement.randomized_benchmarking.clifford_decompositions \
    import(gate_decomposition)
# Basic states
# desnity matrices in pauli basis
X0 = 1/np.sqrt(2) * np.matrix([1,  1, 0, 0]).T
X1 = 1/np.sqrt(2) * np.matrix([1,  -1, 0, 0]).T
Y0 = 1/np.sqrt(2) * np.matrix([1, 0, 1, 0]).T
Y1 = 1/np.sqrt(2) * np.matrix([1, 0, -1, 0]).T
Z0 = 1/np.sqrt(2) * np.matrix([1, 0, 0, 1]).T
Z1 = 1/np.sqrt(2) * np.matrix([1, 0, 0, -1]).T

polar_states = [X0, X1, Y0, Y1, Z0, Z1]

# Superoperators for our gate set
Gi = np.eye(4)
Gx90 = np.matrix([[1.0, 0, 0, 0],
                 [0, 1.0, 0, 0],
                 [0, 0, 0, -1],
                 [0, 0, 1.0, 0]])

Gx180 = np.matrix([[1.0, 0, 0, 0],
                  [0, 1.0, 0, 0],
                  [0, 0, -1., 0],
                  [0, 0, 0, -1.]])

Gy90 = np.matrix([[1.0, 0, 0, 0],
                 [0, 0, 0, 1.],
                 [0, 0, 1., 0],
                 [0, -1, 0, 0]])


Gy180 = np.matrix([[1.0, 0, 0, 0],
                  [0, -1.0, 0, 0],
                  [0, 0, 1.0, 0],
                  [0, 0, 0, -1.0]])


# Test inner product between states


Ideal_gates = {'I': Gi,
               'X90': Gx90,
               'X180': Gx180,
               'Y90': Gy90,
               'Y180': Gy180,
               'mX90': Gx90**-1,
               'mX180': Gx180**-1,
               'mY90': Gy90**-1,
               'mY180': Gy180**-1,
               }

# Define all the tests

def generate_clifford_operators(gateset,
                                clifford_decomposition=gate_decomposition):
    clifford_group = []*24
    for i, cl in enumerate(gate_decomposition):
        print(cl)

generate_clifford_operators(gateset=Ideal_gates)



class Test_density_vecs(unittest.TestCase):
        def test_overlap_with_self(self):
            for vec in polar_states:
                self.assertAlmostEqual((vec.T * vec), 1)

        def test_overlap_with_orthogonal(self):
            for s0, s1 in zip(polar_states[:-1:2], polar_states[1::2]):
                self.assertAlmostEqual((s0.T * s1), 0)

        def test_overlap_with_different_bases(self):
            for i, s0 in enumerate(polar_states):
                if i % 2 == 0:
                    for j in range(len(polar_states)):
                        if j != i and j != (i+1):
                            self.assertAlmostEqual(
                                (s0.T * polar_states[j]), 0.5)
                else:
                    for j in range(len(polar_states)):
                        if j != i and j != (i-1):
                            self.assertAlmostEqual(
                                (s0.T * polar_states[j]), 0.5)


class Test_basic_operations(unittest.TestCase):
    def test_valid(self):
        g = Ideal_gates
        np.testing.assert_almost_equal(g['X90'], g['X90'])
        np.testing.assert_almost_equal(g['X180'], g['X180'])
        np.testing.assert_almost_equal(g['Y90'], g['Y90'])
        np.testing.assert_almost_equal(g['Y180'], g['Y180'])
        np.testing.assert_almost_equal(g['I'], g['I'])

        # Test some basic operations
    def test_identity(self):
        g = Ideal_gates
        for vec in polar_states:
            np.testing.assert_almost_equal(vec, g['I']*vec)

    def test_basic_rotations(self):
        g = Ideal_gates
        np.testing.assert_almost_equal(X0, g['X180']*X0)
        np.testing.assert_almost_equal(X1, g['Y180']*X0)
        np.testing.assert_almost_equal(X0, g['X90']*X0)
        np.testing.assert_almost_equal(Z1, g['Y90']*X0)
        np.testing.assert_almost_equal(Z0, g['Y90']*X1)

        np.testing.assert_almost_equal(Y1.T*(g['X180']*Y0), 1)
        np.testing.assert_almost_equal(Y0, g['Y180']*Y0)
        np.testing.assert_almost_equal(Z0, g['X90']*Y0)
        np.testing.assert_almost_equal(Z1, g['X90']*Y1)
        np.testing.assert_almost_equal(Y0, g['Y90']*Y0)

        np.testing.assert_almost_equal(Z1, g['X180']*Z0)
        np.testing.assert_almost_equal(Z1, g['Y180']*Z0)
        np.testing.assert_almost_equal(Y1, g['X90']*Z0)
        np.testing.assert_almost_equal(X0, g['Y90']*Z0)

    def test_inverses(self):
        g = Ideal_gates
        np.testing.assert_almost_equal(g['X90']*g['mX90'], g['I'])
        np.testing.assert_almost_equal(g['Y90']*g['mY90'], g['I'])
        np.testing.assert_almost_equal(g['X180']*g['mX180'], g['I'])
        np.testing.assert_almost_equal(g['Y180']*g['mY180'], g['I'])

class Test_clifford_composition(unittest.TestCase):
    def test_case(self):
        True


test_classes_to_run = [Test_density_vecs,
                       Test_basic_operations,
                       Test_clifford_composition,
                       ]

suites_list = []
for test_class in test_classes_to_run:
    suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
    suites_list.append(suite)

combined_test_suite = unittest.TestSuite(suites_list)
runner = unittest.TextTestRunner(verbosity=2).run(combined_test_suite)