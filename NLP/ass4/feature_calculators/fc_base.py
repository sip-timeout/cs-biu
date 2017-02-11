from feature_manager import FeatureManager


class FC_Base:
    def __init__(self):
        pass

    def process(self, sent):
        for candidate in sent['candidates']:
            candidate['features'] = list()
            for feat in self.get_features(sent, candidate['ent1'],candidate['ent2']):
                feat_id = FeatureManager().get_feat_id(feat)
                if feat_id:
                    candidate['features'].append(feat_id)
