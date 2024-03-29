/* Core functions for running a depth-first search algorithm on a hypercube of arbitrary
dimension for the percolation problem. */
#define NO_IMPORT_ARRAY
#include "functions.h"
#include <stdlib.h>
#include <stdio.h>
#include <limits.h>

extern gsl_rng *RNG;


/*
 * Static function:  dijkstra
 * --------------------
 * Helper function used in hypercube_dijkstra and hypercube_dijkstra_LC. This function runs
 * Dijkstra's algorithm from a given site and writes the distances and labels to passed arrays.
 * If the labels feature is not needed, then NULL can be passed as the labels argument.
 *
 * q: a pointer to a queue
 * N: the dimension of the hypercube
 * p: the percolation concentration
 * start_state: hypercube node from which to grow the cluster
 * visited: an array of bools, marking each site as visited (true) or unvisited (false)
 * distances: a pointer to an array of uls representing the distance from the start site to all the others in each cluster
 * number_visited: a pointer to an ul in which to store the size of the cluster explored by one instance of Dijkstra
 * cluster_index: ul used to label each site in the cluster we are about to create
 * labels: pointer to an array of uls which we use to keep track of the cluster labels of each site
 *
 */
static void dijkstra(queue *q, const ul N, const float p, const ul start_site, bool visited[], ul *distances, ul *number_visited, ul cluster_index, ul *labels)
{
    ul u, v, dist;
    ul old_cost, new_cost;
    int err = 0;

    enqueue(q, start_site, &err);
    while(!empty(q))
    {
        u = dequeue(q, &err);
        if (err) goto error;
        (*number_visited)++;

        dist = distances[u];
        visited[u] = true;
        if (labels)
        {
            labels[u] = cluster_index;
        }

        // Explore the neighbours of u
        for (ul i = 0; i < N; i++)
        {
            // flip the ith bit
            v = u ^ (1UL << i);

            if (!visited[v] && (gsl_rng_uniform(RNG) < p))
            {
                old_cost = distances[v];
                new_cost = distances[u] + 1;

                if (new_cost < old_cost)
                {
                    enqueue(q, v, &err);
                    if (err) goto error;
                    distances[v] = new_cost;
                }
            }
        }
    }
    return;

    error:
        if (distances) free(distances);
        if (q)
        {
            free(q->sites);
            free(q);
        }
        if (visited) free(visited);
}

/*
 * Function:  hypercube_dijkstra_LC
 * --------------------
 * Run Dijkstra's algorithm within the LARGEST cluster in a Hypercube.
 * To do this, we have to enumerate all sites.
 *
 * N: the dimension of the hypercube
 * p: the percolation concentration
 *
 * returns: a pointer to the Ndarray.
 */
PyObject *hypercube_dijkstra_LC(PyObject *self, PyObject *args)
{
    PyObject *py_N = NULL; // N as a Python object
    ul N; // hypercube dimension
    float p; // percolation concentration

    if (!PyArg_ParseTuple(args, "Of", &py_N, &p)) goto error;
    N = pyobject_to_ul(py_N);

    // Check for overflow or invalid arguments
    if (PyErr_Occurred() || !check_args(N, 1, p)) goto error;

    // the size of the graph
    ul NH = intpower(2, N); 

    queue *q = setup_queue(NH);
    if (!q) goto error;

    // Each node is initially NOT visited
    bool *visited = malloc(sizeof(bool)*NH);
    if (!visited)
    {
        PyErr_SetString(PyExc_RuntimeError, "Error setting up visited");
        goto error;
    }
    reset_visited(visited, NH);

    // Set all distances to ULONG_MAX except the start site, 0
    ul *distances = malloc(sizeof(ul)*NH);
    if (!distances)
    {
        PyErr_SetString(PyExc_RuntimeError, "Error setting up distances");
        goto error;
    }
    for (ul i = 0; i < NH; i++) distances[i] = ULONG_MAX; 
    
    /* ALGORITHM HERE */

    // label each site by a cluster index, to keep track of the different clusters
    // Set to ULONG_MAX in case of early exit after first cluster (which would result in
    // all sites being labelled with index 0)
    ul *labels = calloc(NH, sizeof(ul));
    for (ul i = 0; i < NH; i++) labels[i] = ULONG_MAX;

    // largest cluster seen so far
    ul largest_cluster_index = 0;
    ul largest_cluster_size = 0;

    // increment this index to uniquely label each cluster
    ul cluster_index = 0;

    // total number of sites grown so far
    ul total_size = 0;

    ul cluster_size;

    for (ul site = 0; site < NH; site++)
    {
        if (!visited[site])
        {
            cluster_size = 0;
            distances[site] = 0;
            dijkstra(q, N, p, site, visited, distances, &cluster_size, cluster_index, labels);

            total_size += cluster_size;
            if (cluster_size > largest_cluster_size)
            {
                largest_cluster_size = cluster_size;
                largest_cluster_index = cluster_index;
            }
            cluster_index++; // update label of cluster

            // early exit condition
            if (largest_cluster_size >= NH - total_size) break;
        }
    }

    // Copy the distances for the largest cluster only into a new array
    ul *finite_distances = malloc(sizeof(ul)*largest_cluster_size);
    if (!finite_distances)
    {
        PyErr_SetString(PyExc_RuntimeError, "Error setting up finite_distances");
        goto error;
    }
    for (ul i = 0, counter = 0; i < NH; i++)
    {
        if (labels[i] == largest_cluster_index)
        {
            finite_distances[counter] = distances[i];
            counter++;
        }
    }

    free(distances);
    free(labels);
    free(q->sites);
    free(q);
    free(visited);

    return CArrayToNumPyArray(finite_distances, largest_cluster_size);

    error:
        if (q)
        {
            free(q->sites);
            free(q);
        }
        if (visited) free(visited);
        if (distances) free(distances);
        if (labels) free(labels);
        return NULL;
}

/*
 * Function:  hypercube_dijkstra
 * --------------------
 * Run Dijkstra's algorithm from the root (0) site of the Hypercube. Return
 * a NumPy array of minimum distances to all the other nodes IN THE CLUSTER. 
 * In other words, the length of the returned array is equal to the size of
 * the cluster containing 0.
 *
 * N: the dimension of the hypercube
 * p: the percolation concentration
 *
 * returns: a pointer to the Ndarray.
 */
PyObject *hypercube_dijkstra(PyObject *self, PyObject *args)
{
    PyObject *py_N = NULL; // N as a Python object
    ul N; // hypercube dimension
    float p; // percolation concentration

    if (!PyArg_ParseTuple(args, "Of", &py_N, &p)) goto error;
    N = pyobject_to_ul(py_N);

    // Check for overflow or invalid arguments
    if (PyErr_Occurred() || !check_args(N, 1, p)) goto error;

    // the size of the graph
    ul NH = intpower(2, N); 

    queue *q = setup_queue(NH);
    if (!q) goto error;

    // Each node is initially NOT visited
    bool *visited = malloc(sizeof(bool)*NH);
    if (!visited)
    {
        PyErr_SetString(PyExc_RuntimeError, "Error setting up visited");
        goto error;
    }
    reset_visited(visited, NH);

    // Set all distances to ULONG_MAX except the start site, 0
    ul *distances = malloc(sizeof(ul)*NH);
    if (!distances)
    {
        PyErr_SetString(PyExc_RuntimeError, "Error setting up distances");
        goto error;
    }
    for (ul i = 0; i < NH; i++) distances[i] = ULONG_MAX; // do this each time?
    

    // ALGORITHM HERE //

    ul number_visited = 0;
    ul start_site = 0;
    distances[start_site] = 0;

    dijkstra(q, N, p, start_site, visited, distances, &number_visited, 0, NULL);
    
    // Copy the distances of the nodes which have been visited
    // to a new array
    ul *finite_distances = malloc(sizeof(ul)*number_visited);
    if (!finite_distances)
    {
        PyErr_SetString(PyExc_RuntimeError, "Error setting up finite_distances");
        goto error;
    }
    for (ul i = 0, counter = 0; i < NH; i++)
    {
        if (visited[i])
        {
            finite_distances[counter] = distances[i];
            counter++;
        }
    }

    free(distances);
    free(q->sites);
    free(q);
    free(visited);

    return CArrayToNumPyArray(finite_distances, number_visited);

    error:
        if (q)
        {
            free(q->sites);
            free(q);
        }
        if (visited) free(visited);
        if (distances) free(distances);
        return NULL;
}

/*
 * Static function:  grow_H_cluster
 * --------------------
 * Helper function used in hypercube_H_LC and hypercube_H_SC. This function runs the DFS algorithm
 * to create a cluster within a Hamiltonian and record its size (through pointers). We update arrays
 * to record which sites have been visited, and also to label each site (in the array labels) with an index
 * (cluster index). If these features are not needed, then NULL can be passed as the labels argument/
 *
 * N: the dimension of the hypercube
 * p: the percolation concentration
 * size: a pointer to an ul in which we put the cluster size
 * s: pointer to an empty stack
 * start_state: hypercube node from which to grow the cluster
 * numpy_array: pointer to a NumPy array representing H, in which we create the cluster
 * visited: an array of bools, marking each site as visited (true) or unvisited (false)
 * error_flag: pointer to an integer used to flag errors
 * cluster_index: ul used to label each site in the cluster we are about to create
 * labels: pointer to an array of uls which we use to keep track of the cluster labels of each site
 *
 */
static void grow_H_cluster(const ul N, const float p, ul *size, stack *s, const ul start_state, PyArrayObject *numpy_array, bool visited[], int *error_flag, ul cluster_index, ul *labels)
{
    ul u, v;
    int connected = 1;
    int disconnected = 0;

    if (s->top != 0)
    {
        PyErr_SetString(PyExc_RuntimeError, "Error in DFS algorithm! Stack not empty.");
        goto error;
    }
    push(s, start_state);

    while (s->top > 0)
    {

        u = pop(s, error_flag);
        if (*error_flag == -1) goto error;

        if (visited[u]) continue;
        visited[u] = true;

        // if we are labelling
        if (labels)
        {
            labels[u] = cluster_index;
        }

        (*size)++;

        for (ul i = 0; i < N; i++)
        {
            // flip the ith bit
            v = u ^ (1UL << i);

            if (!visited[v])
            {
                int *array_ptr = (int *) PyArray_GETPTR2(numpy_array, u, v);
                // ptr to the transpose element
                int *array_ptr_T = (int *) PyArray_GETPTR2(numpy_array, v, u);

                // with probability p, create a link
                if (gsl_rng_uniform(RNG) < p)
                {
                    if (push(s, v) == 1) goto error;
                    *array_ptr = connected;
                    *array_ptr_T = connected; // hermiticity!
                }
                else
                {
                    *array_ptr = disconnected;
                    *array_ptr_T = disconnected; // hermiticity!
                }
            }
        }
    }

    return;

    error:
        if (numpy_array) Py_DECREF(numpy_array);
        if (s)
        {
            free(s->sites);
            free(s);
        }
        if (visited) free(visited);
}

/* Function: hypercube_H_LC
 * ----------------------
 * Construct the Hamiltonian matrix for the largest cluster of the Hypercube.
 * To do this, we must enumerate all of the clusters in a single realisation.
 * Return the matrix and the size of the cluster in a Python Tuple object.
 * 
 * N : the dimension of the hypercube
 * p: the percolation concentration
 * 
 * returns: a tuple (H, size), where H is a NumPy ndarray of the Hamiltonian,
 * and size the size of the cluster. Tuple returned as a pointer to a PyObject.
*/
PyObject *hypercube_H_LC(PyObject *self, PyObject *args)
{

    PyObject *py_N = NULL; // N as a Python object
    ul N; // hypercube dimension
    float p; // percolation concentration

    if (!PyArg_ParseTuple(args, "Of", &py_N, &p)) goto error;

    N = pyobject_to_ul(py_N);
    // Check for overflow
    if (PyErr_Occurred() || !check_args(N, 1, p)) goto error;

    // the size of the graph
    ul NH = intpower(2, N); 

    // Create the hamiltonian in which ALL the clusters will be placed
    npy_intp dimensions[2] = {NH, NH};
    PyArrayObject *hamiltonian = (PyArrayObject *) PyArray_ZEROS(2, dimensions, NPY_INT, 0);
    if (!hamiltonian)
    {
        PyErr_SetString(PyExc_RuntimeError, "Unable to create NumPy array in hypercube_H_SC");
        goto error;
    }

    /* Setup objects needed for the DFS algorithm */
    stack *s = setup_stack(NH);
    if (!s) goto error;

    bool *visited = malloc(sizeof(bool)*NH);
    if (!visited)
    {
        PyErr_SetString(PyExc_RuntimeError, "Error setting up visited");
        goto error;
    }
    reset_visited(visited, NH);

    // label each site by a cluster index, to keep track of the different clusters
    // Set to ULONG_MAX in case of early exit after first cluster (which would result in
    // all sites being labelled with index 0)
    ul *labels = calloc(NH, sizeof(ul));
    for (ul i = 0; i < NH; i++) labels[i] = ULONG_MAX;

    // largest cluster seen so far
    ul largest_cluster_index = 0;
    ul largest_cluster_size = 0;

    // increment this index to uniquely label each cluster
    ul cluster_index = 0;

    // total number of sites grown so far
    ul total_size = 0;

    int error_flag = 0;
    ul cluster_size;

    for (ul site = 0; site < NH; site++)
    {
        // loop over sites
        if (!visited[site])
        {
            cluster_size = 0;
            grow_H_cluster(N, p, &cluster_size, s, site, hamiltonian, visited, &error_flag, cluster_index, labels);
            total_size += cluster_size;
            if (cluster_size > largest_cluster_size)
            {
                largest_cluster_size = cluster_size;
                largest_cluster_index = cluster_index;
            }
            cluster_index++; // update label of cluster

            // early exit condition
            if (largest_cluster_size >= NH - total_size) break;
        }   
    }

    // Create a new Hamiltonian into which to copy only the largest cluster
    PyArrayObject *hamiltonian_LC = (PyArrayObject *) PyArray_ZEROS(2, dimensions, NPY_INT, 0);
    if (!hamiltonian_LC)
    {
        PyErr_SetString(PyExc_RuntimeError, "Unable to create hamiltonian_LC array in hypercube_H_SC");
        goto error;
    }
    // copy the largest cluster into hamiltonian_LC
    for (ul i = 0; i < NH; i++)
    {
        if (labels[i] == largest_cluster_index)
        {
            for (int k = 0; k < NH; k++)
            {
                int *hamiltonian_ptr = (int *) PyArray_GETPTR2(hamiltonian, i, k);
                int *hamiltonian_LC_ptr = (int *) PyArray_GETPTR2(hamiltonian, i, k);
                int *hamiltonian_LC_ptr_T = (int *) PyArray_GETPTR2(hamiltonian_LC, k, i);

                *hamiltonian_LC_ptr = *hamiltonian_ptr;
                *hamiltonian_LC_ptr_T = *hamiltonian_ptr;
            }
        }
        
    }

    // Package the tuple (H, size)
    PyObject *result = PyTuple_New(2);
    if (!result) goto error;
    PyTuple_SetItem(result, 0, (PyObject *)hamiltonian_LC);
    PyTuple_SetItem(result, 1, PyLong_FromUnsignedLong(largest_cluster_size));

    // Free memory and return
    Py_DECREF(hamiltonian);
    free(s->sites);
    free(s);
    free(labels);

    return result;

    error:
        if (hamiltonian) Py_DECREF(hamiltonian);
        if (hamiltonian_LC) Py_DECREF(hamiltonian_LC);
        if (labels) free(labels);
        if (s)
        {
            free(s->sites);
            free(s);
        }
        if (visited) free(visited);
        return NULL;
}

/* Function: hypercube_H_SC
 * ----------------------
 * Construct the Hamiltonian matrix for a single cluster of the Hypercube.
 * Return the matrix and the size of the cluster in a Python Tuple object.
 * 
 * N : the dimension of the hypercube
 * p: the percolation concentration
 * 
 * returns: a tuple (H, size), where H is a NumPy ndarray of the Hamiltonian,
 * and size the size of the cluster. Tuple returned as a pointer to a PyObject.
*/
PyObject *hypercube_H_SC(PyObject *self, PyObject *args)
{

    /* Setup the matrix */

    PyObject *py_N = NULL; // N as a Python object
    ul N; // hypercube dimension
    float p; // percolation concentration

    if (!PyArg_ParseTuple(args, "Of", &py_N, &p)) goto error;

    N = pyobject_to_ul(py_N);
    // Check for overflow
    if (PyErr_Occurred() || !check_args(N, 1, p)) goto error;

    ul NH = intpower(2, N); 

    // Create a new NumPy array of integers of dimension (2**N, 2**N)
    npy_intp dimensions[2] = {NH, NH};
    PyArrayObject *numpy_array = (PyArrayObject *) PyArray_ZEROS(2, dimensions, NPY_INT, 0);
    if (!numpy_array)
    {
        PyErr_SetString(PyExc_RuntimeError, "Unable to create NumPy array in hypercube_H_SC");
        goto error;
    }

    /* Setup objects needed for the DFS algorithm */

    stack *s = setup_stack(NH);
    if (!s) goto error;

    bool *visited = malloc(sizeof(bool)*NH);
    if (!visited)
    {
        PyErr_SetString(PyExc_RuntimeError, "Error setting up visited");
        goto error;
    }
    reset_visited(visited, NH);

    int error_flag = 0;
    ul start_state = 0;
    ul size = 0;
    
    // RUN ALGORITHM HERE
    grow_H_cluster(N, p, &size, s, start_state, numpy_array, visited, &error_flag, 0, NULL);

    /* Clean up and return tuple, or handle errors. */
    PyObject *result = PyTuple_New(2);
    if (!result) goto error;

    PyTuple_SetItem(result, 0, (PyObject *)numpy_array);
    PyTuple_SetItem(result, 1, PyLong_FromUnsignedLong(size));


    free(s->sites);
    free(s);
    free(visited);


    return result;

    error:
        if (numpy_array) Py_DECREF(numpy_array);
        if (s)
        {
            free(s->sites);
            free(s);
        }
        if (visited) free(visited);
        return NULL;
}

/*
 * Function:  H_hypercube
 * --------------------
 * build the Hamiltonian (adjacency matrix) for the hypercube, as a NumPy array.
 *
 * N: the dimension of the hypercube
 * p: the percolation concentration
 *
 * returns: a pointer to the Ndarray (Hamiltonian matrix).
 */
PyObject *hypercube_H(PyObject *self, PyObject *args)
{
    
    PyObject *py_N = NULL; // N as a Python object
    ul N; // hypercube dimension
    float p; // percolation concentration

    if (!PyArg_ParseTuple(args, "Of", &py_N, &p)) goto error;

    N = pyobject_to_ul(py_N);
    // Check for overflow
    if (PyErr_Occurred() || !check_args(N, 1, p)) goto error;

    // the size of the graph
    ul NH = intpower(2, N); 

    // Create a new NumPy array of integers with the same dimensions
    npy_intp dimensions[2] = {NH, NH};
    PyArrayObject *numpy_array = (PyArrayObject *) PyArray_ZEROS(2, dimensions, NPY_INT, 0);
    if (!numpy_array)
    {
        PyErr_SetString(PyExc_RuntimeError, "Unable to create NumPy array in H_hypercube");
        goto error;
    }

    int connected = 1;
    int disconnected = 0;
    // Loop over the matrix elements
    for (ul row = 0; row < NH; row++) 
    {
        for (ul i = 0; i < N; i++)
        {
            // flip the ith bit
            ul col = row ^ (1UL << i);

            int *array_ptr = (int *) PyArray_GETPTR2(numpy_array, row, col);
            // ptr to the transpose element
            int *array_ptr_T = (int *) PyArray_GETPTR2(numpy_array, col, row);

            // with probability p, create a link
            if (gsl_rng_uniform(RNG) < p)
            {
                
                *array_ptr = connected;
                *array_ptr_T = connected; // hermiticity!
            }
            else
            {
                *array_ptr = disconnected;
                *array_ptr_T = disconnected; // hermiticity!
            }
        }
    }

    return numpy_array;

    error:
        if (numpy_array) Py_DECREF(numpy_array);
        return NULL;
}

/*
 * Function:  hypercube_clusters
 * --------------------
 * driver code for running DFS_hypercube many times and returning a NumPy array of cluster sizes.
 * Checks the user input.
 *
 * N: the dimension of the hypercube
 * NR: the Number of Realisations: number of clusters to grow
 * p: the percolation concentration. 0 <= p <= 1
 *
 * returns: a PyObject * (NumPy array) of NR cluster sizes, of type NPY_ULONG (unsigned long)
 */
PyObject *hypercube_clusters(PyObject *self, PyObject *args)
{
    PyObject *py_N = NULL; // N as a Python object
    ul N; // hypercube dimension
    int NR; // Number of Realisations
    float p; // percolation concentration

    if (!PyArg_ParseTuple(args, "Oif", &py_N, &NR, &p)) goto error;

    N = pyobject_to_ul(py_N);
    // Check for overflow
    if (PyErr_Occurred() || !check_args(N, NR, p)) goto error;

    ul NH = intpower(2, N); // the size of the graph

    stack *s = setup_stack(NH);
    if (!s) goto error;

    bool *visited = malloc(sizeof(bool)*NH);
    if (!visited)
    {
        PyErr_SetString(PyExc_RuntimeError, "Error setting up visited");
        goto error;
    }


    ul start_site = 0; 

    // Create a NumPy array of uls
    npy_intp dimensions[1] = {NR};
    PyArrayObject *numpy_array = (PyArrayObject *) PyArray_SimpleNew(1, dimensions, NPY_ULONG);
    if (!numpy_array)
    {
        PyErr_SetString(PyExc_RuntimeError, "Unable to create NumPy array in hypercube_clusters");
        goto error;
    }

    int error_flag = 0;
    // run the DFS algorithm over NR realisations
    npy_intp index[1];
    for (npy_intp i = 0; i < NR; i++)
    {
        // set all nodes to not visited
        reset_visited(visited, NH); 

        // run DFS algorithm, get a cluster size
        index[0] = i;
        ul *array_ptr = (ul *) PyArray_GetPtr(numpy_array, index);
        *array_ptr = DFS_hypercube(s, visited, p, N, start_site, &error_flag);

        if (error_flag == -1) goto error;
    }

    // free heap memory, except cluster sizes
    free(s->sites);
    free(s);
    free(visited);

    return numpy_array;

    error:
        if (s)
        {
            free(s->sites);
            free(s);
        }
        if (visited) free(visited);
        if (numpy_array) Py_DECREF(numpy_array);
        return NULL;

}

/*
 * Function:  DFS_hypercube
 * --------------------
 * grows a percolation cluster on a hypercube with a depth-first search:
 *
 * s: a pointer to a stack, defined in functions.h
 * visited: an array of bools of length NH, to record whether each site has been visited
 * p: the percolation strength. 0 <= p <= 1
 * N: the dimension of the hypercube. (E.g. N=3 is a regular cube.)
 * start_state: which site on the hypercube to grow the cluster from
 * RNG: a random number generator from the gsl library
 * error: a pointer to an error flag, in case something goes wrong
 *
 * returns: the size of the cluster. I.e., the number of sites visited by the DFS algorithm.
 */
ul DFS_hypercube(stack *s, bool visited[], const float p, const ul N, const ul start_state, int *error)
{
    ul size = 0; // cluster size
    ul u, v;

    if (s->top != 0)
    {
        PyErr_SetString(PyExc_RuntimeError, "Error in DFS algorithm! Stack not empty.");
        *error = -1; 
        return 0;
    }
    push(s, start_state);

    while (s->top > 0)
    {

        u = pop(s, error);
        if (*error == -1)
        {
            // error flag has been set, so return.
            return 0;
        }

        if (visited[u])
        {
            continue;
        }
        visited[u] = true;
        size++;

        for (ul i = 0; i < N; i++)
        {
            // flip the ith bit
            v = u ^ (1UL << i);

            if (!visited[v] && (gsl_rng_uniform(RNG) < p))
            {
                if (push(s, v) == 1) 
                { 
                    *error = -1; 
                    return 0;
                }
            }
        }
    }
    return size;
}
