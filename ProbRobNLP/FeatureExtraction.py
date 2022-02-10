import spacy


def get_words_and_tags(sentence):
    nlp = spacy.load("en_core_web_sm")
    sents = nlp(sentence).to_json()

    # print(sents['tokens'])

    for i, token in enumerate(sents['tokens']):
        word = sentence[token['start']:token['end']]
        tag = token['tag']
        dep = token['dep']
        pos = token['pos']
        head = token['head']
        yield {'id': i, 'word': word, 'tag': tag, 'dep': dep, 'pos': pos, 'head': head}