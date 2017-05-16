#!/usr/bin/python
# -*- coding: UTF-8 -*-
from operator import itemgetter


class MPByCategoryRatio:
    def __init__(self, dataset, item_category_map):
        self.__dataset = dataset
        self.__item_category_map = item_category_map

        self.item_popularity = {}
        self.n_items = 0
        self.__sorted_item_popularity_top200 = []
        self.__category_sorted_item_popularity_top100 = {}

    def calc_item_popularity(self):
        for item_ratings in self.__dataset.values():
            for item in item_ratings.keys():
                self.item_popularity.setdefault(item, 0)
                self.item_popularity[item] += 1

        self.n_items = len(self.item_popularity)
        self.__sorted_item_popularity_top200 = sorted(
            self.item_popularity.items(), key=itemgetter(1), reverse=True)[:200]

    def recommend(self, user, n_rec_items):
        rank = {}
        interacted_items = self.__dataset[user].keys()

        user_category_count = {}
        for item in self.__dataset[user]:
            for category in self.__item_category_map[item]:
                user_category_count.setdefault(category, 0)
                user_category_count[category] += 1
        count_sum = sum(user_category_count.values())
        user_category_ratio = {}
        for category, count in user_category_count.items():
            user_category_ratio[category] = float(count) / count_sum

        for item, popularity in self.__sorted_item_popularity_top200:
            if item in interacted_items:
                continue
            rank[item] = 0
            for category in self.__item_category_map[item]:
                if category not in user_category_ratio:
                    continue
                rank[item] += popularity * user_category_ratio[category]

        return sorted(rank.items(), key=itemgetter(1), reverse=True)[:n_rec_items]
