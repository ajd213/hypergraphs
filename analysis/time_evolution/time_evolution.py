""" Functions to analyse the dynamical properties of the hypercube at percolation concentration p"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
import gmpy2
import distributions

DATA_PATH = "/Users/alex/Code/Hypercubes/analysis/data/"


def psi_0(vecs, N):
    """ The starting state |0> in the eigenbasis of the Hamiltonian. """
    NH = 2**N

    psi = np.zeros(NH)
    psi[0] = 1

    return np.dot(U_T(vecs), psi)


def psi_t(eigs, psi0, t):
    """ |\psi(t)> in the eigenbasis. """
    te_operator = TE_operator(eigs, t)
    return te_operator * psi0


def TE_operator(eigs, t):
    return np.exp(-1j * t * eigs)


def Hamming_distances(N):
    NH = 2**N
    return np.fromiter((gmpy2.popcount(i) for i in range(NH)), dtype=np.uint)


def D(vecs, N):
    """ The Hamming Distance operator in the eigenbasis. """
    NH = 2**N
    D_site_basis = np.diag(Hamming_distances(N))
    
    return U_T(vecs) @ D_site_basis @ U(vecs)


def HD(eigs, vecs, tlist, N):
    """ Compute the Hamming distance of a time-evolving state,
    given the eigenvalues and eigenvectors of a Hamiltonian. """
    psi0 = psi_0(vecs, N)
    D_op = D(vecs, N)
    HDs = np.zeros(len(tlist))

    for ti, t in enumerate(tlist):
        psit = psi_t(eigs, psi0, t)
        ham_dist = np.vdot(psit, D_op @ psit)
        HDs[ti] = ham_dist

    return HDs


def MHD(N, N_coeff, t_max, NT, NR, log=True):
    """ Attempt to load the MHD data, else generate it (from saved H data) and save it."""

    p = N_coeff/N
    NH = 2**N

    name = f"MHD_LC_hypercube_N{N}_NR{NR}_p{p:.4f}_NT{NT}_TMAX{t_max}_LOG{log}.npy"

    try:
        res = np.load(DATA_PATH + name)
    except FileNotFoundError:
        if log:
            tlist = np.logspace(0, np.log10(t_max), NT)
        else:
            tlist = np.linspace(0, t_max, NT)

        res = np.zeros(NT) # Store the result here

        # Load the Hamiltonians and cluster sizes
        H_data = distributions.get_H_LC_hypercube(N, NR, p, DATA_PATH)

        for di, data in enumerate(H_data):
            print(f"{(di/NR)*100:.3f}% done", end='\r')
            H = data[0].toarray()
            eigs, vecs = np.linalg.eigh(H)
            res += HD(eigs, vecs, tlist, N)

        res /= NR
        np.save(DATA_PATH + name, res)
    return res


""" U and U_T are such that U_T @ H @ U = diag(eigs). 
    Correctly accounts for complex eigenvectors. """

def U(vecs):
    return vecs

def U_T(vecs):
    return vecs.conj().T