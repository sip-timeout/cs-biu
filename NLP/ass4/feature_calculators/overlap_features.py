from fc_base import FC_Base
from reading_utils import *

class OverLapFeatures(FC_Base):
    def __init__(self):
        FC_Base.__init__(self)

    def get_features(self, sent, ent1, ent2):
        index1 = min(entry_index(ent1), entry_index(ent2))
        index1_end = min(entry_index(ent1, False), entry_index(ent2, False))
        index2 = max(entry_index(ent1), entry_index(ent2))
        index2_end = max(entry_index(ent1, False), entry_index(ent2, False))
        distance = index2 - index1_end

        features = []
        if distance <= 4: wb = 'short'
        elif distance <= 8: wb = 'medium'
        else: wb = 'long'
        features.append('WB'+wb)

        entites_between = 0
        for word in sent['entries'][index1_end+1 : index2]:
            if word.ent_type and word.bio == 'B':
                entites_between += 1
        features.append('MB' + str(entites_between))



        return features
