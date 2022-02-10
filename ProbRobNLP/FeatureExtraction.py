import spacy


def get_words_and_tags(sentence):
    """ Parses the sentence using Spacy
    yielding a list of dictionaries contianing the words of the sentence and the tags extracted by the spacy model

    :param sentence: str the sentence to parse
    :return: {id, word, tag, dep, pos, head}
    """
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


def get_potential_referents(sentence):
    """ Extract the entities in the sentence

    :param sentence: str the sentence to extract entities from
    :return: list of entities ([{word1}, {word2}])
    """
    sentence = list(get_words_and_tags(sentence))
    for word in sentence:
        out = []
        if 'obj' in word['dep'] or 'subj' in word['dep'] or 'dative' in word['dep'] or 'attr' in word['dep']:

            for w in sentence:
                if w['head'] == word['id'] and w['dep'] != 'acl':
                    out.append(w)
            out.append(word)
            yield out


def list_to_string(word_list):
    """Creates a string representation of the output of get_words_and_tags"""
    return ' '.join([w['word'] for w in word_list])


def exact_string_match(entity1, entity2):
    """Checks if two strings are the same"""
    return list_to_string(entity1).lower() == list_to_string(entity2).lower()


def sub_string_match(antecedent, target):
    """Checks if the target is represented in the antecedent"""
    return list_to_string(target).lower() in list_to_string(antecedent).lower()


def word_overlap_match(antecedent, target):
    """Checks if any of the words in the target are in the antecedent"""
    antecedent = list_to_string(antecedent).lower()

    for word in target:
        if word['word'].lower() in antecedent:
            return True
    return False


def levenshtein(s1, s2):
    """Given the levenshtein distance between two strings"""
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[
                             j + 1] + 1  # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1  # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def edit_distance(antecedent, target, threshold=2):
    """Checks if the levenshtein distance is below a threshold"""
    return levenshtein(antecedent, target) <= threshold


list_of_definites = ["his", "her", "my", "your", "its", "our", "their", "this", "these", "that", "those", "the"]


def definiteness(antecedent, definites=list_of_definites):
    """Checks if the entity is a definite as defined by the list of definites"""
    words = [a['word'].lower() for a in antecedent]
    return any([definite in words for definite in definites])


def proper_noun(entity):
    """Checks if the entity is a proper noun"""
    return all([word['pos'] == "PROPN" for word in entity])


def pronoun(entity):
    """Checks if the entity is a ponoun"""
    return all([word['pos'] == "PRON" for word in entity])


def subject(entity):
    """Checks if the entity is in the subject position"""
    return any(["nsubj" in word['dep'] for word in entity])


def direct_object(entity):
    """Checks if the entity is in the direct object position"""
    return any(["dobj" in word['dep'] for word in entity])


def dative(entity):
    """Checks if the entity is in the dative position (indirect object)"""
    return any(["dative" in word['dep'] for word in entity])


def number(entity):
    """Checks the number of an entity"""
    if pronoun(entity):
        if entity[0]['word'] == 'they':
            return "p"
        else:
            return "s"
    else:
        if any([word['tag'] == "NNS" for word in entity]):
            return "p"
        else:
            return "s"


def number_match(antecedent, target):
    """Checks if there is agreement between the number of two entities"""
    return number(antecedent) == number(target)


def feature_vector(antecedent, target):
    """Creates a feature vector for co-reference of two entitites."""
    return {
        "exact_match": exact_string_match(antecedent, target),
        "substring_match": sub_string_match(antecedent, target),
        "word_overlap": word_overlap_match(antecedent, target),
        "edit_distance": edit_distance(list_to_string(antecedent), list_to_string(target)),
        "ant_definite": definiteness(antecedent),
        "tar_defnite": definiteness(target),
        "proper_noun": proper_noun(antecedent) == proper_noun(target),
        "pronoun_antecedent": pronoun(antecedent),
        "pronoun_target": pronoun(target),
        "subject": subject(target) == subject(antecedent),
        "direct_object": direct_object(target) == direct_object(antecedent),
        "indirect_object": dative(target) == dative(antecedent),
        "number_match": number_match(antecedent, target),
    }
    # TODO gender, Animacy, Quotation Semantic featuers

