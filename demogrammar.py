#!/usr/bin/env python
# makes a demo grammar that is compliant with HW4 in form but completely ignores the
# input data (the grammar from the class slides is output instead)

import argparse
import sys
import codecs
if sys.version_info[0] == 2:
  from itertools import izip
else:
  izip = zip
from collections import defaultdict as dd
import re
import os.path
import gzip
import tempfile
import shutil
import atexit
from nltk.tree import Tree
import math


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
  parser = argparse.ArgumentParser(description="ignore input; make a demo grammar that is compliant in form",
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  addonoffarg(parser, 'debug', help="debug mode", default=False)
  parser.add_argument("--infile", "-i", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="input file (ignored)")
  parser.add_argument("--outfile", "-o", nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="output file (grammar)")

  try:
    args = parser.parse_args()
  except IOError as msg:
    parser.error(str(msg))

  #workdir = tempfile.mkdtemp(prefix=os.path.basename(__file__), dir=os.getenv('TMPDIR', '/tmp'))

  # def cleanwork():
  #   shutil.rmtree(workdir, ignore_errors=True)
  # if args.debug:
  #   print(workdir)
  # else:
  #   atexit.register(cleanwork)


  infile = prepfile(args.infile, 'r')
  outfile = prepfile(args.outfile, 'w')
  all_rules = {}
  all_non_term = {}

  for line in infile:
    t=Tree.fromstring(line)
    for x in (t.productions()):
      if (all_rules.get(x,0)==0):
        all_rules[x] = 1
      else:
        all_rules[x]+=1

      if(all_non_term.get(str(x).split()[0],0)==0):
        all_non_term[str(x).split()[0]] = 1
      else:
        all_non_term[str(x).split()[0]] += 1

  print("--------------------------------");
  print (len(all_non_term))
  print("--------------------------------");
  print(len(all_rules))
  print("--------------------------------");

  # for w in sorted(all_rules,key=all_rules.get,reverse=True):
  #   print(w,all_rules[w])

  for x in all_rules:
    lhs = str(x).split()[0]
    val = float(all_rules.get(x))
    totval = float(all_non_term.get(lhs))
    newval = (val/totval)
    #newval = math.log10(newval)
    all_rules[x] = newval

  #print all_rules


  for x,y in all_rules.items():
   outfile.write(str(x).replace('\'','')+" # "+str(y)+"\n")

if __name__ == '__main__':
  main()
