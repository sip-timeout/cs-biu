import sys
import re

# globals
allTags=[]
tagToIndex = {}
unigramMap = {}
bigramMap = {}
trigramMap = {}
transitionMap = {}
wordMap = {}
classMap = {}
regexArr = []

#lambdas
l1 = 0.64
l2 = 0.31
l3 = 0.05

#util funcs
def getPair(tup):
    splittedWord = tup.split('/')
    return "".join(splittedWord[0:-1]), splittedWord[-1]

def increaseCount(map, key):
    if key not in map:
        map[key] = 0
    map[key]+=1

def mapToStrings(dict):
    return map(lambda k: '_'.join([k, str(dict[k])]),dict)

def tranMapToStrings(dict):
    return map(lambda k: '<->'.join([k, str(dict[k])]),dict)

def sumArray(arr):
    return reduce(lambda x, y: x + y, arr)

def wordMapToStrings(dict):
    return map(lambda k: '_'.join([k, str(dict[k])])+'@'+str(sumArray(dict[k])),dict)

def getOrZero(map,key):
    value = 0
    if key in map:
        value = map[key]
    return value

def safeDiv(n,d):
    if n == 0:
        return 0

    return float(n)/float(d)

#funcs
def processLine(l):
    words =[['###start###', 'start'], ['###start###', 'start']] + map((lambda word: getPair(word)), l.split(' '))
    calculateEmissions(words)
    calculateTramsitions(words)

def calculateTramsitions(words):
    tags = map(lambda tup: tup[1],words)
    for i in range(0,len(tags)):
        if  tags[i] != 'end':
            increaseCount(unigramMap, tags[i])
            increaseCount(bigramMap, '@'.join(tags[i:i + 2]))
            increaseCount(trigramMap,'@'.join(tags[i:i+3]))

def calculateWordClasses(word,tag,index):
    for regex,cls in regexArr:
        if (index==0):
            word = word.lower()
        if re.match(regex,word):
            classMap[cls][tagToIndex[tag]] += 1
            break

def calculateEmissions(words):
    i = 0
    for tup in words:
        word,tag = tup
        if tag != 'start' and tag != 'end':
            if word not in wordMap:
                wordMap[word] = [0] * len(allTags)
            wordMap[word][tagToIndex[tag]]+=1
            calculateWordClasses(word,tag,i-2)
            i+=1

def extractAllTags(lines):
    global allTags
    for line in lines:
        for tup in line.split(' '):
            allTags.append(getPair(tup)[1])
        allTags = list(set(allTags + ['start']))


def createTagsMap():
    i=0
    for tag in allTags:
        tagToIndex[tag]=i
        i+=1

def initClassMapping():
    global regexArr
    global classMap
    with open('classes.txt') as f:
        lines = f.read().splitlines()
    for line in lines:
        key,_,val = line.partition('@@@')
        regexArr.append([key,val])
        classMap[val] = [0] * len(allTags)

def calcTriplet(a,b,c,allWordsCount):
    return (l1 * safeDiv(getOrZero(trigramMap,'@'.join([a,b,c])),getOrZero(bigramMap,'@'.join([a, b]))) +
            l2 * safeDiv(getOrZero(bigramMap,'@'.join([b, c])),getOrZero(unigramMap,b)) +
            l3 * safeDiv(getOrZero(unigramMap,c),allWordsCount))

def createTransitionMap():
    allWordsCount = sumArray(unigramMap.values())
    for a in allTags:
        for b in allTags:
            tagsWithoutStart = list(allTags)
            tagsWithoutStart.remove('start')
            for c in tagsWithoutStart:
                transitionMap[' '.join([a,b,c])] = calcTriplet(a,b,c,allWordsCount)



def createTransitionsFile(outputFile):
    with open(outputFile,'w') as f:
        f.write('\n'.join(tranMapToStrings(transitionMap)))

def createEmissionsFile(outputFile):
    with open(outputFile, 'w') as f:
        f.write('\n'.join(['!TAGS_IN_FILE!',
                  '###'.join(('@'.join([val,str(i)]) for i, val in enumerate(allTags))),
                  '!SINGLE_POS_QUANTITIES!'] +
                  mapToStrings(unigramMap) +
                  ['!WORD_QUANTITIES!'] +
                  wordMapToStrings(wordMap)+
                  ['!SIGNATURE_QUANTITIES!']+
                  mapToStrings(classMap)));

with open(sys.argv[1]) as f:
    lines = f.read().splitlines()

extractAllTags(lines)
createTagsMap()
initClassMapping()

for l in lines:
    processLine(l)

createTransitionMap()
createTransitionsFile('q.mle')
createEmissionsFile('e.mle')
print('finished processing file.')