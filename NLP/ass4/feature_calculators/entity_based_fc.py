from fc_base import FC_Base


class EntityBasedFC(FC_Base):
    def __init__(self):
        FC_Base.__init__(self)

    def get_features(self, sent, ent1, ent2):
        #print ent1['text'] + ' - ' + ent2['text']
        return ['t_ent1' + ent1['type'],
                't_ent2' + ent2['type'] ,
                't_both' + ent1['type'] + ent2['type'] ]

        #todo: add entity head features