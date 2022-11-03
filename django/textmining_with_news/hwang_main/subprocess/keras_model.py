from keras.models import load_model
from keras.preprocessing import sequence
from keras.preprocessing.text import Tokenizer
from hwang_main.subprocess.subprocessed import Subprocessed
import nltk
from Common import Common
import pickle

class KerasModel():
    def execution(value):
        with open('./hwang_main/subprocess/model/tokenizer.pickle', 'rb') as handle:
            tok = pickle.load(handle)
        model = load_model('./hwang_main/subprocess/model/keras_lstm.h5')

        token_stc = value.split(' ')
        sequence_data = tok.texts_to_sequences([token_stc])
        pad_sequence_data = sequence.pad_sequences(sequence_data, maxlen=15)
        pre = model.predict(pad_sequence_data)
        return pre.argmax()
