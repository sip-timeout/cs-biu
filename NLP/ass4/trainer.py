import sys

from pre_processors.candidates_extractor import CandidatesExtractor
from pre_processors.entity_extractor import EntityExtractor
from feature_calculators.entity_based_fc import EntityBasedFC
from input_reader import InputReader
from feature_manager import FeatureManager

pre_processors = [EntityExtractor(), CandidatesExtractor()]
feature_calcs = [EntityBasedFC()]

input_file = sys.argv[1]
input_rdr = InputReader(input_file)

sentences = list(input_rdr.get_sentences_generator())

for sent in sentences:
    for proc in pre_processors:
        proc.preprocess(sent)
    for calc in feature_calcs:
        calc.process(sent)

FeatureManager().export()