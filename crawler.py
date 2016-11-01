import urllib3
from bs4 import BeautifulSoup
from queue import Queue
import argparse
import threading
import sys
import os


# Disable warnings for https
urllib3.disable_warnings()

#link class has url and depth
class Link ():
    ''' Plain class to store links including the url and their depth

        depth is how far from the root the link was discovered
    '''
    def __init__(self,url,depth):
        #initialize
        self.url = url
        self.depth = depth

class Crawler():

    def __init__(self, hops, directory, num_pages):
        ''' Initialize the crawler for crawling the web
        '''
        # Tells the crawler when to stop
        self.keep_going = True
        # Hashset for visited links
        self.visited_links = set()
        # Queue to handle links
        self.links_queue = Queue()
        # Number of links visited
        self.visited = 0
        # Number of hops
        self.hops = hops
        # directory
        self.directory = directory
        # max number of pages to crawl
        self.num_pages = num_pages
        # Setup urllib 3
        self.http = urllib3.PoolManager(timeout=2.0)

    def has_visited(self, url):
        ''' Check if a link has been visited before
        '''
        return url in self.visited_links

    def enqueue_link(self, link):
        ''' Add a link to the queue externally
        '''
        self.links_queue.put(link, False)

    def start_crawling(self):
        ''' Starts crawling with specified number of threads.

            Once queue is empty, stops crawling.
        '''
        for i in range(10):
            t = threading.Thread(target=self.crawler_daemon)
            t.daemon = True
            t.start()
        self.links_queue.join()

    def crawl(self, link):
        ''' When given a link and a hop level, will parse the html for the given
            link, grab all of the hrefs, and throw them in a queue to be parsed
            later.

            Hop level is how deep the crawler will go.
            e.g. hop level of 1 means it will only parse the links found on the
            given page. hop 2 means all the links of all sub pages of the initial
            link, etc.
        '''
        # If in visited_links, return
        if self.has_visited(link.url):
            return

        # Check if we are already at max pages to crawl
        if len(self.visited_links) >= self.num_pages:
            self.keep_going = False
        # If we're done, return
        if not self.keep_going:
            return

        # Setup urllib3
        r = self.http.request('GET', link.url)
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

        # We only want pages that end in .edu
        if not domain.endswith('.edu'):
            return

        domainDir = "{}/{}".format(self.directory, domain)
        # If domain doesn't have a dir in output_dir, make one
        if not os.path.exists(domainDir):
            os.makedirs(domainDir)

        i = 0
        while os.path.exists("{}/{}_{}.html".format(domainDir, domain, i)):
            i += 1

        # Download to dir
        with open("{}/{}_{}.html".format(domainDir, domain, i),'w') as fid:
            fid.write(str(html))

        # Mark the page as visited
        self.visited_links.add(link.url)

        if self.hops - link.depth <= 0:
            return

        # Adds link to the queue
        for pageLink in soup.find_all('a'):

            url = pageLink.get('href')
            if url is None:
                continue

            # Filter out or fix malformed/incomplete links
            if url.startswith('/'):
                url = scheme + domain + url

            if not url.startswith('http://'):
                continue

            #check if url is in hashset
            if url not in self.visited_links:
                self.links_queue.put(Link(url, link.depth+1), False)

    def crawler_daemon(self):
        ''' Takes a link off the parse queue, crawls and saves the page,
            and then marks the link as completed.
        '''
        while True:
            link = self.links_queue.get()
            try:
                if self.keep_going:
                    self.crawl(link)
            except Exception as e:
                print('Error: {}'.format(e))
                pass
            finally:
                self.links_queue.task_done()


def main():
    ''' Sets up the initial queue with the seeds provided and crawls the links
        until all of the levels are exhausted
    '''
    # Set up arguments parser for variables we need
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

    # Create the crawler to do the crawling
    crawler = Crawler(hops=args.hops,
                      directory=args.output_dir,
                      num_pages=args.num_pages)

    # Create output_dir if it doesn't exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # Open the file and put num_pages of lines in the queue
    with open(args.seed_file, 'r') as f:
        for line in f:
            crawler.enqueue_link(Link(line.rstrip(), 1))

    # We're all set. Start crawling
    crawler.start_crawling()

    # Printing out all of the links
    print("\n".join(str(e) for e in crawler.visited_links))

if __name__ == '__main__':
    main()

