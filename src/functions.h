#define PY_SSIZE_T_CLEAN
#define PY_ARRAY_UNIQUE_SYMBOL hypergraphs_ARRAY_API
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>
#include <numpy/arrayobject.h>
#include <gsl/gsl_matrix.h>
#include <gsl/gsl_rng.h> 
#include <stdbool.h>

typedef unsigned long ul;

typedef struct stack
{
    ul *sites;
    ul length;
    ul top;
    ul NH;
}
stack;

typedef struct queue {
    ul *sites;
    ul writeIdx;
    ul readIdx;
    ul length;
}
queue;

/* Stack functions */
int push(stack *s, ul site);
ul pop(stack *s, int *error);
stack *setup_stack(ul NH);
void reset_visited(bool visited[], ul length);

/* Queue functions */
queue *setup_queue(ul length);
void enqueue(queue *q, ul item, int *err);
ul dequeue(queue *q, int *err);
bool empty(queue *q);

/* Hypercube functions */
ul DFS_hypercube(stack *s, bool visited[], const float p, const ul N, const ul start_state, int *error);
PyObject *hypercube_clusters(PyObject *self, PyObject *args);
PyObject *hypercube_H(PyObject *self, PyObject *args);
PyObject *hypercube_H_SC(PyObject *self, PyObject *args);
PyObject *hypercube_H_LC(PyObject *self, PyObject *args);
PyObject *hypercube_dijkstra(PyObject *self, PyObject *args);
PyObject *hypercube_dijkstra_LC(PyObject *self, PyObject *args);

/* PXP functions */
void populate_sites_PXP(ul *sites, ul N);
ul *construct_PXP_sitelist(ul N);
bool PXP_flip_allowed(ul u, ul i, ul N);
ul DFS_PXP(stack *s, ul *sites, bool visited[], const float p, const ul N, const ul start_state, int *error);
PyObject *PXP_clusters(PyObject *self, PyObject *args);
PyObject* PXP_H(PyObject *self, PyObject *args);
PyObject *PXP_sites(PyObject *self, PyObject *args);

/* Maths functions */
ul intpower(ul base, ul exponent);
ul binomialCoeff(ul n, ul r);
ul index_site(ul *sites, ul site, ul left, ul right, int *idx_flag);
ul fibonacci(ul n);

/* Misc functions */
bool check_args(ul N, ul NR, float p);
PyObject *CArrayToNumPyArray(ul *arr, ul length);
ul pyobject_to_ul(PyObject *positive_int);
PyObject *Hamming_distance(PyObject *self, PyObject *args);
PyObject *RNG_test(PyObject *self, PyObject *args);



