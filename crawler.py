import urllib3
from bs4 import BeautifulSoup
from queue import Queue
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
    # Setup urllib3
    http = urllib3.PoolManager(timeout=2.0)
    r = http.request('GET', link.url)
    # Decode everything with utf8 support
    html = r.data
    # Parse the document so it can be processed
    soup = BeautifulSoup(html, 'html.parser')

    
     
    # Parse and store page
    
    # If in hashset, return
    if (link.url in hashSet):
        return
    
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
    if ( not os.path.exists(domainDir)):
        os.makedirs(domainDir)
    
    i = 0
    while os.path.exists("{}/{}_%s.html".format(domainDir,domain) % i):
        i+=1

    # Download to dir  
    with open("{}/{}_%s.html".format(domainDir,domain) % i,'w') as fid:
        fid.write(str(html))

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

        # Filter out or fix malformed/incomplete links
        if (url.startswith('/')):
            url = scheme + domain + url


        if (url is None or not url.startswith('http://')):
            continue
  
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
    global directory
    # Make sure they provide a seeds file
    if (len(sys.argv) <= 1):
        print("{}\n\n{}".format(
            'Usage:',
            'python3 crawler.py <seed-File:seed.txt> <num-pages:1000> <hops-away: 6> <output-dir>',
        ))
        sys.exit(1)
    
    # Seeds file is the first argument (not the python file name)
    links_list = sys.argv[1]
    num_pages = int(sys.argv[2])
    hops = int(sys.argv[3])   
    output_dir = sys.argv[4] 
    directory = output_dir

    # Create output_dir if it doesn't exist
    if ( not os.path.exists(output_dir)):
        os.makedirs(output_dir)

    # If hops equals 0, return
    if ( hops == 0):
        return

    # Open the file and put num_pages of lines in the queue
    with open(links_list, 'r') as f:
        pages = 0
        for line in f:
            if (pages < int(num_pages)):
                links.put( Link(line.rstrip(),1))
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

if (__name__ == '__main__'):
    main()

