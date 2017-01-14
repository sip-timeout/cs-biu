from corpus_entry import CorpusEntry
from all_content_co_occurence_calculator import AllContentCoOccurrenceCalculator
from window_content_co_occurence_calculator import WindowContentCoOccurrenceCalculator
from word_freq_calculator import WordFreqCalculator


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
    calculators = [AllContentCoOccurrenceCalculator(), WindowContentCoOccurrenceCalculator(), freq_calc]
    needed_words = ['car', 'bus', 'hospital', 'hotel', 'gun', 'bomb', 'horse', 'fox', 'table', 'bowl', 'guitar',
                    'piano']

    while len(calculators) > 0:
        calc = calculators.pop()
        i = 1
        sentences = get_sentences('trainAll')
        for sentence in sentences:
            calc.process_sentence(sentence)
            if i % 500 == 0:
                print 'processed sentence ' + str(i)
            i += 1
            if i > limit:
                break

        if calc != freq_calc:
            calc.initialize_pmi_matrix()
            for word in needed_words:
                print 'words similar to ' + word + ':' + calc.get_top_similar_words(word, 20)
