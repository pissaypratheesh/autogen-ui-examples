import re

def split_into_sentences(paragraph):
    sentences = [{"text": sentence.strip()} for sentence in re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', paragraph)]
    return sentences

paragraph = "Yo, so Election Commission dropped a notice bomb on Rahul for calling the PM a bad omen at a rally. Opposition was triggered and filed a complaint, now EC's like, \"Explain yourself by Saturday, fam!\" Rahul dissed by saying he jinxed India's World Cup final. EC's all serious, talking Model Code of Conduct violations and crores waivers drama. They even brought up the Supreme Court vibes. Rahul, you in some political hot water, bro!"

sentences_array = split_into_sentences(paragraph)
print(sentences_array)
