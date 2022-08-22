import spacy
import copy
import probRobScene
import numpy as np
from ProbRobNLP import logic

from ProbRobNLP import FeatureExtraction
from ProbRobNLP.dep_parsing import parse_sentence
from ProbRobNLP.logic import reset_reference, reset_variable, reset_event, reset_event_variable


#
# class Entity:
#     def __init__(self, wordlist):
#         self.head = wordlist[-1]
#         self.wordlist = wordlist
#         self.DRS = self._get_semantics()
#
#     def __repr__(self):
#         return ' '.join([w['word'] for w in self.wordlist])
#
#     def get_semantics(self):
#         return self.DRS
#
#     def _get_semantics(self):
#         og = copy.deepcopy(self)
#         ref = []
#         log = []
#         for word in self.wordlist:
#             if word['pos'] == 'DET':
#                 reference = get_reference()
#                 if word['word'] == 'a':
#                     pass
#                 elif word['word'] == 'the' or word['word'] == 'that':
#                     reference = reference + '=?'
#                 ref.append(reference)
#             else:
#                 log.append(sem(word['word'], [reference]))
#
#         if len(log) == 1 and log[0].name in special_names:
#             ref = [special_names[log[0].name]]
#             log = []
#
#         head = self.wordlist[-1]
#         role = head['dep']
#         head['ref'][reference] = og
#         return DRSish(ref, log, role=role)


def generate_images(scenario_file, save_location="", max_generations=9):
    scenario = probRobScene.scenario_from_file(scenario_file)

    rejections_per_scene = []
    for i in range(max_generations):
        # print(f"Generation {i}")
        ex_world, used_its = scenario.generate(verbosity=2)
        rejections_per_scene.append(used_its)
        ex_world.show_3d(save_location=save_location+f"test{i}.png")

    # avg_rejections = np.average(rejections_per_scene)


class DialogueHistory:

    def __init__(self):
        self.sentences = []
        self.semantics = []
        self.most_recent_mention = {}
        self.time = -1

    def update(self, sentence, sem):
        self.time += 1
        self.sentences.append(sentence)
        self.semantics.append(sem)
        for ref in sem.ref:
            self.most_recent_mention[ref] = self.time

    def add_reference(self, reference):
        self.most_recent_mention[reference] = self.time

    def get_time_diff(self, r1, r2):
        return self.most_recent_mention[r2] - self.most_recent_mention[r1]


class Dialogue:

    def __init__(self, prs_file='tmp.prs'):
        reset_reference()
        reset_variable()
        reset_event()
        reset_event_variable()
        self.current_state = None
        # self.refs = {}
        self.dialogue_history = DialogueHistory()
        self.prs_file = prs_file

    def get_candidates(self, reference):
        constraints = [a for a in self.current_state.get_first_predicates(reference) if a.pred.arity == 1]
        print(constraints)
        print(self.current_state)
        print(self.current_state.ref)
        possible_candidates = [ref for ref in self.current_state.ref if ref != reference
                               and isinstance(ref, logic.Constant) and (reference.is_event() == ref.is_event())]
        print(possible_candidates)
        for ref in possible_candidates:
            print(ref, self.current_state.test_reference_matches(ref, constraints))
        candidates = [ref for ref in possible_candidates if self.current_state.test_reference_matches(ref, constraints)]
        return candidates

    def read_sentence(self, sentence, verbose=False):
        # sentence = Sentence(sentence)

        # drs_sent = sentence.get_semantics()

        drs_sent = parse_sentence(sentence, verbose=verbose)
        if verbose:
            print(drs_sent)

        # self.refs.update(drs_sent['sem'].ref)
        drs = drs_sent['sem']

        self.dialogue_history.update(sentence, drs)

        # print(self.refs)
        # print(drs_sent)

        # assert (len(drs_sent) == 1)

        drs = drs_sent['sem']

        if self.current_state is None:
            self.current_state = drs
        else:
            self.current_state = self.current_state + drs

    def resolve_reference(self):

        unresolved = [r for r in self.current_state.ref if isinstance(r, logic.Variable)]
        if len(unresolved) > 0:

            print('unresolved', unresolved)

            for r in unresolved:
                candidates = self.get_candidates(r)

                print('candidates', candidates)
                if len(candidates) == 1:
                    replacement = candidates[0]
                    self.current_state.replace_reference(r, replacement)
                    self.dialogue_history.add_reference(replacement)
                    # self.dialogue_history[-1][1]['ref'][replacement] = self.dialogue_history[-1][1]['ref'][r]
                else:
                    best_candidate = None
                    best_candidate_time = -1

                    for candidate in candidates:
                        time_diff = self.dialogue_history.get_time_diff(candidate, r)
                        if best_candidate is None and time_diff != 0:
                            # print('default candidate', candidate)
                            best_candidate = candidate
                            best_candidate_time = self.dialogue_history.get_time_diff(candidate, r)
                            best_candidate_features = FeatureExtraction.coreference_features(candidate, r)
                        elif time_diff != 0:

                            features = FeatureExtraction.coreference_features(candidate, r)

                            if features['direct_object_antecedent'] is True:

                                if (time_diff <= best_candidate_time or best_candidate_features[
                                        'direct_object_antecedent'] is False) and time_diff != 0:
                                    best_candidate = candidate
                                    best_candidate_time = time_diff
                                    best_candidate_features = features

                    print(best_candidate, r)
                    self.current_state.replace_reference(r, best_candidate)
                    self.dialogue_history.add_reference(best_candidate)
                    # self.dialogue_history[-1][1]['ref'][best_candidate] = self.dialogue_history[-1][1]['ref'][r]

                    # print(candidate, r, self.get_time_diff(candidate, r))
                    # print(FeatureExtraction.feature_vector(dlg.refs[candidate].wordlist, dlg.refs[r].wordlist))

                    # raise NotImplementedError("not implemented how to resolve situations with more than one candidate")
    def update(self, sentence):
        self.read_sentence(sentence)
        self.resolve_reference()


    def get_time_diff(self, ref1, ref2):
        time1 = 0
        time2 = 0

        for i, (_, d) in enumerate(self.dialogue_history):
            if ref1 in d['ref']:
                time1 = i
            if ref2 in d['ref']:
                time2 = i
        return time2 - time1

    def draw(self, save_location='', max_generations=9):

        try:
            prs_data = str(self.current_state.draw())
        except AttributeError:
            prs_data = 'from model import *'
        with open(self.prs_file, 'w') as f:
            f.write(prs_data)

        print(prs_data)
        generate_images(self.prs_file, save_location, max_generations=max_generations)
