This script produces e.mle and q.mle for the usage of a HMMTagger.
the e.mle contains counts needed for tagging while the q.mle contains probabilities calculated using the following lambdas:
for trigrams: 0.64
for bigrams: 0.31
for unigrams: 0.05

the q.mle file also contains triplets of the form
### tag1 tag2 <-> 0.
these are actually all of the pairs we saw together, and this is used for the tagger to perform it's pruning.

for unknown words i used the regexes shown in classes.txt,
the class of a word is the first regex matching it, or none if no match could be found.
the script assumes that the classes.txt file is present on its dir.
