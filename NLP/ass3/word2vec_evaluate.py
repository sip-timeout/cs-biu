import numpy as np


class Word2vecEvaluate:            
    def evaluate(self, fileName, words_to_check):
        inFile = open(fileName)
        w_mat = []
        w_vec = []
        i = 0
        isCreated = False
        #extracting data (large files cause memory errors so work in chunks of 10000)
        for line in inFile:
            if (i % 10000) == 0:
                print "line number:", i
            i += 1
            lineArr = line.split(" ")
            w_vec.append(lineArr[0])
            vec = lineArr[1:]
            w_mat.append(vec)
            if (i % 10000) == 0:
                if isCreated:
                    words = np.append(words, w_vec)
                    np.concatenate((W, np.array(w_mat)), axis=0)
                    w_mat = []
                    w_vec = []
                else:
                    W = np.array(w_mat)
                    words = np.array(w_vec)
                    w_vec = []
                    w_mat = []
                    isCreated = True
        #if small file
        if not isCreated:
            W = np.array(w_mat)
            words = np.array(w_vec)
        #convert to float and normalize
        W = W.astype(np.float)
        W /= np.linalg.norm(W)
        w2i = {w : i for i,w in enumerate(words)}

        #create dictionary
        d = dict()
        for word in words_to_check:
            the_vec = W[w2i[word]]
            sims = W.dot(the_vec)
            most_similar = sims.argsort()[-1:-22:-1]
            sim_words = words[most_similar]
            sim_words = sim_words[1:]
            #print "word: " + word + " sim: "  + str(sim_words)
            d[word] = sim_words
        return d




"""w2vE = Word2vecEvaluate()
#w2vE.evaluate("word2vec_1.txt")
my_d = w2vE.evaluate("bow5.words", ['car', 'bus', 'hospital', 'hotel', 'gun', 'bomb', 'horse', 'fox', 'table', 'bowl', 'guitar', 'piano'])
print my_d['car']"""
