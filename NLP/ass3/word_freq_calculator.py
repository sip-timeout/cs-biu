from utils import Utils
from string_mapper import StringMapper
from singleton import Singleton


class WordFreqCalculator(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.word_freq_dic = dict()
        print 'init'

    def process_sentence(self, sentence):
        for word in sentence:
            Utils.add_or_increase_key(self.word_freq_dic, word.lemma)
            # Utils.add_or_increase_key(self.word_freq_dic, word.lemma)


