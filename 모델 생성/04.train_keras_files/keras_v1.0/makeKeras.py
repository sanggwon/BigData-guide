import tensorflow as tf
import pickle
from keras.preprocessing.text import Tokenizer
from keras.preprocessing import sequence
from keras.models import Sequential
from keras.layers import Dense, Embedding, LSTM, Dropout, GlobalMaxPool1D
from keras.utils import np_utils
from keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.model_selection import train_test_split
from hdfs import InsecureClient

def start(datas) :
    config = tf.compat.v1.ConfigProto()
    config.gpu_options.allow_growth = True
    session = tf.compat.v1.Session(config=config)
    
    news_x_data, news_y_data = [], []
    blog_x_data, blog_y_data = [], []

    for data in datas:
        if b'naver_news:collection_token' in data[1]:
            token = str(data[1][b'naver_news:collection_token'].decode('utf-8')).replace('b\'', '').replace('\'','')
            category = str(data[1][b'naver_news:collection_category'].decode('utf-8')).replace('b\'', '').replace('\'','')
            news_x_data.append(token)
            news_y_data.append(category)
        elif b'naver_blog:collection_token' in data[1]:
            token = str(data[1][b'naver_blog:collection_token'].decode('utf-8')).replace('b\'', '').replace('\'','')
            category = str(data[1][b'naver_blog:collection_category'].decode('utf-8')).replace('b\'', '').replace('\'','')
            blog_x_data.append(token)
            blog_y_data.append(category)

    makeModel(news_x_data, news_y_data, 'news')
    makeModel(blog_x_data, blog_y_data, 'blog')

def makeModel(x_data, y_data, gbn) :
    set_y_data = list(set(y_data))
    nb_classes = len(set(y_data))

    y_data = [list(set(set_y_data)).index(data) for data in y_data]
    y_data = np_utils.to_categorical(y_data, nb_classes)

    max_word = 7000
    max_len = 500

    tok = Tokenizer(num_words = max_word)
    tok.fit_on_texts(x_data)
    print(gbn + '==> ' + str(len(tok.word_index)))

    sequences = tok.texts_to_sequences(x_data)
    print(gbn + '==> ' + str(len(sequences[0])))
    print(sequences[0])

    sequences_matrix = sequence.pad_sequences(sequences, maxlen=max_len)
    print(gbn + '==> ' + str(len(sequences_matrix)))

    x_train, x_test, y_train, y_test = train_test_split(sequences_matrix, y_data, test_size=0.2)
    print(x_train.shape)

    file_name = gbn + '/keras_lstm.h5'

    with tf.device('/device:GPU:0'):
        model = Sequential()
        
        model.add(Embedding(max_word, 64, input_length=max_len))
        model.add(LSTM(60, return_sequences=True))
        model.add(GlobalMaxPool1D())
        model.add(Dropout(0.2))
        model.add(Dense(50, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(nb_classes, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        checkpoint = ModelCheckpoint(filepath='./datas/' + file_name, monitor="val_loss", verbose=1, save_best_only=True)
        early_stopping = EarlyStopping(monitor='val_loss', patience=3)

    model.summary()

    hist = model.fit(x_train, y_train, batch_size=500, epochs=20, validation_split=0.2, callbacks=[checkpoint, early_stopping])
    print(gbn + '==> ' + "정확도 : %.4f" % (model.evaluate(x_test, y_test)[1]))

    # saving
    with open('./datas/'+ gbn +'/tokenizer.pickle', 'wb') as handle:
        pickle.dump(tok, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # HDFS의 URL을 지정합니다.
    HDFS_URL = '''http://192.168.0.144:9870'''

    # HDFS 클라이언트와 연결합니다.
    client = InsecureClient(HDFS_URL, user='daeho')

    # HDFS의 디렉토리를 생성합니다.
    client.makedirs('data')
    client.makedirs('data/' + gbn)

    # 파일을 업로드합니다.
    client.upload('data/'+ gbn +'/keras_lstm.h5', './datas/'+ gbn +'/keras_lstm.h5', overwrite=True)

    # 파일을 업로드합니다.
    client.upload('data/'+ gbn +'/tokenizer.pickle', './datas/'+ gbn +'/tokenizer.pickle', overwrite=True)
