from utils import Utils


class CoOccurrenceCalculatorBase:
    def __init__(self):
        self.__word_to_feat__ = dict()
        self.__word_to_total_count__ = dict()
        self.__feat_to_total_count__ = dict()
        self.__total_pairs__ = 0

    def __add_feature_to_word__(self, word, feat):
        feats_dic = Utils.get_or_create(self.__word_to_feat__, word, dict())
        Utils.add_or_increase_key(feats_dic, feat)
        Utils.add_or_increase_key(self.__feat_to_total_count__, feat)
        Utils.add_or_increase_key(self.__word_to_total_count__, word)
        self.__total_pairs__ += 1


def get_matrix():
    pass
