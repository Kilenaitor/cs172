import urllib3
from bs4 import BeautifulSoup
import queue
import sys

# Disable warnings for https
urllib3.disable_warnings()

# Queue to handle all of the links
links = queue.Queue()


def crawl(link, hop=1):
    http = urllib3.PoolManager()
    r = http.request('GET', link)
    html = r.data.decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a'):
        links.put(link.get('href'))


if __name__ == '__main__':
    if (len(sys.argv) <= 1):
        print("{}\n\n{}".format(
            'Usage:',
            'python3 crawler.py <list of files>',
        ))
        sys.exit(1)

    links_list = sys.argv[1]
    with open(links_list, 'r') as f:
        for line in f:
            links.put(line)
    
    while (not links.empty()):
        if (links.qsize() < 100):
            crawl(links.get())
        else:
            break
            
    while (not links.empty()):
        print(links.get())

