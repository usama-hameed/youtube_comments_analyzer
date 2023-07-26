from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.exceptions import HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from youtube_comments import get_video_comments
from comments_text_cleaning import clean_comments_text
from mongodb_config import db, collection
import multiprocessing

app = FastAPI()


class Analysis(BaseModel):
    name: str
    owner: str


@app.post('/analysis')
def create(project: Analysis):
    try:
        db.objects.create(name=project.name, owner=project.owner)
        return Response({'message': 'Analysis Created'}, status_code=200)
    except Exception as error:
        raise HTTPException(detail=str(error), status_code=400)


@app.get('/comments')
def fetch_comments(_id: str):
    try:
        multiprocessing.freeze_support()
        result_queue = multiprocessing.Queue()
        process = multiprocessing.Process(target=get_video_comments, args=(_id, result_queue))
        process.start()
        comments = result_queue.get()
        if comments:
            collection.insert_one({'source_id': _id, 'comments': result_queue.get()})
            return {'source_id': _id, 'comments': comments}
    except Exception as error:
        raise HTTPException(detail=str(error), status_code=500)


@app.get('/analyze')
def analyze(source_id: str):
    raw_comments = collection.find_one({'source_id': source_id}).get('comments')
    print(raw_comments)
    cleaned_comments = clean_comments_text(raw_comments)
    return {'cleaned_comments': cleaned_comments}
