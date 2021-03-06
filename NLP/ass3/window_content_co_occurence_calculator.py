from co_occurrence_calculator_base import CoOccurrenceCalculatorBase
from word_freq_calculator import WordFreqCalculator
from consts import Consts


class WindowContentCoOccurrenceCalculator(CoOccurrenceCalculatorBase):
    def __init__(self):
        CoOccurrenceCalculatorBase.__init__(self)

    def get_window(self, sentence, i):
        return sentence[max(i - 2, 0):i] + sentence[i + 1:i + 3]

    def get_name(self):
        return 'Window_Words'

    def process_sentence(self, sentence):
        sentence = filter(lambda entry: not entry.is_function_word, sentence)
        for i, entry in enumerate(sentence):
            if WordFreqCalculator().word_freq_dic[entry.lemma] > Consts.WORD_FREQ_THRES:
                window_entries = self.get_window(sentence, i)
                for window_entry in window_entries:
                    self.__add_feature_to_word__(entry.lemma, window_entry.lemma)

