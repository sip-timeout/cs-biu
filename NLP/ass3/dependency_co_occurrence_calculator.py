from co_occurrence_calculator_base import CoOccurrenceCalculatorBase
from word_freq_calculator import WordFreqCalculator
from consts import Consts


class DependencyCoOccurrenceCalculator(CoOccurrenceCalculatorBase):
    def __init__(self):
        CoOccurrenceCalculatorBase.__init__(self)

    def is_preposition(self, tag):
        return tag == "IN"

    def get_modifier_idx(self, sentence, prep_idx):
        for entry in sentence:
            if (int(entry.head) - 1) == prep_idx:
                return int(entry.head)
        return None

    def process_sentence(self, sentence):
        originalSentence = sentence
        sentence = filter(lambda entry: not entry.is_function_word, sentence)
        idx = 0
        for entry in sentence:
            label = entry.deprel
            modified = originalSentence[int(entry.head) - 1].lemma
            modifier = entry.lemma
            if (WordFreqCalculator().word_freq_dic[entry.lemma] > Consts.WORD_FREQ_THRES and
                WordFreqCalculator().word_freq_dic[modifier] > Consts.WORD_FREQ_THRES):
                #add normal feature
                feature_modified = "<" + modifier + "," + label + ",incoming>"
                self.__add_feature_to_word__(modified, feature_modified)
                feature_modifier = "<" + modified + "," + label + ",outgoing>"
                self.__add_feature_to_word__(modifier, feature_modifier)

                #The target word modifies the preposition
                if self.is_preposition(originalSentence[int(entry.head) - 1].cpostag):
                    #handle a) (i)
                    preposition_lemma = modified
                    modified = originalSentence[int(originalSentence[int(entry.head) - 1].head) - 1].lemma
                    modified_label = originalSentence[int(originalSentence[int(entry.head) - 1].head) - 1].deprel
                    feature_p_modifies = "-" + label+ "->" + preposition_lemma + "-" + modified_label + "->" + modified
                    self.__add_feature_to_word__(modifier, feature_p_modifies)

                elif self.is_preposition(entry.cpostag):
                    #handle a) (ii)
                    preposition_lemma = modifier
                    modifier_idx = self.get_modifier_idx(originalSentence, idx)
                    if None != modified_idx:
                        modifier = originalSentence[modifier_idx - 1].lemma
                        modifier_label = originalSentence[modifier_idx - 1].deprel
                        feature = modifier + "-" + modifier_label + "->" + preposition_lemma + "-" + modifier_label + "->"
                        self.__add_feature_to_word__(modified, feature)
            idx += 1
            
        #todo: implement!!!
