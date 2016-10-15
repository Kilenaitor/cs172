import urllib3
from bs4 import BeautifulSoup
import queue
import sys

# Disable warnings for https
urllib3.disable_warnings()

# Queue to handle all of the links
links = queue.Queue()


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
    http = urllib3.PoolManager()
    r = http.request('GET', link)
    # Decode everything with utf8 support
    html = r.data.decode('utf-8')
    # Parse the document so it can be processed
    soup = BeautifulSoup(html, 'html.parser')
    
    # Add every link to the queue
    # TODO: Add a hop check
    # TODO: Filter out malformed/incomplete links
    # TODO: Hash and don't add already-visited links
    for link in soup.find_all('a'):
        links.put(link.get('href'))
        
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
    
    # Grab 100 links
    while (not links.empty()):
        if (links.qsize() < 100):
            crawl(links.get())
        else:
            break
            
    # Print out all 100 links
    while (not links.empty()):
        print(links.get())


if __name__ == '__main__':
    main()

