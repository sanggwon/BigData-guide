import os, glob
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from keras.preprocessing.text import Tokenizer
from keras.preprocessing import sequence
from keras.models import Sequential
from keras.layers import Dense, Embedding, LSTM, Dropout, GlobalMaxPool1D
from keras.utils import np_utils
from keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.model_selection import train_test_split
import pickle
import numpy as np

target_path = 'tokenizer_files/datas'
save_path = 'train_keras_files/datas'

if not os.path.exists(save_path):
    os.mkdir(save_path)

config = tf.compat.v1.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.compat.v1.Session(config=config)

list_files = glob.glob(target_path + '/*/*/*.csv')

allData = []
# dir_list = os.listdir(target_path)
# for dir in dir_list:
#     file_list = os.listdir(target_path + '/' + dir)
#     for file in list_files:
#         data = pd.read_csv(file)
#         data = pd.DataFrame({'날짜':data.iloc[:,0], '내용':data.iloc[:,1], '구분':data.iloc[:,2]})
#         allData.append(data)

for file in list_files:
    data = pd.read_csv(file)
    data = pd.DataFrame({'날짜':data.iloc[:,0], '내용':data.iloc[:,1], '구분':data.iloc[:,2]})
    allData.append(data)


data = pd.concat(allData, axis=0, ignore_index=True, sort = False)
df = data.sample(frac=1).reset_index(drop=True)

print(len(df.iloc[:, 0]))

x_data = df.iloc[:, 1].values
y_data = df.iloc[:, 2].values

nb_classes = len(set(y_data))

y_data = np_utils.to_categorical(y_data, nb_classes)

max_word = 7000
max_len = 500

tok = Tokenizer(num_words = max_word)
tok.fit_on_texts(x_data)
print(len(tok.word_index))

sequences = tok.texts_to_sequences(x_data)
print(len(sequences[0]))
print(sequences[0])

sequences_matrix = sequence.pad_sequences(sequences, maxlen=max_len)
print(len(sequences_matrix))

x_train, x_test, y_train, y_test = train_test_split(sequences_matrix, y_data, test_size=0.2)
print(x_train.shape)

model_dir = 'train_keras_files/datas'
if not os.path.exists(model_dir):
    os.mkdir(model_dir)
model_path = model_dir + "/keras_lstm.h5"

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
    checkpoint = ModelCheckpoint(filepath=model_path, monitor="val_loss", verbose=1, save_best_only=True)
    early_stopping = EarlyStopping(monitor='val_loss', patience=3)

model.summary()

hist = model.fit(x_train, y_train, batch_size=500, epochs=20, validation_split=0.2, callbacks=[checkpoint, early_stopping])
print("정확도 : %.4f" % (model.evaluate(x_test, y_test)[1]))

y_vloss = hist.history['val_loss']
y_loss = hist.history['loss']

x_len = np.arange(len(y_loss))

plt.plot(x_len, y_vloss, marker='.', c='red', label='val_set_loss')
plt.plot(x_len, y_loss, marker='.', c='blue', label='train_set_loss')
plt.legend()
plt.xlabel('epochs')
plt.ylabel('loss')
plt.grid()
plt.show()

y_vacc = hist.history['val_accuracy']
y_acc = hist.history['accuracy']

x_len = np.arange(len(y_loss))

plt.plot(x_len, y_vacc, marker='.', c='red', label='val_set_acc')
plt.plot(x_len, y_acc, marker='.', c='blue', label='train_set_acc')
plt.legend()
plt.xlabel('epochs')
plt.ylabel('acc')
plt.grid()
plt.show()

# saving
with open('train_keras_files/datas/tokenizer.pickle', 'wb') as handle:
    pickle.dump(tok, handle, protocol=pickle.HIGHEST_PROTOCOL)