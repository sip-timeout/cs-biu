class EntityExtractor:
    def __init__(self):
        pass

    def preprocess(self, sent):
        entities = list()
        cur_ent = None
        for entry in sent['entries']:
            if entry.bio == 'B':
                cur_ent = dict()
                cur_ent['entries'] = list()
                if entry.word != 'the':
                    cur_ent['entries'].append(entry)
                cur_ent['type'] = entry.ent_type
            elif entry.bio == 'I':
                cur_ent['entries'].append(entry)
            else:
                if cur_ent:
                    cur_ent['text'] = ' '.join([ent.word for ent in cur_ent['entries']])
                    entities.append(cur_ent)
                    cur_ent = None

        sent['entities'] = entities
