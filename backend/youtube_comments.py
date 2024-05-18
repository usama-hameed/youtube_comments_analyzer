from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


DEVELOPER_KEY = 'AIzaSyC54aGdtQKFWZ57-RlRBfAZebXMt4m7n9o'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)


def get_video_comments(video_id, analysis_id, limit, result_queue):

    try:
        results = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            textFormat='plainText',
            maxResults=100
        ).execute()
        end = False
        comments = []
        while results:
            for item in results['items']:
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                author = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
                comments.append({'author': author, 'comment': comment, 'analysis_id': analysis_id})

                if len(comments) > limit:
                    result_queue.put(comments)
                    end = True
                    break
            if end:
                break
            if 'nextPageToken' in results:
                results = youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    textFormat='plainText',
                    maxResults=100,
                    pageToken=results['nextPageToken']
                ).execute()
            else:
                break

        result_queue.put(comments)

    except HttpError as e:
        print(f'An HTTP error {e.resp.status} occurred: {e.content}')
