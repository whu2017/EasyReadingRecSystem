# -*- coding:utf-8 -*-
import numpy as np


class Node:
    def __init__(self, cent, left=None, right=None, distance=0.0, id=None):
        self.left = left
        self.right = right
        self.cent = cent
        self.id = id
        self.distance = distance


def __euclidean_dist(vector1, vector2):
    return np.linalg.norm(vector1 - vector2)


def __get_leaves_deep_first(node):
    if node.left is None and node.right is None:
        return [node.id]
    return __get_leaves_deep_first(node.left) + __get_leaves_deep_first(node.right)


def __get_node_sum_and_count(node):
    if node.left is None and node.right is None:
        return node.cent, 1
    sum_l, count_l = __get_node_sum_and_count(node.left)
    sum_r, count_r = __get_node_sum_and_count(node.right)
    return sum_l + sum_r, count_l + count_r


def __get_new_cent(node1, node2):
    sum1, count1 = __get_node_sum_and_count(node1)
    sum2, count2 = __get_node_sum_and_count(node2)
    sum = sum1 + sum2
    return (sum1 + sum2) / float(count1 + count2)


def find_best_k_by_hiera_clustering(dataset):
    cluster_centers = [Node(cent=dataset[i, :], id=i) for i in range(dataset.shape[0])]
    distances = {}
    min_dist_pair = None
    current_clustered = -1
    best_k = 0
    best_cluster_centers = None
    last_cluster_centers = None
    last_see = None
    max_see_growth = None
    while len(cluster_centers) > 1:
        min_dist = np.inf
        n_cluster = len(cluster_centers)
        for i in range(n_cluster - 1):
            for j in range(i + 1, n_cluster):
                if (cluster_centers[i].id, cluster_centers[j].id) not in distances:
                    distances[(cluster_centers[i].id, cluster_centers[j].id)] = __euclidean_dist(
                        cluster_centers[i].cent, cluster_centers[j].cent)
                d = distances[(cluster_centers[i].id, cluster_centers[j].id)]
                if d < min_dist:
                    min_dist = d
                    min_dist_pair = (i, j)

        cent1, cent2 = min_dist_pair
        new_cent = __get_new_cent(cluster_centers[cent1], cluster_centers[cent2])
        new_node = Node(new_cent, left=cluster_centers[cent1], right=cluster_centers[cent2], distance=min_dist,
                      id=current_clustered)
        current_clustered -= 1
        tmp1 = cluster_centers[cent1]
        tmp2 = cluster_centers[cent2]
        cluster_centers.remove(tmp1)
        cluster_centers.remove(tmp2)
        cluster_centers.append(new_node)

        if len(cluster_centers) == 16:
            cluster_assment = [__get_leaves_deep_first(cluster_centers[i]) for i in range(len(cluster_centers))]
            see_sum = 0
            for i in range(len(cluster_centers)):
                for j in cluster_assment[i]:
                    see_sum += __euclidean_dist(cluster_centers[i].cent, dataset[j]) ** 2
            last_see = see_sum

        if len(cluster_centers) == 15:
            cluster_assment = [__get_leaves_deep_first(cluster_centers[i]) for i in range(len(cluster_centers))]
            see_sum = 0
            for i in range(len(cluster_centers)):
                for j in cluster_assment[i]:
                    see_sum += __euclidean_dist(cluster_centers[i].cent, dataset[j]) ** 2
            max_see_growth = see_sum - last_see
            last_cluster_centers = cluster_centers[:]
            last_see = see_sum

        if len(cluster_centers) < 15:
            cluster_assment = [__get_leaves_deep_first(cluster_centers[i]) for i in range(len(cluster_centers))]
            see_sum = 0
            for i in range(len(cluster_centers)):
                for j in cluster_assment[i]:
                    see_sum += __euclidean_dist(cluster_centers[i].cent, dataset[j]) ** 2
            see_growth = see_sum - last_see
            if see_growth > max_see_growth * 1.3:
                max_see_growth = see_growth
                best_cluster_centers = last_cluster_centers
                best_k = len(best_cluster_centers)
            last_cluster_centers = cluster_centers[:]
            last_see = see_sum

    return best_k, [best_cluster_centers[i].cent.tolist()[0] for i in range(best_k)]
