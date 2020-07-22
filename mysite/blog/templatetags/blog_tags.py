from django import template
from ..models import Post

from django.db.models import Count

import datetime


register = template.Library()

format_string = "%b %x %X %Z %p"

@register.simple_tag
def total_posts():
    return Post.published.count()

@register.simple_tag(name = 'time')
def show_current_time():
     return datetime.datetime.now().strftime(format_string)


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


@register.simple_tag
def get_most_commented_posts(count = 5):
     return Post.published.annotate(total_comments = Count('comments')).order_by('-total_comments')[:count]   