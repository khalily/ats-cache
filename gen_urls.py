#!/usr/bin/env python
# encoding: utf-8

import uuid
import sys

def gen_tag():
  return uuid.uuid1().hex

def gen_one_url(host):
  return 'http://' + host + '/' + gen_tag()

if len(sys.argv) < 2:
  print 'usage: %s host_file [num_per_host=10]' % sys.argv[0]
  sys.exit(1)

host_file = sys.argv[1]
num_per_host = 10

if len(sys.argv) == 3:
  num_per_host = int(sys.argv[2])

with open(host_file) as f:
  lines = f.readlines()

out_file = open('/dev/stdout', 'w+')

for line in lines:
  urls = [gen_one_url(line.strip('\n')) + '\n' for x in xrange(num_per_host)]
  out_file.writelines(urls)

