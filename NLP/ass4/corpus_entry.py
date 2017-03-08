class CorpusEntry:
    function_dic = {
        'IN': 1, 'PRP': 1, 'PRP$': 1, 'DT': 1, 'CC': 1, 'aux': 1, 'advmod': 1, 'neg': 1 , 'p':1
    }

    def __init__(self, entry_string):
        # keys = ['id', 'form', 'lemma', 'cpostag', 'postag', 'head', 'deprel', 'bio','ent_type']
        values = entry_string.split('\t')
        # self.__dict__ = dict(zip(keys, values))
        self.id = values[0]
        self.word = values[1]
        self.lemma = values[2]
        self.cpostag = values[3]
        self.head = values[5]
        self.deprel = values[6]
        self.bio = values[7]
        self.ent_type = values[8]
        self.is_function_word = self.cpostag in self.function_dic or self.deprel in self.function_dic

        self.position = int(self.id) - 1