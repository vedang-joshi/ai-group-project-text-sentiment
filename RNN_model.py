from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Dense, Embedding, concatenate, Dropout, concatenate
from tensorflow.keras.layers import Bidirectional
from sklearn.metrics import accuracy_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from TextToTensor import TextToTensor
from embeddings_matrix import *

class RNN():
    """
    A recurrent neural network for semantic analysis
    """

    def __init__(self, embedding_matrix, embedding_dim, max_len, X_additional=None):
        
        inp1 = Input(shape=(max_len,))
        x = Embedding(embedding_matrix.shape[0], embedding_dim, weights=[embedding_matrix])(inp1)
        x = Bidirectional(LSTM(256, return_sequences=True))(x)
        x = Bidirectional(LSTM(150))(x)
        x = Dense(128, activation="relu")(x)
        x = Dropout(0.1)(x)
        x = Dense(64, activation="relu")(x)
        x = Dense(1, activation="sigmoid")(x)    
        model = Model(inputs=inp1, outputs=x)

        model.compile(loss = 'binary_crossentropy', optimizer = 'adam')
        self.model = model



class Pipeline:
    """
    A class for the machine learning pipeline
    """
    def __init__(self, X_train: list, Y_train: list, embed_path: str, embed_dim: int,
        X_test=[], Y_test=[],epochs=3,batch_size=256):

        # Preprocecing the text
        #X_train = [clean_text(text, stop_words=stop_words) for text in X_train]
        Y_train = np.asarray(Y_train)
        Y_test = np.asarray(Y_test)
        
        # Tokenizing the text
        tokenizer = Tokenizer()
        tokenizer.fit_on_texts(X_train)

        # Creating the embedding matrix
        embedding = Embeddings(embed_path, embed_dim)
        embedding_matrix = embedding.create_embedding_matrix(tokenizer, len(tokenizer.word_counts))

        # Creating the padded input for the deep learning model
        max_len = np.max([len(text.split()) for text in X_train])
        TextToTensor_instance = TextToTensor(tokenizer=tokenizer, max_len=max_len)
        X_train = TextToTensor_instance.string_to_tensor(X_train)

        # Creating the model
        rnn = RNN(embedding_matrix=embedding_matrix, embedding_dim=embed_dim, max_len=max_len)
        rnn.model.fit(X_train,Y_train, batch_size=batch_size, epochs=epochs)

        self.model = rnn.model

        # If X_test is provided we make predictions with the created model
        if len(X_test)>0:
            #X_test = [clean_text(text) for text in X_test]
            X_test = TextToTensor_instance.string_to_tensor(X_test)
            yhat = [x[0] for x in rnn.model.predict(X_test).tolist()]
            
            self.yhat = yhat

            # If true labels are provided we calculate the accuracy of the model
            if len(Y_test)>0:
                self.acc = accuracy_score(Y_test, [1 if x > 0.5 else 0 for x in yhat])
                #self.f1 = f1_score(Y_test, [1 if x > 0.5 else 0 for x in yhat])