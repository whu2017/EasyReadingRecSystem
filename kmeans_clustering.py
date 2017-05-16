#!/usr/bin/python
# -*- coding: UTF-8 -*-
import numpy as np


def __cosine_sim(vector1, vector2):
    return float(vector1 * vector2.T) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))


def __rand_cent(matrix, k):
    n_samples, dim = matrix.shape
    centroids = np.mat(np.zeros((k, dim)))
    for i in range(k):
        index = int(np.random.uniform(0, n_samples))
        centroids[i, :] = matrix[index, :]
    return centroids


def kmeans(matrix, k, max_iter=np.inf, dist_meas=__cosine_sim, create_cent=__rand_cent, init_cent=None):
    n_sample = matrix.shape[0]
    # first column stores which cluster this sample belongs to,
    # second column stores the error between this sample and its centroid
    cluster_assment = np.mat(np.zeros((n_sample, 2)))
    cluster_changed = True

    # step 1: init centroids
    if init_cent is not None:
        centroids = init_cent
    else:
        centroids = create_cent(matrix, k)

    iterator = 0
    while cluster_changed and iterator < max_iter:
        cluster_changed = False
        # for each sample
        for i in xrange(n_sample):
            min_dist = np.inf
            min_index = -1
            # for each centroid
            # step 2: find the closest centroid
            for j in range(k):
                dist = dist_meas(centroids[j, :], matrix[i, :])
                if dist < min_dist:
                    min_dist = dist
                    min_index = j

            # step 3: update its cluster
            if cluster_assment[i, 0] != min_index:
                cluster_changed = True
            cluster_assment[i, :] = min_index, min_dist ** 2

        # step 4: update centroids
        for j in range(k):
            vectors_in_cluster = matrix[np.nonzero(cluster_assment[:, 0].A == j)[0]]
            centroids[j, :] = np.mean(vectors_in_cluster, axis=0)
        iterator += 1

    return centroids, cluster_assment
