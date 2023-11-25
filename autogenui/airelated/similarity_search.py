from sentence_transformers import SentenceTransformer, util

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
        similarity_score = calculate_similarity(query, video_title)
        print("🚀 ~ file: similarity_search.py:15 ~ similarity_score:", similarity_score,video_title)
        if similarity_score > threshold:
            filtered_titles.append(video)

    return filtered_titles

def filter_sentences(query, sentences,title_key='title', threshold=0.5):
    filtered_result = filter_video_titles(query, sentences, title_key, threshold=threshold)
    for video_data in filtered_result:
        print(f"Filtered Video Title: ",video_data)
    return filtered_result