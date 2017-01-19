from corpus_entry import CorpusEntry
from all_content_co_occurence_calculator import AllContentCoOccurrenceCalculator
from utils import Utils
from window_content_co_occurence_calculator import WindowContentCoOccurrenceCalculator
from dependency_co_occurrence_calculator import DependencyCoOccurrenceCalculator
from word_freq_calculator import WordFreqCalculator
from word2vec_evaluate import Word2vecEvaluate

import gc

def get_sentences(input_file_path):
    cur_sentence = list()

    with open(input_file_path) as input_file:
        for line in input_file:
            line = line.rstrip('\n')
            if line != '':
                cur_sentence.append(CorpusEntry(line))
            else:
                yield cur_sentence
                cur_sentence = list()


if __name__ == "__main__":
    limit = 1000000

    freq_calc = WordFreqCalculator()
    calculators = [AllContentCoOccurrenceCalculator(), WindowContentCoOccurrenceCalculator(),
                   DependencyCoOccurrenceCalculator(), freq_calc]
    needed_words = ['car', 'bus', 'hospital', 'hotel', 'gun', 'bomb', 'horse', 'fox', 'table', 'bowl', 'guitar',
                    'piano']

    # calculators = [AllContentCoOccurrenceCalculator(),freq_calc]
    # needed_words = ['car']

    results = dict()


    w2vE = Word2vecEvaluate()
    d_bow5 = w2vE.evaluate("bow5.words", needed_words)

    calc_entry = Utils.get_or_create(results, 'word2vec_d_bow5', dict())
    for word in d_bow5:
        calc_entry[word] = d_bow5[word]

    d_deps = w2vE.evaluate("deps.words", needed_words)
    calc_entry = Utils.get_or_create(results, 'word2vec_deps', dict())

    for word in d_deps:
        calc_entry[word] = d_deps[word]

    w2vE = None
    print ""

    while len(calculators) > 0:
        calc = calculators.pop()
        i = 1
        sentences = get_sentences('trainAll')
        for sentence in sentences:
            calc.process_sentence(sentence)
            if i % 10000 == 0:
                print 'processed sentence ' + str(i)
            i += 1
            if i > limit:
                break
        if calc != freq_calc:
            calc.initialize_pmi_matrix()
            calc_entry = Utils.get_or_create(results, calc.get_name(), dict())
            for word in needed_words:
                calc_entry[word] = calc.get_top_similar_words(word, 20)
                print 'calculated similarities for ' + word

    freq_calc = None
    calc = None

    for word in needed_words:
        print 'Similarities for ' + word
        types = '\t'.join(results.keys())
        print types.expandtabs(20)
        for i in range(0, 20):
            row = ''
            for type in results:
                row += results[type][word][i] + '\t'
            print row.expandtabs(20)
