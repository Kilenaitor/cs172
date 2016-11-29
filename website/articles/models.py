from django.db import models
from time import time
import os
from django.db.models import signals
from django.conf import settings
import os.path
from website import settings

# Create your models here.

class Article(models.Model):
    title = models.CharField(max_length = 200)
    body = models.TextField()
    creation_date = models.DateTimeField('date posted')
    url = models.TextField() 
    page_rank = models.IntegerField(1)
    
    # any aditional fields


    def __unicode__(self):
        return self.title

    def get_url(self):
        return self.url

    # EXTRA CREDIT: Provide good snippets with results
    '''
    def get_snippet(self):
        snippet = get_snippet(self.body) 

    '''