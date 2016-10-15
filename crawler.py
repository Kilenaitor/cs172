import urllib3
from bs4 import BeautifulSoup

def main():
    test_link = "https://en.wikipedia.org/wiki/Apple_Inc."
    http = urllib3.PoolManager()

    r = http.request('GET', test_link)
    
    html = r.data
    
    soup = BeautifulSoup(html, 'html.parser')
    
    for link in soup.find_all('a'):
        print(link.get('href'))

if __name__ == '__main__':
    main()

