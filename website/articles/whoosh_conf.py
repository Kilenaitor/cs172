from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.analysis import StandardAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import sys, glob, os, unicodedata
from django.conf import settings
from bs4 import BeautifulSoup

stopset = set(stopwords.words('english'))

if not os.path.exists('whoosh'):
    os.mkdir('whoosh')

schema = Schema(title=TEXT(stored=True), path=TEXT(stored=True), body=TEXT(stored=True, phrase=True, analyzer=StandardAnalyzer(stoplist=None)))

ix = create_in('whoosh', schema)

writer = ix.writer()

for url in os.listdir('articles/static/'):
    for html_file in os.listdir('articles/static/' + url):
        filename = html_file
        path = 'articles/static/' + url + '/' + html_file
        with open(path, 'r') as content_file:
            soup = BeautifulSoup(content_file, "html.parser")

            title = ""
            if soup.title is not None:
                title = soup.title.string
                if title is not None:
                    title = title.strip()

            for script in soup(["script", "style"]):
                script.extract()

            body = soup.find('body')
            if body is None:
                text = ""
            else:
                text = body.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
            writer.add_document(title=title, path=path[9:], body=text)

writer.commit()
