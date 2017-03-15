import itertools
from consts import Consts
import utils

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
      return [cand for cand in candidates if self.is_possible_canditate(cand , possbilites) ]

    def is_possible_canditate(self, cand , possbilites):
        return (cand['ent1']['type'] , cand['ent2']['type']) in possbilites


    def make_candidates(self , sentences ):
        all_cands = list(itertools.chain.from_iterable(map(lambda sent: sent['candidates'], sentences)))
        possible_set = self.extract_possible_candidates_tags(all_cands)
        utils.save_obj(possible_set, 'candidates')


    def filter_candidates(self , sentences):
        all_cands = list(itertools.chain.from_iterable(map(lambda sent: sent['candidates'], sentences)))
        possible_set = utils.load_obj('candidates')
        return self.extract_candidates(all_cands, possible_set)