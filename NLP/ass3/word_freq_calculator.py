from utils import Utils
from string_mapper import StringMapper

class WordFreqCalculator:
    def __init__(self):
        self.word_freq_dic = dict()

    def process_sentence(self, sentence):
        for word in sentence:
            Utils.add_or_increase_key(self.word_freq_dic,StringMapper().get_int(word.lemma))
            #Utils.add_or_increase_key(self.word_freq_dic, word.lemma)
