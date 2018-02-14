#!/usr/bin/env python

'''A Penn Treebank-style tree
   author: Liang Huang <lhuang@isi.edu>
   modified: by Ali to add "binarize()", "deBinarize()" and "getProductions()"
'''

import sys
logs = sys.stderr

class Tree(object):

    def __init__(self, label, span, wrd=None, subs=None):

        assert (wrd is None) ^ (subs is None), \
               "not good tree %s %s %s" % (label, wrd, subs)
        self.subs = subs
        self._str = None
        self.span = span
        self.word = wrd
        self._hash = None
        self.label = label


    def is_terminal(self):
        return self.word is not None

    def dostr(self):
        return "(%s %s)" % (self.label, self.word) if self.is_terminal() \
               else "(%s %s)" % (self.label, " ".join(map(str, self.subs)))

    def __str__(self):
        if True or self._str is None:
            self._str = self.dostr()
        return self._str


    def deBinarize(self):
        '''Assumes that this is a binary tree. if a node has more than 2 children, we MIGHT mess up'''

        if self.subs is not None:

            while self.subs[-1].label[-1] == "'":
                rhsNode = self.subs[-1]

                rhsLabel = rhsNode.label
                #print rhsLabel
                if rhsLabel[-1] == "'":  #apostrophe indicates this is a temp node, the result of binarization
                    #take both children of this node
                    #remove it from the list

                    #print "this node requires fixing"
                    self.subs.pop()

                    self.subs.extend(rhsNode.subs)

        if self.subs is not None:
            for child in self.subs:
                child.deBinarize()





