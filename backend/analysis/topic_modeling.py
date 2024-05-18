from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from db.models import Topics
from db.connection import engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()


def create_topics(comments, analysis_id):

    all_comments = []
    vectorizer = TfidfVectorizer(lowercase=True, max_features=500,
                                 max_df=0.8, min_df=5, ngram_range=(1, 3), stop_words="english")

    for comment in comments:
        all_comments.append(list(comment.values())[0])

    vectors = vectorizer.fit_transform(all_comments)
    feature_names = vectorizer.get_feature_names_out()
    dense = vectors.todense()
    denselist = dense.tolist()

    all_keywords = []
    '''
    [[0 1 2 3 ][4 7 7 8]]
    '''
    for comment in denselist:
        x = 0
        keywords = []

        for word in comment:
            if word > 0:
                keywords.append(feature_names[x])
            x = x+1
        all_keywords.append(keywords)

    true_k = 20
    model = KMeans(n_clusters=true_k, init="k-means++", max_iter=500, n_init=1)
    model.fit(vectors)
    order_centroids = model.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names_out()

    save_topics(terms, analysis_id)


def save_topics(topics, analysis_id):
    for topic in topics:
        topic_obj = Topics(topic=topic, analysis_id=analysis_id)
        session.add(topic_obj)
    session.commit()
