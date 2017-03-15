import sys
import itertools
import subprocess

from consts import Consts
from pre_processors.candidates_extractor import CandidatesExtractor
from pre_processors.entity_extractor import EntityExtractor
from feature_calculators.entity_based_fc import EntityBasedFC
from feature_calculators.BOWFeatures import BOWFeatures
from feature_calculators.overlap_features import OverLapFeatures
from input_reader import InputReader
from feature_manager import FeatureManager
from train_file_maker import TrainFileMaker
from result_file_maker import ResultFileMaker
import utils

FeatureManager(tag_mode=True)
ex = CandidatesExtractor()
pre_processors = [EntityExtractor(),ex]
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



all_cands = ex.filter_candidates(sentences)

TrainFileMaker(Consts.FEATURE_FILE_NAME).make(all_cands)

subprocess.call(['java','-Xmx1g','-cp','liblinear.jar','de.bwaldvogel.liblinear.Predict',Consts.FEATURE_FILE_NAME,'train_model',Consts.PREDICTION_FILE_NAME])

with open(Consts.PREDICTION_FILE_NAME) as pred_file:
    for i,line in enumerate(pred_file):
        all_cands[i]['class'] = int(line[0])

ResultFileMaker(Consts.RESULT_FILE_NAME).make(sentences)


