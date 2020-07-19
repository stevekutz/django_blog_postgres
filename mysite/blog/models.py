from django.db import models
from django.utils import timezone # needed for timestamp of publish, created, & updated attributes
from django.contrib.auth.models import User
from django.urls import reverse

from taggit.managers import TaggableManager

# Create your models here.

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')



class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    title = models.CharField(max_length = 250)
    slug = models.SlugField(max_length = 250, unique_for_date = 'publish')
    author = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'blog_posts')
    body = models.TextField()
    publish = models.DateTimeField(default = timezone.now) # date with timezone info
    created = models.DateField(auto_now_add = True) # date when post initially created
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length = 10, choices = STATUS_CHOICES, default = 'draft')

    objects = models.Manager()
    published = PublishedManager()

    class Meta:     # just a class container with some options (metadata)
        ordering = ('-publish', )   # the negative puts in descending order from most recently pubished

    def __str__(self):   # creates a human-readable representation of the object
        return self.title

    def get_absolute_url(self):
        return reverse("blog:post_detail",   # define args next, kwargs can also be implmented
                         args=[self.publish.year,
                               self.publish.month,
                               self.publish.day,
                               self.slug ])
    
    tags = TaggableManager()

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default = True)

    class Meta:  # just a class container with some options (metadata)
        ordering: ('created',)

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'    
