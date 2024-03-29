import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
import unittest
import hypergraphs
import time_evolution as te
import os, shutil
import distributions
from scipy import linalg as la
from scipy.special import comb

# where to save the temp data for testing
DATA_PATH = "./data/testing/"

class Testeigenstates(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(DATA_PATH):
            os.makedirs(DATA_PATH)

    def tearDown(self):
        # delete the contents of the data/testing directory
        for filename in os.listdir(DATA_PATH):
            file_path = os.path.join(DATA_PATH, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    def test_U_U_T(self):
        # Test the unitary operators which take us between the site and eigenbasis

        N = 7
        p = 1
        H = hypergraphs.hypercube_H(N, p)

        eigs, vecs = np.linalg.eigh(H)

        U = te.U(vecs)
        Ut = te.U_T(vecs)

        # U_T @ H @ U = diag(eigs)
        diag_H = np.diag(Ut @ H @ U)
        np.testing.assert_array_almost_equal(eigs, diag_H, 6)


        # Now let's test with a complex random matrix! Test we're getting
        # the complex conjugation right.

        c_matrix = np.random.rand(100, 100) + 1j*np.random.rand(100, 100)
        c_matrix_hermitian = c_matrix + np.conjugate(c_matrix.T)

        eigs, vecs = np.linalg.eigh(c_matrix_hermitian)

        U = te.U(vecs)
        Ut = te.U_T(vecs)

        # U_T @ H @ U = diag(eigs)
        diag_H = np.diag(Ut @ c_matrix_hermitian @ U)
        np.testing.assert_array_almost_equal(eigs, diag_H, 6)

    def test_psi_0(self):
        # Test the construction of the initial state

        N = 6
        p = 1

        H = hypergraphs.hypercube_H(N, p)
        eigs, vecs = np.linalg.eigh(H)

        psi_0 = te.psi_0(vecs, 37, N)
        self.assertEqual(len(psi_0), 2**N)

        # test normalised
        self.assertAlmostEqual(np.vdot(psi_0, psi_0), 1, places=10)

    def test_psi_t(self):

        # Several tests of the time-evolved state

        N = 10
        NH = 2**N
        p = 1
        H = hypergraphs.hypercube_H(N, p)
        eigs, vecs = np.linalg.eigh(H)

        site = 111

        # TE through a time t and check that the state remains normalised
        psi0 = te.psi_0(vecs, site, N)
        t = 100
        psit = te.psi_t(eigs, psi0, t)
        self.assertAlmostEqual(np.vdot(psit, psit), 1, places=10)


        # Check against explicit TE. Convert psi_t back into site basis
        psi0_explicit = np.zeros(NH)
        psi0_explicit[site] = 1
        psit_explicit = la.expm(-1j*H*t) @ psi0_explicit
        np.testing.assert_array_almost_equal(np.abs(psit_explicit), np.abs(vecs @ psit), decimal=8)

    def test_D(self):

        # For this test, let's perform a calculation in the eigenbasis
        # (using D), and also manually in the site basis.

        N = 6
        NH = 2**N
        p = 0.7
        site = 53 # start from some random site

        H = hypergraphs.hypercube_H(N, p)
        eigs, vecs = np.linalg.eigh(H)
        D = te.D(vecs, site, N)


        # Firstly, we know that the MHD is zero in the start state
        psi0 = te.psi_0(vecs, site, N)
        MHD = np.vdot(psi0, D @ psi0)
        self.assertAlmostEqual(MHD, 0, places=10)


        # Now let's do the same calculation, but with some time-evolution.
        # This will also test other parts of the code, e.g. time evolution.
        t = 99.98
        psit = te.psi_t(eigs, psi0, t)
        MHD = np.vdot(psit, D @ psit)

        psi_0_site_basis = np.zeros(NH)
        psi_0_site_basis[site] = 1
        psit_exact_site_basis = np.dot(la.expm(-1j * t * H), psi_0_site_basis)

        
        hds = te.Hamming_distances(N, site)
        MHD_exact = np.dot(hds, np.abs(psit_exact_site_basis)**2)

        self.assertAlmostEqual(MHD, MHD_exact, places=10)

    def test_time_evolution(self):
        # Carry out a time evolution in the eigenbasis, and compare to 
        # the same calculation performed in the site basis

        # Get one H matrix for a single cluster, as an array
        N = 7
        NH = 2**N
        p = 0.1
        t = 312.312
        NR = 1
        H = distributions.get_H_LC_hypercube(N, NR, p, DATA_PATH)[0][0].toarray()
        eigs, vecs = np.linalg.eigh(H)
        
        start_site = te.find_start_site(H, N)

        # Compute |\psi(t)> manually in the site basis
        psi_0_site = np.zeros(NH)
        psi_0_site[start_site] = 1
        psi_t_site = np.dot(la.expm(-1j * t * H), psi_0_site)

        # Convert it to the eigenbasis
        psi_t_eigen = np.dot(vecs.conj().T, psi_t_site)

        # Now repeat the calculation using the te functions
        psi_0 = te.psi_0(vecs, start_site, N)
        psi_t = te.psi_t(eigs, psi_0, t)

        # Assert both methods are equal in the eigenbasis
        np.testing.assert_array_almost_equal(psi_t, psi_t_eigen, decimal=10)

        # Assert both methods are equal in the site basis
        np.testing.assert_array_almost_equal(psi_t_site, np.dot(vecs, psi_t), decimal=10)

    def test_find_start_state(self):
        N = 7
        NH = 2**N
        site = 66
        mock_H = np.zeros((NH, NH))
        mock_H[site, site+1] = 1
        mock_H[site+1, site] = 1

        index = te.find_start_site(mock_H, N)
        self.assertEqual(index, site)

    def test_HD(self):
        # Test the final calculation: the computation of the Hamming distance for
        # an input array of times t.

        N = 7
        NH = 2**N
        p = 0.29
        NR = 1
        tlist = np.linspace(0, 1000, 20)

        # Use te and hypergraphs functions to compute HD(tlist)
        H = hypergraphs.hypercube_H_LC(N, p)[0]
        start_site = te.find_start_site(H, N)
        eigs, vecs = np.linalg.eigh(H)
        HDs = te.HD(eigs, vecs, start_site, tlist, N)

        # Do one of them manually, and compare
        psi0 = te.psi_0(vecs, start_site, N)
        t = tlist[-2]
        psit = te.psi_t(eigs, psi0, t)
        D = te.D(vecs, start_site, N)
        HD = np.vdot(psit, D @ psit)

        np.testing.assert_array_almost_equal(HD, HDs[-2], decimal=10)

    def test_MHD(self):
        # Try to test the final product: the mean hamming distance as a function of time

        def exact_MHD_hypercube(N, tlist):
            """Exact expression for the MHD at p = 1"""
            mhd = np.zeros(len(tlist))
            for j in range(1, N+1):
                term = j * np.power(np.cos(tlist), 2*(N-j)) * np.power(np.sin(tlist), 2*j) * comb(N, j, exact=True)
                mhd += term
            
            return mhd
        
        # FIRST TEST: compare MHD with exact analytic expression at p = 1
        N = 7
        NT = 20
        t_max = 10**6
        NR = 10

        # Use the MHD function in time_evolution
        data = te.MHD(N, N, t_max, NT, NR)
        data = te.MHD(N, N, t_max, NT, NR)

        # Compare to the exact expression
        tlist = np.logspace(0, np.log10(t_max), NT)
        exact_data = exact_MHD_hypercube(N, tlist)
        np.testing.assert_array_almost_equal(data, exact_data, decimal = 8)


        # SECOND TEST: p = 0
        data = te.MHD(N, 0, t_max, NT, NR)
        np.testing.assert_array_equal(data, np.zeros(NT))


if __name__ == "__main__":
    unittest.main()
