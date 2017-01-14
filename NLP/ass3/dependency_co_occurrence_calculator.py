from co_occurrence_calculator_base import CoOccurrenceCalculatorBase
from word_freq_calculator import WordFreqCalculator
from consts import Consts


class DependencyCoOccurrenceCalculator(CoOccurrenceCalculatorBase):
    def __init__(self):
        CoOccurrenceCalculatorBase.__init__(self)

    def process_sentence(self, sentence):
        sentence = filter(lambda entry: not entry.is_function_word, sentence)
        #todo: implement!!!
