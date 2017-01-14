from utils import Utils
from numpy import linalg
from consts import Consts
from string_mapper import StringMapper
import math
import numpy


class CoOccurrenceCalculatorBase:
    def __init__(self):
        self.__word_to_feat__ = dict()
        self.__word_to_total_count__ = dict()
        self.__feat_to_total_count__ = dict()
        self.__total_pairs__ = 0

        self.__word_to_normalized_pmi__ = dict()
        self.initialized_pmi = False

    def __add_feature_to_word__(self, word, feat):
        word_int_rep = StringMapper().get_int(word)
        feat_int_rep = StringMapper().get_int(feat)
        #word_int_rep = word
        #feat_int_rep = feat
        feats_dic = Utils.get_or_create(self.__word_to_feat__, word_int_rep, dict())
        Utils.add_or_increase_key(feats_dic, feat_int_rep)
        Utils.add_or_increase_key(self.__feat_to_total_count__, feat_int_rep)
        Utils.add_or_increase_key(self.__word_to_total_count__, word_int_rep)
        self.__total_pairs__ += 1

    def __calculate_pmi__(self, word, feat):
        return max(math.log(float(self.__word_to_feat__[word][feat] * self.__total_pairs__) / (
            self.__word_to_total_count__[word] * self.__feat_to_total_count__[feat])), 0)

    def initialize_pmi_matrix(self, word_freq):
        key_list = list(self.__word_to_feat__.keys())
        for word in key_list:
            if word_freq[word] > Consts.WORD_FREQ_THRES:
                self.__word_to_normalized_pmi__[word] = dict()
                word_features = self.__word_to_feat__[word]
                pmi_vector = list()
                for feat in word_features:
                    pmi = self.__calculate_pmi__(word, feat)
                    self.__word_to_normalized_pmi__[word][feat] = pmi
                    pmi_vector.append(pmi)
                norm = linalg.norm(numpy.array(pmi_vector))
                for feat in word_features:
                    self.__word_to_normalized_pmi__[word][feat] /= norm

            self.__word_to_feat__.pop(word)

    def get_similarity_score(self, word_a, word_b):
        sim_score = 0
        word_a_features = self.__word_to_normalized_pmi__[word_a]
        word_b_features = self.__word_to_normalized_pmi__[word_b]

        for feat in word_a_features:
            if feat in word_b_features:
                sim_score += word_a_features[feat] * word_b_features[feat]

        return sim_score

    def get_top_similar_words(self, word, k):
        similar_words = list()
        word = StringMapper().get_int(word)
        for other_word in self.__word_to_normalized_pmi__:
            if word != other_word:
                similar_words.append((other_word, self.get_similarity_score(word, other_word)))

        similar_words.sort(key=lambda tup: tup[1], reverse=True)

        english_similiar_words = map(lambda int_rep_word: StringMapper().get_string(int_rep_word[0]), similar_words[:k])
        #english_similiar_words = similar_words[:k]
        return english_similiar_words
