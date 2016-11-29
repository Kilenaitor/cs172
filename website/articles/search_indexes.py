import datetime
from haystack import indexes
from articles.models import Article

class ArticleIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, user_template=True)
    creation_date = indexes.DateTimeField(model_attr = 'creation_date') 
