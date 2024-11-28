from django.shortcuts import render, redirect, get_object_or_404
from accounts.forms import NewUserForm, profileForm
from app.models import *
from app.forms import *
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.db.models import Count
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q

# Create your views here.
def post_page(request, slug):
    post = Post.objects.get(slug=slug)
    comments = Comments.objects.filter(post=post, parent=None)
    form = commentForm()
    parent = None
    comment_count = Comments.objects.filter(post=post, parent=None).count()

    bookmarked = False
    if post.bookmarks.filter(id=request.user.id).exists():
        bookmarked = True

    liked = False
    if post.like.filter(id=request.user.id).exists():
        liked = True
    likes = post.like_count()

    if request.POST:
        comment_form = commentForm(request.POST)
        if comment_form.is_valid():
            parent_id = request.POST.get("parent")
            if parent_id:
                parent = Comments.objects.get(id=parent_id)
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = Profile.objects.get(user=request.user)
            comment.parent = parent
            comment.save()
            return redirect(reverse("post_page", args=[slug]))

    if post.view_count:
        post.view_count += 1
    else:
        post.view_count = 1
    post.save()

    top_authors = (
        Profile.objects.annotate(post_count=Count("post")).order_by("-post_count"))[0:2]
    recent_from_authors = (
        Post.objects.exclude(id=post.id)
        .filter(author=post.author)
        .order_by("-date")[0:2]
    )
    related_posts = []
    for rel_post in Post.objects.all():
        for tag in rel_post.tags.all():
            if tag in post.tags.all():
                if rel_post in related_posts:
                    pass
                else:
                    related_posts.append(rel_post)
    related_posts = related_posts[0:2]
    top_tags = Tag.objects.annotate(post_count=Count("posts")).order_by("-post_count")
    context = {
        "post": post,
        "form": form,
        "comment_count": comment_count,
        "comments": comments,
        "bookmarked": bookmarked,
        "liked": liked,
        "likes": likes,
        "top_authors": top_authors,
        "related_posts": related_posts,
        "recent_from_authors": recent_from_authors,
        "top_tags": top_tags,
    }
    return render(request, "app/post.html", context)


def home(request):
    posts = Post.objects.all()
    latest_posts = Post.objects.all().order_by("-date")[0:3]
    top_posts = Post.objects.all().order_by("-view_count")[0:3]
    subscribe = False
    website_info = None
    featured_post=None

    if WebsiteMeta.objects.all().exists():
        website_info = WebsiteMeta.objects.all()[0]
    try:
        featured_post = Post.objects.get(is_featured=1)
    except:
        featured_post=None
    context = {
        "posts": posts,
        "latest_posts": latest_posts,
        "top_posts": top_posts,
        "subscribe": subscribe,
        "featured_post": featured_post,
        "website_info": website_info,
    }
    return render(request, "app/index.html", context)


def tag_page(request, name):
    tag = Tag.objects.get(name=name)
    tags = Tag.objects.all()
    topPosts = Post.objects.filter(tags__in=[tag.id]).order_by("-view_count")[0:3]
    latestPosts = Post.objects.filter(tags__in=[tag.id]).order_by("-date")[0:3]
    context = {
        "tag": tag,
        "tags": tags,
        "latest_posts": latestPosts,
        "top_posts": topPosts,
    }
    return render(request, "app/tag.html", context)

@login_required(login_url='login')
def author_page(request, slug):
    author_profile = Profile.objects.get(slug=slug)
    print(request.user.username)
    authors = Profile.objects.annotate(post_count=Count("post")).order_by("-post_count")

    topPosts = Post.objects.filter(author=author_profile).order_by("-view_count")[0:2]
    allPosts = Post.objects.filter(author=author_profile).order_by("-date")[0:]

    context = {
        "author_profile": author_profile,
        "authors": authors,
        "all_posts": allPosts,
        "top_posts": topPosts,
    }
    return render(request, "app/author.html", context)

@login_required(login_url='login')
def profile_page(request, slug):
    profile = Profile.objects.select_related('user').get(slug=slug)
    bookmarked_posts = Post.objects.filter(bookmarks=profile.user)
    liked_posts = Post.objects.filter(like=profile.user)
      

    author_posts = Post.objects.filter(author=profile)

    if request.POST:
        profile_form = profileForm(request.POST, request.FILES, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            return redirect(reverse("profile_page", args=[slug]))

    display_posts = None
    if request.GET:
        display_posts = request.GET.get('display_posts')
        if display_posts == "bookmarks":
            display_posts = "bookmarks"  
        elif display_posts == "likes":
            display_posts = "likes"
        elif display_posts == "your_posts":
            display_posts = "author_posts"
        
    profile_form = profileForm(instance=profile)

    context = {
        "user": profile.user,
        "profile": profile,
        "bookmarked_posts": bookmarked_posts,
        "liked_posts": liked_posts,
        "display_posts": display_posts,
        "profile_form": profile_form,
        "author_posts": author_posts,
    }
    return render(request, "app/yourpage.html", context)

@login_required(login_url='login')
def post_blog(request, slug):
    user_profile = Profile.objects.select_related('user').get(slug=slug)
    postform = PostForm()
    if request.POST:
        print(request.POST)
        postform = PostForm(request.POST, request.FILES)
        if postform.is_valid():
            post = postform.save(commit=False)
            post.author = user_profile
            post.save()
            tags = request.POST.getlist('tags')
            print(tags)
            for tag_name in tags:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                post.tags.add(tag)
            return HttpResponseRedirect(reverse('post_page', args=[post.slug]))
        else:
            print('errors', postform.errors)
    context = {"postform":postform, "user_profile":user_profile,}
    return render(request, "app/post_blog.html", context)

@login_required(login_url='login')
def tag_suggestions(request):
    query = request.GET.get('query', '')
    suggestions = Tag.objects.filter(name__icontains=query).values_list('name', flat=True)[:5]
    return JsonResponse({'tags': list(suggestions)})


@login_required(login_url='login')
def update_blog(request, post_slug):
    post = Post.objects.get(slug=post_slug)
    profile = post.author
    if request.POST:
        updateBlog = PostForm(request.POST, request.FILES ,instance=post)
        if updateBlog.is_valid():
            updated_blog = updateBlog.save()
            return redirect(reverse("post_page", args=[updated_blog.slug]))
    else:
        updateBlogForm = PostForm(instance=post)
        
    context = {"post":post, "postform":updateBlogForm, "user_profile":profile}
    return render(request, "app/post_blog.html", context)

@login_required(login_url='login')
def delete_blog(request, post_slug):
    post = Post.objects.get(slug=post_slug)
    profile = post.author
    delete=True
    if request.POST:
        post.delete()
        return redirect(reverse("profile_page", args=[profile.slug]))
    else:
        updateBlogForm = PostForm(instance=post)
    context = {
        "post":post, 
        "postform":updateBlogForm, 
        "delete":delete, 
        "user_profile":profile
    }
    return render(request, "app/post_blog.html", context)

@login_required(login_url='login')
def search(request, default_sort_by=""):
    tags = Tag.objects.all()
    search_query = request.GET.get("q")
    sort_by = request.GET.get("sort_by")
    if sort_by:
        sort_by = sort_by
    else:
        sort_by = default_sort_by
    filter_tag = request.GET.get("filter_tag")

    posts = Post.objects.all()

    if filter_tag:
        posts = posts.filter(tags__name=filter_tag)
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(author__user__username__icontains=search_query)
        )

    if sort_by == "famous":
        posts = posts.order_by("-view_count")
    elif sort_by == "alphabetical":
        posts = posts.order_by("title")
    elif sort_by == "newest":
        posts = posts.order_by("-date")

    context = {
        "posts": posts,
        "search_query": search_query,
        "sort_by": sort_by,
        "tags": tags,
        "filter_tag": filter_tag,
    }
    return render(request, "app/search.html", context)


def about(request):
    about = None
    if WebsiteMeta.objects.all().exists():
        about = WebsiteMeta.objects.all()[0].About
    context = {"about": about}
    return render(request, "app/about.html", context)

@login_required(login_url='login')
def bookmarks(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if post.bookmarks.filter(id=request.user.id).exists():
        post.bookmarks.remove(request.user)
    else:
        post.bookmarks.add(request.user)
    return redirect(reverse("post_page", args=[slug]))

@login_required(login_url='login')
def like_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if post.like.filter(id=request.user.id).exists():
        post.like.remove(request.user)
    else:
        post.like.add(request.user)
    return redirect(reverse("post_page", args=[slug]))

