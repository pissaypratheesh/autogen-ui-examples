from sentence_transformers import SentenceTransformer, util
import requests
from urllib.parse import urlparse

def extract_filename_without_extension(url):
    parsed_url = urlparse(url)
    path_segments = parsed_url.path.split("/")
    filename_with_extension = path_segments[-1]

    # Remove file extension
    filename_without_extension = filename_with_extension.rsplit('.', 1)[0]

    return filename_without_extension

def attach_filenames_to_data(data):
    for item in data:
        url = item.get("url", "")
        filename_without_extension = extract_filename_without_extension(url)
        item["img_str"] = filename_without_extension

    return data




def is_image_url_valid(url):
    try:
        response = requests.get(url)
        return response.status_code == 200 and 'image' in response.headers.get('content-type')
    except requests.RequestException:
        return False

def filter_valid_images(image_array, url_key='url'):
    valid_images = []
    for image in image_array:
        if is_image_url_valid(image[url_key]):
            valid_images.append(image)
        else:
            print(f"Invalid image URL: {image[url_key]}")
    return valid_images

def sort_assets(image_array, sort_key='height', reverse=True):
    sorted_images = sorted(image_array, key=lambda x: x[sort_key], reverse=reverse)
    return sorted_images

def calculate_similarity(query, sentence):
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    query_embedding = model.encode(query, convert_to_tensor=True)
    sentence_embedding = model.encode(sentence, convert_to_tensor=True)
    similarity_score = util.pytorch_cos_sim(query_embedding, sentence_embedding).item()
    return similarity_score

def filter_video_titles(query, video_data, title_key='title', threshold=0.5):
    filtered_titles = []
    for video in video_data:
        video_title = video.get(title_key, '')  # Get the title using the specified key
        description = ""
        if video.get("descriptionSnippet") is not None:
            description = "".join(snippet["text"] for snippet in video["descriptionSnippet"])
            video["title"] = video_title + ". description: " + description
            del video["descriptionSnippet"]
        similarity_score = calculate_similarity(query, video_title)
        print("\n🚀 ~ file: similarity_search.py:15 ~ similarity_score:", similarity_score,video_title)
        if similarity_score > threshold:
            video['similarity_score'] = similarity_score            
            filtered_titles.append(video)

    return filtered_titles

def filter_sentences(query, sentences,title_key='title', threshold=0.5):
    filtered_result = filter_video_titles(query, sentences, title_key, threshold=threshold)
    for video_data in filtered_result:
        print(f"\n\n\n\n\n\nFiltered Assets Title: ",video_data)
    return sort_assets(filtered_result,'similarity_score') #filtered_result


#usage: print(get_relevant_imgs(query, array))
def get_relevant_imgs(query, array, url_key='url', threshold=0.2):
    valid_images = filter_valid_images(array, url_key)
    withnames = attach_filenames_to_data(valid_images)
    ultraFilteredVids = filter_sentences(query,withnames,'img_str',threshold)
    print("\n\n\nsorted-->",sort_assets(ultraFilteredVids,'similarity_score'))
    return sort_assets(ultraFilteredVids,'similarity_score')

