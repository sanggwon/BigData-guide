import os, numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import json

def start(datas) :
    news_x, blog_x = [], []
    for data in datas:
        if b'naver_news:collection_token' in data[1]:
            token = str(data[1][b'naver_news:collection_token'].decode('utf-8')).replace('b\'', '').replace('\'','')
            news_x.append(token)
        elif b'naver_blog:collection_token' in data[1]:
            token = str(data[1][b'naver_blog:collection_token'].decode('utf-8')).replace('b\'', '').replace('\'','')
            blog_x.append(token)

    makeJson(news_x, 'news')
    makeJson(blog_x, 'blog')

def makeJson(x, gbn):
    word_count_dic = {}
    for doc in x:
        # 단어 COUNT
        word_count(doc, word_count_dic)
    try:
        vector = TfidfVectorizer(min_df=1, analyzer='word', token_pattern=r'\w{1,}')
        #특성 이름을 구한다.
        sp_matrix = vector.fit_transform(x)
        feature_names = np.array(vector.get_feature_names())
        max_value = sp_matrix.max(axis=0).toarray().ravel()
        sorted_by_tfidf = max_value.argsort()

        print("tfidf가 가장 낮은 특성 20 개 : \n", feature_names[sorted_by_tfidf[:20]])
        print("tfidf가 가장 높은 특성 20 개 : \n ", feature_names[sorted_by_tfidf[:-20:-1]])

        m =  feature_names[sorted_by_tfidf[::-1]]

        tf_idf_json = {}
        for words in m:
            if words not in tf_idf_json:
                if words in word_count_dic:
                    tf_idf_json[words] = str(word_count_dic[words])

        print(len(tf_idf_json))

        if not os.path.exists('./datas/' + gbn):
            os.mkdir('./datas/' + gbn)

        with open('./datas/'+ gbn +'/tf-idf.json', 'w+', encoding='UTF-8') as f:
            json.dump(tf_idf_json, f, ensure_ascii=False)
    except:
        pass

def word_count(doc, word_count_dic):
    word_list = doc.split()
    for word in word_list:
        if word in word_count_dic:
            word_count_dic[word] += 1
        else:
            word_count_dic[word] = 1