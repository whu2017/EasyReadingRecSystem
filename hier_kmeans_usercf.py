#!/usr/bin/python
# -*- coding: UTF-8 -*-
import math
import kmeans_clustering
import hierarchical_clustering
import random
import numpy as np
from operator import itemgetter


class HieraKmeansUserCF:
    def __init__(self, preprocessed_dataset, item_category_map, n_hier_sample=1500, max_iter=np.inf):
        self.__dataset = preprocessed_dataset
        self.__item_category_map = item_category_map
        self.__n_hier_sample = n_hier_sample
        self.__max_iter = max_iter

        self.__user_sim_matrix = None
        self.__user_cluster_map = {}
        self.__user_list = preprocessed_dataset.keys()

    def __create_user_item_matrix(self):
        category_set = set()
        for categories in self.__item_category_map.values():
            category_set |= categories
        category_list = list(category_set)

        n_user = len(self.__user_list)
        n_category = len(category_list)
        user_category_matrix = [[0 for col in range(n_category)] for row in range(n_user)]
        for i, user in enumerate(self.__user_list):
            user_category_count = {}
            for item in self.__dataset[user]:
                for category in self.__item_category_map[item]:
                    user_category_count.setdefault(category, 0)
                    user_category_count[category] += 1

            for j in range(n_category):
                if category_list[j] in user_category_count:
                    user_category_matrix[i][j] = user_category_count[category_list[j]]
        return np.mat(user_category_matrix)

    def calc_user_sim(self):
        user_category_matrix = self.__create_user_item_matrix()

        if len(self.__user_list) > self.__n_hier_sample:
            sample_matrix = random.sample(user_category_matrix.tolist(), self.__n_hier_sample)
        else:
            sample_matrix = random.sample(user_category_matrix.tolist(), len(self.__user_list))
        k, centers = hierarchical_clustering.find_best_k_by_hiera_clustering(np.mat(sample_matrix))

        self.__user_sim_matrix = [{} for x in range(k)]
        centroids, cluster_assment = kmeans_clustering.kmeans(
            user_category_matrix, k, max_iter=self.__max_iter, init_cent=np.mat(centers))

        for i, user in enumerate(self.__user_list):
            self.__user_cluster_map[user] = int(cluster_assment[i, 0])

        clustered_datasets = [{} for x in range(k)]
        for user, cluster_index in self.__user_cluster_map.items():
            clustered_datasets[cluster_index][user] = self.__dataset[user]

        for i in range(k):
            item_users = {}
            for user, items in clustered_datasets[i].items():
                for item in items:
                    item_users.setdefault(item, set())
                    item_users[item].add(user)

            for item, users in item_users.items():
                for u in users:
                    self.__user_sim_matrix[i].setdefault(u, {})
                    for v in users:
                        if u == v:
                            continue
                        self.__user_sim_matrix[i][u].setdefault(v, 0)
                        self.__user_sim_matrix[i][u][v] += 1  # / math.log(1 + len(users))

            for u, related_users in self.__user_sim_matrix[i].items():
                for v, count in related_users.items():
                    self.__user_sim_matrix[i][u][v] = count / math.sqrt(
                        len(self.__dataset[u]) * len(self.__dataset[v]))

    def recommend(self, user, n_sim_users, n_rec_items):
        rank = {}
        interacted_items = self.__dataset[user]

        cluster_index = self.__user_cluster_map[user]
        for v, sim_factor in sorted(self.__user_sim_matrix[cluster_index][user].items(), key=itemgetter(1),
                                    reverse=True)[:n_sim_users]:
            for item in self.__dataset[v]:
                if item in interacted_items:
                    continue
                rank.setdefault(item, 0)
                rank[item] += sim_factor * self.__dataset[v][item]

        return sorted(rank.items(), key=itemgetter(1), reverse=True)[:n_rec_items]
