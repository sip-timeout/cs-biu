from consts import Consts

class ResultFileMaker:
    def __init__(self, result_file_path):
        self.result_file_path = result_file_path
        self.class_map = {Consts.LIVES_IN_ID:'Lives_In',Consts.WORK_FOR_ID:'Work_For'}

    def make(self, sentences):
        with open(self.result_file_path, 'w') as output_file:
            for sent in sentences:
                output_file.write(sent['id']+':'+sent['text']+'\n')

                for cand in sent['candidates']:
                    if 'class' in cand and  cand['class'] != Consts.NONE_ID:
                        output_file.write('\t'.join([cand['ent1']['text'],self.class_map[cand['class']],cand['ent2']['text']])+'\n')

                output_file.write('\n')
