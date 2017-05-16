#!/usr/bin/python
# -*- coding: UTF-8 -*-
import numpy as np


def preprocess_data(original_dataset):
    preprocessed_dataset = {}
    for user, item, rating in original_dataset:
        preprocessed_dataset.setdefault(user, {})
        preprocessed_dataset[user][item] = rating
    return preprocessed_dataset


def get_user_list(preprocessed_dataset):
    return preprocessed_dataset.keys()


def get_item_list(preprocessed_dataset):
    item_set = set()
    for items in preprocessed_dataset.values().keys():
        item_set |= set(items)
    return list(item_set)


def create_user_item_matrix(preprocessed_dataset, user_list, item_list):
    n_user = len(user_list)
    n_item = len(item_list)
    user_item_matrix = [[0 for col in range(n_item)] for row in range(n_user)]
    for i, user in enumerate(user_list):
        for j in range(n_item):
            if item_list[j] in preprocessed_dataset[user]:
                user_item_matrix[i][j] = preprocessed_dataset[user][item_list[j]]
    return np.mat(user_item_matrix)
