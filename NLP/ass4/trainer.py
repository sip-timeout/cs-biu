import sys
import itertools
import subprocess

from consts import Consts
from pre_processors.candidates_extractor import CandidatesExtractor
from pre_processors.entity_extractor import EntityExtractor
from pre_processors.annotation_creator import AnnotationsCreator
from feature_calculators.entity_based_fc import EntityBasedFC
from feature_calculators.BOWFeatures import BOWFeatures
from feature_calculators.overlap_features import OverLapFeatures
from input_reader import InputReader
from feature_manager import FeatureManager
from train_file_maker import TrainFileMaker

ann_creator = AnnotationsCreator(sys.argv[2])
pre_processors = [EntityExtractor(), CandidatesExtractor(), ann_creator]
feature_calcs = [EntityBasedFC(), BOWFeatures(), OverLapFeatures()]

input_file = sys.argv[1]
# input_file = 'data/Corpus.DEV.processed'

input_rdr = InputReader(input_file)

sentences = list(input_rdr.get_sentences_generator())

for sent in sentences:
    for proc in pre_processors:
        proc.preprocess(sent)
    for calc in feature_calcs:
        calc.process(sent)

all_cands = itertools.chain.from_iterable(map(lambda sent: sent['candidates'], sentences))

TrainFileMaker(Consts.TRAINING_FILE_NAME).make(all_cands)
FeatureManager().export()

subprocess.call(['java','-Xmx1g','-cp','liblinear.jar','de.bwaldvogel.liblinear.Train','-s','0','train_file','train_model'])

