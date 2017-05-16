#!/usr/bin/python
# -*- coding: UTF-8 -*-
from operator import itemgetter


class MostPopular:
    def __init__(self, dataset):
        self.__dataset = dataset

        self.__item_popularity = {}
        self.__n_items = 0
        self.__sorted_item_popularity = []

    def calc_item_popularity(self):
        for item_ratings in self.__dataset.values():
            for item in item_ratings.keys():
                self.__item_popularity.setdefault(item, 0)
                self.__item_popularity[item] += 1

        self.__n_items = len(self.__item_popularity)
        self.__sorted_item_popularity = sorted(self.__item_popularity.items(), key=itemgetter(1), reverse=True)

    def recommend(self, n_rec_items, user=None):
        rec_items = []
        if user is None:
            interacted_items = []
        else:
            interacted_items = self.__dataset[user].keys()

        for item, popularity in self.__sorted_item_popularity:
            if item in interacted_items:
                continue
            rec_items.append([item, popularity])
            if len(rec_items) >= n_rec_items:
                break
        return rec_items
