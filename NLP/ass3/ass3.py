from corpus_entry import CorpusEntry
from all_content_co_occurence_calculator import AllContentCoOccurrenceCalculator
from window_content_co_occurence_calculator import WindowContentCoOccurrenceCalculator


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
    sentences = get_sentences('trainAll')
    limit = 20000

    calculators = [AllContentCoOccurrenceCalculator(), WindowContentCoOccurrenceCalculator()]
    i = 1
    for sentence in sentences:
        for calc in calculators:
            calc.process_sentence(sentence)
        if i % 500 == 0:
            print 'processed sentence ' + str(i)
        i += 1
        if i > limit:
            break

    for calc in calculators:
        calc.initialize_pmi_matrix()

    for calc in calculators:
        print calc.get_top_similar_words('doctor',20)


