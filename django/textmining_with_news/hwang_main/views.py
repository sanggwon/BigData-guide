import json
from django.shortcuts import render, redirect
from django.views import View
from gensim.models import word2vec
from hwang_main.subprocess.subprocessed import Subprocessed
from hwang_main.subprocess.keras_model import KerasModel

# Create your views here.
class HwangMain(View):
    
    def get(self, request, *args, **kwargs):
        template_name = 'main/index.html'
        return render(request, template_name)

    def post(self, request, *args, **kwargs):
        value = request.POST.get('python_value')
        token_data = Subprocessed.execution(value)
        origin_data = value
        pre = KerasModel.execution(token_data)

        category = ['정치', '경제', '사회', '생활/문화', 'IT/과학', '세계', '오피니언']
        cat = category[pre]
        # tf-idf처리
        tf_idf_data = {}
        w2v = {}
        token_data_array = token_data.split(" ")

        with open('./hwang_main/subprocess/tf_idf_json.json', 'r', encoding='utf8') as f:
            data = json.load(f)

        for token in token_data_array:
            if token in data:
                if token in tf_idf_data: continue
                else : tf_idf_data[token] = '1'
        with open('./hwang_main/subprocess/tf_idf_json_test.json', 'w') as f:
            json.dump(tf_idf_data, f)
        #이제 이 키값과  word2vec 진행.
        w2v_model = word2vec.Word2Vec.load("./hwang_main/subprocess/word2vec.model")
        for key, value in tf_idf_data.items():
            word_dic={}
            try:
                wordlist = w2v_model.most_similar(positive=[key])
                for w in wordlist:
                    word_dic[w[0]] = w[1]
                w2v[key] = word_dic
            except:
                w2v[key] = word_dic
        template_name = 'main/after_input_value.html'
        return render(request, template_name, {'origin_data' : origin_data, 'token_data' : token_data, 'pre':pre, 'category':cat, 'tf_idf':tf_idf_data, 'w2v':w2v})
