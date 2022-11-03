import os
import pandas as pd

target_path = 'tokenizer_files/datas'
save_path = 'text_split_files/datas'

# n개씩 분할
def list_split(lst, n):
    return [lst[i:i+n] for i in range(0, len(lst), n)]
    
if __name__ == "__main__":
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    dir_list = os.listdir(target_path)

    # 7개 분류
    tokenized_data = [[] for _ in range(7)]
    for dir in dir_list:
        file_list = os.listdir(target_path + '/' + dir)
        for file in file_list:
            fname = target_path + '/' + dir + '/' + file
            data_ = pd.read_csv(fname)
            x_ = data_.iloc[:,1].values
            y_ = data_.iloc[:,2].values
            for i in range(1,len(x_)):
                tokenized_data[y_[i]].extend(x_[i].split(' '))

    # 전체 토큰 리스트 반복문
    for i in range(0, len(tokenized_data)):
        # 500개씩 나눔
        list_splited = list_split(tokenized_data[i], 500)
        # 텍스트 파일 저장
        for j in range(0, len(list_splited)):
            file_path = save_path + '/' + str(i)
            if not os.path.exists(file_path):
                os.mkdir(file_path)
            with open(file_path + '/news_' + str(j) + '.txt', 'w+', encoding='utf-8-sig', newline='') as f:
                f.write(' '.join(list_splited[j]))
    print('textSplit done.')