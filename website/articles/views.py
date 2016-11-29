from django.shortcuts import render
from django.http import HttpResponse

from django.conf import settings
from whoosh.index import open_dir
from whoosh.qparser import QueryParser

# Create your views here.

def index(request):
    return render(request, 'articles/index.html', )

def search(request):
    ix = open_dir('whoosh')
    hits = []
    query = request.GET.get('q', None)
    if query is not None and query != u"":
        query = query.replace('+', ' AND ').replace(' -', ' NOT ')
        parser = QueryParser('body', schema=ix.schema)
        try:
            qry = parser.parse(query)
        except:
            qry = None
        if qry is not None:
            searcher = ix.searcher()
            hits = searcher.search(qry)

    return render(request, 'articles/search.html', {'query': query, 'hits': hits})
