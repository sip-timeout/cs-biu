import sys
import re

# globals
allTags=[]
tagToIndex = {}
featureMap = {}
featToCount = {}
idxToFeat = {}
wordMap = {}
regexArr = []
featureCount = 0;
featureVectors = [];
#util funcs
def getPair(tup):
    splittedWord = tup.split('/')
    return "".join(splittedWord[0:-1]), splittedWord[-1]

def increaseCount(map, key):
    if key not in map:
        map[key] = 0
    map[key]+=1

#funcs
def processLine(l,func):
    words = [['###start###','start'], ['###start###', 'start']] +  map((lambda word: getPair(word)), l.split(' ')) + [['###end###','end'],['###end###','end']]
    func(words)

def getFeature(feat):
    global featureCount
    global featToCount
    if feat in featureMap:
        featToCount[featureMap[feat]] += 1
        return featureMap[feat]
    else:
        featureCount += 1
        featureMap[feat]=featureCount
        idxToFeat[featureCount] = feat
        featToCount[featureCount] = 1
        return featureCount

def getWordFeature(word):
    return appendFeat([],'w-'+word)

def appendFeat(fv,feat):
    fv.append(getFeature(feat))
    return fv

def getRareFeatures(word):
    rv = []
    runLen = min(5,len(word)+1)
    for i in range(1,runLen):
        appendFeat(rv,'p-'+word[0:i])
        appendFeat(rv, 's-'+word[-i:])
    if re.match('[0-9]',word):
        appendFeat(rv,'digit')
    if re.match('[A-Z]',word):
        appendFeat(rv,'upper')
    if re.match('-',word):
        appendFeat(rv,'hyphen')
    return rv

def getEnvFeatures(env):
    fv = []

    appendFeat(fv,'pt-'+env[1][1])
    appendFeat(fv, 'ppt-' + env[0][1] +'@' + env[1][1])

    appendFeat(fv, 'pw-' + env[1][0])
    appendFeat(fv, 'ppw-' + env[0][0])
    appendFeat(fv,'nw-'+env[2][0])
    appendFeat(fv, 'nnw-' + env[3][0])

    return fv

def calculateFeatures(words):
    for i in range(0,len(words)):
        if words[i][1]!='start' and words[i][1]!='end':
            fv= []
            curWord = words[i][0]
            if wordMap[curWord] > 4:
                fv += getWordFeature(curWord)
            else:
                fv+= getRareFeatures(curWord)

            envFeat = getEnvFeatures(words[i - 2:i] + words[i + 1:i + 3])
            fv += envFeat

            featureVectors.append([list(set(fv)),tagToIndex[words[i][1]]])

def calculateWords(words):
    for tup in words:
        word,tag = tup
        if tag!='start' and tag!='end':
            increaseCount(wordMap, word)


def extractAllTags(lines):
    global allTags
    for line in lines:
        for tup in line.split(' '):
            allTags.append(getPair(tup)[1])
    allTags = list(set(allTags + ['start', 'end']))


def createTagsMap():
    i=0
    for tag in allTags:
        tagToIndex[tag]=i
        i+=1

def createTrainingFile(outputFile):
    with open(outputFile, 'w') as f:
        for fv in featureVectors:
            fv[0].sort()
            #filteredFeatures = filter(lambda feat: featToCount[feat] > 10,fv[0])
            vectorString = ' '.join(map(lambda feat: str(feat)+':1',fv[0]))
            #englishVector = ' '.join(map(lambda feat: idxToFeat[feat] + ':1', fv[0]))
            f.write(str(fv[1])+' '+ vectorString + '\n')
            #f.write(str(allTags[fv[1]]) + ' ' + englishVector+ '\n')

def createFeaturesFile(outputFile):
    with open(outputFile, 'w') as f:
        for i in range(1,featureCount+1):
            f.write(idxToFeat[i] + '_' + str(i)+'\n')

def createTagsFile(outputFile):
    with open(outputFile, 'w') as f:
        f.write('\n'.join(('@'.join([val, str(i)]) for i, val in enumerate(allTags))))



with open(sys.argv[1]) as f:
    lines = f.read().splitlines()

extractAllTags(lines)
createTagsMap()


for l in lines:
    processLine(l,calculateWords)

for l in lines:
    processLine(l,calculateFeatures)

createTrainingFile('train2.txt')
createFeaturesFile('features.txt')
createTagsFile('tags.txt')
print featureCount
print('finished processing file.')