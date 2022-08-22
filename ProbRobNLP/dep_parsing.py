
from ProbRobNLP import FeatureExtraction, logic
from ProbRobNLP.logic import DRSish, get_reference, get_variable, get_event, get_event_variable


class Sentence:
    """Performs dependency parsing on a sentence and returns a ditionary where the key is the position in the sentence
    and the value is a dicitonary including the word, dependency tag, POS tag, """
    def __init__(self, sentence):
        self.sentence = {i: w for i, w in enumerate(FeatureExtraction.get_words_and_tags(sentence))}

    def get_root(self):
        for word in self.sentence.values():
            if word['dep'] == 'ROOT':
                return word

    def get_head(self):
        for word in self.sentence.values():
            if word['id'] == word['head']:
                return word

    def get_children(self, id_):
        return [word for word in self.sentence.values() if word['head'] == id_ and word['id'] != id_]

    def get_leaves(self):
        heads = set([word['head'] for word in self.sentence.values()])
        return [word for word in self.sentence.values() if word['id'] not in heads]

    def __repr__(self):
        return '\n'.join([f"{i}: {w}" for i, w in self.sentence.items()])

    def __iter__(self):
        return self.sentence.items()

    def __getitem__(self, item):
        return self.sentence[item]

    def __setitem__(self, item, value):
        self.sentence[item] = value

    def items(self):
        return self.sentence.items()

    def values(self):
        return list(self.sentence.values())

    def __len__(self):
        return len(self.sentence)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError as e:
            return default

    def join(self, head_id, child_id):
        """Combines the entry of two entries at head_id and child_id
        """
        head = self.sentence[head_id]
        child = self.sentence[child_id]

        head_words = [(i, w) for i, w in zip(head['word_positions'], head['word'].split())]
        child_words = [(i, w) for i, w in zip(child['word_positions'], child['word'].split())]

        new_words = sorted(head_words + child_words)

        ids, words = zip(*new_words)

        head['word'] = ' '.join(words)
        head['word_positions'] = ids

        self[head_id] = head

        self.sentence = {id_: word for id_, word in self.items()
                         if not (word['head'] == head['id'] and word['word'] in head['word']) or word['dep'] == 'ROOT'}

        for key, word in self.items():
            if word['head'] == child['id']:
                word['head'] = head['id']



multiword_expressions = {
    ('the', 'centre'): (lambda: DRSish([logic.Atom(logic.Predicate('Vector3D', 3), [0, 0, 0])], []), 0, 1),
    ('to', 'the', 'left', 'of'): (
    lambda e, x, y: DRSish([e, x, y], [logic.Atom(logic.Predicate('left_of', 3), [e, x, y], fp=True)],
                           holes={'control': (x, None), 'pobj': (y, None)}), 3,
    0),
    ('to', 'the', 'right', 'of'): (
    lambda e, x, y: DRSish([e, x, y], [logic.Atom(logic.Predicate('right_of', 3), [e, x, y], fp=True)],
                           holes={'control': (x, None), 'pobj': (y, None)}), 3,
    0)}


def combine_multword_expression(sentence, expression, start_location):
    words = [sentence[i] for i in range(start_location, start_location + len(expression))]
    heads = [w['head'] for w in words]
    leaves = [w for w in words if w['id'] not in heads]
    while leaves != []:
        next_one = leaves[0]
        sentence.join(next_one['head'], next_one['id'])
        words.remove(next_one)
        heads = [w['head'] for w in words]
        leaves = [w for w in words if w['id'] not in heads]
    return sentence, [words[0]]


def match_multiword_expression(sentence, multiword_expression, semantics):
    drs_lambda, num_variables, head_position = semantics
    for i in range(len(sentence)):
        if all([sentence.get(i + j, {}).get('word', '') == word for j, word in enumerate(multiword_expression)]):
            # print("found match!", i, i + len(multiword_expression) - 1)

            for j in range(i, i + len(multiword_expression)):
                if j != i + head_position:
                    sentence.join(sentence[j]['head'], j)

            vars = [get_variable() for i in range(num_variables)]
            if num_variables == 3:
                vars[0] = get_event()
            # vars[0].update_features({[]})
            drs = drs_lambda(*vars)
            sentence[i + head_position]['sem'] = drs
    return sentence


class SubstitutionRule:

    def __init__(self, name, checking_function, semantics_function):
        self.name = name
        self.checking_function = checking_function
        self.semantics_function = semantics_function

    def applies(self, id_, word, sentence):
        return self.checking_function(id_, word, sentence)

    def apply(self, id_, word, sentence):
        if self.applies(id_, word, sentence):
            return self.semantics_function(word)
        else:
            return None


class RulesGroup:

    def __init__(self, rules):
        self.rules = rules

    def apply(self, id_, word, sentence):
        for rule in self.rules:
            if (sem := rule.apply(id_, word, sentence)) is not None:
                return sem


def check_det(det):
    def det_checker(id_, word, sentence):
        return word['tag'] == 'DT' and word['word'] == det
    return det_checker

def a_sem(word):
    constant = get_reference()
    constant.update_features({
        'words': [word['word']],
        'positions': [word['word_positions']],
        'number': 1, })
    return DRSish([constant], [])


def the_sem(word):
    variable = get_variable()
    variable.update_features({
        'words': [word['word']],
        'positions': [word['word_positions']],
    })
    return DRSish([variable], [])


def that_sem(word):
    variable = get_variable()
    variable.update_features({
        'words': [word['word']],
        'positions': [word['word_positions']],
        'number': 1,
    })
    return DRSish([variable], [])


# def check_that(id_, word, sentence):
#     return word['word'] == 'that'


def check_pos(pos):
    def pos_checker(id_, word, sentence):
        return word['tag'] == pos
    return pos_checker


def noun_adj_sem(word):
    variable = get_variable()
    variable.update_features({
        'words': [word['word']],
        'positions': [word['word_positions']],
    })

    if word['tag'] == 'NN':
        variable.update_features({'number': 1})

    if word['dep'] == 'dobj':
        variable.update_features({'dobj': True})

    p = logic.Predicate(word['word'], 1)
    a = logic.Atom(p, [variable])
    return DRSish([variable], [a])


def IN_sem(word):
    x = get_variable()
    y = get_variable()
    e = get_event()
    p = logic.Predicate(word['word'], 3)
    a = logic.Atom(p, [e, x, y], fp=True)
    return DRSish([e, x, y], [a], holes={'control': (x, None), 'pobj': (y, None)})


def VB_sem(word):
    e = get_event()
    x = get_variable()
    e_prim = get_event_variable()
    p = logic.Predicate(word['word'], 3)
    a = logic.Atom(p, [e, x, e_prim])
    return DRSish([e], [a], holes={'dobj': (x, None), 'prep': (e_prim, ('control', x))})


def prp_sem(word):
    x = get_variable()
    x.update_features({
        'words': [word['word']],
        'positions': [word['word_positions']],
    })
    return DRSish([x], [])


def check_be(id_, word, sentence):
    return word['tag'] == 'VB' and word['word'] in ['be', 'is']


def be_sem(word):
    x = get_variable()
    e = get_event_variable()
    return DRSish([], [], holes={'nsubj': (x, None), 'prep': (e, ('control', x))})


def md_sem(word):
    return DRSish([], [])

def word_checker(word):
    def check_word(id_, w, s):
        return w['word'] == word
    return check_word

substitution_rules = RulesGroup(
    [SubstitutionRule('a', check_det('a'), a_sem),
     SubstitutionRule('the', check_det('the'), the_sem),
     SubstitutionRule('that', check_det('that'), that_sem),
     SubstitutionRule('it', word_checker('it'), that_sem),
     SubstitutionRule('noun', check_pos('NN'), noun_adj_sem),
     SubstitutionRule('NNP', check_pos('NNP'), noun_adj_sem),
     SubstitutionRule('adj', check_pos('JJ'), noun_adj_sem),
     SubstitutionRule('IN', check_pos('IN'), IN_sem),
     SubstitutionRule('be', check_be, be_sem),
     SubstitutionRule('VB', check_pos('VB'), VB_sem),
     SubstitutionRule('MD', check_pos('MD'), md_sem),
    ])


def substitution(sentence):
    for expression, semantics in multiword_expressions.items():
        sentence = match_multiword_expression(sentence, expression, semantics)

    for id_, word in sentence.items():
        if len(word['word'].split()) > 1:
            continue
        else:
            word['sem'] = substitution_rules.apply(id_, word, sentence)

    return sentence


rules = {'amod': lambda head, child: head.join_on_reference(child),
         'det': lambda head, child: child.join_on_reference(head),
         'pobj': lambda head, child: head.fill_gap(child, 'pobj'),
         'prep': lambda head, child: head.fill_gap(child, 'prep'),
         'dobj': lambda head, child: head.fill_gap(child, 'dobj'),
         'nsubj': lambda head, child: head.fill_gap(child, 'nsubj'),
         'aux': lambda head, child: head + child}


def compose(sentence, position):
    child = sentence.sentence[position]
    head_id = child['head']
    head = sentence.sentence[head_id]

    dep = child['dep']

    sem_child = child['sem']
    sem_head = head['sem']

    new_sem = rules[dep](sem_head, sem_child)

    sentence.sentence[head_id]['sem'] = new_sem
    sentence.join(head_id, child['id'])
    return sentence


def parse_sentence(s, verbose=False):
    s = Sentence(s)
    if verbose:
        print('Sentence:')
        print(s)
        print()
    s = substitution(s)
    if verbose:
        print('Substitution: ')
        print(s)
        print()

    while ((leaves := s.get_leaves()) != []):
        l = leaves[0]
        h = s.sentence[l['head']]
        # print(l, h)
        compose(s, l['id'])

    return s.values()[0]