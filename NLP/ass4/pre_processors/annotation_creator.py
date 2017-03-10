from utils import Utils
from consts import Consts


class AnnotationsCreator:
    def __init__(self, annotations_file):
        self.sentences_annotations = {}
        self.create_annotations(annotations_file)

    def either_contained(self, str1, str2):
        return str1 in str2 or str2 in str1

    def get_relation_type(self, rel):
        if rel == 'Live_In':
            return Consts.LIVES_IN_ID
        elif rel == 'Work_For':
            return Consts.WORK_FOR_ID
        else:
            return Consts.NONE_ID

    def create_annotations(self, annotations_file):
        with open(annotations_file) as input_file:
            for line in input_file:
                line = line.rstrip('\n')

                ann_parts = line.split('\t')

                sent_id = ann_parts[0]
                annotation = {'ent1': ann_parts[1], 'ent2': ann_parts[3], 'type': self.get_relation_type(ann_parts[2])}

                sent_annot = Utils.get_or_create(self.sentences_annotations, sent_id, list())
                sent_annot.append(annotation)

    def print_unmatched(self):
        for key in self.sentences_annotations:
            annotations = self.sentences_annotations[key]
            for ann in annotations:
                if not 'match' in ann:
                    print ' '.join([str(val) for val in ann.values()])

    def preprocess(self, sent):
        annotations = self.sentences_annotations[sent['id']]

        for annotation in annotations:
            for cand in sent['candidates']:
                if self.either_contained(cand['ent1']['text'], annotation['ent1']) \
                        and self.either_contained(cand['ent2']['text'], annotation['ent2']):
                    cand['train_class'] = annotation['type']
                    annotation['match'] = True
