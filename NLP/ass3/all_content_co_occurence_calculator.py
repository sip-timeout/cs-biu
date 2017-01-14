from co_occurrence_calculator_base import CoOccurrenceCalculatorBase
from word_freq_calculator import WordFreqCalculator
from consts import Consts


class AllContentCoOccurrenceCalculator(CoOccurrenceCalculatorBase):
    def __init__(self):
        CoOccurrenceCalculatorBase.__init__(self)

    def process_sentence(self, sentence):
        sentence = filter(lambda entry: not entry.is_function_word, sentence)
        for entry in sentence:
            if WordFreqCalculator().word_freq_dic[entry.lemma] > Consts.WORD_FREQ_THRES:
                other_entries = list(sentence)
                other_entries.remove(entry)
                for other_entry in other_entries:
                    self.__add_feature_to_word__(entry.lemma, other_entry.lemma)
