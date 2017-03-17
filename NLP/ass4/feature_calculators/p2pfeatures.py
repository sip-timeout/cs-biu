from fc_base import FC_Base
from reading_utils import *
from random import randint

class P2PFeatures(FC_Base):
    def __init__(self):
        FC_Base.__init__(self)

    def get_features(self, sent, ent1, ent2):     
        features = []
        #find ent1 path to root
        idx_h = int(ent1['entries'][0].id)
        path_1 =[idx_h]
        cur_entry = ent1['entries'][0]
        while idx_h:
            idx_h = int(cur_entry.head)
            cur_entry = get_entry(idx_h, sent)
            path_1.append(idx_h)
        
        idx_h = int(ent2['entries'][0].id)
        path_2 =[idx_h]
        cur_entry = ent2['entries'][0]
        while idx_h:
            idx_h = int(cur_entry.head)
            cur_entry = get_entry(idx_h, sent)
            path_2.append(idx_h)

        id_1 = int(ent1['entries'][0].id)
        id_2 = int(ent2['entries'][0].id)

        idx_list = []
        #check if ent2 is a descendent of ent1
        if id_1 in path_2:
            for i in path_2:
                idx_list.append(i)
                if i == id_1:
                    break
        elif id_2 in path_1:
            for i in path_1:
                idx_list.append(i)
                if i == id_2:
                    break
        else:
            found = False
            for i in path_1:
                idx_list.append(i)
                if i in path_2:
                    idx2 = []
                    for j in path_2:
                        if i != j:
                            idx2.append(j)
                        else:
                            found = True
                            break
                    if found:
                        idx2.reverse()
                        idx_list = idx_list + idx2
                        break
        ptp = "PTP_" # + ent1['entries'][0].word + "_"
        tpt = "TPT_"
        dtd = "DTD_"
        for i in idx_list:
            e = get_entry(i, sent)
            if i == 0:
                #ptp += "ROOT_"
                pass
            else:
                ptp += e.cpostag + "_"
                tpt += e.ent_type + "_"
                dtd += e.deprel + "_"
        #ptp += ent2['entries'][0].word
        features.append(ptp)
        #features.append(tpt)
        features.append(dtd)
        return features
