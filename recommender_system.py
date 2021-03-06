#!/usr/bin/python
# -*- coding: UTF-8 -*-
import data_preprocessing
import MySQLdb
import sys
import threading
import time
import random
from hier_kmeans_usercf import HieraKmeansUserCF
from most_popular import MostPopular
from MP_by_category_ratio import MPByCategoryRatio
from SimpleXMLRPCServer import SimpleXMLRPCServer


sys.setrecursionlimit(1000000)
mutex = threading.Lock()
USER_CF = None
MP = None
MP_BY_RATIO = None
PREPROCESSED_DATASET = None
ALL_BOOK_NOT_BEEN_READ = None
n_sim_user = 40
n_rec_item = 20
max_iter = 100
n_sample = 1000


def personalized_recommend(user, amount=n_rec_item):
    if user not in PREPROCESSED_DATASET:
        rec_list = MP.recommend(amount, None)
    elif len(PREPROCESSED_DATASET[user]) < 20:
        rec_list = MP_BY_RATIO.recommend(user, amount)
    else:
        rec_list = USER_CF.recommend(user, n_sim_user, amount)
    ret_list = []
    for book in rec_list:
        ret_list.append(book[0])
    if len(ret_list) < n_rec_item:
        n = n_rec_item - len(ret_list)
        if n > len(ALL_BOOK_NOT_BEEN_READ):
            ret_list += ALL_BOOK_NOT_BEEN_READ
        else:
            ret_list += random.sample(ALL_BOOK_NOT_BEEN_READ, n)
    return ret_list


def popular_recommend(user=None, amount=n_rec_item):
    rec_list = MP.recommend(amount, user)
    ret_list = []
    for book in rec_list:
        ret_list.append(book[0])
    if len(ret_list) < n_rec_item:
        n = n_rec_item - len(ret_list)
        if n > len(ALL_BOOK_NOT_BEEN_READ):
            ret_list += ALL_BOOK_NOT_BEEN_READ
        else:
            ret_list += random.sample(ALL_BOOK_NOT_BEEN_READ, n)
    return ret_list


def update_data():
    global PREPROCESSED_DATASET,MP, MP_BY_RATIO, USER_CF, ALL_BOOK_NOT_BEEN_READ
    dataset = set()
    item_category_map = {}
    try:
        conn = MySQLdb.connect(
            host='oott.me',
            port=3306,
            user='master',
            passwd='whu2017test-master',
            db='whu2017_master',
        )
        cur = conn.cursor()
        count = cur.execute("select `user_id`, `book_id` from `read_record`")
        dataset |= set(cur.fetchmany(count))
        count = cur.execute("select `user_id`, `book_id` from `buy_record`")
        dataset |= set(cur.fetchmany(count))
        dataset = list(dataset)
        count = cur.execute("select `id`, `category_id` from `book`")
        for item, category in cur.fetchmany(count):
            # item_category_map[item] = set(category.split('|'))
            item_category_map[item] = set()
            item_category_map[item].add(category)
        count = cur.execute("select `id` from `book` where `id` not in("
                            "select distinct `book_id` from `read_record`) "
                            "and `id` not in(select distinct `book_id` from `buy_record`)")
        result = cur.fetchmany(count)
        all_book_not_been_read = []
        for row in result:
            all_book_not_been_read.append(row[0])
        cur.close()
        conn.commit()
        conn.close()
    except Exception, e:
        print Exception, ':', e

    preprocessed_dataset = data_preprocessing.preprocess_data(dataset)
    mp = MostPopular(preprocessed_dataset)
    mp.calc_item_popularity()
    mp_by_ratio = MPByCategoryRatio(preprocessed_dataset, item_category_map)
    mp_by_ratio.calc_item_popularity()
    user_cf = HieraKmeansUserCF(preprocessed_dataset, item_category_map, n_sample, max_iter)
    user_cf.calc_user_sim()

    mutex.acquire()
    PREPROCESSED_DATASET = preprocessed_dataset
    ALL_BOOK_NOT_BEEN_READ = all_book_not_been_read
    MP = mp
    MP_BY_RATIO = mp_by_ratio
    USER_CF = user_cf
    mutex.release()
    print 'update complete'


def update_data_by_interval(seconds):
    while True:
        time.sleep(seconds)
        t = threading.Thread(target=update_data)
        t.setDaemon(True)
        t.start()


if __name__ == "__main__":
    update_data()
    t = threading.Thread(target=update_data_by_interval, args=(3600,))
    t.setDaemon(True)
    t.start()

    server = SimpleXMLRPCServer(('localhost', 45213), allow_none=True)
    print 'Listening on port 45213...'
    server.register_multicall_functions()
    server.register_function(personalized_recommend, 'personalized_recommend')
    server.register_function(popular_recommend, 'popular_recommend')
    print 'Server is running...'
    server.serve_forever()
