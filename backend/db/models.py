from sqlalchemy import Column, Integer, String, ForeignKey, Index
from sqlalchemy.orm import relationship
from .connection import Base, engine


class User(Base):
    __tablename__ = 'user'

    username = Column(String, primary_key=True, unique=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    analysis = relationship('Analysis', back_populates='user', cascade='all, delete-orphan')


class Analysis(Base):
    __tablename__ = 'analysis'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    username = Column(String, ForeignKey('user.username'), nullable=False)
    comments = relationship('Comments', back_populates='analysis', cascade='all, delete-orphan')
    topics = relationship('Topics', back_populates='analysis', cascade='all, delete-orphan')
    user = relationship('User', back_populates='analysis')
    sentiments = relationship('Sentiments', back_populates='analysis', cascade='all, delete-orphan')


class Comments(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    comment = Column(String)
    author = Column(String)
    # sentiment = Column(String, nullable=True)
    analysis_id = Column(Integer, ForeignKey('analysis.id'))
    analysis = relationship('Analysis', back_populates='comments')
    sentiments = relationship('Sentiments', back_populates='comments', cascade='all, delete-orphan')


class Topics(Base):
    __tablename__ = 'topics'

    id = Column(Integer, primary_key=True)
    topic = Column(String)
    analysis_id = Column(Integer, ForeignKey('analysis.id'))
    analysis = relationship('Analysis', back_populates='topics')


class Sentiments(Base):
    __tablename__ = 'sentiments'

    id = Column(Integer, primary_key=True)
    comment_id = Column(Integer, ForeignKey('comments.id'))
    analysis_id = Column(Integer, ForeignKey('analysis.id'))
    sentiments = Column(String, nullable=True)
    analysis = relationship('Analysis', back_populates='sentiments')
    comments = relationship('Comments', back_populates='sentiments')


# index_name = 'index_analysis_id'
# existing_indexes = engine.execute(f"SELECT indexname FROM pg_indexes WHERE indexname = '{index_name}'").fetchall()
#
# if not existing_indexes:
#     index_analysis_id = Index('index_analysis_id', Comments.analysis_id)
#     index_analysis_id.create(engine)

Base.metadata.create_all(engine)
