import sys


def split_line(line):
    return filter(lambda x: x != '', line.split(' '))


with open(sys.argv[1]) as ret_file:
    with open(sys.argv[2]) as rel_file:
        relevant_words = [line.rstrip('\n') for line in rel_file.readlines()]
        ret_lines = [line.rstrip('\n') for line in ret_file.readlines()]

ret_words = dict()
for idx, tp in enumerate(split_line(ret_lines[0])):
    ret_words[tp] = {'idx': idx, 'word_list': list(), 'ap': 0.0}

for line in ret_lines[1:]:
    line_words = split_line(line)
    for tp in ret_words:
        entry = ret_words[tp]
        entry['word_list'].append(line_words[entry['idx']])

for tp in ret_words:
    entry = ret_words[tp]
    for i in range(1, 21):
        if entry['word_list'][i - 1] in relevant_words:
            j_score = 0.0
            for j in range(0, i):
                if entry['word_list'][j] in relevant_words:
                    j_score += 1
            j_score /= i
            entry['ap'] += j_score
    entry['ap'] /= len(relevant_words)

for tp in ret_words:
    print tp + ':' + str(ret_words[tp]['ap'])
