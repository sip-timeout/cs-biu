from corpus_entry import CorpusEntry
from all_content_co_occurence_calculator import AllContentCoOccurrenceCalculator
from window_content_co_occurence_calculator import WindowContentCoOccurrenceCalculator
from dependency_co_occurrence_calculator import DependencyCoOccurrenceCalculator
from word_freq_calculator import WordFreqCalculator
from word2vec_evaluate import Word2vecEvaluate


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
    calculators = [AllContentCoOccurrenceCalculator(), WindowContentCoOccurrenceCalculator(), DependencyCoOccurrenceCalculator(), freq_calc]
    needed_words = ['car', 'bus', 'hospital', 'hotel', 'gun', 'bomb', 'horse', 'fox', 'table', 'bowl', 'guitar',
                    'piano']

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
            for word in needed_words:
                print 'words similar to ' + word + ':' + str(calc.get_top_similar_words(word, 20))

    print ""
    w2vE = Word2vecEvaluate()
    d_bow5 = w2vE.evaluate("bow5.words", needed_words)

    for word in d_bow5:
        print 'words similar to ' + word + ':' + str(d_bow5[word])
    
    d_deps = w2vE.evaluate("deps.words", needed_words)

    for word in d_deps:
        print 'words similar to ' + word + ':' + str(d_deps[word])
