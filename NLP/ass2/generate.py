"""Generate.

Usage:
  generate.py <grammer> [-n <sentences>] [-t]

Options:
  -h --help     Show this screen.
  -n <sentences>  number of sentences [default: 1]
  -t              print tree

"""

from collections import defaultdict
import random
from docopt import docopt
class PCFG(object):
    def __init__(self):
        self._rules = defaultdict(list)
        self._sums = defaultdict(float)


    def add_rule(self, lhs, rhs, weight):
        assert(isinstance(lhs, str))
        assert(isinstance(rhs, list))
        self._rules[lhs].append((rhs, weight))
        self._sums[lhs] += weight

    @classmethod
    def from_file(cls, filename):
        grammar = PCFG()
        with open(filename) as fh:
            for line in fh:
                line = line.split("#")[0].strip()
                if not line: continue
                w,l,r = line.split(None, 2)
                r = r.split()
                w = float(w)
                grammar.add_rule(l,r,w)
        return grammar

    def is_terminal(self, symbol): return symbol not in self._rules

    def gen(self, symbol):
        if self.is_terminal(symbol):
            self.tree+= symbol +' '
            return symbol
        else:

            self.depth+=1
            expansion = self.random_expansion(symbol)
            self.tree+='('+symbol +' '

            res = " ".join(self.gen(s) for s in expansion)

            self.depth -= 1
            self.tree+=')\n  '+'\t'*self.depth

            return res

    def random_sent(self):
        self.depth = 0
        self.tree = ''
        return self.gen("ROOT")

    def random_expansion(self, symbol):
        """
        Generates a random RHS for symbol, in proportion to the weights.
        """
        p = random.random() * self._sums[symbol]
        for r,w in self._rules[symbol]:
            p = p - w
            if p < 0:
                return r
        return r


if __name__ == '__main__':
    arguments = docopt(__doc__)
    pcfg = PCFG.from_file(arguments['<grammer>'])

    n = int(arguments['-n'])
    t = arguments['-t']

    for i in range(0,n):
        print pcfg.random_sent()
        if t:
            print pcfg.tree
