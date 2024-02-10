# %% [markdown]
# # Processing and narrating a video with GPT's visual capabilities and the TTS API
# 
# This notebook demonstrates how to use GPT's visual capabilities with a video. GPT-4 doesn't take videos as input directly,
# but we can use vision and the new 128K context window to describe the static frames of a whole video at once.
# We'll walk through two examples:
# 
# 1. Using GPT-4 to get a description of a video
# 

# %%
#from IPython.display import display, Image, Audio
from IPython.display import display, Image, Audio

import cv2  # We're using OpenCV to read video, to install !pip install opencv-python
import base64
import time
import pytube
import urllib.request
from openai import OpenAI
import os
import requests
import uuid
import json

client = OpenAI(api_key="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")


def download_yt_video(url, filename):
    video = pytube.YouTube(url)
    video.streams.first().download(filename=filename)
    return filename
def download_video(url, filename):
    urllib.request.urlretrieve(url, filename)


def describe_video(video_url):
    """  video_filename = "temp_video.mp4"
    download_video(video_url, video_filename)
    video = cv2.VideoCapture(video_filename)
    print("🚀 ~ file: videovision.py:35 ~ video:", video) """

    # Get the directory of the current Python script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Generate a unique filename using uuid
    unique_filename = str(uuid.uuid4())
    video_filename = os.path.join(script_dir, f"{unique_filename}.mp4")

    # Download the video
    download_video(video_url, video_filename)

    # Use cv2 to capture the video
    video = cv2.VideoCapture(video_filename)
    print("🚀 ~ file: videovision.py:35 ~ video:", video)
    base64Frames = []
    max_frames_to_pick = 3
    #frame_interval = len(base64Frames) # max_frames_to_pick
    while video.isOpened():
        success, frame = video.read()
        if not success:
            print(" \n\n failed to read")
            break
        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))

    total_frames = len(base64Frames)
    frame_interval = max(1, total_frames // max_frames_to_pick)   # Pick frames with a specified interval
    print("🚀 ~ file: videovision.py:68 ~ frame_interval, max_frames_to_pick:", frame_interval,max_frames_to_pick)
    picked_frames = base64Frames[::frame_interval][:max_frames_to_pick]
    #print("\n\n\n\n\n🚀 ~ file: videovision.py:68 ~ picked_frames:", picked_frames)

    video.release()
    print(len(base64Frames), "frames read.")

   #Generate a compelling description that I can upload along with the video.
    #Return result in a json format like               `{ rating: 8, outof: 10}`
    # %%
    PROMPT_MESSAGES = [
        {
            "role": "user",
            "content": [
                """These are frames from a video that i am providing you with. Describe me what is happening in this video in 20 words?
                Read the text in any in the image and send in json.
                Don't miss to  return result in a json format like `{ description: `$description`, text: `$text found in image`}`  """,
                *map(lambda x: {"image": x, "resize": 768}, picked_frames),
            ],
        },
    ]

    params = {
        "model": "gpt-4-vision-preview",
        "messages": PROMPT_MESSAGES,
        "max_tokens": 200,
    }

    result = client.chat.completions.create(**params)
    content = result.choices[0].message.content
    cleaned_content = content.replace("```json", "").replace("```", "").strip()
    # Parse the JSON content
    print("🚀 ~ file: videovision.py:101 ~ cleaned_content:", cleaned_content)
    try:
        parsed_json = json.loads(cleaned_content)
        print(parsed_json)
        return parsed_json
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return { "error": "Error decoding JSON" }

#print(describe_video("http://localhost:3000/shorts/qHt3WuGENXo"))