import logging
from typing import Dict
from ..datamodel import GenerateWebRequest
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
import os
from ..search.image_api import getBingImages, extract_video_data
from ..airelated.similarity_search import filter_sentences
from fastapi.middleware.cors import CORSMiddleware
from youtubesearchpython import VideosSearch
from pytube import YouTube
from ..create_img_dalle_n_vision import create_image_by_agents

import sys   

from ..manager import Manager
import traceback

logger = logging.getLogger("autogenui")


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



@api.post("/generate")
async def generate(req: Request) -> Dict:
    """Generate a response from the autogen flow"""
    req = await req.json()
    prompt = req.get("prompt")
    history = req.get("history", "")

    prompt_with_history = f"{history}\n\n{prompt}"
    print("******history******", history)

    try:

        manager = Manager()
        cases = {
            "/system_design": lambda: manager.run_system_design_flow(prompt=prompt),
            "/teachable": lambda: manager.run_teachable_agent_flow(prompt=prompt),
            "/local_llm": lambda: manager.run_local_llm_flow(prompt=prompt),
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
        images = getBingImages(query)
        return {"images": images}
    else:
        return {"error": "Missing query parameter"}
    

@api.get("/assets")
async def images(request: Request):
    query = request.query_params.get("query")
    time_in_min_video_threshold = 3
    if query:
        images = getBingImages(query)
        videosSearch = VideosSearch(query, limit = 15)
        vidResults = videosSearch.result()
        vidRes = vidResults['result']
        print("🚀 ~ file: app.py:123 ~ vidRes:", vidRes)
        filtered_videos = [video for video in vidRes if video.get("duration") and sum(int(x) * 60 ** i for i, x in enumerate(reversed(video["duration"].split(":")))) < time_in_min_video_threshold * 60]
        print("\n\n\n\n fitlered by duration🚀 ~ file: app.py:127 ~ filtered_videos:", filtered_videos)
        ultraFilteredVids = filter_sentences(query,filtered_videos,'title',0.5)
        return {
            "images": images,
            "videos": extract_video_data(ultraFilteredVids)
        }
    else:
        return {"error": "Missing query parameter"}
    
@api.get("/test")
async def test(request: Request):
    array =[{"link":"https://www.youtube.com/watch?v=2OVnoivV3fY","title":"NO-CONFIDENCE motion a floor test for the Opposition: PM Modi in Lok Sabha"},{"link":"https://www.youtube.com/watch?v=lyV1OPQNpDs","title":"PM Modi chairs a meeting to review the situation in relation to Odisha Train Accident | Balasore"},{"link":"https://www.youtube.com/watch?v=dFNPr7nUsl8","title":"The country looks upon you and stands by you : PM Modi to Men in Blue | #shorts"},{"link":"https://www.youtube.com/watch?v=Eh1Zv8URTJg","title":"\"Oh My God\": Watch PM Modi's Epic Reply To Reporters| #PMModi #Shorts"},{"link":"https://www.youtube.com/watch?v=Y_JGOGAtdSs","title":"PM Modi took a dig at the Congress as he replied to the motion of thanks on the President's address"},{"link":"https://www.youtube.com/watch?v=xZtBxi_2Dmc","title":"PM Modi gets a traditional welcome in Nagpur!"},{"link":"https://www.youtube.com/watch?v=mh3b1Tn-Hy4","title":"PM Modi's arrival in Abu Dhabi, UAE | PM Modi in UAE"},{"link":"https://www.youtube.com/watch?v=Fn4WmLaQX7A","title":"PM Modi reveals the secret behind India's rising global stature"}]
    res = filter_sentences("Modi in Dubai",array,'title')
    return {"result": res}

@api.get("/create_img")
async def create_img(request: Request):
    prompt = request.query_params.get("prompt")
    if prompt:
        return create_image_by_agents(prompt)
    else:
        return {"error": "Missing prompt parameter"}

@api.get("/get_image")
async def get_image(request: Request):
    hash_value = request.query_params.get("hash")
    if hash_value:
        folder_path = f"./dalle_images/{hash_value}"
        if os.path.exists(folder_path):
            image_files = [f for f in os.listdir(folder_path) if f.endswith(".png") or f.endswith(".jpg")]
            if image_files:
                image_path = os.path.join(folder_path, random.choice(image_files))
                return FileResponse(image_path, media_type="image/png")
            else:
                return {"error": "No images found in the folder"}
        else:
            return {"error": "Folder does not exist"}
    else:
        return {"error": "Missing hash parameter"}
