import urllib3
from bs4 import BeautifulSoup
from queue import Queue
import threading
import sys

# Disable warnings for https
#urllib3.disable_warnings()

#hash for visited links
hashSet = set()
# Queue to handle links
links = Queue(5000)
visited = 0
hops = 0
# links_visited = []
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
    # Setup urllib3
    http = urllib3.PoolManager(timeout=2.0)
    r = http.request('GET', link.url)
    # Decode everything with utf8 support
    html = r.data
    # Parse the document so it can be processed
    soup = BeautifulSoup(html, 'html.parser')

    
    # TODO: Filter out malformed/incomplete links
    
    # Parse and store page
    
    #If hop is 0 return
    print("{} {} {}".format(hops-link.depth, len(hashSet), links.qsize()))
    hashSet.add(link.url)
    if (hops - link.depth <= 0):
        return
        
    # Adds link to the queue
    for pageLink in soup.find_all('a'):
        global keep_going
        if (links.full()):
            keep_going = False
        if (not keep_going):
            break  
        url = pageLink.get('href')
        if (url is None or not url.startswith('http://')):
            continue
              
        # print( hashSet)
  
        #check if url is in hashset
        if (url not in hashSet):
            links.put( Link(url, link.depth +1))

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
    hops = int(hops)
    
    # Seeds file is the first argument (not the python file name)
    links_list = sys.argv[1]

    # Open the file and put every line in the queue
    with open(links_list, 'r') as f:
        pages = 0
        for line in f:
            if (pages <= int(numPages)):
                links.put( Link(line.rstrip(),0))
                pages += 1
            else:
                break
    

    for i in range(100):
        t = threading.Thread(target=crawler)
        t.daemon = True
        t.start()

    links.join()
    
    
    
    print (len(hashSet))
    # Printing out all of the links
    print("\n".join(str(e) for e in hashSet))

if __name__ == '__main__':
    main()

