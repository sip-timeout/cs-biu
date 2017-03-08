from fc_base import FC_Base
from reading_utils import  *

class BOWFeatures(FC_Base):
    def __init__(self):
        FC_Base.__init__(self)

    def words_between(self, sent, index1, index2):
        words = sent['entries'][index1 + 1: index2]
        return words



    def get_features(self, sent, ent1, ent2):
        features = []

        index1 = min(entry_index(ent1), entry_index(ent2))
        index1_end = min(entry_index(ent1 , False), entry_index(ent2,False))
        index2 = max(entry_index(ent1), entry_index(ent2))
        index2_end = max(entry_index(ent1,False), entry_index(ent2,False))
        distance = index2 - index1_end

        if distance == 1:
            features.append('WBNULL')
        else:
            first_between , last_between = index1_end + 1 , index2 - 1

            if distance == 2:
                features.append('WBFL'+get_lemma(sent,first_between))
            else :
                features.append('WBF' + get_lemma(sent, first_between))
                features.append('WBL' + get_lemma(sent, last_between))
                words = self.words_between(sent, first_between, last_between)
                words = ['WBO'+word.lemma for word in words]
                features = features + words


        left_to_m1_f, left_to_m1_l = index1 - 1, index1 - 2
        right_to_m2_f, right_to_m2_l = index2_end + 1, index2_end + 2

        if left_to_m1_f > 0 : features.append('BM1F' + get_lemma(sent, left_to_m1_f))
        if left_to_m1_l > 0: features.append('BM1L' + get_lemma(sent, left_to_m1_l))
        if right_to_m2_f < len(sent['entries']): features.append('AM2F' + get_lemma(sent, right_to_m2_f))
        if right_to_m2_l < len(sent['entries']): features.append('AM2L' + get_lemma(sent, right_to_m2_l))





        bow1 = ['WM1'+word.lemma for word in ent1['entries'] ]
        bow2 = ['WM2' + word.lemma for word in ent2['entries']]
        features = features + bow1 + bow2

        features.append('HM1'  +  get_head(ent1))
        features.append('HM2' + get_head(ent2))
        features.append('HM12' + get_head(ent1) + get_head(ent2))

        return features






