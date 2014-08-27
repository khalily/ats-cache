#!/usr/bin/python2.6
# encoding: utf-8

from __future__ import print_function

from multiprocessing import Pool
import multiprocessing
import subprocess
import re
import urllib2
import time
import sys
import os

from socket import *

SERVER_URL = 'http://192.168.5.152:8080'
FILE_PATH = '5K'
PROCESS_NUMBER = 8
WORKLOAD = 200

ERR_URLS_PATH = 'error/error-urls'

def warning(*objs):
  print("WARNING: ", *objs, file=sys.stderr)

def extract_url(lines):
  urls = set()
  for line in lines:
    url = line.split()[7][1:]
    url = re.sub('(^http.+\.com\.cn)|(^http.+\.com)', SERVER_URL, url)
    urls.add(url)
  return urls

def replace_url(url, repl):
  return re.sub('(^http.+\.com\.cn)|(^http.+\.com)', repl, url)

def push_worker(urls):
  pusher = Pusher(FILE_PATH)
  for url in urls:
    #url = replace_url(url, SERVER_URL).strip('\n')
    url=url.strip('\n')
    print('push one:', url)
    try:
      pusher.push_one(url)
    except Exception, e:
      #print e
      warning(e)
    #print repr(url)

class Pusher(object):
  def __init__(self, file_path, err_url_path=None):
    with file(file_path) as f:
      data = f.read()
    length = len(data)
    self.response = "HTTP/1.0 200 OK\r\nContent-Type: application/octet-stream; charset=binary\r\nContent-Length: %d\r\n\r\n%s\r\n" % (length, data)
    self.len_push = len(self.response)
    #self.opener = urllib2.build_opener(urllib2.HTTPHandler)
    if not err_url_path:
      err_url_path = ERR_URLS_PATH+'.pid-%d' % os.getpid()
    self.error_urls_file = file(err_url_path, 'w+')

  def __del__(self):
    self.error_urls_file.close()

  def push_one(self, url):
    sock = socket(AF_INET, SOCK_STREAM, 0)
    sock.connect(('192.168.5.152', 80))
    #sock.settimeout(2)
    push_package = "PUSH %s HTTP/1.0\r\nContent-Length: %d\r\n\r\n%s" % (url, self.len_push, self.response)
    sock.send(push_package)
#    request = urllib2.Request(url, data = self.response)
#    #request.add_header('Content-Length', len())
#    request.get_method = lambda: 'PUSH'
#    return self.opener.open(request)
    response = sock.recv(1024)
    if response.startswith('HTTP/1.0 200 OK') or response.startswith('HTTP/1.0 201 Created'):
      print(response)
    else:
      warning(response)
      self.error_urls_file.write(url+'\n')
    sock.close()

class LogProfile(object):
  def __init__(self, path):
    print('start read file', time.ctime())
    with file(path) as f:
      self.lines = f.readlines()
    self.total = len(self.lines)
    print('end read file', time.ctime())
    print('read lines:', self.total)

  def get_urls(self):
    self.urls = self.lines
    return self.urls

  def clean(self):
    self.lines = None

  def parallel_profile(self, process_number=PROCESS_NUMBER, workload=WORKLOAD):
    pool = Pool(process_number)

#    urls_list = pool.map(extract_url,
#            (self.lines[x:x+workload] for x in xrange(0, self.total, workload)))
#    print urls_list

    #results = set()
    #for urls in urls_list:
    #  results = results | urls
    #return list(results)

def push_data(urls):
  for url in urls:
    subprocess.Popen('tspush -f 5K -u %s' % url, shell=True)
    #print url

class TrafficPusher(object):
  def __init__(self, urls):
    self.urls = urls
    self.total = len(self.urls)
    self.worker = PROCESS_NUMBER
    self.workload = self.total/self.worker
    self.pool = []

  def init(self):
    for x in xrange(0, self.total, self.workload):
      args = ()
      if self.total - x < self.workload:
        args = (self.urls[x:], )
      else:
        args = (self.urls[x:x+self.workload],)
      self.pool.append(multiprocessing.Process(target=push_worker, args=args))
#    if x < self.total:
#      self.pool.append(multiprocessing.Process(target=push_worker,
#		args=(self.urls[x:],)))

  def push(self):
    for p in self.pool:
      p.start()
    self.urls = None

  def join_all(self):
    for p in self.pool:
      p.join()

  def push_one(self, file_path, url):
    pass

  def push_all(self):
    pool = Pool(self.worker)
    pool.map(
        push_worker,
        (
          self.urls[x:x+self.workload]
          for x in xrange(0, self.total, self.workload)
        )
    )

def process_one_url(url):
  pusher = Pusher('5K', ERR_URLS_PATH+'.one-test')
  pusher.push_one(url)

if __name__ == "__main__":
  import sys
  if len(sys.argv) < 2:
    print('usgae: %s file_path' % sys.argv[0])
    sys.exit(1)

  if sys.argv[1] == '-u':
    process_one_url(sys.argv[2])
    sys.exit(0)

  start = time.time()

  urls_file = sys.argv[1]

  log_profile = LogProfile(urls_file)
  urls = log_profile.get_urls()

  log_profile.clean()

  tpr = TrafficPusher(urls)

  urls = None

  tpr.init()
  tpr.push()
  tpr.join_all()

  end = time.time()
  warning('finish %f seconds' % (end - start))

  # test push one url

  #pusher = Pusher('5K')
  #for line in file(sys.argv[1]).readlines():
  #  url = replace_url(line, SERVER_URL)
  #  print url
  #  pusher.push_one(url)
  #  break

