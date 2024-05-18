from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from pydantic import BaseModel, validator
from youtube_comments import get_video_comments
from comments_text_cleaning import clean_comments_text
from analysis.topic_modeling import create_topics
from analysis.sentiment_analysis import calculate_sentiments
from db.models import User, Analysis, Comments, Topics
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from db.connection import engine
from fastapi.responses import JSONResponse
from typing import Optional
import multiprocessing

app = FastAPI()
Session = sessionmaker(bind=engine)
session = Session()


class UserSchema(BaseModel):
    username: str
    first_name: str
    last_name: str


@app.post('/user')
def create(user: UserSchema):
    try:
        user = User(username=user.username, first_name=user.first_name, last_name=user.last_name)
        session.add(user)
        session.commit()
        return JSONResponse(content={"message": "User Created Successfully"}, status_code=200)
    except Exception as error:
        raise HTTPException(detail=str(error), status_code=500)


@app.put('/user/{username}')
def update_user(username: str, user: UserSchema):
    try:
        db_user = session.query(User).filter(User.username == username).first()
        if db_user:
            db_user.username = user.username
            db_user.first_name = user.first_name
            db_user.last_name = user.last_name
            session.commit()
            return JSONResponse(content={"message": "User Updated Successfully"}, status_code=200)
        else:
            raise HTTPException(detail="User not found", status_code=404)
    except Exception as error:
        raise HTTPException(detail=str(error), status_code=500)


@app.delete('/user/{username}')
def delete_user(username: str):
    try:
        db_user = session.query(User).filter(User.id == username).first()
        if db_user:
            session.delete(db_user)
            session.commit()
            return JSONResponse(content={"message": "User Deleted Successfully"}, status_code=200)
        else:
            raise HTTPException(detail="User not found", status_code=404)
    except Exception as error:
        raise HTTPException(detail=str(error), status_code=500)


class AnalysisSchema(BaseModel):
    name: str
    username: str


@app.post('/analysis')
def create(analysis: AnalysisSchema):
    try:
        user = session.query(User).filter(User.username == analysis.username).first()
        if not user:
            raise HTTPException(detail="User Not Found", status_code=401)
        analysis = Analysis(name=analysis.name, username=user.username)
        session.add(analysis)
        session.commit()
        return JSONResponse(content={"message": "Analysis Updated Successfully"}, status_code=200)
    except Exception as error:
        raise HTTPException(detail=str(error), status_code=500)


class CommentsSchema(BaseModel):
    url: str
    limit: Optional[int] = 500
    analysis: int

    @validator('url')
    def extract_video_id(cls, url):
        if url:
            return url.split('?')[-1][2:]
        return None


@app.get('/comments')
def fetch_comments(comments: CommentsSchema):
    try:
        analysis_obj = session.query(Analysis).filter(Analysis.id == comments.analysis).first()
        if not analysis_obj:
            raise HTTPException(detail="Analysis Not Found", status_code=401)
        multiprocessing.freeze_support()
        result_queue = multiprocessing.Queue()
        process = multiprocessing.Process(target=get_video_comments, args=(comments.url, analysis_obj.id,
                                                                           comments.limit, result_queue))
        process.start()
        all_comments = result_queue.get()
        data = []
        if all_comments:
            for item in all_comments:
                comment_obj = Comments(**item)
                del item['analysis_id']
                data.append(item)
                session.add(comment_obj)
            session.commit()
            return JSONResponse(content={"comments": data}, status_code=200)
        else:
            return JSONResponse(content={"message": "No Comments Found"}, status_code=200)
    except Exception as error:
        raise HTTPException(detail=str(error), status_code=500)


@app.post('/analyze/{analysis_id}')
def analyze(analysis_id: int):
    raw_comments = get_comments(analysis_id)
    cleaned_comments = clean_comments_text(raw_comments)
    topic_modeling_process = multiprocessing.Process(target=create_topics, args=(cleaned_comments, analysis_id))
    sentiment_analysis_modeling_process = multiprocessing.Process(target=calculate_sentiments(cleaned_comments,
                                                                                              analysis_id),
                                                                  args=(cleaned_comments, analysis_id))
    topic_modeling_process.start()
    sentiment_analysis_modeling_process.start()

    topic_modeling_process.join()
    sentiment_analysis_modeling_process.join()

    return JSONResponse(content={"message": "Analysis Done"}, status_code=200)


def get_comments(analysis_id):
    comments = []
    query = text('select id, comment from Comments where analysis_id = :analysis_id')
    with engine.connect() as connection:
        result = connection.execute(query, {'analysis_id': analysis_id})
        rows = result.fetchall()
    for row in rows:
        comments.append({row[0]: row[1]})
    return comments
