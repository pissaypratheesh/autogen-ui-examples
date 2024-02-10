from sentence_transformers import SentenceTransformer, util

import re

def split_into_sentences(paragraph):
    sentences = [{"text": sentence.strip()} for sentence in re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', paragraph)]
    return sentences
#from .similarity_search import calculate_similarity
def calculate_similarity(query, sentence):
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    query_embedding = model.encode(query, convert_to_tensor=True)
    sentence_embedding = model.encode(sentence, convert_to_tensor=True)
    similarity_score = util.pytorch_cos_sim(query_embedding, sentence_embedding).item()
    return similarity_score

# Function to attribute images to sentences in Set A
def attribute_images_to_sentences(images, set_a_sentences):
    image_attributes = {}

    for img in images:
        max_similarity = 0
        selected_sentence = None

        for sentence in set_a_sentences:
            # Check if the sentence has fewer than 5 images attributed
            sentence_text = sentence['text']
            if len(image_attributes.get(sentence_text, [])) < 5:
                similarity = calculate_similarity(img['img_str'], sentence_text)

                if similarity > max_similarity:
                    max_similarity = similarity
                    selected_sentence = sentence_text

        # Attribute the image to the selected sentence
        image_attributes.setdefault(selected_sentence, []).append(img)

    return image_attributes

# Function to attribute scenes to sentences in Set A
def attribute_scenes_to_sentences(videos, set_a_sentences):
    scene_attributes = {}

    for video in videos:
        for scene in video['scenes']:
            max_similarity = 0
            selected_sentence = None

            for sentence in set_a_sentences:
                # Check if the sentence has fewer than 2 scenes attributed
                sentence_text = sentence['text']
                if len(scene_attributes.get(sentence_text, [])) < 2:
                    similarity = calculate_similarity(scene['script'], sentence_text)

                    if similarity > max_similarity:
                        max_similarity = similarity
                        selected_sentence = sentence_text

            # Attribute the scene to the selected sentence
            scene_attributes.setdefault(selected_sentence, []).append(scene)

    return scene_attributes

def chunk_and_attribute(summary, images, videos):
    summary_sentences = split_into_sentences(summary)
    # Attribute images to sentences
    image_attributes = attribute_images_to_sentences(images, summary_sentences)
    print("Image Attributes:", image_attributes)
    #videos_array = []
    for i, obj in enumerate(videos):
        obj["scenes"] = [{"script" : obj.get('title')}]
    videos_array = [{ "scenes": [{"script" : obj.get("title"),**item}]} for item in videos]

    #videos_array = videos
    # Attribute scenes to sentences
    scene_attributes = attribute_scenes_to_sentences(videos_array, summary_sentences)
    print("Scene Attributes:", scene_attributes)

    # Assuming each sentence in summary_sentences is a dictionary with a 'text' key
    for sentence in summary_sentences:
        sentence_text = sentence['text']
        sentence['images'] = image_attributes.get(sentence_text, [])

        # Similarly, you can set the 'videos' field using the scene_attributes
        sentence['videos'] = scene_attributes.get(sentence_text, [])
    
    return summary_sentences

    """ 


images = [{"url":"https://www.opindia.com/wp-content/uploads/2019/05/Election-Commission-Rahul-Gandhi1.jpeg","width":772,"height":1018,"img_str":"Election-Commission-Rahul-Gandhi1","similarity_score":0.6047244668006897},{"url":"https://images1.livehindustan.com/uploadimage/library/2020/10/22/16_9/16_9_1/pm_modi_and_congress_leader_rahul_gandhi_will_start_election_meetings_chunavi_sabha_together_in_biha_1603383062.jpg","width":640,"height":360,"img_str":"pm_modi_and_congress_leader_rahul_gandhi_will_start_election_meetings_chunavi_sabha_together_in_biha_1603383062","similarity_score":0.5125911235809326},{"url":"https://www.oneindia.com/ph-big/2021/03/congress-leader-rahul-gandhi-during-his-election-campaign-for-upcoming-tamil-nadu-assembly-polls_161459595720.jpg","width":680,"height":416,"img_str":"congress-leader-rahul-gandhi-during-his-election-campaign-for-upcoming-tamil-nadu-assembly-polls_161459595720","similarity_score":0.5108347535133362},{"url":"https://thewire.in/wp-content/uploads/2017/12/Rahul-Gandhi-questions_Reuters2.jpg","width":1280,"height":730,"img_str":"Rahul-Gandhi-questions_Reuters2","similarity_score":0.5021032691001892},{"url":"https://images.firstpost.com/wp-content/uploads/2013/10/Modi_Rahul_AFP_Reuters2.jpg","width":380,"height":285,"img_str":"Modi_Rahul_AFP_Reuters2","similarity_score":0.49109208583831787},{"url":"https://imagevars.gulfnews.com/2019/04/13/Congress_President_Rahul_Gandhi_resources1_16a4505c35a_large.jpg","width":750,"height":563,"img_str":"Congress_President_Rahul_Gandhi_resources1_16a4505c35a_large","similarity_score":0.4856153428554535},{"url":"https://www.thestatesman.com/wp-content/uploads/2019/05/Rahul-Gandhi-6.jpg","width":1200,"height":799,"img_str":"Rahul-Gandhi-6","similarity_score":0.47680944204330444},{"url":"https://ptcnews-wp.s3.ap-south-1.amazonaws.com/wp-content/uploads/2019/05/Rahul-Gandhi-1_edited.jpg","width":699,"height":399,"img_str":"Rahul-Gandhi-1_edited","similarity_score":0.4696268141269684},{"url":"https://thenewsmill.com/wp-content/uploads/2019/03/Rahul-Gandhi-in-Itanagar.jpeg","width":1200,"height":674,"img_str":"Rahul-Gandhi-in-Itanagar","similarity_score":0.46670782566070557},{"url":"https://images.cnbctv18.com/wp-content/uploads/2019/05/Rahul-Gandhi-768x555.jpg","width":768,"height":555,"img_str":"Rahul-Gandhi-768x555","similarity_score":0.4608924984931946},{"url":"https://www.jantakareporter.com/wp-content/uploads/2019/05/rahul-gandhi.jpg","width":1280,"height":720,"img_str":"rahul-gandhi","similarity_score":0.44464126229286194},{"url":"https://images.indianexpress.com/2019/07/rahul-gandhi.jpg","width":759,"height":422,"img_str":"rahul-gandhi","similarity_score":0.44464126229286194},{"url":"https://i.ndtvimg.com/mt/2013-10/Rahul_Gamdhi_rally_295x200.jpg","width":295,"height":200,"img_str":"Rahul_Gamdhi_rally_295x200","similarity_score":0.4382268786430359},{"url":"https://resize.indiatvnews.com/en/resize/oldbucket/715_-/politicsnational/Election-Commis17471.jpg","width":570,"height":400,"img_str":"Election-Commis17471","similarity_score":0.4058525264263153},{"url":"https://img.theweek.in/content/dam/week/news/india/images/2019/10/18/rahul-gandhi-pti181019.jpg","width":760,"height":443,"img_str":"rahul-gandhi-pti181019","similarity_score":0.3944050073623657},{"url":"https://images.indianexpress.com/2019/06/rahul-gandhi-delhi-confidential-1200.jpg","width":1200,"height":667,"img_str":"rahul-gandhi-delhi-confidential-1200","similarity_score":0.3735713064670563},{"url":"https://c.ndtvimg.com/2019-04/30j0preo_rahul-gandhi_625x300_16_April_19.jpg","width":650,"height":400,"img_str":"30j0preo_rahul-gandhi_625x300_16_April_19","similarity_score":0.34885647892951965},{"url":"https://cdn.dnaindia.com/sites/default/files/styles/full/public/2017/12/14/632968-rahul-gandhipti.jpg","width":1280,"height":720,"img_str":"632968-rahul-gandhipti","similarity_score":0.28683361411094666},{"url":"https://i.ndtvimg.com/i/2017-12/rahul-gandhi-650_650x400_51512721748.jpg","width":650,"height":400,"img_str":"rahul-gandhi-650_650x400_51512721748","similarity_score":0.2825142443180084},{"url":"https://www.lifeberrys.com/img/article/rahul-gandhi-1556859827-lb.jpg","width":740,"height":425,"img_str":"rahul-gandhi-1556859827-lb","similarity_score":0.2189139723777771},{"url":"https://www.thestatesman.com/wp-content/uploads/2019/05/rahul-pitroda.jpg","width":1200,"height":800,"img_str":"rahul-pitroda","similarity_score":0.20836740732192993}]
videos = [{"type":"video","id":"i81KwXrpNjk","link":"https://www.youtube.com/watch?v=i81KwXrpNjk","duration":"3:05","title":"Baat pate Ki: आपत्तिजनक बयान पर Rahul Gandhi को EC को देना होगा जबाव।","descriptionSnippet":[{"text":"Baat pate Ki: After "},{"text":"Rahul Gandhi's objectionable statement","bold":"true"},{"text":" on "},{"text":"PM Modi","bold":"true"},{"text":" in Rajasthan "},{"text":"elections","bold":"true"},{"text":", "},{"text":"Election Commission","bold":"true"},{"text":" sent a "},{"text":"notice","bold":"true"},{"text":" ..."}],"viewCount":{"text":"3,318 views","short":"3.3K views"},"similarity_score":0.6687649488449097},{"type":"video","id":"Hx_OE0gger0","link":"https://www.youtube.com/watch?v=Hx_OE0gger0","duration":"2:53","title":"Rahul Gandhi gets EC notice over law to kill tribals remark against PM Modi","descriptionSnippet":[{"text":"1. The "},{"text":"Election Commission","bold":"true"},{"text":" has issued a "},{"text":"notice","bold":"true"},{"text":" to Congress president "},{"text":"Rahul Gandhi","bold":"true"},{"text":" for allegedly claiming at a Madhya ..."}],"viewCount":{"text":"605 views","short":"605 views"},"similarity_score":0.652764081954956},{"type":"video","id":"AV9_YG-DDVg","link":"https://www.youtube.com/watch?v=AV9_YG-DDVg","duration":"4:25","title":"Rahul Gandhi Gets Poll Body Notice For 'Panauti' Comments On PM Modi","descriptionSnippet":[{"text":"Congress's "},{"text":"Rahul Gandhi","bold":"true"},{"text":" has come under the lens of the "},{"text":"Election Commission","bold":"true"},{"text":" over his Panauti "},{"text":"comment","bold":"true"},{"text":" on "},{"text":"Prime Minister","bold":"true"},{"text":" ..."}],"viewCount":{"text":"3,425 views","short":"3.4K views"},"similarity_score":0.6427271366119385},{"type":"video","id":"_UZHzJBKY84","link":"https://www.youtube.com/watch?v=_UZHzJBKY84","duration":"2:27","title":"NCW sends notice to Rahul Gandhi over insulting remark on Defence Minister Nirmala Sitharaman","descriptionSnippet":[{"text":"New Delhi, Jan 10 (ANI): National "},{"text":"Commission","bold":"true"},{"text":" for Women (NCW) has sent a "},{"text":"notice","bold":"true"},{"text":" to Congress president "},{"text":"Rahul Gandhi","bold":"true"},{"text":" over his ..."}],"viewCount":{"text":"277 views","short":"277 views"},"similarity_score":0.6059170961380005}]


# Example data
summary_sentences = [{'text': 'Yo, so Election Commission dropped a notice bomb on Rahul for calling the PM a bad omen at a rally.'}, {'text': 'Opposition was triggered and filed a complaint, now EC\'s like, "Explain yourself by Saturday, fam!" Rahul dissed by saying he jinxed India\'s World Cup final.'}, {'text': "EC's all serious, talking Model Code of Conduct violations and crores waivers drama."}, {'text': 'They even brought up the Supreme Court vibes.'}, {'text': 'Rahul, you in some political hot water, bro!'}]
#[{"text": "Sentence 1"}, {"text": "Sentence 2"}, {"text": "Sentence 3"}, {"text": "Sentence 4"}, {"text": "Sentence 5"}, {"text": "Sentence 6"}]
images_array = images#[{"img_str": "Image 1"}, {"img_str": "Image 2"}, {"img_str": "Image 3"}, {"img_str": "Image 4"}, {"img_str": "Image 5"}]
# expected: videos_array = [{"scenes": [{"script": "Scene 1"}, {"script": "Scene 2"}]},
#                           {"scenes": [{"script": "Scene 3"}, {"script": "Scene 4"}]}]

videos_array = [{
    "scenes":[
                     {"type":"video","id":"i81KwXrpNjk","link":"https://www.youtube.com/watch?v=i81KwXrpNjk","duration":"3:05","title":"Baat pate Ki: आपत्तिजनक बयान पर Rahul Gandhi को EC को देना होगा जबाव।","descriptionSnippet":"null","viewCount":{"text":"3,318 views","short":"3.3K views"},"similarity_score":0.6687649488449097,"script":"Baat pate Ki: आपत्तिजनक बयान पर Rahul Gandhi को EC को देना होगा जबाव।"},
                     {"type":"video","id":"Hx_OE0gger0","link":"https://www.youtube.com/watch?v=Hx_OE0gger0","duration":"2:53","title":"Rahul Gandhi gets EC notice over law to kill tribals remark against PM Modi","descriptionSnippet":"null","viewCount":{"text":"605 views","short":"605 views"},"similarity_score":0.652764081954956,"script":"Rahul Gandhi gets EC notice over law to kill tribals remark against PM Modi"},
                     {"type":"video","id":"AV9_YG-DDVg","link":"https://www.youtube.com/watch?v=AV9_YG-DDVg","duration":"4:25","title":"Rahul Gandhi Gets Poll Body Notice For 'Panauti' Comments On PM Modi","descriptionSnippet":"null","viewCount":{"text":"3,425 views","short":"3.4K views"},"similarity_score":0.6427271366119385,"script":"Rahul Gandhi Gets Poll Body Notice For 'Panauti' Comments On PM Modi"},
                     {"type":"video","id":"_UZHzJBKY84","link":"https://www.youtube.com/watch?v=_UZHzJBKY84","duration":"2:27","title":"NCW sends notice to Rahul Gandhi over insulting remark on Defence Minister Nirmala Sitharaman","descriptionSnippet":"null","viewCount":{"text":"277 views","short":"277 views"},"similarity_score":0.6059170961380005,"script":"NCW sends notice to Rahul Gandhi over insulting remark on Defence Minister Nirmala Sitharaman"}
            ]
 }]
# Attribute images to sentences
image_attributes = attribute_images_to_sentences(images_array, summary_sentences)
print("Image Attributes:", image_attributes)

# Attribute scenes to sentences
scene_attributes = attribute_scenes_to_sentences(videos_array, summary_sentences)
print("Scene Attributes:", scene_attributes)

# Assuming each sentence in summary_sentences is a dictionary with a 'text' key
for sentence in summary_sentences:
    sentence_text = sentence['text']
    sentence['images'] = image_attributes.get(sentence_text, [])

    # Similarly, you can set the 'videos' field using the scene_attributes
    sentence['videos'] = scene_attributes.get(sentence_text, [])

# Print summary sentences with image and video attributions
for sentence in summary_sentences:
    print("Sentence:", sentence['text'])
    print("Images:", sentence['images'])
    print("Videos:", sentence['videos'])
    print() """