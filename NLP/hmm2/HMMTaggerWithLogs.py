import sys
import re
import os
import math

bad_score = -100

class MapCreator:
    def __init__(self):
        self.tagsSet = list()
        self.majority = 'NN'
        self.regexpMap = dict()
        self.wordsList = dict()
        self.regexOp = []

    def initRegexOp(self, fileName):
        inFile = open(fileName, 'r')

        for line in inFile:
            line = line.replace('\n','')
            splitted = line.split('@@@')
            self.regexOp.append(splitted)

        inFile.close()
        return self.regexOp

    def seperate(self, fileName):
        inFile = open(fileName, 'r')
        tagMap = {}
        posMap = {}
        wordMap = {}
        sigMap = {}

        mode = 0
        for line in inFile:
            line = line.replace('\n','')
            # if "#majority#<->" in line:
            #     self.majority = line.split('<->')[1].rstrip()
            if line == '!TAGS_IN_FILE!':
                mode = 1
            elif line =='!SINGLE_POS_QUANTITIES!':
                mode = 2
            elif line == '!WORD_QUANTITIES!':
                mode = 3
            elif line == '!SIGNATURE_QUANTITIES!':
                mode = 4
            else:
                if mode == 1:
                    self.tagsSet = map(lambda tag: tag.split('@')[0],line.split('###'))
                    for i in range(0,len(self.tagsSet)):
                        tagMap[self.tagsSet[i]] = i
                elif mode == 2:
                    splitted = line.split('_')
                    posMap[tagMap[splitted[0]]] = splitted[1]
                elif mode == 3:
                    splitted = line.split('_')
                    sndSplit = splitted[1].split('@')
                    if int(sndSplit[1]) < 5:
                        continue
                    self.wordsList[splitted[0]] = True
                    wordArr = sndSplit[0].lstrip('[').rstrip(']').replace(' ', '').split(',')
                    for i in range(0,len(wordArr)):
                        if wordArr[i] == '0':
                            continue
                        wordMap[splitted[0]+' '+self.tagsSet[i]] = self.doLog(float(wordArr[i]) / float(posMap[i]) )
                elif mode == 4:
                    splitted = line.split('_')
                    wordArr = splitted[1].lstrip('[').rstrip(']').replace(' ', '').split(',')
                    for i in range(0, len(wordArr)):
                        sigMap[splitted[0] + ' ' + self.tagsSet[i]] = self.doLog(float(wordArr[i]) / float(posMap[i]))


        inFile.close()

        self.regexpMap= sigMap
        return wordMap

    def getWords(self):
        return self.wordsList

    def getRegexpMap(self):
        return self.regexpMap

    def  doLog(self,x):
        if x==0:
            return bad_score
        else:
            return math.log(x)

    def getMajority(self):
        return self.majority

    def createTagsSet(self, fileName):
        tagsFile = open(fileName, 'r')
        newMap = dict()
        for line in tagsFile:
            lineArr = line.split("<->")
            if len(lineArr) > 1:
                key = lineArr[0]
                val = self.doLog(float(lineArr[1]))
                newMap[key] = val

        tagsFile.close()
        return newMap

    def getTags(self):
        return self.tagsSet



class Path:
    def __init__(self):
        self.path = list()
        self.length = 0
        self.currentValue = 1

    def getLength(self):
        return self.length

    def setPath(self, path):
        self.path = path
        self.length = len(path)

    def add(self, item):
        self.path.append(item)
        self.length += 1

    def getPath(self):
        return self.path

    def getValue(self):
        return self.currentValue

    def setValue(self, val):
        self.currentValue = val
        
    def getItem(self, index):
        if index < self.length:
            return self.path[index]
        else:
            return None

class ViterbiAlgo:
    def __init__(self, tags, calculator, majorityTag):
        self.tags = tags
        self.vCalc = calculator
        self.majority = majorityTag
        self.mis = 0
        
        
    def doViterbi(self, lineArr):
        vitMat = []
        for a in range(0, len(self.tags)):
            vitMat.append([])
            for b in range(0, len(self.tags)):
                vitMat[a].append(Path())
                vitMat[a][b].add(self.tags[a])
                val = self.vCalc.calcInit(self.tags[a], lineArr[0])
                val += self.vCalc.getValue(self.tags[b], vitMat[a][b], lineArr[1])
                vitMat[a][b].add(self.tags[b])
                vitMat[a][b].setValue(val)

        for wordIndex in range(2, len(lineArr)):
            nextVitMat = []
            for a in range(0, len(self.tags)):
                nextVitMat.append([])
                for b in range(0, len(self.tags)):
                    nextVitMat[a].append(Path())
            for c in range(0, len(self.tags)):
                argMax = []
                valMax = -sys.maxint
                for b in range(0, len(self.tags)):
                    for a in range(0, len(self.tags)):
                        vPath = vitMat[a][b]
                        vProb = self.vCalc.getValue(self.tags[c], vPath, lineArr[wordIndex])

                        if vProb > valMax:
                            argMax = list(vPath.getPath()) + [self.tags[c]]
                            valMax = vProb

                    nextVitMat[b][c] = Path()
                    nextVitMat[b][c].setPath(argMax)
                    nextVitMat[b][c].setValue(valMax)
            vitMat = nextVitMat

        max_val = -sys.maxint
        maxPath = None
        for a in range(0, len(self.tags)):
            for b in range(0, len(self.tags)):
                if vitMat[a][b].getValue() > max_val:
                    max_val = vitMat[a][b].getValue()
                    maxPath = list(vitMat[a][b].getPath())

        return maxPath              

                
                
                
    

class ViterbiCalculator:
    def __init__(self, eMap, qMap, regexpMap,regexOp, words):
        self.eMap = eMap
        self.qMap = qMap
        self.regexpMap = regexpMap
        self.regexOp = regexOp
        self.words = words
    #calculates max scure using regexp table
    def getMax(self, word, tag):
        maxVal = 0
        for key in self.regexpMap:
            reg = key.split(" ")[0]
            keyTag = key.split(" ")[1]
            if re.match(reg, word) and keyTag == tag:
                if self.regexpMap[key] > maxVal:
                    maxVal = self.regexpMap[key]
                    return maxVal
        return 0
            
    #claculates score for ginven triple (key_q) word+tag (key_e) and tag.
    def calc(self, key_q, key_e, val, tag):
        if key_q in self.qMap:
            qRes = self.qMap[key_q]
            eRes = bad_score
            if key_e in self.eMap:
                eRes = self.eMap[key_e]
            else:
                word = key_e.split(" ")[0]
                if word not in self.words:
                    for reg in self.regexOp:
                        if re.match(reg[0],word):
                            eRes = self.regexpMap[reg[1]+' '+tag]
                            break

            result = val + qRes + eRes
            return result
        else:
            return val + bad_score

    #calculates score for first word in the sentence
    def calcInit(self, tag, word):
        a = "start"
        b = "start"
        key_q = a + " " + b + " " + tag
        key_e = word + " " + tag
        return self.calc(key_q, key_e, 0, tag)

    #creates the patterns to calculate scores for
    def getValue(self, tag, pathObj, word):
        pathLength = pathObj.getLength()

        if pathLength > 1:
            a = pathObj.getItem(pathLength - 2)
            b = pathObj.getItem(pathLength - 1)
            key_q = a + " " + b + " " + tag
            key_e = word + " " + tag
            return self.calc(key_q, key_e, pathObj.getValue(), tag)
        elif pathLength == 1:
            a = "start"
            b = pathObj.getItem(pathLength - 1)
            key_q = a + " " + b + " " + tag
            key_e = word + " " + tag
            return self.calc(key_q, key_e, pathObj.getValue(), tag)
        else:
            a = "start"
            b = "start"
            key_q = a + " " + b + " " + tag
            key_e = word + " " + tag
            return self.calc(key_q, key_e, pathObj.getValue(), tag) 
            


class ViterbiOperator:
    def __init__(self, viterbiAlgo):
        self.viterbiAlgo = viterbiAlgo

    #break the file into lines and calculate stags for each line
    def operate(self, inputFile, outFile):
        toTagInput = open(inputFile, 'r')
        toWrite = open(outFile, 'w')
        lineNum = 1
        lines = toTagInput.readlines()
        for line in lines:
            line = line.rstrip()
            lineArr = line.split(" ")
            path = self.viterbiAlgo.doViterbi(lineArr)
            i = 0
            for tag in path:
                if i < len(lineArr) - 1:
                    toWrite.write(lineArr[i] + "/" + tag + " ")
                else:
                    toWrite.write(lineArr[i] + "/" + tag)
                i += 1
            print "line:", lineNum
            lineNum += 1
            if lineNum <= len(lines):
                toWrite.write("\n")
        toTagInput.close()
        toWrite.close()

def main(argv):
    mm = MapCreator()
    #should be given by argv!
    eMap = mm.seperate("e.mle")
    regexpMap = mm.getRegexpMap()
    majorityTag = mm.getMajority()
    qMap = mm.createTagsSet("q2.mle")
    tagsList = mm.getTags()
    words = mm.getWords()
    regexOp = mm.initRegexOp("classes.txt")
    vCalc = ViterbiCalculator(eMap, qMap, regexpMap,regexOp, words)
    vAlgo = ViterbiAlgo(tagsList, vCalc, majorityTag)
    vOper = ViterbiOperator(vAlgo)
    print "start working calculating..."
    #should be given by argv!
    vOper.operate("tagsTest.txt", "output.txt")
    



if __name__ == "__main__":
    main(sys.argv)
