import gensim
import os
from hdfs import InsecureClient

def start(datas) :
    news_token_data, blog_token_data = [], []
    for data in datas:
        if b'naver_news:collection_token' in data[1]:
            token = str(data[1][b'naver_news:collection_token'].decode('utf-8')).replace('b\'', '').replace('\'','')
            news_token_data.append(token.split(' '))
        elif b'naver_blog:collection_token' in data[1]:
            token = str(data[1][b'naver_blog:collection_token'].decode('utf-8')).replace('b\'', '').replace('\'','')
            blog_token_data.append(token.split(' '))
    
    makeModel(news_token_data, 'news')
    makeModel(blog_token_data, 'blog')

def makeModel(data, gbn) :
    if not os.path.exists('./datas/' + gbn):
        os.mkdir('./datas/' + gbn)
        
    model = gensim.models.Word2Vec(sentences = data, size = 100, window = 5, min_count = 5, workers = 4, sg = 0)
    model.save('./datas/'+ gbn +'/word2vec.model')

    # HDFS의 URL을 지정합니다.
    HDFS_URL = '''http://192.168.0.144:9870'''

    # HDFS 클라이언트와 연결합니다.
    client = InsecureClient(HDFS_URL, user='daeho')

    # HDFS의 디렉토리를 생성합니다.
    client.makedirs('data')
    client.makedirs('data/' + gbn)

    # 파일을 업로드합니다.
    client.upload('data/'+ gbn +'/word2vec.model', './datas/'+ gbn +'/word2vec.model', overwrite=True)
