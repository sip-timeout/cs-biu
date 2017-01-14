from co_occurrence_calculator_base import CoOccurrenceCalculatorBase


class AllContentCoOccurrenceCalculator(CoOccurrenceCalculatorBase):
    def __init__(self):
        CoOccurrenceCalculatorBase.__init__(self)

    def process_sentence(self, sentence):
        for entry in sentence:
            other_entries = list(sentence)
            other_entries.remove(entry)
            for other_entry in other_entries:
                self.__add_feature_to_word__(entry.lemma, other_entry.lemma)
