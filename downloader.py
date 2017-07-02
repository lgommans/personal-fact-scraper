#!/usr/bin/env python3

import sys, os, time, requests, hashlib
from base64 import b64encode
from urllib.parse import urljoin

def err(s):
    sys.stderr.write(s + '\n')

def usage():
    err('''Usage:
  downloader <url> <next-url> [throttle] [-cat] [-cache] [-v] [-n]
Where:
  url is the starting URL.
  next-url is some text after the 'href=' that you want to use.
  throttle is the number of seconds (float) to wait between each request.
           Default is 0 (no delay).
  -f file output. If not specified, it will write all data to stdout.
  -l live (do not use cache). If not specified, it will create a cache/ folder
     to cache URLs indefinitely.
  -v enables verbose mode.
  -n never downloads (only uses cache).
''')
    sys.exit(1)

if len(sys.argv) < 3:
    usage()

url = sys.argv[1]
nexturl = sys.argv[2]
throttle = float(sys.argv[3]) if len(sys.argv) > 3 else 0
catmode = '-f' not in sys.argv
cache = '-l' not in sys.argv
verbose = '-v' in sys.argv
neverdownload = '-n' in sys.argv

if cache:
    if not os.path.isdir('cache'):
        os.mkdir('cache')

req = 0
while True:
    fname = b'cache/' + bytes(str(b64encode(hashlib.sha256(bytes(url, 'UTF-8')).digest()), 'UTF-8').replace('/', '-'), 'UTF-8')
    if os.path.isfile(fname) and cache:
        data = open(fname, 'r').read()
    else:
        if neverdownload:
            # Apparently we're out of cache. The end.
            break

        if verbose:
            err('Downloading {}'.format(url))

        data = requests.get(url).text
        time.sleep(throttle)
        if cache:
            f = open(fname, 'w')
            f.write(data)
            f.close()

    if nexturl not in data:
        # No more next link? The end.
        break

    if catmode:
        print(data)
    else:
        open('{}.html'.format(req), 'w')
        req += 1

    httpstart = data.rfind('href=', 0, data.index(nexturl)) + 6
    nextquote = data[httpstart:].index('"')
    nextapostrophe = data[httpstart:].index("'")
    newurl = data[httpstart : httpstart+min(nextquote, nextapostrophe)].replace('&amp;', '&')
    if '://' not in newurl[0:10]:
        url = urljoin(url, newurl)
    else:
        url = newurl

    if verbose:
        err('Found next URL: {}'.format(url))

