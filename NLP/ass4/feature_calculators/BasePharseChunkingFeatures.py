from fc_base import FC_Base
from reading_utils import *

class BasePharseChunkingFeatures(FC_Base):
    def __init__(self):
        FC_Base.__init__(self)

    def get_features(self, sent, ent1, ent2):       
        
        features = []
        
        et1dw1 = 'ET1DW1_' + str(ent1['entries'][0].word) + str(ent1['entries'][0].ent_type) + "_"
        et2dw2 = 'ET2DW2_' + str(ent2['entries'][0].word) + str(ent2['entries'][0].ent_type) + "_"

        head_1 = "Root"
        try:
            head_1 = sent['text'].split(" ")[int(ent1['entries'][0].head)]
        except:
            pass

        head_2 = "Root"
        try:
            head_2 = sent['text'].split(" ")[int(ent2['entries'][0].head)]
        except:
            pass
        
        h1dw1 = 'H1DW1_' + str(head_1) + "_"
        h2dw2 = 'H2DW2_' + str(head_2) + "_"

        dependent_1 = getDependentWords(ent1['entries'][0].id, sent)
        dependent_2 = getDependentWords(ent2['entries'][0].id, sent)

        if len(dependent_1) == 0:
            features.append(et1dw1)
            h1dw1 += "None"
            features.append(h1dw1)
        else:
            for d in dependent_1:
                temp = et1dw1 + d
                features.append(temp)
                temp = h1dw1 + d
                features.append(temp)

        if len(dependent_2) == 0:
            features.append(et2dw2)
            h2dw2 += "None"
            features.append(h2dw2)
        else:
            for d in dependent_2:
                temp = et2dw2 + d
                features.append(temp)
                temp = h2dw2 + d
                features.append(temp)

        return features
