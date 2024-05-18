import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split
from keras.models import save_model

import pickle
import pandas as pd

dataset = pd.read_csv("Tweets.csv", sep=',')

dataset['text'] = dataset['text'].astype(str)

dataset = dataset.loc[(dataset['sentiment'] == 'positive') | (dataset['sentiment'] == 'negative')]

dataset.loc[dataset['sentiment'] == 'positive', 'sentiment'] = 1
dataset.loc[dataset['sentiment'] == 'negative', 'sentiment'] = 0

dataset['sentiment'] = dataset['sentiment'].astype(int)

# dataset["text"] = dataset["text"].astype(str)
# dataset["text"] = dataset['text'].apply(lambda x: " ".join([y.lemma_ for y in nlp(x) if not y.is_stop]))
# dataset['text'] = dataset['text'].apply(lambda x: x.lower())

train_data, test_data = train_test_split(dataset, test_size=0.2, random_state=42)

# Tokenization for training data
tokenizer = Tokenizer()
tokenizer.fit_on_texts(train_data['text'])
train_sequences = tokenizer.texts_to_sequences(train_data['text'])
maxlen = max([len(x) for x in train_sequences])
padded_train_sequences = pad_sequences(train_sequences, maxlen=maxlen, padding='post')

# Tokenization for testing data
test_sequences = tokenizer.texts_to_sequences(test_data['text'])
padded_test_sequences = pad_sequences(test_sequences, maxlen=maxlen, padding='post')

train_labels = np.array(train_data['sentiment'])
test_labels = np.array(test_data['sentiment'])

embedding_dim = 16
vocab_size = len(tokenizer.word_index) + 1

model = Sequential([
    Embedding(vocab_size, embedding_dim, input_length=maxlen),
    LSTM(64, dropout=0.2, recurrent_dropout=0.2),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

model.fit(padded_train_sequences, train_labels, epochs=10, batch_size=32)

# Evaluate the model on the test set
loss, accuracy = model.evaluate(padded_test_sequences, test_labels)
print("Test Accuracy:", accuracy)  # 85%

save_model(model, "sentiment_analysis_model.h5")


# # prediction = model.predict("This video is very bad")
# # print(prediction)
# pickle_out = open("sentiment_analysis_model.pkl", "wb")
# pickle.dump(model, pickle_out)
# pickle_out.close()
