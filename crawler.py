import urllib3
from bs4 import BeautifulSoup
from queue import Queue
import threading
import sys

# Disable warnings for https
urllib3.disable_warnings()

# Queue to handle all of the links
links = Queue(5000)
visited = 0

links_visited = []
keep_going = True


def crawl(link, hop=1):
    ''' When given a link and a hop level, will parse the html for the given
        link, grab all of the hrefs, and throw them in a queue to be parsed
        later.

        Hop level is how deep the crawler will go.
        e.g. hop level of 1 means it will only parse the links found on the
        given page. hop 2 means all the links of all sub pages of the initial
        link, etc.
    '''
    # Setup urllib3
    http = urllib3.PoolManager(timeout=2.0)
    r = http.request('GET', link)
    # Decode everything with utf8 support
    html = r.data
    # Parse the document so it can be processed
    soup = BeautifulSoup(html, 'html.parser')

    # Add every link to the queue
    # TODO: Add a hop check
    # TODO: Filter out malformed/incomplete links
    # TODO: Hash and don't add already-visited links
    for link in soup.find_all('a'):
        global keep_going
        if (links.full()):
            keep_going = False
        if (not keep_going):
            break
        href = link.get('href')
        if (href is None or not href.startswith('http://')):
            continue
        links_visited.append(href)
        links.put(href)


def crawler():
    while True:  
        global visited
        print("Crawling and parsing #" + str(visited)) 
        visited += 1
        link = links.get()
        try:
            crawl(link)
        except Exception:
            pass
        finally:
            links.task_done()


def main():
    ''' Sets up the initial queue with the seeds provided and crawls the links
        until all of the levels are exhausted
    '''
    # Make sure they provide a seeds file
    if (len(sys.argv) <= 1):
        print("{}\n\n{}".format(
            'Usage:',
            'python3 crawler.py <list of files>',
        ))
        sys.exit(1)

    # Seeds file is the first argument (not the python file name)
    links_list = sys.argv[1]

    # Open the file and put every line in the queue
    with open(links_list, 'r') as f:
        for line in f:
            links.put(line)

    for i in range(100):
        t = threading.Thread(target=crawler)
        t.daemon = True
        t.start()

    links.join()
    
    print("Printing links!")
    print(links_visited)

if __name__ == '__main__':
    main()

