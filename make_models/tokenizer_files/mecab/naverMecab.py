import MeCab, csv, os
import pandas as pd
import multiprocessing
from functools import partial
from tqdm import tqdm
from datetime import datetime
from datetime import timedelta

m = MeCab.Tagger('./mecab_dic/mecab-ko-dic')
target_path = os.getcwd() + '/crawling_files/datas/'
save_path = os.getcwd() + '/tokenizer_files/datas/'

def week_no(y, m, d):
    def _ymd_to_datetime(y, m, d):
        s = f'{y:04d}-{m:02d}-{d:02d}'
        return datetime.strptime(s, '%Y-%m-%d')
    target_day = _ymd_to_datetime(y, m, d)
    firstday = target_day.replace(day=1)
    while firstday.weekday() != 0:
        firstday += timedelta(days=1)
    if target_day < firstday:
        return str(y) + '-' + str(m) + '-' + str(0)
    return str(y) + '-' + str(m) + '-' + str((target_day - firstday).days // 7 + 1)

#불용어 리스트
def stopwords():
    currentpath = os.getcwd()
    with open(currentpath + '\\stopwords.txt', 'rt', encoding='UTF8') as f:
        stopwords = f.read().splitlines()
    return stopwords

def file_to_ids(file, dir, dir2, week):
    category_, date_, content_ = ['날짜'], ['내용'], ['구분']
    #tags for tokenizer
    tag_classes = ['VV', 'VA', 'NNG+XS', 'NNG+VC', 'XR', 'NNG', 'NNP','VA', 'VV+EC', 'XSV+EP', 'XSV+EF', 'XSV+EC', 'VV+ETM', 'MAG', 'MAJ', 'NP', 'NNBC', 'IC', 'XR', 'VA+EC']
    #데이터 읽어오고.
    fname = target_path + dir + '/' + dir2 + '/' +file
    data = pd.read_csv(fname)
    #각각 분류
    title = data.iloc[:,0].values
    date = data.iloc[:, 1].values
    content = data.iloc[:, 2].values
    category = data.iloc[:, 3].values

    for cnt, value in tqdm(enumerate(title)):
        result = []
        value = m.parseToNode(str(title[cnt]).strip() + str(content[cnt]).strip())
        while value:
            tag = value.feature.split(",")[0]
            word = value.feature.split(",")[3]
            if tag in tag_classes:
                if word == "*": value = value.next
                result.append(word)
            value = value.next

        result = [word for word in result if not word in stopwords()] # 불용어 제거
        content_.append(' '.join(result))
        date_.append(date[cnt])
        category_.append(category[cnt])
    
    if not os.path.exists(save_path + week):
        os.mkdir(save_path + week)
    if not os.path.exists(save_path + week + '/' + dir2):
        os.mkdir(save_path + week + '/' + dir2)

    with open(save_path + week + '/' + dir2 + '/' + file, 'w+', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        for cnt, i in enumerate(content_):
            date__ = date_[cnt]
            content__ = content_[cnt]
            if content__ != '' :
                category__ = category_[cnt]
                writer.writerow((date__, content__, category__))
        f.truncate()

def start(file_list, dir, dir2, week) :
    try :
        multiprocessing.freeze_support()
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        pool.map(partial(file_to_ids, dir=dir, dir2=dir2, week=week), file_list)
        pool.close()
        pool.join()
    except:
        pass   

if __name__ == "__main__":
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    
    dir_list = os.listdir(target_path)
    weeks = {}
    for dir in dir_list:
        dir2_list = os.listdir(target_path + '/' + dir)
        for dir2 in dir2_list:
            dt = datetime.strptime(dir2, '%Y%m%d')
            week = week_no(dt.year, dt.month, dt.day)
            if week not in weeks :
                weeks[week] = [] 
            weeks[week].append(dir2)

    for week in weeks :
        for day in weeks[week]:
            file_list = os.listdir(target_path + '/' + day[:6] + '/' + day)
            start(file_list, day[:6], day, week)

    print('mecab done.')
    