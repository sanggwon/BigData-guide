import os

path = os.path.dirname(os.path.realpath(__file__)) + '\datas'
if not os.path.exists(path):
    os.mkdir(path)

mecab_words = []
target_path = 'word_dic_files/datas'
save_path = 'tokenizer_files/mecab/mecab_dic/user-dic'
with open(target_path + '/word_dic.txt', encoding='utf-8-sig') as f:
    words = f.readlines()
    for word in words:
        word = word.strip()
        word = word+",,,0,NNP,*,F,"+word+",*,*,*,*"
        mecab_words.append(word)
with open(save_path + '/user.csv', 'w+', encoding='utf-8') as f:
    for word in mecab_words:
        f.write(word+"\n")