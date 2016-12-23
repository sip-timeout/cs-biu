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
    return tup, ''

#funcs
def processLine(l,func,i):
    words = [['###start###','start'], ['###start###', 'start']] +  map((lambda word: getPair(word)), l.split(' ')) + [['###end###','end'],['###end###','end']]
    func(words,i)

def getFeature(feat):
    global featToCount
    if feat in featureMap:
        return featureMap[feat]
    else:
        return None

def getWordFeature(word):
    return appendFeat([],'w-'+word)

def appendFeat(fv,feat):
    featureId = getFeature(feat)
    if featureId:
        fv.append(featureId)
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

    appendFeat(fv, 'pw-' + env[1][0])
    appendFeat(fv, 'ppw-' + env[0][0])
    appendFeat(fv,'nw-'+env[2][0])
    appendFeat(fv, 'nnw-' + env[3][0])

    return fv

def calculateFeatures(words,lineIdx):
    global featureVectors
    featureVectors.append([])
    for i in range(0,len(words)):
        if words[i][1]!='start' and words[i][1]!='end':
            fv= []
            curWord = words[i][0]
            fv += getWordFeature(curWord)

            #if word feature does not exist:
            if (len(fv) == 0):
                fv += getRareFeatures(curWord)

            envFeat = getEnvFeatures(words[i - 2:i] + words[i + 1:i + 3])
            fv += envFeat

            featureVectors[lineIdx].append(list(set(fv)))

def createFeatuesMap(featureLines):
    for l in featureLines:
        splitted = l.split('_')
        featureMap[splitted[0]] = int(splitted[1])

def createWordFeatuesFile(outputFile):
    with open(outputFile, 'w') as f:
        for lineVector in featureVectors:
            wordFeatures = []
            for fv in lineVector:
                fv.sort()
                #filteredFeatures = filter(lambda feat: featToCount[feat] > 10,fv[0])
                vectorString = ','.join(map(lambda feat: str(feat),fv))
                #englishVector = ' '.join(map(lambda feat: idxToFeat[feat] + ':1', fv[0]))
                wordFeatures.append(vectorString)
            f.write('_'.join(wordFeatures)+'\n')


with open(sys.argv[1]) as f:
    lines = f.read().splitlines()

with open(sys.argv[2]) as f:
    featureLines = f.read().splitlines()

createFeatuesMap(featureLines)

i=0
for l in lines:
    processLine(l,calculateFeatures,i)
    i+=1
createWordFeatuesFile('fileFeatures.txt')
print('finished processing file.')