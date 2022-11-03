import os, json
from gensim.models import word2vec
from keras.models import load_model
from keras.preprocessing import sequence
import pickle
import MeCab

class Service:
    news_file_json = {}
    category_file_json = {}
    all_file_json = {}

    def init():
        news_file_list = os.listdir('./model/news/')
        category_file_list = os.listdir('./model/category/')

        for file in news_file_list:
            with open('./model/news/' + file, 'r', encoding='utf8') as f:
                data = json.load(f)
                Service.news_file_json[file.replace('.json', '')] = data

        for file in category_file_list:
            with open('./model/category/' + file, 'r', encoding='utf8') as f:
                data = json.load(f)
                Service.category_file_json[file.replace('.json', '')] = data

        with open('./model/all.json', 'r', encoding='utf8') as f:
            Service.all_file_json = json.load(f)
            
    def keyword(keyword):
        w2v_model = word2vec.Word2Vec.load("./model/word2vec.model")
        w2v = {}
        word_dic={}
        try:
            wordlist = w2v_model.most_similar(positive=[keyword])
            for w in wordlist:
                word_dic[w[0]] = w[1]
            w2v[keyword] = {}
            w2v[keyword]['연관어'] = dict(sorted(word_dic.items(), key=lambda x: x[1], reverse=True))
        except:
            w2v[keyword] = {}
            w2v[keyword]['연관어'] = {}
        w2v[keyword]['검색건수'] = Service.keywordCount(keyword)
        w2v[keyword]['카테고리'] = max(w2v[keyword]['검색건수']['category'], key=w2v[keyword]['검색건수']['category'].get)
        for word in w2v[keyword]['연관어']:
            value = w2v[keyword]['연관어'][word]
            w2v[keyword]['연관어'][word] = {}
            w2v[keyword]['연관어'][word]['연관도'] = value
            w2v[keyword]['연관어'][word]['검색건수'] = Service.keywordCount(word)
            w2v[keyword]['연관어'][word]['카테고리'] = max(w2v[keyword]['연관어'][word]['검색건수']['category'], key=w2v[keyword]['연관어'][word]['검색건수']['category'].get)

        for keyword in word_dic: 
            word_dic = {}
            try:
                wordlist = w2v_model.most_similar(positive=[keyword])
                for w in wordlist:
                    word_dic[w[0]] = w[1]
                w2v[keyword] = {}
                w2v[keyword]['연관어'] = dict(sorted(word_dic.items(), key=lambda x: x[1], reverse=True))
            except:
                w2v[keyword] = {}
                w2v[keyword]['연관어'] = {}
            w2v[keyword]['검색건수'] = Service.keywordCount(keyword)
            w2v[keyword]['카테고리'] = max(w2v[keyword]['검색건수']['category'], key=w2v[keyword]['검색건수']['category'].get)
            for word in w2v[keyword]['연관어']:
                value = w2v[keyword]['연관어'][word]
                w2v[keyword]['연관어'][word] = {}
                w2v[keyword]['연관어'][word]['연관도'] = value
                w2v[keyword]['연관어'][word]['검색건수'] = Service.keywordCount(word)
                w2v[keyword]['연관어'][word]['카테고리'] = max(w2v[keyword]['연관어'][word]['검색건수']['category'], key=w2v[keyword]['연관어'][word]['검색건수']['category'].get)
        return w2v

    def keywordCount(keyword):
        news_file_json = Service.news_file_json
        category_file_json = Service.category_file_json
        all_file_json = Service.all_file_json
        word_cnt = {}

        word_cnt['news'] = {}
        for data in news_file_json:
            if keyword in news_file_json[data]:
                word_cnt['news'][data] = int(news_file_json[data][keyword])
            else:
                word_cnt['news'][data] = 0

        word_cnt['category'] = {}
        for data in category_file_json:
            if keyword in category_file_json[data]:
                word_cnt['category'][data] = int(category_file_json[data][keyword])
            else:
                word_cnt['category'][data] = 0

        word_cnt['total'] = {}
        if keyword in all_file_json:
            word_cnt['total'] = int(all_file_json[keyword])
        else:
            word_cnt['total'] = 0
        return word_cnt

    def text(text):
        token_data = Service.subprocessed(text)
        origin_data = text
        pre = Service.kerasModel(token_data)

        category = ['정치', '경제', '사회', '생활/문화', 'IT/과학', '세계', '오피니언']
        cat = category[pre]
        # tf-idf처리
        tf_idf_data = {}
        w2v = {}
        token_data_array = token_data.split(" ")

        with open('./model/tf_idf_json.json', 'r', encoding='utf8') as f:
            data = json.load(f)

        for token in token_data_array:
            if token in data:
                if token in tf_idf_data: continue
                else : tf_idf_data[token] = '1'

        #이제 이 키값과  word2vec 진행.
        w2v_model = word2vec.Word2Vec.load("./model/word2vec.model")
        for key, value in tf_idf_data.items():
            word_dic={}
            try:
                wordlist = w2v_model.most_similar(positive=[key])
                for w in wordlist:
                    word_dic[w[0]] = w[1]
                w2v[key] = word_dic
            except:
                w2v[key] = word_dic
        return {'origin_data' : origin_data, 'token_data' : token_data, 'pre':str(pre), 'category':cat, 'tf_idf':tf_idf_data, 'w2v':w2v}

    
    def kerasModel(value):
        with open('./model/tokenizer.pickle', 'rb') as handle:
            tok = pickle.load(handle)
        model = load_model('./model/keras_lstm.h5')

        token_stc = value.split(' ')
        sequence_data = tok.texts_to_sequences([token_stc])
        pad_sequence_data = sequence.pad_sequences(sequence_data, maxlen=15)
        pre = model.predict(pad_sequence_data)
        return pre.argmax()

    def subprocessed(value):
        m = MeCab.Tagger('-d C:\mecab\mecab-ko-dic')
        tag_classes = ['NNG', 'NNP','VA', 'VV+EC', 'XSV+EP', 'XSV+EF', 'XSV+EC', 'VV+ETM', 'MAG', 'MAJ', 'NP', 'NNBC', 'IC', 'XR', 'VA+EC']
        result = ''
        value = m.parseToNode(value)
        print(value)
        while value:
            tag = value.feature.split(",")[0]
            word = value.feature.split(",")[3]
            if tag in tag_classes:
                if word == "*": value = value.next
                result += word.strip()+" "
            value = value.next
        return result