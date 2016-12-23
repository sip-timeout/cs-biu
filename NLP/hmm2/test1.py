import os
import re

"""if re.match(r'(.)*', "Ab112233ddsds"):
    print "Match!"
input()"""

newCorpus = open("output.txt", 'r')
oldCorpus = open("tagtestAnswers.txt", 'r')

listOld = list()
count = 0
for line in oldCorpus:
    lineArr = line.split(" ")
    for word in lineArr:
            listOld.append(word)
            count += 1

mistakes = 0
i = 0
j = 1
for line in newCorpus:
    lineArr = line.split(" ")
    for word in lineArr:
        if word != listOld[i]:
            print str(j) + ": old: " + listOld[i] + " : " + "new: " + word
            j += 1
            mistakes += 1
        i += 1

total = float(mistakes)/count
total *= 100
total = 100 - total
print count
print total
