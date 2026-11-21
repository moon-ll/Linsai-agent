# R3 arXiv batch re-verify (critic round 3)
import json
import re
import urllib.request
import urllib.parse

ids = ['2606.02238', '2508.00296', '2602.16454', '2503.15932',
       '2605.21925', '2606.22714', '2512.24553', '2512.23538']
q = ','.join(i.split('v')[0] for i in ids)
url = 'http://export.arxiv.org/api/query?id_list=' + q + '&max_results=30'
req = urllib.request.Request(url, headers={'User-Agent': 'nsfc-critic/3.0'})
xml = urllib.request.urlopen(req, timeout=40).read().decode('utf-8', 'ignore')

entries = re.findall(r'<entry>(.*?)</entry>', xml, flags=re.S)
print('returned entries:', len(entries))
for e in entries:
    eid = re.search(r'<id>http://arxiv.org/abs/([^<]+)</id>', e)
    title = re.search(r'<title>([^<]+)</title>', e)
    authors = re.findall(r'<name>([^<]+)</name>', e)
    pub = re.search(r'<published>([^<]+)</published>', e)
    print('-' * 8)
    print('id:', eid.group(1) if eid else '?')
    print('title:', re.sub(r'\s+', ' ', title.group(1)).strip()[:110] if title else '?')
    print('authors:', ', '.join(authors[:4]), ('...+%d' % (len(authors)-4)) if len(authors) > 4 else '')
    print('published:', pub.group(1)[:10] if pub else '?')
