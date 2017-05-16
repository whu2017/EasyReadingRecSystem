#!/usr/bin/python
# -*- coding: UTF-8 -*-
import data_preprocessing
import MySQLdb
import sys
import threading
import time
from hier_kmeans_usercf import HieraKmeansUserCF
from most_popular import MostPopular
from MP_by_category_ratio import MPByCategoryRatio
from SimpleXMLRPCServer import SimpleXMLRPCServer


sys.setrecursionlimit(1000000)
mutex = threading.Lock()
USER_CF = None
MP = None
MP_BY_RATIO = None
preprocessed_dataset = None
n_sim_user = 40
n_rec_item = 20
max_iter = 100
n_sample = 1000


class RecommendResult:
    def __init__(self, book_id, name, image_url):
        self.book_id = book_id
        self.name = name
        self.image_url = image_url


class RecommendResultList:
    def __init__(self):
        self.recommend_list = []


def personalized_recommend(user, amount=n_rec_item):
    if len(preprocessed_dataset[user]) < 20:
        rec_list = MP_BY_RATIO.recommend(user, amount)
    else:
        rec_list = USER_CF.recommend(user, n_sim_user, amount)
    ret_list = RecommendResultList()
    for book in rec_list:
        ret_list.recommend_list.append(RecommendResult(book[0], 'test', 'www.test.com'))
    return ret_list


def popular_recommend(user=None, amount=n_rec_item):
    rec_list = MP.recommend(amount, user)
    ret_list = RecommendResultList()
    for book in rec_list:
        ret_list.recommend_list.append(RecommendResult(book[0], 'test', 'www.test.com'))
    return ret_list


def update_data():
    global preprocessed_dataset, MP, MP_BY_RATIO, USER_CF
    dataset = []
    item_category_map = {}
    try:
        conn = MySQLdb.connect(
            host='localhost',
            port=3306,
            user='root',
            passwd='L0veU13112720212',
            db='MovieLens',
        )
        cur = conn.cursor()
        count = cur.execute("select `UserID`, `MovieID`, `Rating` from `Ratings`")
        dataset = cur.fetchmany(count)
        count = cur.execute("select `MovieID`, `Genres` from `Movies`")
        for item, category in cur.fetchmany(count):
            item_category_map[item] = set(category.split('|'))
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

    server = SimpleXMLRPCServer(('localhost', 45213))
    print 'Listening on port 45213...'
    server.register_multicall_functions()
    server.register_function(personalized_recommend, 'personalized_recommend')
    server.register_function(popular_recommend, 'popular_recommend')
    print 'Server is running...'
    server.serve_forever()
