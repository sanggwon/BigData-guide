from genericpath import isfile
import os, numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import json
import datetime

target_path = 'tokenizer_files/datas/'
save_path = 'tfidf_files/datas/'

def save_json(df, dir, file):
    x = df.iloc[:, 1].values
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

        # 저장 경로
        news_dir = save_path + 'news'
        if not os.path.exists(news_dir):
            os.mkdir(news_dir)
        model_dir = save_path + dir
        if not os.path.exists(model_dir):
            os.mkdir(model_dir)
        with open(save_path + dir + '/' + file.replace('csv', 'json'), 'w+', encoding='UTF-8') as f:
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

def get_week_number(sourceDate):
    weekNumber = sourceDate.isocalendar()
    return weekNumber

if __name__ == "__main__":
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    dir_list = os.listdir(target_path)
    category = ['정치', '경제', '사회', '생활', 'IT', '세계', '오피니언', '연예', '스포츠', '기타']

    all_data = []
    # week_list = {}
    news_data = {}
    for dir in dir_list:
        dir2_list = os.listdir(target_path + '/' + dir)
        for dir2 in dir2_list:
            file_list = os.listdir(target_path + '/' + dir + '/' + dir2)
            # week = get_week_number(datetime.datetime(int(dir2[:4]), int(dir2[4:6]), int(dir2[6:])))
            # if str(week[0]) + str(week[1]) not in week_list:
            #     week_list[str(week[0]) + str(week[1])] = {}
            for file in file_list:
                fname = target_path + '/' + dir + '/' + dir2 + '/'+ file
                data = pd.read_csv(fname)
                data = pd.DataFrame({'날짜':data.iloc[:,0], '내용':data.iloc[:,1], '구분':data.iloc[:,2]})
                news = file.replace('.csv', '')
                # 언론사별로 구분
                if news not in news_data:
                    news_data[news] = []
                else :
                    news_data[news].append(data)
                # if news not in week_list[str(week[0]) + str(week[1])]:
                #     week_list[str(week[0]) + str(week[1])][news] = []
                # week_list[str(week[0]) + str(week[1])][news].append(data)
                # 전체 데이터 저장
                all_data.append(data)

    # 전체 데이터
    data = pd.concat(all_data, axis=0, ignore_index=True, sort = False)
    a_df = data.sample(frac=1).reset_index(drop=True)
    save_json(a_df, '', 'all.csv')

    # for week in week_list:
    #     # 언론사별
    #     for news in week_list[week]:
    #         # 언론사 데이터 전체 union
    #         data = pd.concat(week_list[week][news], axis=0, ignore_index=True, sort = False)
    #         df = data.sample(frac=1).reset_index(drop=True)
    #         save_json(df, 'news/' + week, news + '.csv')

    # 언론사별
    for news in news_data:
        data = pd.concat(news_data[news], axis=0, ignore_index=True, sort = False)
        df = data.sample(frac=1).reset_index(drop=True)
        save_json(df, 'news/', news + '.csv')

    category_len = []
    # 카테고리별
    for i in range(len(category)):
        save_json(a_df[a_df['구분']==i], 'category', category[i] + '.csv')
        category_len.append({category[i] : len(a_df[a_df['구분']==i])})

    with open(save_path + 'count.json', 'w+', encoding='utf-8-sig') as f :
        f.write(str(category_len))
        f.truncate()
        f.close()