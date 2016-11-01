import urllib3
from bs4 import BeautifulSoup
from queue import Queue
import argparse
import threading
import sys
import os


# Disable warnings for https
#urllib3.disable_warnings()

# Hashset for visited links
hashSet = set()
# Queue to handle links
links = Queue(5000)
# Number of links visited
visited = 0
# Max number of pages to crawl
num_pages = 0
# Number of hops
hops = 0
# directory
directory = ""
keep_going = True

#link class has url and depth
class Link ():
    def __init__(self,url,depth):
        #initialize
        self.url = url
        self.depth = depth

def crawl(link):
    ''' When given a link and a hop level, will parse the html for the given
        link, grab all of the hrefs, and throw them in a queue to be parsed
        later.

        Hop level is how deep the crawler will go.
        e.g. hop level of 1 means it will only parse the links found on the
        given page. hop 2 means all the links of all sub pages of the initial
        link, etc.
    '''
    global hashSet

    # If in hashset, return
    if (link.url in hashSet):
        return

    # Setup urllib3
    http = urllib3.PoolManager(timeout=2.0)
    r = http.request('GET', link.url)
    # Decode everything with utf8 support
    html = r.data
    # Parse the document so it can be processed
    soup = BeautifulSoup(html, 'html.parser')

    # Parse and store page
    scheme = ""
    domain = ""
    endIndex = link.url.index("/",8)
    if (link.url[:7] == "http://"):
        scheme = "http://"
        domain = link.url[7:endIndex]
    else:
        scheme = "https://"
        domain = link.url[8:endIndex]

    domainDir = "{}/{}".format(directory,domain)
    # If domain doesn't have a dir in output_dir, make one
    if not os.path.exists(domainDir):
        os.makedirs(domainDir)

    i = 0
    while os.path.exists("{}/{}_{}.html".format(domainDir,domain, i)):
        i += 1

    # Download to dir
    with open("{}/{}_{}.html".format(domainDir,domain, i), 'w') as fid:
        fid.write(str(html))

    hashSet.add(link.url)

    if hops - link.depth <= 0:
        return

    # Adds link to the queue
    for pageLink in soup.find_all('a'):
        global keep_going
        global num_pages
        if len(hashSet) >= num_pages:
            print("-------------------------------- DONE -------------------------------")
            keep_going = False
        if not keep_going:
            break
        url = pageLink.get('href')

        if url is None:
            continue

        # Filter out or fix malformed/incomplete links
        if url.startswith('/'):
            url = scheme + domain + url

        if not url.startswith('http://'):
            continue

        # Check if url is in hashset
        if url not in hashSet:
            links.put(Link(url, link.depth +1), timeout=2.0)


def crawler():
    while True:
        global visited
        print("Crawling and parsing #" + str(visited))
        visited += 1
        link = links.get()
        try:
            crawl(link)
        except Exception as e:
            print("Error: {}".format(e))
            pass
        finally:
            links.task_done()


def main():
    ''' Sets up the initial queue with the seeds provided and crawls the links
        until all of the levels are exhausted
    '''
    global hops
    global directory
    global num_pages
    parser = argparse.ArgumentParser(prog='CS172 Web Crawler',
                                     description='Web Crawler')
    parser.add_argument('-s', '--seed-file', dest='seed_file', type=str,
                        required=True, nargs='?',
                        help='List of files to start the crawler on')
    parser.add_argument('-n', '--num-pages', dest='num_pages', type=int,
                        default=1000, required=True, nargs='?',
                        help='Total number of pages to crawl before stopping')
    parser.add_argument('-p', '--hops', dest='hops', type=int,
                        default=0, required=True, nargs='?',
                        help='How deep the crawler will go down a link path')
    parser.add_argument('-o', '--output-directory', dest='output_dir', type=str,
                        default='crawler_pages', required=True, nargs='?',
                        help=('The directory where you want the text of the'
                              'pages to be saved to')
                        )
    args = parser.parse_args()
    directory = args.output_dir
    hops = args.hops
    num_pages = args.num_pages

    # Create output_dir if it doesn't exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # Open the file and put num_pages of lines in the queue
    with open(args.seed_file, 'r') as f:
        for line in f:
            links.put(Link(line.rstrip(),1), timeout=2.0)

    for i in range(100):
        t = threading.Thread(target=crawler)
        t.daemon = True
        t.start()

    links.join()

    # Printing out all of the links
    print("\n".join(str(e) for e in hashSet))

if __name__ == '__main__':
    main()

