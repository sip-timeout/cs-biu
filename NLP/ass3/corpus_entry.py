class CorpusEntry:
    def __init__(self, entry_string):
        #keys = ['id', 'form', 'lemma', 'cpostag', 'postag', 'feats', 'head', 'deprel', 'phead', 'pdeprel']
        values = entry_string.split('\t')
        # self.__dict__ = dict(zip(keys, values))
        self.lemma = values[2]
