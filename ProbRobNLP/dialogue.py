import spacy
import copy
import probRobScene
import numpy as np

from ProbRobNLP import FeatureExtraction, probrob

special_names = {'centre': probrob.Vector3D(0, 0, 0)}


class Sentence:

    def __init__(self, sentence):
        self.sentence = {i: w for i, w in enumerate(FeatureExtraction.get_words_and_tags(sentence))}

    def get_head(self):
        for word in self.sentence.values():
            if word['id'] == word['head']:
                return word

    def get_children(self, id_):
        for word in self.sentence.values():
            if word['head'] == id_:
                yield word

    def __repr__(self):
        return '\n'.join([f"{i}: {w}" for i, w in self.sentence.items()])

    def get_entities(self):

        sentence = list(self.sentence.values())
        for word in sentence:
            out = []
            if 'obj' in word['dep'] or 'subj' in word['dep'] or 'dative' in word['dep'] or 'attr' in word['dep']:

                for w in sentence:
                    if w['head'] == word['id'] and w['dep'] != 'acl' and w['dep'] != 'prep':
                        out.append(w)
                out.append(word)
                yield Entity(out)

    def join(self, head_id, child_id):
        head = self.sentence[head_id]
        child = self.sentence[child_id]

        head['word'] = head['word'] + ' ' + child['word']

        self.sentence[head_id] = head

        self.sentence = {id_: word for id_, word in self.sentence.items()
                     if not (word['head'] == head['id'] and word['word'] in head['word'])}

    def get_semantics(self):
        word_list = copy.deepcopy(self.sentence)
        entities = self.get_entities()
        for entity in entities:
            head = entity.head
            head['word'] = str(entity)
            head['sem'] = entity.DRS
            word_list[head['id']] = head
            head['dep'] = head['dep'] + '/NP'
            word_list = {id_: word for id_, word in word_list.items()
                         if not (word['head'] == head['id'] and word['word'] in head['word'])}

        for word in word_list.values():
            if word['dep'] == 'prep':
                for word2 in word_list.values():
                    if word2['head'] == word['id']:
                        assert ('NP' in word2['dep'])
                        drs2 = word2['sem']
                        r1 = drs2.ref[0]
                        ref = [get_reference() + '=<dobj>', r1]
                        log = [sem(word['word'], ref)]
                        drs1 = DRSish(ref, log)
                        drs = drs1 + drs2

                        word['sem'] = drs
                        word['dep'] = 'PP'
                        word['word'] = word['word'] + ' ' + word2['word']
                        word['ref'].update(word2['ref'])

                        word_list = {id_: w for id_, w in word_list.items()
                                     if not (w['head'] == word['id'] and w['word'] in word['word'])}

        head = self.get_head()
        dobj = None
        pp = None
        for word in word_list.values():
            if word['head'] == head['id']:

                if 'dobj' in word['dep']:
                    dobj = word

                elif 'PP' == word['dep']:
                    pp = word

                if dobj is not None and pp is not None:
                    dobj_drs = dobj['sem']
                    pp_drs = pp['sem']
                    drs = pp_drs.unify(dobj_drs)

                    head['sem'] = drs
                    head['dep'] = 'S'
                    head['word'] = head['word'] + ' ' + dobj['word'] + ' ' + pp['word']
                    head['ref'].update(dobj['ref'])
                    head['ref'].update(pp['ref'])

                    word_list = {id_: head if head['id'] == id_ else w for id_, w in word_list.items()}

                    word_list = {id_: w for id_, w in word_list.items()
                                 if
                                 not (w['head'] == head['id'] and w['word'] in head['word'] and w['id'] != head['id'])}

        return word_list


reference_id = 0
variable_id = 0

def get_variable():
    global variable_id
    x = f'X{variable_id}'
    variable_id += 1
    return x


def reset_variable():
    global variable_id
    variable_id = 0

def get_reference():
    global reference_id
    x = f'x{reference_id}'
    reference_id += 1
    return x


def reset_reference():
    global reference_id
    reference_id = 0

event_id = 0

def get_event():
    global event_id
    x = f'e{event_id}'
    event_id += 1
    return x

def reset_event():
    global event_id
    event_id = 0


class Entity:
    def __init__(self, wordlist):
        self.head = wordlist[-1]
        self.wordlist = wordlist
        self.DRS = self._get_semantics()

    def __repr__(self):
        return ' '.join([w['word'] for w in self.wordlist])

    def get_semantics(self):
        return self.DRS

    def _get_semantics(self):
        og = copy.deepcopy(self)
        ref = []
        log = []
        for word in self.wordlist:
            if word['pos'] == 'DET':
                reference = get_reference()
                if word['word'] == 'a':
                    pass
                elif word['word'] == 'the' or word['word'] == 'that':
                    reference = reference + '=?'
                ref.append(reference)
            else:
                log.append(sem(word['word'], [reference]))

        if len(log) == 1 and log[0].name in special_names:
            ref = [special_names[log[0].name]]
            log = []

        head = self.wordlist[-1]
        role = head['dep']
        head['ref'][reference] = og
        return DRSish(ref, log, role=role)


class DRSish:

    def __init__(self, ref, log, role=None):
        self.ref = ref
        self.log = log
        self.role = role

    def __repr__(self):
        return str(self.ref) + str(self.log) + ' r: ' + str(self.role)

    def __add__(self, other):
        ref = list(set(self.ref + other.ref))
        log = self.log + other.log
        return DRSish(ref, log)

    def get_predicates(self, reference):
        assert (reference in self.ref)

        for l in self.log:
            if reference in l.refs:
                yield l

    def get_first_predicates(self, reference):
        assert (reference in self.ref)

        for l in self.log:
            if reference == l.refs[0]:
                yield l

    def unify(self, other):

        new_ref = []
        log = copy.deepcopy(self.log)
        assert (len(other.ref) == 1)
        for ref in self.ref:

            if isinstance(ref, str) and '<' in ref:

                hole = ref.split('<')[1].strip('>')
                if hole == other.role:
                    new_ref.append(other.ref[0])
                    new_log = []
                    for formula in log:
                        if ref in formula.refs:
                            refs = [other.ref[0] if r == ref else r for r in formula.refs]
                            new_log.append(sem(formula.name, refs))
                        else:
                            new_log.append(formula)
                    log = new_log
            else:
                new_ref.append(ref)
        new_ref = [r for r in new_ref if isinstance(r, str)]
        return DRSish(new_ref, log + other.log, self.role)

    def replace_reference(self, hole, antecedent):
        new_ref = [r for r in self.ref if r != hole] + ([antecedent] if antecedent not in self.ref else [])
        log = copy.deepcopy(self.log)
        new_log = []
        for l in log:
            if hole in l.refs:
                refs = [r if r != hole else antecedent for r in l.refs]
                new_log.append(sem(l.name, refs))
            else:
                new_log.append(l)
        self.ref = new_ref
        self.log = list(set(new_log))

    def to_PRS(self):
        order = self.order_prs()
        entities = {entity.name: entity for entity in self._to_PRS()}
        for name in order:
            yield entities[name]

    def remove_predicate(self, p):
        self.log = [l for l in self.log if p != l]

    def remove_reference(self, ref):
        self.ref = [r for r in self.ref if r != ref]

    def _to_PRS(self):
        types = {'tray': 'Tray', 'cup': 'Cup', 'bowl': 'Bowl', 'bucket': 'Bucket',
                 'chair': 'DiningChair', 'filled_cup': 'FilledCup',
                 'plate': 'Plate', 'table': 'Table', 'robot': 'Robot', 'camera': 'Camera', 'peg': 'HexagonalPegBase',
                 'gear': 'HexagonalGear', 'cube': 'Cube', 'toy_cube': 'ToyCube', 'cylinder': 'Cylinder',
                 'rope link': 'RopeLink',
                 'rope bucket': 'RopeBucket', 'conveyor belt': 'CircularConveyorBelt'}

        two_place = {'on': probrob.OnConstraint, 'in': probrob.OnConstraint}

        colour_dict = {'red': '"0.1"', 'blue': '"0.2"', 'green': '"0.3"', 'grey': '"0.4"', 'orange': '"0.5"',
                       'purple': '"0.7"', 'pink': '"0.6"', 'black': '"0"', 'white': '"1"'}

        # for l in self.log:
        #     if l.name in special_names:
        #         self.remove_predicate(l)
        #         self.replace_reference(l.refs[0], l.name)
        #         self.remove_reference(l.name)

        for ref in self.ref:

            preds = self.get_first_predicates(ref)

            constraints = []
            type_ = None
            for pred in preds:
                if pred.name in types:
                    type_ = types[pred.name]
                elif pred.name in two_place:
                    constraints.append(two_place[pred.name](
                        pred.refs[1] if pred.refs[1] not in special_names else special_names[pred.refs[1]]))
                elif pred.name in colour_dict:
                    constraints.append(probrob.PropConstraint('color', f'"{pred.name}"'))

            if type_ is not None:
                yield probrob.Entity(type_, ref, constraints)
            else:
                print(f'Warning: {ref} identified as type None')

    def order_prs(self):
        constraints = []
        for entity in self._to_PRS():
            for constraint in entity.constraints:
                try:
                    r = constraint.referent
                    constraints.append((r, entity.name))
                except AttributeError:
                    pass

        constraint_dict = {}
        for entity in self._to_PRS():
            c = [d for (d, i) in constraints if i == entity.name and d in self.ref]
            constraint_dict[entity.name] = c

        order = []
        i = 0
        while len(constraint_dict) > 0 and i < 20:
            print(constraint_dict)
            new_dict = {}
            for name, cons in constraint_dict.items():
                if cons == [] or all([x in order for x in cons]):
                    order.append(name)
                else:
                    new_dict[name] = cons
            constraint_dict = new_dict
            i += 1
        return order

    def draw(self):
        prs_lines = self.to_PRS()
        imp = probrob.Import('model', '*')
        scene = probrob.WorldModel(prs_lines, [imp])
        return scene

    def test_reference_matches(self, reference, constraints):

        preds = [c.name for c in self.get_first_predicates(reference)]
        # print('reference', reference, 'preds', preds, 'constraints', constraints)
        # print(all([c.name in preds for c in constraints]))
        return all([c.name in preds for c in constraints])


class sem:
    def __init__(self, name, refs):
        self.name = name
        self.refs = refs

    def __repr__(self):
        return f'{str(self.name)}({", ".join(map(str, self.refs))})'

    def __eq__(self, other):
        return self.name == other.name and self.refs == other.refs

    def __hash__(self):
        # hash(custom_object)
        return hash((self.name, ' '.join(map(str, self.refs))))


def generate_images(scenario_file, save_location=""):
    scenario = probRobScene.scenario_from_file(scenario_file)

    max_generations = 9
    rejections_per_scene = []
    for i in range(max_generations):
        # print(f"Generation {i}")
        ex_world, used_its = scenario.generate(verbosity=2)
        rejections_per_scene.append(used_its)
        ex_world.show_3d(save_location=save_location+f"test{i}.png")

    # avg_rejections = np.average(rejections_per_scene)


class Dialogue:

    def __init__(self, prs_file='tmp.prs'):
        reset_reference()
        self.current_state = None
        self.refs = {}
        self.dialogue_history = []
        self.prs_file = prs_file

    def read_sentence(self, sentence):
        sentence = Sentence(sentence)

        drs_sent = sentence.get_semantics()

        self.refs.update(drs_sent[0]['ref'])

        self.dialogue_history.append((sentence, drs_sent[0]))

        print(self.refs)
        # print(drs_sent)

        assert (len(drs_sent) == 1)

        drs = drs_sent[0]['sem']

        if self.current_state is None:
            self.current_state = drs
        else:
            self.current_state = self.current_state + drs

        if any(['?' in r for r in filter(lambda x: isinstance(x, str), self.current_state.ref)]):
            unresolved = [r for r in self.current_state.ref if '?' in r]

            print('unresolved', unresolved)

            for r in unresolved:

                constraints = list(self.current_state.get_first_predicates(r))

                candidates = [ref for ref in self.current_state.ref if
                              self.current_state.test_reference_matches(ref, constraints) and ref != r]

                print('candidates', candidates)
                if len(candidates) == 1:
                    replacement = candidates[0]
                    self.current_state.replace_reference(r, replacement)
                    self.dialogue_history[-1][1]['ref'][replacement] = self.dialogue_history[-1][1]['ref'][r]
                else:
                    best_candidate = None
                    best_candidate_time = -1

                    for candidate in candidates:
                        time_diff = self.get_time_diff(candidate, r)
                        if best_candidate is None and time_diff != 0:
                            # print('default candidate', candidate)
                            best_candidate = candidate
                            best_candidate_time = self.get_time_diff(candidate, r)
                            best_candidate_features = FeatureExtraction.feature_vector(self.refs[candidate].wordlist,
                                                                                       self.refs[r].wordlist)
                        elif time_diff != 0:

                            features = FeatureExtraction.feature_vector(self.refs[candidate].wordlist,
                                                                        self.refs[r].wordlist)
                            # print('trying candidate', candidate)
                            # print('time diff', time_diff)
                            # print('direct object target', features['direct_object_antecedent'])
                            # print('candidate direct object', best_candidate_features['direct_object_antecedent'])
                            if features['direct_object_antecedent'] is True:

                                if (time_diff <= best_candidate_time or best_candidate_features[
                                    'direct_object_antecedent'] is False) and time_diff != 0:
                                    best_candidate = candidate
                                    best_candidate_time = time_diff
                                    best_candidate_features = features

                    print(best_candidate, r)
                    self.current_state.replace_reference(r, best_candidate)
                    self.dialogue_history[-1][1]['ref'][best_candidate] = self.dialogue_history[-1][1]['ref'][r]

                    # print(candidate, r, self.get_time_diff(candidate, r))
                    # print(FeatureExtraction.feature_vector(dlg.refs[candidate].wordlist, dlg.refs[r].wordlist))

                    # raise NotImplementedError("not implemented how to resolve situations with more than one candidate")

    def get_time_diff(self, ref1, ref2):
        time1 = 0
        time2 = 0

        for i, (_, d) in enumerate(self.dialogue_history):
            if ref1 in d['ref']:
                time1 = i
            if ref2 in d['ref']:
                time2 = i
        return time2 - time1

    def draw(self, save_location=''):

        try:
            prs_data = str(self.current_state.draw())
        except AttributeError:
            prs_data = 'from model import *'
        with open(self.prs_file, 'w') as f:
            f.write(prs_data)

        print(prs_data)
        generate_images(self.prs_file, save_location)


