from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.exceptions import HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from comments.youtube_comments import get_video_comments
from mongodb_config import db
import multiprocessing

app = FastAPI()


SM_PLATFORMS = {'youtube': get_video_comments,
                'instagram': None}


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


@app.post('/comments')
def fetch_comments(platform: str, _id: str):
    multiprocessing.freeze_support()
    result_queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=SM_PLATFORMS[platform], args=(_id, result_queue))
    process.start()
    if result_queue.get():
        return {"comments": result_queue.get()}
