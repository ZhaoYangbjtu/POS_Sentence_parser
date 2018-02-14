#!/usr/bin/env python3
# right branching "parser"
# from  boilerplate code by Jon May (jonmay@isi.edu)
import argparse
import sys
import codecs

import math

if sys.version_info[0] == 2:
  from itertools import izip
else:
  izip = zip
from collections import defaultdict as dd, defaultdict
import re
import os.path
import gzip
import tempfile
import shutil
import atexit
from mtree import Tree

#from matplotlib import pyplot as plt
import time

scriptdir = os.path.dirname(os.path.abspath(__file__))


reader = codecs.getreader('utf8')
writer = codecs.getwriter('utf8')


def prepfile(fh, code):
  if type(fh) is str:
    fh = open(fh, code)
  ret = gzip.open(fh.name, code if code.endswith("t") else code+"t") if fh.name.endswith(".gz") else fh
  if sys.version_info[0] == 2:
    if code.startswith('r'):
      ret = reader(fh)
    elif code.startswith('w'):
      ret = writer(fh)
    else:
      sys.stderr.write("I didn't understand code "+code+"\n")
      sys.exit(1)
  return ret

def addonoffarg(parser, arg, dest=None, default=True, help="TODO"):
  ''' add the switches --arg and --no-arg that set parser.arg to true/false, respectively'''
  group = parser.add_mutually_exclusive_group()
  dest = arg if dest is None else dest
  group.add_argument('--%s' % arg, dest=dest, action='store_true', default=default, help=help)
  group.add_argument('--no-%s' % arg, dest=dest, action='store_false', default=default, help="See --%s" % arg)

def main():
  parser = argparse.ArgumentParser(description="trivial right-branching parser that ignores any grammar passed in",
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  addonoffarg(parser, 'debug', help="debug mode", default=False)
  parser.add_argument("--infile", "-i", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="input (one sentence per line strings) file")
  parser.add_argument("--grammarfile", "-g", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="grammar file; ignored")
  parser.add_argument("--outfile", "-o", nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="output (one tree per line) file")


  try:
    args = parser.parse_args()
  except IOError as msg:
    parser.error(str(msg))

  # workdir = tempfile.mkdtemp(prefix=os.path.basename(__file__), dir=os.getenv('TMPDIR', '/tmp'))
  #
  # def cleanwork():
  #   shutil.rmtree(workdir, ignore_errors=True)
  # if args.debug:
  #   print(workdir)
  # else:
  #   atexit.register(cleanwork)


  infile = prepfile(args.infile, 'r')
  outfile = prepfile(args.outfile, 'w')
  gram = prepfile(args.grammarfile, 'r')

  tim = []
  lent = []
  for line in infile:
    line = line.strip()  #get rid of the whitespace
    # t0= time.time()
    s = CKYSolver(line)
    x = s.compute(line)
    # t1=time.time()
    # tot = round(float((t1-t0)), 5)
    # tim.append(tot)
    # lent.append(round(float(((len(line.split())))),5))
    outfile.write(str(x)+'\n')

  # plt.plot(lent,tim)
  # plt.show()
  print "done"

class CKYSolver:
  def __init__(self, text):
    self.nonterminals = set()
    self.allproductions = set()
    self.table = defaultdict(float)
    self.backptrs = {}
    self.text = text.split()
    self.actualtext = list(self.text)
    self.probabilities = defaultdict(float)
    self.terminals = {}

    try:
      if open("multiword"):
        trainDict = open("multiword")
        multiWords = []
        for word in trainDict.readlines():
          multiWords.append(word.strip())

        i=0
        for word in self.text:
          if word not in multiWords:
            self.text[i] = "<unk>"
          i+=1
    except:
      print("multiword file not found")


    self.n = len(self.text)


  def backtrack(self, n):

    if (0, n, 'TOP') not in self.backptrs:
      # print "NONE"
      return None

    t = self.back((0, n, 'TOP'))

    t.deBinarize()
    return t

  def back(self, next):

    low = next[0]
    high = next[1]
    label = next[2]

    if next not in self.backptrs:
      if next in self.terminals:
        word = self.actualtext[next[0]]
        t = Tree(label=label, subs=None, wrd=word, span=(low, high))
      return t

    branches = self.backptrs[next]

    brlen = len(branches)
    if brlen == 1:
      l=low
      h= high
      b= branches[0]
      next = (l,h,b)

      t1 = self.back(next)
      t = Tree(label=label, subs=[t1], wrd=None, span=t1.span)
      return t


    elif len(next) == 3:
      (split, left, right) = branches
      next1 = (low, split, left)  #split left
      next2 = (split, high, right) #split right

      t1 = self.back(next1)  # left side
      t2 = self.back(next2)  # right side

      spanlo = t1.span[0]
      spanhi = t2.span[1]
      t = Tree(label=label, subs=[t1, t2], wrd=None, span=(spanlo, spanhi)) #create a new tree
      return t

  def initterminals(self):
    for i in range(0, self.n):
      for lhs in self.nonterminals:
        word = self.text[i]
        unary = (lhs, word)
        if unary in self.allproductions:
          self.table[(i, i + 1, lhs)] = self.probabilities[(lhs, word)]
          self.terminals[(i, i + 1, lhs)] = word

  def compute(self, inputline):

    readfile = open("demogrammar","r")
    for line in readfile:
      rule = re.split(r"\-\>",line.strip())
      ruleprob = re.split(r"\#",rule[1])

      lhs = rule[0].strip()
      rhs = ruleprob[0].strip()
      rprob = float(ruleprob[1])

      self.nonterminals.add(lhs)
      self.allproductions.add((lhs, rhs))
      self.probabilities[(lhs, rhs)] = rprob

    self.initterminals()

    #readfile = open("alpairs", "w")
    for cols in range(2, self.n + 1):
      for start in range(0, self.n - cols + 1):
        end = cols+start
        for split in range(start + 1, end):
          #readfile.write("begin= "+str(begin)+"end= "+str(end-1)+"span= "+str(span)+"\n")

          for D, X in self.allproductions:

            rhs = X.split()
            numonrhs = len(rhs)
            if numonrhs == 2:
              rhs[1] = rhs[1].strip()
              Z = rhs[1]
              rhs[0] = rhs[0].strip()
              Y = rhs[0]

              scoreY = self.table[(start, split, Y)]
              scoreZ = self.table[(split, end, Z)]
              probrule = self.probabilities[(D, X)]

              prob = scoreY * scoreZ * probrule

              if prob > self.table[(start, end, D)]:
                #readfile.write("updating "+D+"\n")
                self.table[(start, end, D)] = prob
                self.backptrs[(start, end, D)] = (split, Y, Z)


    t = self.backtrack(len(self.text))
    if t is None:
      return "NONE"
    else:
      return t



if __name__ == '__main__':
  main()
