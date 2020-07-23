from django.contrib.sitemaps import Sitemap
from .models import Post

class PostSitemap(Sitemap):
     changefreq = 'weekly'
     priority = '0.9'    # max is 1

     # Django will call the get_abolsute_url method created in Post model
     #    def get_absolute_url(self):
     def items(self):
          return Post.published.all()


     # should return a datetime obj
     # defined in Post model as
     #    updated = models.DateTimeField(auto_now=True)
     def lastmod(self, obj):
          return obj.updated     
