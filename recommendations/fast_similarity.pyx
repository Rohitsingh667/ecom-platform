# cython: language_level=3, boundscheck=False, wraparound=False, nonecheck=False
import numpy as np
cimport numpy as cnp
cimport cython
from libc.math cimport sqrt, fabs

ctypedef cnp.float64_t DTYPE_t

@cython.boundscheck(False)
@cython.wraparound(False)
def cosine_similarity_optimized(cnp.ndarray[DTYPE_t, ndim=2] X, cnp.ndarray[DTYPE_t, ndim=2] Y=None):
    cdef int n_samples_X = X.shape[0]
    cdef int n_features = X.shape[1]
    cdef int n_samples_Y
    cdef cnp.ndarray[DTYPE_t, ndim=2] similarities
    cdef cnp.ndarray[DTYPE_t, ndim=1] norms_X, norms_Y
    cdef DTYPE_t dot_product, norm_x, norm_y
    cdef int i, j, k
    cdef bint same_matrix = False
    
    if Y is None:
        Y = X
        same_matrix = True
        n_samples_Y = n_samples_X
    else:
        n_samples_Y = Y.shape[0]
    
    norms_X = np.zeros(n_samples_X, dtype=np.float64)
    norms_Y = np.zeros(n_samples_Y, dtype=np.float64)
    
    for i in range(n_samples_X):
        norm_x = 0.0
        for k in range(n_features):
            norm_x += X[i, k] * X[i, k]
        norms_X[i] = sqrt(norm_x)
    
    if not same_matrix:
        for j in range(n_samples_Y):
            norm_y = 0.0
            for k in range(n_features):
                norm_y += Y[j, k] * Y[j, k]
            norms_Y[j] = sqrt(norm_y)
    else:
        norms_Y = norms_X
    
    similarities = np.zeros((n_samples_X, n_samples_Y), dtype=np.float64)
    
    for i in range(n_samples_X):
        for j in range(n_samples_Y):
            if same_matrix and j < i:
                similarities[i, j] = similarities[j, i]
                continue
                
            dot_product = 0.0
            for k in range(n_features):
                dot_product += X[i, k] * Y[j, k]
            
            if norms_X[i] != 0.0 and norms_Y[j] != 0.0:
                similarities[i, j] = dot_product / (norms_X[i] * norms_Y[j])
            else:
                similarities[i, j] = 0.0
    
    return similarities

@cython.boundscheck(False)
@cython.wraparound(False)
def euclidean_distance_optimized(cnp.ndarray[DTYPE_t, ndim=2] X, cnp.ndarray[DTYPE_t, ndim=2] Y=None):
    cdef int n_samples_X = X.shape[0]
    cdef int n_features = X.shape[1]
    cdef int n_samples_Y
    cdef cnp.ndarray[DTYPE_t, ndim=2] distances
    cdef DTYPE_t diff, dist
    cdef int i, j, k
    cdef bint same_matrix = False
    
    if Y is None:
        Y = X
        same_matrix = True
        n_samples_Y = n_samples_X
    else:
        n_samples_Y = Y.shape[0]
    
    distances = np.zeros((n_samples_X, n_samples_Y), dtype=np.float64)
    
    for i in range(n_samples_X):
        for j in range(n_samples_Y):
            if same_matrix and j < i:
                distances[i, j] = distances[j, i]
                continue
                
            dist = 0.0
            for k in range(n_features):
                diff = X[i, k] - Y[j, k]
                dist += diff * diff
            
            distances[i, j] = sqrt(dist)
    
    return distances

@cython.boundscheck(False)
@cython.wraparound(False)
def pearson_correlation_optimized(cnp.ndarray[DTYPE_t, ndim=2] X):
    cdef int n_samples = X.shape[0]
    cdef int n_features = X.shape[1]
    cdef cnp.ndarray[DTYPE_t, ndim=2] correlations
    cdef cnp.ndarray[DTYPE_t, ndim=1] means, stds
    cdef DTYPE_t mean_i, mean_j, std_i, std_j, covariance
    cdef int i, j, k
    
    means = np.zeros(n_samples, dtype=np.float64)
    for i in range(n_samples):
        for k in range(n_features):
            means[i] += X[i, k]
        means[i] /= n_features
    
    stds = np.zeros(n_samples, dtype=np.float64)
    for i in range(n_samples):
        for k in range(n_features):
            diff = X[i, k] - means[i]
            stds[i] += diff * diff
        stds[i] = sqrt(stds[i] / (n_features - 1))
    
    correlations = np.zeros((n_samples, n_samples), dtype=np.float64)
    
    for i in range(n_samples):
        for j in range(i, n_samples):
            if i == j:
                correlations[i, j] = 1.0
                continue
                
            covariance = 0.0
            for k in range(n_features):
                covariance += (X[i, k] - means[i]) * (X[j, k] - means[j])
            covariance /= (n_features - 1)
            
            if stds[i] != 0.0 and stds[j] != 0.0:
                correlations[i, j] = covariance / (stds[i] * stds[j])
                correlations[j, i] = correlations[i, j]
            else:
                correlations[i, j] = 0.0
                correlations[j, i] = 0.0
    
    return correlations

@cython.boundscheck(False)
@cython.wraparound(False)
def top_k_similarities(cnp.ndarray[DTYPE_t, ndim=2] similarity_matrix, int k):
    cdef int n_items = similarity_matrix.shape[0]
    cdef cnp.ndarray[cnp.int32_t, ndim=2] top_indices
    cdef cnp.ndarray[DTYPE_t, ndim=2] top_values
    cdef cnp.ndarray[cnp.int32_t, ndim=1] sorted_indices
    cdef int i, j, actual_k
    
    actual_k = min(k, n_items - 1)
    
    top_indices = np.zeros((n_items, actual_k), dtype=np.int32)
    top_values = np.zeros((n_items, actual_k), dtype=np.float64)
    
    for i in range(n_items):
        row = similarity_matrix[i, :]
        sorted_indices = np.argsort(row)[::-1]
        
        j = 0
        count = 0
        while count < actual_k and j < n_items:
            if sorted_indices[j] != i:
                top_indices[i, count] = sorted_indices[j]
                top_values[i, count] = row[sorted_indices[j]]
                count += 1
            j += 1
    
    return top_indices, top_values
