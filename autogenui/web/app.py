import logging
from typing import Dict
from ..datamodel import GenerateWebRequest
from fastapi import FastAPI, Request
import re
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
from ..search.image_api import getBingImages, extract_video_data
from ..airelated.similarity_search import filter_sentences, get_relevant_imgs
from ..airelated.attribution import chunk_and_attribute
from ..airelated.videovision import describe_video
from fastapi.middleware.cors import CORSMiddleware
from youtubesearchpython import VideosSearch
from pytube import YouTube
from ..create_img_dalle_n_vision import create_image_by_agents
from ..tasks.numeric_hash import create_numeric_hash

import sys   

from ..manager import Manager
import traceback

logger = logging.getLogger("autogenui")

NO_OF_VIDEOS = 5

app = FastAPI()
# allow cross origin requests for testing on localhost: 800 * ports only
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:8001", "http://localhost:3000"],
    allow_credentials="true",
    allow_methods=["*"],
    allow_headers=["*"],
)

api = FastAPI(root_path="/api")
app.mount("/api", api)


root_file_path = os.path.dirname(os.path.abspath(__file__))
files_static_root = os.path.join(root_file_path, "files/")
static_folder_root = os.path.join(root_file_path, "ui")


os.makedirs(files_static_root, exist_ok="true")
api.mount("/files", StaticFiles(directory=files_static_root, html="true"), name="files")


app.mount("/", StaticFiles(directory=static_folder_root, html="true"), name="ui")

stopWords = ["a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any","are","aren't","as","at","be","because","been","before","being","below","between","both","but","by","can't","cannot","could","couldn't","did","didn't","do","does","doesn't","doing","don't","down","during","each","few","for","from","further","had","hadn't","has","hasn't","have","haven't","having","he","he'd","he'll","he's","her","here","here's","hers","herself","him","himself","his","how","how's","i","i'd","i'll","i'm","i've","if","in","into","is","isn't","it","it's","its","itself","let's","me","more","most","mustn't","my","myself","no","nor","not","of","off","on","once","only","or","other","ought","our","ours","ourselves","out","over","own","same","shan't","she","she'd","she'll","she's","should","shouldn't","so","some","such","than","that","that's","the","their","theirs","them","themselves","then","there","there's","these","they","they'd","they'll","they're","they've","this","those","through","to","too","under","until","up","very","was","wasn't","we","we'd","we'll","we're","we've","were","weren't","what","what's","when","when's","where","where's","which","while","who","who's","whom","why","why's","with","won't","would","wouldn't","you","you'd","you'll","you're","you've","your","yours","yourself","yourselves"]

def remove_stop_words(query):
    query_words = query.split()
    filtered_words = [word for word in query_words if word.lower() not in stopWords]
    filtered_query = " ".join(filtered_words)
    return filtered_query

@api.post("/generate")
async def generate(req: Request) -> Dict:
    """Generate a response from the autogen flow"""
    req = await req.json()
    prompt = req.get("prompt")
    id = req.get("id")
    title = req.get("title")
    history = req.get("history", "")

    prompt_with_history = f"{history}\n\n{prompt}"
    print("******history******", history)

    try:

        manager = Manager()
        cases = {
            "/system_design": lambda: manager.run_system_design_flow(prompt=prompt),
            "/teachable": lambda: manager.run_teachable_agent_flow(prompt=prompt),
            "/local_llm": lambda: manager.run_local_llm_flow(prompt=prompt),
            "/summarize": lambda: manager.run_summarization_flow(prompt=prompt, id=id, title=title),
            "/title_summary": lambda: manager.run_simple_summary_flow(prompt=prompt),
            # Add more cases here
        }

        for case, action in cases.items():
            if prompt.startswith(case):
                agent_response = action()
                return { "data" : agent_response, "status": "true" }

        # If no case matches, perform a default action
        agent_response = manager.run_flow(prompt=prompt_with_history)

        response = {
            "data": agent_response,
            "status": "true"
        }
    except Exception as e:
        traceback.print_exc()
        response = {
            "data": str(e),
            "status": False
        }

    return response


@api.get("/videos")
async def videos(request: Request):
    query = request.query_params.get("query")
    if query:
         videosSearch = VideosSearch(query, limit = 5)
         res = videosSearch.result()
         if res:
             return extract_video_data(res['result'])
         else:
             return {"error": "No videos found"}
    else:
        return {"error": "Missing query parameter"}
   


@api.get("/images")
async def images(request: Request):
    query = request.query_params.get("query")
    if query:
        imagesWithoutFiltered = getBingImages(remove_stop_words(query))
        images = get_relevant_imgs(query,imagesWithoutFiltered, 'url',0.2)
        return {"images": images}
    else:
        return {"error": "Missing query parameter"}
    

@api.post("/assets")
async def images(request: Request):
    query = request.query_params.get("query")
    data = await request.json()
    summary = data.get("summary")
    time_in_min_video_threshold = 7
    if query:
        print("\n\nquery --> ",remove_stop_words(query))
        imagesWithoutFiltered = getBingImages(remove_stop_words(query))
        images = get_relevant_imgs(query,imagesWithoutFiltered, 'url',0.2)
        videosSearch = VideosSearch(remove_stop_words(query), limit = NO_OF_VIDEOS) #"indian express: " + 
        vidResults = videosSearch.result()
        vidRes = vidResults['result']
        print("🚀 ~ file: app.py:123 ~ vidRes:", vidRes)
        filtered_videos = [video for video in vidRes if video.get("duration") and sum(int(x) * 60 ** i for i, x in enumerate(reversed(video["duration"].split(":")))) < time_in_min_video_threshold * 60]
        print("\n\n\n\n fitlered by duration🚀 ~ file: app.py:127 ~ filtered_videos:", filtered_videos)
        ultraFilteredVids = filter_sentences(query,filtered_videos,'title',0.5)
        videosWithData =  extract_video_data(ultraFilteredVids)
        mapping = chunk_and_attribute(summary,images,videosWithData)
        return {
            "images": images,
            "videos":videosWithData,
            "mapping": mapping
        }
    else:
        return {"error": "Missing query parameter"}
    
@api.get("/test")
async def test(request: Request):
    array =[{"link":"https://www.youtube.com/watch?v=2OVnoivV3fY","title":"NO-CONFIDENCE motion a floor test for the Opposition: PM Modi in Lok Sabha"},{"link":"https://www.youtube.com/watch?v=lyV1OPQNpDs","title":"PM Modi chairs a meeting to review the situation in relation to Odisha Train Accident | Balasore"},{"link":"https://www.youtube.com/watch?v=dFNPr7nUsl8","title":"The country looks upon you and stands by you : PM Modi to Men in Blue | #shorts"},{"link":"https://www.youtube.com/watch?v=Eh1Zv8URTJg","title":"\"Oh My God\": Watch PM Modi's Epic Reply To Reporters| #PMModi #Shorts"},{"link":"https://www.youtube.com/watch?v=Y_JGOGAtdSs","title":"PM Modi took a dig at the Congress as he replied to the motion of thanks on the President's address"},{"link":"https://www.youtube.com/watch?v=xZtBxi_2Dmc","title":"PM Modi gets a traditional welcome in Nagpur!"},{"link":"https://www.youtube.com/watch?v=mh3b1Tn-Hy4","title":"PM Modi's arrival in Abu Dhabi, UAE | PM Modi in UAE"},{"link":"https://www.youtube.com/watch?v=Fn4WmLaQX7A","title":"PM Modi reveals the secret behind India's rising global stature"}]
    res = filter_sentences("Modi in Dubai",array,'title')
    return {"result": res}

#http://localhost:8081/api/create_img?prompt=elephant%20and%20rabbit%20having%20running%20race%20together%20in%20same%20direction
@api.get("/create_img")
async def create_img(request: Request):
    prompt = request.query_params.get("prompt")
    if prompt:
        return create_image_by_agents(prompt)
    else:
        return {"error": "Missing prompt parameter"}

#http://localhost:8081/api/get_image?hash=43989934125119128162879437038109310099668647771280565966691187460338044253308
#http://localhost:8081/api/create_img?prompt=elephant%20and%20rabbit%20having%20running%20race%20together%20in%20same%20direction
@api.get("/get_image")
async def get_image(request: Request):
    hash_value = request.query_params.get("hash")
    prompt = request.query_params.get("prompt")
    if not hash_value and prompt:
        hash_value = create_numeric_hash(prompt)
    if hash_value:
        folder_path = f"./dalle_images/{hash_value}"
        if os.path.exists(folder_path):
            image_files = [f for f in os.listdir(folder_path) if f.endswith(".png") or f.endswith(".jpg")]
            if image_files:
                image_files.sort(key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else -1, reverse=True)
                image_path = os.path.join(folder_path, image_files[0])
                return FileResponse(image_path, media_type="image/png")
            else:
                return {"error": "No images found in the folder"}
        else:
            return {"error": "Folder does not exist"}
    else:
        return {"error": "Missing hash parameter"}

@api.get("/create_get_image")
async def create_get_img(request: Request):
    prompt = request.query_params.get("prompt")
    if prompt:
        images = create_image_by_agents(prompt)
        hash_value = images['created_image']
        folder_path = f"./dalle_images/{hash_value}"
        if os.path.exists(folder_path):
            image_files = [f for f in os.listdir(folder_path) if f.endswith(".png") or f.endswith(".jpg")]
            if image_files:
                image_files.sort(key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else -1, reverse=True)
                image_path = os.path.join(folder_path, image_files[0])
                return FileResponse(image_path, media_type="image/png")
            else:
                return {"error": "No images found in the folder"}
        else:
            return {"error": "Folder does not exist"}
    else:
        return {"error": "Missing prompt parameter"}
    
@api.get("/describe/video")
async def describe_vid(request: Request):
    query = request.query_params.get("q") or request.query_params.get("query") or request.query_params.get("url")
    viddesc = describe_video(query)
    return viddesc
