import os
from keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer
from db.connection import engine
from db.models import Sentiments
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()


def calculate_sentiments(comments, analysis_id):

    all_comments = []
    for comment in comments:
        all_comments.append(list(comment.values())[0])

    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, "sentiment_analysis_model.h5")

    model = load_model(model_path,  compile=False)
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(all_comments)
    sequences = tokenizer.texts_to_sequences(all_comments)

    max_len = 34
    padded_sequences = pad_sequences(sequences, maxlen=max_len)

    comment_sentiments = dict()
    all_comments_sentiments = []
    predictions = []
    for padded_seq in padded_sequences:
        padded_seq = padded_seq.reshape(1, -1)
        prediction = model.predict(padded_seq)
        predictions.append(prediction)

    for comment, prediction in zip(comments, predictions):
        if prediction > 0.1:
            _id = list(comment.keys())[0]
            comment_sentiments['comment_id'] = _id
            comment_sentiments['analysis_id'] = analysis_id
            comment_sentiments['sentiments'] = 'positive'
        else:
            _id = list(comment.keys())[0]
            comment_sentiments['comment_id'] = _id
            comment_sentiments['analysis_id'] = analysis_id
            comment_sentiments['sentiments'] = 'negative'
        all_comments_sentiments.append(comment_sentiments)

    save_sentiments(all_comments_sentiments)


def save_sentiments(sentiments):
    for sentiment in sentiments:
        sentiment_obj = Sentiments(**sentiment)
        session.add(sentiment_obj)
    session.commit()
