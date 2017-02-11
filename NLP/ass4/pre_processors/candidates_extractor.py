import itertools


class CandidatesExtractor:
    def __init__(self):
        pass

    def preprocess(self, sent):
        candidates = list()
        for duo in itertools.permutations(sent.entities, 2):
            candidates.append({'ent1': duo[0], 'ent2': duo[1]})

        sent['candidates'] = candidates
