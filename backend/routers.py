from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.exceptions import HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from youtube_comments import get_video_comments
from mongodb_config import db
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
        comments = dict()
        multiprocessing.freeze_support()
        result_queue = multiprocessing.Queue()
        process = multiprocessing.Process(target=get_video_comments, args=(_id, result_queue))
        process.start()
        if result_queue.get():
            comments['comments'] = result_queue.get()
            return comments
    except Exception as error:
        return Response({'error': str(error)})


@app.post('/analyze')
def analyze():
    pass
