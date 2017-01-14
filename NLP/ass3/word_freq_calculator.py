from utils import Utils

class WordFreqCalculator:
    def __init__(self):
        self.word_freq_dic = dict()

    def process_sentence(self, sentence):
        for word in sentence:
            Utils.add_or_increase_key(self.word_freq_dic,word.lemma)
