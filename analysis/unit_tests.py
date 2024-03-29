""" Unit tests for the hypergraphs module, as well as the functions contained
in distributions.py. Test cluster and Hamiltonian generation for both the 
hypercube and the PXP model (Fibonacci cube).

As some of these test are probabilistic, there is a small chance they will fail,
though there is no error present. If any failures occur, check the details and run
the tests again. For instance, one test is to check that the Hamiltonian has 50% of
the edges of the full graph when p=0.5. As the percolation process is random, there
is a probability that this test could fail, if unusually many or few edges are present."""

import unittest
import distributions
import hypergraphs
import numpy as np
import os, shutil
from scipy.special import comb
import networkx as nx
import gmpy2

# where to save the temp data for testing
DATA_PATH = "./data/testing/"

class Testdistributions(unittest.TestCase):

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

    # def test_cluster_properties(self):

    #     # test parameters
    #     N = 10
    #     NH = 2**N
    #     NR = 111

    #     # first test an intermediate value of p. Check that the right
    #     # number of clusters are generated.
    #     p = 0.5
    #     cs = distributions.get_clusters_hypercube(N, NR, p, DATA_PATH)
    #     self.assertEqual(len(cs), NR)

    #     # for p=0, check that all the clusters are of size 1.
    #     p = 0
    #     cs = distributions.get_clusters_hypercube(N, NR, p, DATA_PATH)
    #     np.testing.assert_equal(cs, 1)

    #     # for p=1, check that all clusters span the whole graph.
    #     p = 1
    #     cs = distributions.get_clusters_hypercube(N, NR, p, DATA_PATH)
    #     np.testing.assert_equal(cs, NH)

    # def test_cluster_numbers(self):

    #     # test parameters
    #     N = 8
    #     NH = 2**N
    #     NR = 97

    #     # test p = 0: minimally connected
    #     p = 0
    #     cs = distributions.get_clusters_hypercube(N, NR, p, DATA_PATH)
    #     s, n_s = distributions.cluster_numbers(cs)

    #     # for p=0, there should only be one cluster number
    #     self.assertEqual(len(n_s), 1)

    #     # its value should be 1, as there is one 1-cluster per lattice site
    #     self.assertEqual(n_s[0], 1)


    #     # test p = 1: maximally connected
    #     p = 1
    #     cs = distributions.get_clusters_hypercube(N, NR, p, DATA_PATH)
    #     s, n_s = distributions.cluster_numbers(cs)

    #     # again, there should only be one cluster number, as every cluster
    #     # is equal in size to NH, the total number of lattice nodes
    #     self.assertEqual(len(n_s), 1)

    #     # its value should be 1/NH
    #     self.assertEqual(n_s[0], 1/NH)


    #     # test p = 0.5
    #     p = 0.5
    #     cs = distributions.get_clusters_hypercube(N, NR, p, DATA_PATH)
    #     s, n_s = distributions.cluster_numbers(cs)

    #     # for intermediate p, we check normalisation. This essentially says
    #     # that every site is in a cluster of some size.
    #     # for bond percolation, the rule is: \sum_s s*n_s = 1
    #     np.testing.assert_almost_equal(np.sum([s*n_s]), 1, 4)


    #     # For N = 2, test the cluster numbers against analytic results
    #     # We need to use many realisations to achieve convergence.

    #     NR = 1000000
    #     N = 2
    #     NH = 2**N
    #     p = 0.8
    #     cs = distributions.get_clusters_hypercube(N, NR, p, DATA_PATH)
    #     s, n_s = distributions.cluster_numbers(cs)


    #     # analytic results for cluster numbers on a square
    #     n_1 = (1-p)**2
    #     n_2 = p*((1-p)**2)
    #     n_3 = (p**2)*((1-p)**2)
    #     n_4 = p**3 - (3/4)*(p**4)

    #     # aim for numerical calculations to be within one percent of the analytics.
    #     # as this is a random process, it might sometimes fail by a small amount
    #     np.testing.assert_allclose(np.array([n_1, n_2, n_3, n_4]), np.array([n_s[0], n_s[1], n_s[2], n_s[3]]), rtol = 0.01)

    # def test_w_s(self):

    #     # test parameters
    #     N = 12
    #     NR = 100
    #     p = 0.49

    #     # test for normalisation. w_s is a probability, and so its 
    #     # values should sum to 1.
    #     cs = distributions.get_clusters_hypercube(N, NR, p, DATA_PATH)
    #     s, w_s = distributions.w_s(cs)
    #     self.assertAlmostEqual(1, sum(w_s), places=5)


    #     # test p = 0
    #     p = 0
    #     cs = distributions.get_clusters_hypercube(N, NR, p, DATA_PATH)
    #     s, w_s = distributions.w_s(cs)

    #     # when p=0, there should only be the value s=1 returned
    #     self.assertEqual(s[0], 1)
    #     self.assertEqual(len(s), 1)

    #     # when p=0, the probability of ending up in a 1-cluster is 1.
    #     self.assertEqual(w_s[0], 1)
    #     self.assertEqual(len(w_s), 1)


    #     # test p = 1
    #     p = 1
    #     cs = distributions.get_clusters_hypercube(N, NR, p, DATA_PATH)
    #     s, w_s = distributions.w_s(cs)

    #     # when p=1, the probability of ending up in a 2**N-cluster is 1.
    #     self.assertEqual(s[0], 2**N)
    #     self.assertEqual(len(s), 1)
    #     self.assertEqual(w_s[0], 1)
    #     self.assertEqual(len(w_s), 1)

    # def test_S(self):

    #     N = 7
    #     NR = 99

    #     # check the result that the mean cluster size is equal to 1
    #     # when p=0.
    #     p = 0
    #     cs = distributions.get_clusters_hypercube(N, NR, p, DATA_PATH)
    #     S = distributions.S(cs)
    #     self.assertEqual(S, 1)


    #     # when p=1, the mean cluster size should be NH = 2**N, the total number
    #     # of nodes
    #     p = 1
    #     cs = distributions.get_clusters_hypercube(N, NR, p, DATA_PATH)
    #     S = distributions.S(cs)
    #     self.assertEqual(S, 2**N)

    # def test_PXP_clusters(self):
        
    #     # check that for p=1, the sizes of the clusters for a given N are equal to F(N+2)
    #     NR = 7
    #     p = 1

    #     # the first 25 Fibonacci numbers
    #     fib = lambda n:pow(2<<n,n+1,(4<<2*n)-(2<<n)-1)%(2<<n)

    #     for index in range(1, 23):
    #         N = index
    #         cs = distributions.get_clusters_PXP(N, NR, p, DATA_PATH)
    #         np.testing.assert_equal(cs, fib(N+2))
        
    #     # check that for p=0, the cluster size should be 1
    #     NR = 16
    #     p = 0
    #     N = 12
    #     cs = distributions.get_clusters_PXP(N, NR, p, DATA_PATH)
    #     np.testing.assert_equal(cs, 1)

    #     # check that the right number of clusters are produced for intermediate p
    #     NR = 111
    #     N = 7
    #     p = 0.25
    #     cs = distributions.get_clusters_PXP(N, NR, p, DATA_PATH)
    #     self.assertEqual(len(cs), NR)


    #     # test w_s for intermediate p
    #     N = 12
    #     NR = 100
    #     p = 0.49

    #     # test for normalisation. w_s is a probability, and so its 
    #     # values should sum to 1.
    #     cs = distributions.get_clusters_PXP(N, NR, p, DATA_PATH)
    #     s, w_s = distributions.w_s(cs)
    #     self.assertAlmostEqual(1, sum(w_s), places=5)

    # def test_H(self):

    #     Nlist = range(1, 11)
    #     HS_DIM_LIST = np.power(2, Nlist)


    #     # first test p = 1. The Hamiltonian should represent a complete hypercube
    #     p = 1
    #     for j in range(len(Nlist)):
    #         N = Nlist[j]
    #         NH = HS_DIM_LIST[j]
    #         H = hypergraphs.hypercube_H(N, p)

    #         # ensure that the Hamiltonian matrix has dim 2**N by 2**N
    #         np.testing.assert_equal(H.shape, (NH, NH))

    #         # ensure that all rows and all columns sum to N
    #         np.testing.assert_equal(np.fromiter((np.sum(row) for row in H), dtype=int), N)
    #         np.testing.assert_equal(np.fromiter((np.sum(row) for row in H.T), dtype=int), N)

        
    #     # next, let's use NetworkX to check if we get a hypercube for large N
    #     # this is INREDIBLY slow, so use it once

    #     N = 10
    #     nx_hypercube = nx.hypercube_graph(N)
    #     H = hypergraphs.hypercube_H(N, 1)
    #     self.assertTrue(nx.is_isomorphic(nx_hypercube, nx.from_numpy_array(H)))


    #     # test p = 0: in this limit, each node is disconnected
    #     p = 0

    #     for j in range(len(Nlist)):
    #         N = Nlist[j]
    #         NH = HS_DIM_LIST[j]
    #         H = hypergraphs.hypercube_H(N, p)

    #         # ensure that the Hamiltonian matrix has dim 2**N by 2**N
    #         np.testing.assert_equal(H.shape, (NH, NH))

    #         # ensure that everything is just zeros!
    #         np.testing.assert_equal(H, 0)

        
    #     # a couple of tests for p = 0.5
    #     p = 0.5

    #     for j in range(len(Nlist)):
    #         N = Nlist[j]
    #         NH = HS_DIM_LIST[j]
    #         H = hypergraphs.hypercube_H(N, p)

    #         # ensure that the Hamiltonian matrix has dim 2**N by 2**N
    #         np.testing.assert_equal(H.shape, (NH, NH))

    #         # ensure hermiticity
    #         np.testing.assert_array_equal(H, H.T)

        
    #     N = 14
    #     NH = 2**N
    #     H = hypergraphs.hypercube_H(N, p)

    #     # for large N, ensure that approx. the correct number of nodes are present
    #     np.testing.assert_almost_equal(np.sum(H)/(N*(2**N)), 0.5, decimal=1)
    
    # def test_symmetry(self):
    #     """ Here we test the symmetry of the eigenvalues. """
        
    #     N = 12
    #     p = 1

    #     H = hypergraphs.PXP_H(N, p)

    #     eigs, vecs = np.linalg.eigh(H)

    #     np.testing.assert_array_almost_equal(eigs, -np.flip(eigs), decimal=10)

    # def test_H_PXP(self):
        
    #     """ Test the Fibonacci cube against analytic results from the 
    #     mathematics literature. """


    #     # source: http://fare.tunes.org/files/fun/fibonacci.lisp
    #     fib = lambda n:pow(2<<n,n+1,(4<<2*n)-(2<<n)-1)%(2<<n)

    #     def number_edges(n):
    #         """ The number of edges a Fibonacci cube of dim N has.
    #         see: https://www.sciencedirect.com/science/article/pii/S0012365X05002748"""

    #         fiblist1 = np.array([fib(i) for i in range(1, n-1)])
    #         fiblist2 = np.array([fib(n+1-i) for i in range(1, n-1)])
    #         num_e = fib(n+1) + np.sum(fiblist1 * fiblist2)

    #         return num_e

    #     Nlist = range(1, 11)
    #     HS_DIM_LIST = np.array([fib(N+2) for N in Nlist])

    #     # first test p = 1. The Hamiltonian should represent a complete PXP graph
    #     p = 1
    #     for Ni, N in enumerate(Nlist):
    #         NH = HS_DIM_LIST[Ni]

    #         H = hypergraphs.PXP_H(N, p)

    #         # ensure that the Hamiltonian matrix has correct dimensions
    #         np.testing.assert_equal(H.shape, (NH, NH))

    #         # ensure that the total number of edges is correct
    #         self.assertEqual(np.sum(H)/2, number_edges(N))

    #         # ensure that the matrix is Hermitian
    #         np.testing.assert_array_equal(H, H.T)

    #         # finally, test against Wouter's code to give independent test
    #         wouters_H = Wouters_PXP_H(N)
    #         np.testing.assert_array_equal(H, wouters_H)
        
    #     p = 0
    #     for Ni, N in enumerate(Nlist):
    #         NH = HS_DIM_LIST[Ni]

    #         H = hypergraphs.PXP_H(N, p)
            
    #         # ensure that the Hamiltonian matrix has correct dimensions
    #         np.testing.assert_equal(H.shape, (NH, NH))

    #         # ensure that the total number of edges is correct
    #         self.assertEqual(np.sum(H), 0)

    #         # ensure that the matrix is Hermitian
    #         np.testing.assert_array_equal(H, H.T)


    #     p = 0.5
    #     for Ni, N in enumerate(Nlist):
    #         NH = HS_DIM_LIST[Ni]

    #         H = hypergraphs.PXP_H(N, p)
            
    #         # ensure that the Hamiltonian matrix has correct dimensions
    #         np.testing.assert_equal(H.shape, (NH, NH))

    #         # ensure that the matrix is Hermitian
    #         np.testing.assert_array_equal(H, H.T)
        
    #     # for large enough N, ensure that we have approx. the correct number of edges
    #     N = 20; p = 0.5
    #     H = hypergraphs.PXP_H(N, p)
    #     np.testing.assert_almost_equal(np.sum(H)/(2*number_edges(N)), 0.5, decimal=1)

    # def test_PXP_site_generation(self):

    #     def basis_states(N):
    #         """ Construct the basis states for the PXP model. """
    #         sites = [i for i in range(2**N) if (i & (i >> 1) == 0)]
    #         return sites

    #     # first test: manually construct sites which we KNOW are not allowed
    #     # to be present in the PXP graph. Check that they are indeed not there.

    #     # WARNING: NEXT FEW LINES ARE HARD-CODED
    #     Nlist = np.array([2, 5, 8, 11, 13])
    #     disallowed_sites = [[0b11],
    #                        [0b11111, 0b10011, 0b11000], 
    #                        [0b00001111, 0b11011010, 0b00101101], 
    #                        [0b11010101010, 0b01101010100, 0b11101010101], 
    #                        [0b0000011000000, 0b1110101010101, 0b1111111111111]]

    #     for Ni, N in enumerate(Nlist):
    #         sites = hypergraphs.PXP_sites(N)

    #         # first check that our "bad states" are not present
    #         bad_sites = disallowed_sites[Ni]
    #         for bad_site in bad_sites:
    #             self.assertTrue(bad_site not in sites)

    #         # now check against the above Python function for constructing the 
    #         # same basis states.
    #         np.testing.assert_array_equal(sites, basis_states(N))

    # def test_RNG(self):
    #     """A probabilistic test, which might therefore fail with a small probability!"""

    #     randints = [hypergraphs.RNG_test() for _ in range(100)]

    #     # by checking that successive calls to RNG_test(), which returns a random integer,
    #     # we are checking for collisions. I.e., that the RNG is sucessfully seeded once.
    #     for k in range(len(randints) - 1):
    #         self.assertNotEqual(randints[k], randints[k+1])

    # def test_dijkstra(self):

    #     # First test p = 1

    #     # Test the 3-cube for p=1
    #     N = 3
    #     p = 1
    #     distances = sorted(hypergraphs.hypercube_dijkstra(N, p))
    #     cube_dists = [0,1,1,1,2,2,2,3]
    #     np.testing.assert_array_equal(distances, cube_dists)
    #     self.assertEqual(len(distances), 2**N)

    #     # Test for a huge cube by computing the analytic answer
    #     N = 22
    #     p = 1
    #     distances = sorted(hypergraphs.hypercube_dijkstra(N, p))
    #     analytic_distances = sorted(Hamming_distances_from_zero(N))
    #     np.testing.assert_array_equal(distances, analytic_distances)
    #     self.assertEqual(len(distances), 2**N)



    #     # Now test p = 0
    #     N = 28
    #     p = 0
    #     distances = sorted(hypergraphs.hypercube_dijkstra(N, p))
    #     analytic_distances = [0]
    #     np.testing.assert_array_equal(distances, analytic_distances)
    #     self.assertEqual(len(distances), 1)



    #     # Test intermediate value of p
    #     N = 19
    #     p = 0.2
    #     distances = sorted(hypergraphs.hypercube_dijkstra(N, p))
    #     self.assertTrue(len(distances) > 1)
    #     self.assertTrue(len(distances) < 2**N)

    #     # The maximum distance should be less than the maximum possible
    #     # path length in an N-cube
    #     self.assertTrue(max(distances) < 2**N - 1)
        
    #     # cutting bonds should increase the average distance (N/2)
    #     self.assertTrue(np.mean(distances) > N/2)



    #     # Test N = 1: there are two states (up and down)
    #     N = 1
    #     p = 1
    #     distances = sorted(hypergraphs.hypercube_dijkstra(N, p))
    #     np.testing.assert_array_equal(distances, [0, 1])

    # def test_dijkstra_LC(self):

    #     # First test p = 1

    #     # Test the 3-cube for p=1
    #     N = 3
    #     p = 1
    #     distances = sorted(hypergraphs.hypercube_dijkstra_LC(N, p))
    #     cube_dists = [0,1,1,1,2,2,2,3]
    #     np.testing.assert_array_equal(distances, cube_dists)
    #     self.assertEqual(len(distances), 2**N)

    #     # Test for a huge cube by computing the analytic answer
    #     N = 16
    #     p = 1
    #     distances = sorted(hypergraphs.hypercube_dijkstra_LC(N, p))
    #     analytic_distances = sorted(Hamming_distances_from_zero(N))
    #     np.testing.assert_array_equal(distances, analytic_distances)
    #     self.assertEqual(len(distances), 2**N)


    #     # Now test p = 0
    #     N = 11
    #     p = 0
    #     distances = sorted(hypergraphs.hypercube_dijkstra_LC(N, p))
    #     analytic_distances = [0]
    #     np.testing.assert_array_equal(distances, analytic_distances)
    #     self.assertEqual(len(distances), 1)



    #     # Test intermediate value of p
    #     N = 11
    #     p = 0.2
    #     distances = sorted(hypergraphs.hypercube_dijkstra_LC(N, p))
    #     self.assertTrue(len(distances) > 1)
    #     self.assertTrue(len(distances) < 2**N)

    #     # The maximum distance should be less than the maximum possible
    #     # path length in an N-cube
    #     self.assertTrue(max(distances) < 2**N - 1)
        
    #     # cutting bonds should increase the average distance (N/2)
    #     self.assertTrue(np.mean(distances) > N/2)


    #     # Test N = 1: there are two states (up and down)
    #     N = 1
    #     p = 1
    #     distances = sorted(hypergraphs.hypercube_dijkstra_LC(N, p))
    #     np.testing.assert_array_equal(distances, [0, 1])


    #     # An expensive test: check the average size of the max cluster for
    #     # a particular value of N and p

    #     max_sizes_from_H = []

    #     NR = 20000
    #     N = 7
    #     p = 0.3

    #     for _ in range(NR):
    #         H = hypergraphs.hypercube_H(N, p)
    #         max_size = max([len(comp) for comp in nx.connected_components(nx.from_numpy_array(H))])
    #         max_sizes_from_H.append(max_size)
        
    #     max_sizes_from_dijkstra = []
    #     for _ in range(NR):
    #         paths = hypergraphs.hypercube_dijkstra_LC(N, p)
    #         max_sizes_from_dijkstra.append(len(paths))

    #     np.testing.assert_almost_equal(np.mean(max_sizes_from_dijkstra), np.mean(max_sizes_from_H), decimal=0)

    # def test_hypercube_H_SC(self):

    #     # First check that p=1 gives the same result
    #     Nlist = np.arange(1, 11)
    #     p = 1

    #     for N in Nlist:
    #         H_grown = hypergraphs.hypercube_H_SC(N, p)
    #         H = hypergraphs.hypercube_H(N, p)
    #         # Check that the two Hamiltonians are the same
    #         np.testing.assert_array_equal(H, H_grown[0])

    #         # Check that the cluster sizes are correct

    #         NH = 2**N
    #         self.assertEqual(H_grown[1], NH)



    #     # Checks for p = 0
    #     p = 0

    #     for N in Nlist:
    #         H_grown = hypergraphs.hypercube_H_SC(N, p)
    #         np.testing.assert_array_equal(H_grown[0], 0)
    #         self.assertEqual(H_grown[1], 1)


    #     # Checks for intermediate p
    #     p = 0.5

    #     for N in Nlist:
    #         H_grown = hypergraphs.hypercube_H_SC(N, p)
    #         # Test Hermiticity
    #         np.testing.assert_array_equal(H_grown[0], H_grown[0].T)

    #         # Check that the size of the cluster fits with the Hamiltonian
    #         row_sum = np.sum(H_grown[0], axis=0)
    #         size = np.sum([1 for j in row_sum if j > 0])
    #         if size == 0:
    #             self.assertEqual(H_grown[1], 1)
    #         else:
    #             self.assertEqual(size, H_grown[1])
        
    #     # for large N, ensure that approx. the correct number of nodes are present
    #     N = 14
    #     H_grown = hypergraphs.hypercube_H_SC(N, p)
    #     np.testing.assert_almost_equal(np.sum(H_grown[0])/(N*(2**N)), p, decimal=2)

    # def test_hypercube_get_H_SC(self):
    #     N = 6
    #     NR = 12

    #     # First test p = 1
    #     p = 1
    #     H_data = distributions.get_H_SC_hypercube(N, NR, p, DATA_PATH)

    #     # Check the size of the data
    #     self.assertEqual(len(H_data), NR)
    #     self.assertEqual(len(H_data[0]), 2)

    #     for data in H_data:
    #         H = data[0].toarray()
    #         size = data[1]
    #         # Size of the cluster == NH == 2**N
    #         self.assertEqual(size, 2**N)
    #         # Check against whole H code
    #         np.testing.assert_array_equal(H, hypergraphs.hypercube_H(N, p))
        
    #     # Now test p = 0
    #     p = 0
    #     H_data = distributions.get_H_SC_hypercube(N, NR, p, DATA_PATH)
    #     for data in H_data:
    #         H = data[0].toarray()
    #         size = data[1]
    #         # Size of the cluster == 1
    #         self.assertEqual(size, 1)
    #         # Check against whole H code
    #         np.testing.assert_array_equal(H, hypergraphs.hypercube_H(N, p))
    
    # def test_get_path_lengths_hypercube(self):
    #     N = 7
    #     NH = 2**N
    #     NR = 102

    #     # Start with p = 1, where we know some analytic results
    #     # Remember, we have already tested the hypercube_dijkstra() code

    #     p = 1
    #     lengths = distributions.get_path_lengths_hypercube(N, NR, p, DATA_PATH)
    #     lengths = distributions.get_path_lengths_hypercube(N, NR, p, DATA_PATH)

    #     # We should generate NR clusters
    #     self.assertEqual(len(lengths), NR)

    #     # Check clusters are correct size and compare result to analytic 
    #     for i in range(NR): 
    #         self.assertEqual(len(lengths[i]), NH)
    #         np.testing.assert_array_equal(sorted(lengths[i]), sorted(Hamming_distances_from_zero(N)))


    #     # Now check p = 0
    #     p = 0
    #     lengths = distributions.get_path_lengths_hypercube(N, NR, p, DATA_PATH)
        
    #     # We should generate NR clusters
    #     self.assertEqual(len(lengths), NR)

    #     # But each cluster is of size 1, and has path length zero
    #     for i in range(NR): 
    #         np.testing.assert_array_equal(sorted(lengths[i]), np.array([0]))

    # def test_hypercube_H_LC(self):
    #     N = 7
    #     NH = 2**N

    #     # First test p = 1
    #     p = 1
    #     H_LC = hypergraphs.hypercube_H_LC(N, p)
    #     H_exact = hypergraphs.hypercube_H(N, p)
    #     np.testing.assert_array_equal(H_LC[0], H_exact)
    #     self.assertEqual(NH, H_LC[1])


    #     # Next, test p = 0
    #     p = 0
    #     H_LC = hypergraphs.hypercube_H_LC(N, p)
    #     H_exact = hypergraphs.hypercube_H(N, p)
    #     np.testing.assert_array_equal(H_LC[0], H_exact)
    #     self.assertEqual(1, H_LC[1])


    #     # Some tests for intermediate p

    #     p = 0.3
    #     H_LC = hypergraphs.hypercube_H_LC(N, p)

    #     # Hermiticity
    #     np.testing.assert_array_equal(H_LC[0], H_LC[0].T)

    #     # Number of rows containing one or more 1 should be == NH
    #     size_manual = np.sum([1 for row in H_LC[0] if np.sum(row) > 0])
    #     self.assertEqual(size_manual, H_LC[1])

    #     # Use NetworkX to check number of connected components is one
    #     # Cannot use nx.number_connected_components() as it counts "clusters"
    #     # of just one site.
    #     compts = nx.connected_components(nx.from_numpy_array(H_LC[0]))
    #     number_clusters = 0
    #     for comp in compts:
    #         if len(comp) > 1: # count only components containing more than one site
    #             number_clusters += 1
    #     self.assertTrue(number_clusters == 1)

    #     # An expensive test: check the average size of the max cluster for
    #     # a particular value of N and p

    #     max_sizes_from_H = []

    #     NR = 20000
    #     N = 7
    #     p = 0.3

    #     for _ in range(NR):
    #         H = hypergraphs.hypercube_H(N, p)
    #         max_size = max([len(comp) for comp in nx.connected_components(nx.from_numpy_array(H))])
    #         max_sizes_from_H.append(max_size)
        
    #     max_sizes_from_H_LC = []
    #     for _ in range(NR):
    #         H_LC = hypergraphs.hypercube_H_LC(N, p)
    #         max_sizes_from_H_LC.append(H_LC[1])
        
    #     np.testing.assert_almost_equal(np.mean(max_sizes_from_H_LC), np.mean(max_sizes_from_H), decimal=0)
    
    def test_get_path_lengths_hypercube_LC(self):

        N = 7
        NH = 2**N
        NR = 102

        # Start with p = 1, where we know some analytic results
        # Remember, we have already tested the hypercube_dijkstra() code

        p = 1
        lengths = distributions.get_path_lengths_hypercube_LC(N, NR, p, DATA_PATH)
        lengths = distributions.get_path_lengths_hypercube_LC(N, NR, p, DATA_PATH)

        # We should generate NR clusters
        self.assertEqual(len(lengths), NR)

        # Check clusters are correct size and compare result to analytic 
        for i in range(NR): 
            self.assertEqual(len(lengths[i]), NH)
            np.testing.assert_array_equal(sorted(lengths[i]), sorted(Hamming_distances_from_zero(N)))


        # Now check p = 0
        p = 0
        lengths = distributions.get_path_lengths_hypercube_LC(N, NR, p, DATA_PATH)
        
        # We should generate NR clusters
        self.assertEqual(len(lengths), NR)

        # But each cluster is of size 1, and has path length zero
        for i in range(NR): 
            np.testing.assert_array_equal(sorted(lengths[i]), np.array([0]))


    def test_hypercube_get_H_LC(self):
        N = 7
        NR = 12

        # First test p = 1
        p = 1
        H_data = distributions.get_H_LC_hypercube(N, NR, p, DATA_PATH)

        # Check the size of the data
        self.assertEqual(len(H_data), NR)
        self.assertEqual(len(H_data[0]), 2)

        for data in H_data:
            H = data[0].toarray()
            size = data[1]
            # Size of the cluster == NH == 2**N
            self.assertEqual(size, 2**N)
            # Check against whole H code
            np.testing.assert_array_equal(H, hypergraphs.hypercube_H(N, p))
        
        # Now test p = 0
        p = 0
        H_data = distributions.get_H_LC_hypercube(N, NR, p, DATA_PATH)
        for data in H_data:
            H = data[0].toarray()
            size = data[1]
            # Size of the cluster == 1
            self.assertEqual(size, 1)
            # Check against whole H code
            np.testing.assert_array_equal(H, hypergraphs.hypercube_H(N, p))
    

###############################
##### ANCILLARY FUNCTIONS #####
###############################

def Hamming_distances_from_zero(N):
    """I.e., how many bits are set?"""
    NH = 2**N
    return np.fromiter((gmpy2.popcount(i) for i in range(NH)), dtype=np.uint)

def Wouters_PXP_H(L):
    """ Code to construct the PXP Hamiltonian courtesy of Wouter.
    Included as an independent test against my own code. """
    states = np.zeros((2**L, L), dtype=int)
                            
    for i in np.arange(2**L):
        ibin =  np.binary_repr(i, width=L)

        for j in np.arange(L):
            states[i,j] = int(ibin[j])

    # filter out allowed basis states
    trig = np.zeros(2**L, dtype=int)

    for i in np.arange(2**L):
        
        # boundary sites
        trig[i] =  0 # obc

        # bulk sites
        for j in np.arange(L-1):
            trig[i] = trig[i] + states[i,j] * states[i,j+1]

    states = states[np.where(trig == 0), :]
    states = states[0]


    # construct Hamiltonian
    dimH = np.shape(states)[0]
    H = np.zeros((dimH, dimH), dtype=int)

    for i in np.arange(dimH):
        for j in np.arange(i):
            if np.sum(np.abs(states[i] - states[j])) == 1:
                H[i,j] = 1
                H[j,i] = 1
    return np.array(H)

if __name__ == "__main__":
    unittest.main()
