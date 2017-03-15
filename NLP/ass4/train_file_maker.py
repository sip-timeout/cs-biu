

class TrainFileMaker:
    def __init__(self, train_file_path):
        self.train_file_path = train_file_path




    def make(self, candidates):

        with open(self.train_file_path, 'w') as output_file:
            for cand in candidates:
                line = ''
                line += str(cand['train_class']) + ' '
                d = cand['features']
                vector_string = ' '.join(map(lambda feat: str(feat) + ':1', sorted(list(set(d)))))
                line += vector_string

                output_file.writelines([line+'\n'])


