#!/usr/bin/env python
# encoding: utf-8

import hashlib
import os


def cal_hashvalue(string):
  m = hashlib.md5()
  m.update(string)
  return m.hexdigest()

def split_file(file_path, number=10, suffix="_part_"):
  files = {}
  file_names = []
  for x in xrange(1, number + 1):
      file_name = '%s%s%d' % (file_path, suffix, x)
      file_names.append(file_name)
      files[file_name] = open(file_name, 'w')

  with open(file_path) as f:
    lines = f.readlines()

  for line in lines:
    value = cal_hashvalue(line)
    files[file_names[int(value, 16) % number]].write(line)
  for file in files.itervalues():
      file.close()

if __name__ == "__main__":
  import sys
  if len(sys.argv) < 3:
    print 'usage: %s file_path number [suffix]' % sys.argv[0]
    sys.exit(-1)
  if len(sys.argv) == 4:
    split_file(sys.argv[1], int(sys.argv[2]), sys.argv[3])
  else:
    split_file(sys.argv[1], int(sys.argv[2]))

