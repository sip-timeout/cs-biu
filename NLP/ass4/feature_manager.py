import json
from singleton import Singleton
from consts import Consts

class FeatureManager(object):
    __metaclass__ = Singleton

    def __init__(self, tag_mode=False):
        self.feat_to_id = dict()
        self.id_to_feat = dict()

        if tag_mode:
            with open(Consts.FEAT_TO_ID_FILE_NAME, 'r') as fi_file:
                self.feat_to_id = json.load(fi_file)
            with open(Consts.ID_TO_FEAT_FILE_NAME, 'r') as if_file:
                self.id_to_feat = json.load(if_file)

        self.cur_idx = 0
        self.tag_mode = tag_mode

    def get_feat_id(self, feat_name):
        if feat_name not in self.feat_to_id:
            if self.tag_mode:
                return None
            else:
                self.feat_to_id[feat_name] = self.cur_idx
                self.id_to_feat[self.cur_idx] = feat_name
                self.cur_idx += 1
        return self.feat_to_id[feat_name]

    def get_feat_name(self, feat_id):
        feat_name = None
        if feat_id in self.id_to_feat:
            feat_name = self.id_to_feat[feat_id]
        return

    def export(self):
        if not self.tag_mode:
            with open(Consts.FEAT_TO_ID_FILE_NAME,'w') as fi_file:
                json.dump(self.feat_to_id,fi_file)
            with open(Consts.ID_TO_FEAT_FILE_NAME, 'w') as if_file:
                json.dump(self.id_to_feat, if_file)