import gensim
import os, glob
import pandas as pd

target_path = 'tokenizer_files/datas'
save_path = 'word2vec_files/datas'

if __name__ == "__main__":
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    list_files = glob.glob(target_path + '/*/*/*.csv')
    tokenized_data = []

    for file in list_files:
        data = pd.read_csv(file)
        x_ = data.iloc[:,1].values
        for data in x_:
            tokenized_data.append(data.split(' '))

    model = gensim.models.Word2Vec(sentences = tokenized_data, size = 100, window = 5, min_count = 5, workers = 4, sg = 0)

    # dir_list = os.listdir(target_path)

    # tokenized_data = []
    # for dir in dir_list:
    #     file_list = os.listdir(target_path + '/' + dir)
    #     for file in file_list:
    #         fname = target_path + '/' + dir + '/' + file
    #         data_ = pd.read_csv(fname)
    #         x_ = data_.iloc[:,1].values
    #         for data in x_:
    #             tokenized_data.append(data.split(' '))
    # model = gensim.models.Word2Vec(sentences = tokenized_data, size = 100, window = 5, min_count = 5, workers = 4, sg = 0)

    model.save(save_path + '/word2vec.model')
    print('word2vec done.')