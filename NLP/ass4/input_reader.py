from corpus_entry import CorpusEntry


class InputReader:
    def __init__(self, input_file):
        self.input_file_path = input_file

    def get_sentences_generator(self):
        sent = dict()
        corpus_entries = list()

        with open(self.input_file_path) as input_file:
            for line in input_file:
                line = line.rstrip('\n')

                if line.startswith('#id'):
                    sent['id'] = line[line.find(':') + 2:]
                elif line.startswith('#text'):
                    sent['text'] = line[line.find(':') + 2:]
                elif line != '':
                    corpus_entries.append(CorpusEntry(line))
                else:
                    sent['entries'] = corpus_entries
                    yield sent
                    sent = dict()
                    corpus_entries = list()
