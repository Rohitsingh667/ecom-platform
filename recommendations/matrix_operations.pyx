# cython: language_level=3, boundscheck=False, wraparound=False, nonecheck=False
import numpy as np
cimport numpy as cnp
cimport cython
from libc.math cimport sqrt, fabs

ctypedef cnp.float64_t DTYPE_t

@cython.boundscheck(False)
@cython.wraparound(False)
def matrix_factorization_sgd(cnp.ndarray[DTYPE_t, ndim=2] R, int K, double alpha, double beta, int iterations):
    cdef int n_users = R.shape[0]
    cdef int n_items = R.shape[1]
    cdef cnp.ndarray[DTYPE_t, ndim=2] P = np.random.normal(scale=1./K, size=(n_users, K))
    cdef cnp.ndarray[DTYPE_t, ndim=2] Q = np.random.normal(scale=1./K, size=(n_items, K))
    cdef cnp.ndarray[DTYPE_t, ndim=2] Q_T = Q.T
    
    cdef double error, prediction
    cdef double p_ik_old, q_kj_old
    cdef int i, j, k, iteration
    cdef double rating
    
    for iteration in range(iterations):
        for i in range(n_users):
            for j in range(n_items):
                rating = R[i, j]
                if rating > 0:
                    prediction = 0.0
                    for k in range(K):
                        prediction += P[i, k] * Q[j, k]
                    
                    error = rating - prediction
                    
                    for k in range(K):
                        p_ik_old = P[i, k]
                        q_kj_old = Q[j, k]
                        
                        P[i, k] += alpha * (error * q_kj_old - beta * p_ik_old)
                        Q[j, k] += alpha * (error * p_ik_old - beta * q_kj_old)
    
    return P, Q

@cython.boundscheck(False)
@cython.wraparound(False)
def predict_ratings(cnp.ndarray[DTYPE_t, ndim=2] P, cnp.ndarray[DTYPE_t, ndim=2] Q):
    cdef int n_users = P.shape[0]
    cdef int n_items = Q.shape[0]
    cdef int K = P.shape[1]
    cdef cnp.ndarray[DTYPE_t, ndim=2] predictions = np.zeros((n_users, n_items), dtype=np.float64)
    cdef int i, j, k
    cdef double prediction
    
    for i in range(n_users):
        for j in range(n_items):
            prediction = 0.0
            for k in range(K):
                prediction += P[i, k] * Q[j, k]
            predictions[i, j] = prediction
    
    return predictions

@cython.boundscheck(False)
@cython.wraparound(False)
def weighted_average_ratings(cnp.ndarray[DTYPE_t, ndim=1] ratings, 
                           cnp.ndarray[DTYPE_t, ndim=1] similarities, 
                           cnp.ndarray[cnp.int32_t, ndim=1] indices,
                           int top_k):
    cdef double weighted_sum = 0.0
    cdef double similarity_sum = 0.0
    cdef int i
    cdef double sim, rating
    cdef int actual_k = min(top_k, len(ratings))
    
    for i in range(actual_k):
        sim = similarities[i]
        rating = ratings[i]
        
        if sim > 0 and rating > 0:
            weighted_sum += sim * rating
            similarity_sum += fabs(sim)
    
    if similarity_sum > 0:
        return weighted_sum / similarity_sum
    else:
        return 0.0

@cython.boundscheck(False)
@cython.wraparound(False)
def calculate_rmse(cnp.ndarray[DTYPE_t, ndim=2] true_ratings, 
                   cnp.ndarray[DTYPE_t, ndim=2] predicted_ratings,
                   cnp.ndarray[cnp.uint8_t, ndim=2] mask):
    cdef int n_users = true_ratings.shape[0]
    cdef int n_items = true_ratings.shape[1]
    cdef double mse = 0.0
    cdef int count = 0
    cdef double error
    cdef int i, j
    
    for i in range(n_users):
        for j in range(n_items):
            if mask[i, j]:
                error = true_ratings[i, j] - predicted_ratings[i, j]
                mse += error * error
                count += 1
    
    if count > 0:
        return sqrt(mse / count)
    else:
        return 0.0

@cython.boundscheck(False)
@cython.wraparound(False)
def generate_negative_samples(cnp.ndarray[cnp.int32_t, ndim=1] user_items,
                             int n_items,
                             int n_negative,
                             cnp.ndarray[cnp.int32_t, ndim=1] random_items):
    cdef cnp.ndarray[cnp.int32_t, ndim=1] negative_samples = np.zeros(n_negative, dtype=np.int32)
    cdef cnp.ndarray[cnp.uint8_t, ndim=1] user_item_set = np.zeros(n_items, dtype=np.uint8)
    cdef int i, j, item_id
    cdef int samples_found = 0
    
    for i in range(len(user_items)):
        if user_items[i] < n_items:
            user_item_set[user_items[i]] = 1
    
    for i in range(len(random_items)):
        if samples_found >= n_negative:
            break
            
        item_id = random_items[i]
        if item_id < n_items and not user_item_set[item_id]:
            negative_samples[samples_found] = item_id
            samples_found += 1
    
    return negative_samples[:samples_found]

@cython.boundscheck(False)
@cython.wraparound(False)
def sparse_matrix_multiply(cnp.ndarray[DTYPE_t, ndim=1] data,
                          cnp.ndarray[cnp.int32_t, ndim=1] indices,
                          cnp.ndarray[cnp.int32_t, ndim=1] indptr,
                          cnp.ndarray[DTYPE_t, ndim=2] dense_matrix):
    cdef int n_rows = len(indptr) - 1
    cdef int n_cols = dense_matrix.shape[1]
    cdef cnp.ndarray[DTYPE_t, ndim=2] result = np.zeros((n_rows, n_cols), dtype=np.float64)
    
    cdef int i, j, k, col_idx
    cdef int start, end
    cdef double value
    
    for i in range(n_rows):
        start = indptr[i]
        end = indptr[i + 1]
        
        for j in range(start, end):
            col_idx = indices[j]
            value = data[j]
            
            for k in range(n_cols):
                result[i, k] += value * dense_matrix[col_idx, k]
    
    return result
