class EntityExtractor:
    def __init__(self):
        pass

    def preprocess(self, sent):
        entities = list()
        cur_ent = None
        for entry in sent['entries']:
            if entry.bio == 'B':
                cur_ent = dict()
                cur_ent['text'] = entry.word
                cur_ent['entries'] = [entry]
                cur_ent['type'] = entry.ent_type
            elif entry.bio == 'I':
                cur_ent['text'] += ' ' + entry.word
                cur_ent['entries'].append(entry)
            else:
                if cur_ent:
                    entities.append(cur_ent)
                    cur_ent = None

        sent['entities'] = entities
