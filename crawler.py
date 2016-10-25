import urllib3
from bs4 import BeautifulSoup
import queue
import sys

# Disable warnings for https
#urllib3.disable_warnings()

# Queue to handle all of the links
links = queue.Queue()
hashSet = set()

#link class has url and depth
class Link ():
    def __init__(self,url,depth):
        #initialize
        self.url = url
        self.depth = depth

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
    r = http.request('GET', link.url)
    # Decode everything with utf8 support
    html = r.data.decode('utf-8')
    # Parse the document so it can be processed
    soup = BeautifulSoup(html, 'html.parser')
    
    # TODO: Filter out malformed/incomplete links
    
    # Parse and store page
    
    # If hop is 0 return
    if (hop - link.depth == 0):
        return
    
    # Add links to queue
    for pageLink in soup.find_all('a'):
        url = pageLink.get('href')
        #check if url is in set
        if (url not in hashSet):
            links.put( Link(url, link.depth +1))
    
        
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
    
    numPages = 0
    while True: 
        numPages = input('Enter number of pages: ')
        if( not isinstance(numPages,int) ): break
        print ('Response is not an integer')

    hops = 0
    while True: 
        hops = input('Enter number of hops: ')
        if( not isinstance(hops,int) ): break
        print ('Response is not an integer')
    
        
    # Seeds file is the first argument (not the python file name)
    links_list = sys.argv[1]
    
    # Open the file and put every line in the queue
    with open(links_list, 'r') as f:
        pages = 1
        for line in f:
            if (pages == numPages): break
            pages+=1;
            links.put( Link(str(line).rstrip(),0))

    # Grab 100 links
    while (not links.empty()):
        print(links.qsize())
        if (links.qsize() < 100):
            crawl(links.get(), int(hops))
        else:
            break
            
    # Print out all 100 links
    # while (not links.empty()):
    #     print(links.get())
    
    for item in enumerate(hashSet):
        print (item.url)


if __name__ == '__main__':
    main()

