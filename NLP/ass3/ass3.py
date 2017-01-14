from corpus_entry import CorpusEntry
from all_content_co_occurence_calculator import AllContentCoOccurrenceCalculator
from window_content_co_occurence_calculator import WindowContentCoOccurrenceCalculator


def get_sentences(input_file_path):
    sentences = list()
    with open(input_file_path) as input_file:
        lines = map(lambda line: line.rstrip('\n'), input_file.readlines())

    cur_sentence = list()
    for line in lines:
        if line != '':
            cur_sentence.append(CorpusEntry(line))
        else:
            sentences.append(cur_sentence)
            cur_sentence = list()

    return sentences


if __name__ == "__main__":
    sentences = get_sentences('train')

    calculators = [AllContentCoOccurrenceCalculator(), WindowContentCoOccurrenceCalculator()]
    sent_len = str(len(sentences))
    i = 1
    for sentence in sentences:
        for calc in calculators:
            calc.process_sentence(sentence)
        print str(i) + ' out of ' + sent_len
        i += 1

