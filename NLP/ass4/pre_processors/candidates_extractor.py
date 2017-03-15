import itertools
from consts import Consts

class CandidatesExtractor:
    def __init__(self):
        pass

    def preprocess(self, sent):
        candidates = list()
        for duo in itertools.permutations(sent['entities'], 2):
            candidates.append({'ent1': duo[0], 'ent2': duo[1],'train_class': Consts.NONE_ID})

        sent['candidates'] = candidates

    def extract_possible_candidates_tags(self , candidates):
        possible = set()
        for cand in candidates:
            if cand['train_class'] != 0:
                possible.add( (cand['ent1']['type'] , cand['ent2']['type'])  )

        return  possible

    def extract_candidates(self, candidates , possbilites):

      l = []
      for cand in  candidates:
          if self.is_possible_canditate(cand , possbilites):
              l.append(cand)
      return l

    def is_possible_canditate(self, cand , possbilites):
        return (cand['ent1']['type'] , cand['ent2']['type']) in possbilites
