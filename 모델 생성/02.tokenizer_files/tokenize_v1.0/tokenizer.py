import MeCab
from hbaseUtils import HbaseUtils

class Tokenizer(object) :
    def tokenizer(scan):
        if b'naver_news:collection_content' in scan[1]:
            Tokenizer.insertHbase(scan, b'naver_news:collection_content', 'naver_news:collection_token')
        elif b'naver_blog:collection_content' in scan[1]:
            Tokenizer.insertHbase(scan, b'naver_blog:collection_content', 'naver_blog:collection_token')

    def insertHbase(scan, target_col, save_col) :
        m = MeCab.Tagger('./mecab_dic/mecab-ko-dic')
        with open('./stopwords.txt', 'rt', encoding='UTF8') as f:
            stopwords = f.read().splitlines()
        # tags for tokenizer
        tag_classes = ['VV', 'VA', 'NNG+XS', 'NNG+VC', 'XR', 'NNG', 'NNP','VA', 'VV+EC', 'XSV+EP', 'XSV+EF', 'XSV+EC', 'VV+ETM', 'MAG', 'MAJ', 'NP', 'NNBC', 'IC', 'XR', 'VA+EC']

        value = m.parseToNode(scan[1][target_col].decode('utf-8').strip())

        result = []
        while value:
            tag = value.feature.split(",")[0]
            word = value.feature.split(",")[3]
            if tag in tag_classes:
                if word == "*": value = value.next
                result.append(word)
            value = value.next

        result = [word for word in result if not word in stopwords] # 불용어 제거
        hbase_utils = HbaseUtils(host="192.168.0.144", port=9090, size=5)
        hbase_utils.insert('bigdata_collection_list', scan[0], {save_col : ' '.join(result)})
