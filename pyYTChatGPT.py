import os
import requests
import openai
from youtube_transcript_api import YouTubeTranscriptApi

def search_youtube(query):
    api_key = os.getenv('YOUTUBE_API_KEY')
    url = 'https://www.googleapis.com/youtube/v3/search'

    params = {
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'key': api_key,
        'videoDuration': 'medium',
        'maxResults': 3,
        'publishedAfter': '2022-01-01T00:00:00Z'
    }

    response = requests.get(url, params=params)
    data = response.json()

    videos = []
    for item in data['items']:
        video = {
            'title': item['snippet']['title'],
            'description': item['snippet']['description'],
            'video_id': item['id']['videoId']
        }
        videos.append(video)

    return videos


def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        full_text = ''
        for x in transcript:
            full_text += x['text'] + ' '
        return True, full_text
    except Exception:
        return False, f'\nUnable to obtain transcript for video - {video_id}'
    
def ask_gpt3(prompt, model):
    try:
        completions = openai.Completion.create(
            engine=model,
            prompt=prompt,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=.5,
        )
        return True, completions.choices[0].text
    except Exception:
        return False, 'Transcript for the following video is too long - {video_id}'
    

#videos = search_youtube("python videos")

#transcript = get_transcript(videos[0]['video_id'])

#print(transcript)

#success, answer = ask_gpt3("Explain to me what is the best multi-room speaker to buy", "text-davinci-003")
#print(answer)

def test_app(prompt, yt_query):
    videos = search_youtube(yt_query)

    for video in videos:
        video_id = video['video_id']
        video_title = video['title']

        success, transcript = get_transcript(video_id)

        # Check if we could get the transcript
        if not success:
            print(transcript)
            continue

        gpt_prompt = f'{prompt}\n\n{transcript}'
        success, answer = ask_gpt3(gpt_prompt, "text-davinci-003")
        print(video_title, f'https://www.youtube.com/watch?v={video_id}')
        print(answer)


yt_query = "Thomas Frank Tired"
prompt = "Using the following text, Can you summarize the top bullet points from this: \n\n"
test_app(prompt, yt_query)
