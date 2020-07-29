from django.shortcuts import render, get_object_or_404
from .models import Post, Comment

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView

from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail

from taggit.models import Tag

from django.db.models import Count

# Create your views here.
def post_list(request, tag_slug = None):
    object_list = Post.published.all()
    
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug = tag_slug)
        object_list = object_list.filter(tags__in = [tag])


    paginator = Paginator(object_list, 3)   # provide 3 posts per page                          
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:    
        # of page NOT an integer, provide first page
        posts = paginator.page(1)
    except EmptyPage:
        # if Page is out of range, provide last page    
        posts = paginator.page(paginator.num_pages)
    
    
    context = {'page': page, 'posts': posts, 'tag': tag}
    
    return render(request, 'blog/post/list.html', context)


class PostListView(ListView):
    model = Post
    # queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, 
                             slug = post, 
                             status = 'published', 
                             publish__year = year,
                             publish__month = month,
                             publish__day = day)    



    # list of active comments for this post
    comments = post.comments.filter(active = True)

    new_comment = None

    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm( data=request.POST )

        if comment_form.is_valid():
            # create comment obj but do not save to database yet
            new_comment = comment_form.save(commit = False)
            # Assign current post to comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()

    else:  # provide blank comment form
        comment_form = CommentForm()


    post_tags_ids = post.tags.values_list('id', flat = True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    context = {'post': post, 'comments': comments, 
               'new_comment': new_comment, 'comment_form': comment_form,
               'similar_posts': similar_posts }

    return render(request, 'blog/post/detail.html', context)   

def post_share(request, post_id):
    # Retrieve post by ID
    post = get_object_or_404(Post, id = post_id, status = "published")
    sent = False

    if request.method == 'POST':
        # form was submitted with data
        form = EmailPostForm(request.POST)
        print('form is', form)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data 
            print("cd is", cd)
            # ... send email
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " f"{post.title}"
            message = f"Read {post.title} at {post_url} \n\n" f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'sktestdjango@gmail.com', [cd['to']])
            sent = True   # used to show successs message 

    else:  # show blank form
        form = EmailPostForm()        

    context = {'post': post, 'form': form, 'sent': sent}

    return render(request, 'blog/post/share.html', context)    


def post_search(request):
     form = SearchForm()
     query = None
     results = []

     if 'query' in request.GET:
          form = SearchForm(request.GET)
          if form.is_valid():
               query = form.cleaned_data['query']
               # results = Post.published.annotate(search=SearchVector('title', 'body'),).filter(search=query).order_by('-updated')
               search_vector = SearchVector('title', weight = 'A') +  SearchVector('body', weight = 'B')
               search_query = SearchQuery(query)
               # results = Post.published.annotate(search=search_vector, rank = SearchRank(search_vector, search_query)).filter(rank__gte = 0.3).order_by('-rank')
               results = Post.published.annotate(similarity = TrigramSimilarity('title', query),).filter(similarity__gt=0.1).order_by('-similarity')

     context = {
          'form': form,
          'query': query,
          'results': results
     }
     
     return render(request, 'blog/post/search.html', context)         