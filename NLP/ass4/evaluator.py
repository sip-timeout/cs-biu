import sys

from consts import Consts
from pre_processors.annotation_creator import AnnotationsCreator

ann_creator = AnnotationsCreator(sys.argv[2])
input_file_path = sys.argv[1]

counters = {'correct': {'Work_For': 0.0, 'Lives_In': 0.0},
            'made': {'Work_For': 0.0, 'Lives_In': 0.0},
            'total': {'Work_For': 0.0, 'Lives_In': 0.0}}

class_map = {Consts.LIVES_IN_ID: 'Lives_In', Consts.WORK_FOR_ID: 'Work_For'}

with open(input_file_path) as input_file:
    sent_id = ''
    for line in input_file:
        line = line.rstrip('\n')

        if line.startswith('sent'):
            sent_id = line[:line.find(':')]
        elif line != '':
            prediction = line.split('\t')
            counters['made'][prediction[1]] += 1
            for anot in filter(lambda annot: annot['type'] != Consts.NONE_ID,
                               ann_creator.sentences_annotations[sent_id]):
                counters['total'][class_map[anot['type']]] += 1
                if ann_creator.either_contained(prediction[0], anot['ent1']) \
                        and ann_creator.either_contained(prediction[2], anot['ent2']) \
                        and prediction[1] == class_map[anot['type']]:
                    counters['correct'][prediction[1]] += 1

for rel_type in class_map.values():
    precision = counters['correct'][rel_type] / counters['made'][rel_type]
    recall = counters['correct'][rel_type] / counters['total'][rel_type]
    precision = counters['correct'][rel_type] / counters['made'][rel_type]
    f1 = (2*(precision*recall)) / (precision+recall)
    print '%s - Precision:%f, Recall:%f, F1:%f' % (rel_type,precision,recall,f1)

