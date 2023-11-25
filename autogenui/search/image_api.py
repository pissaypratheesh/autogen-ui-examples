import json
import requests
import re
import urllib.parse
from pytube import YouTube
from pytube import exceptions


def _extractBingImages(html):
    pattern = r'mediaurl=(.*?)&amp;.*?expw=(\d+).*?exph=(\d+)'
    matches = re.findall(pattern, html)
    result = []

    for match in matches:
        url, width, height = match
        if url.endswith('.jpg') or url.endswith('.png') or url.endswith('.jpeg'):
            result.append({'url': urllib.parse.unquote(url), 'width': int(width), 'height': int(height)})

    return result

def _extractBingVideos(html):
    pattern = r'mediaurl=(.*?)&amp;.*?expw=(\d+).*?exph=(\d+)'
    matches = re.findall(pattern, html)
    result = []

    for match in matches:
        url, width, height = match
        if url.endswith('.jpg') or url.endswith('.png') or url.endswith('.jpeg'):
            result.append({'url': urllib.parse.unquote(url), 'width': int(width), 'height': int(height)})

    return result


def _extractGoogleImages(html):
  images = []
  regex = re.compile(r"AF_initDataCallback\({key: 'ds:1', hash: '2', data:(.*?), sideChannel: {}}\);")
  match = regex.search(html)
  if match:
      dz = json.loads(match.group(1))         
      for c in dz[56][1][0][0][1][0]:
          try:
              thing = list(c[0][0].values())[0]
              images.append(thing[1][3])
          except:
              pass
  return images


def getBingImages(query, retries=5):
    query = query.replace(" ", "+")
    images = []
    tries = 0
    while(len(images) == 0 and tries < retries):
        response = requests.get(f"https://www.bing.com/images/search?q={query}&first=1")
        if(response.status_code == 200):
            images = _extractBingImages(response.text)
        else:
            print("Error While making bing image searches", response.text)
            raise Exception("Error While making bing image searches")
    if(images):
        return images
    raise Exception("Error While making bing image searches")


def getBingVideos(query, retries=5):
    query = query.replace(" ", "+")
    images = []
    tries = 0
    while(len(images) == 0 and tries < retries):
        response = requests.get(f"https://www.bing.com/videos/search?q={query}&first=1")
        if(response.status_code == 200):
            images = _extractBingImages(response.text)
        else:
            print("Error While making bing image searches", response.text)
            raise Exception("Error While making bing image searches")
    if(images):
        return images
    raise Exception("Error While making bing image searches")


def extract_video_data(input_data):
    output_data = []

    for item in input_data:
        # Introduce a new variable to avoid UnboundLocalError
        current_item = item

        # Parse the JSON string if 'current_item' is a string
        if isinstance(current_item, str):
            current_item = json.loads(current_item)
        try:
            yt = YouTube(current_item.get("link"))
            extracted_data = {
                "type": current_item.get("type"),
                "id": current_item.get("id"),
                "link": current_item.get("link"),
                "duration": current_item.get("duration"),
                "title": current_item.get("title"),
                "descriptionSnippet": current_item.get("descriptionSnippet", []),
                "viewCount": current_item.get("viewCount", {}),
                "stream": yt.streams.get_highest_resolution()
            }
            output_data.append(extracted_data)
        except exceptions.AgeRestrictedError:
            # Handle age-restricted video
            continue
        except Exception as e:
            # Handle any other exceptions
            print(f"An error occurred for video {current_item.get('id')}: {str(e)}")

    return output_data