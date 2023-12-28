from django.shortcuts import render, redirect, get_object_or_404
from app.models import *
from app.forms import *
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Count
from django.contrib.auth import login, logout


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
            return HttpResponseRedirect(reverse("post_page", kwargs={"slug": slug}))

    if post.view_count is None:
        post.view_count = 1
    else:
        post.view_count += 1
    post.save()
    # sidebar
    # author-posts
    # tag_post(related)
    # top_author
    # top_tags

    top_authors = (
        Profile.objects.annotate(post_count=Count("post"))
        .filter(is_author=True)
        .order_by("-post_count")
    )[0:2]
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
    top_tags = Tag.objects.annotate(post_count=Count("post")).order_by("-post_count")
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


def homepage(request):
    posts = Post.objects.all()
    latest_posts = Post.objects.all().order_by("-date")[0:3]
    top_posts = Post.objects.all().order_by("-view_count")[0:3]
    subscribe_form = subscribeForm()
    subscribe = False
    website_info = None
    featured_post=None

    if WebsiteMeta.objects.all().exists():
        website_info = WebsiteMeta.objects.all()[0]
    try:
        featured_post = Post.objects.get(is_featured=1)
    except:
        featured_post=None
    if request.POST:
        subscribe_form = subscribeForm(request.POST)
        if subscribe_form.is_valid():
            subscribe_form.save()
            request.session["subscribed"] = True
            subscribe = True
            subscribe_form = subscribeForm()
    context = {
        "posts": posts,
        "latest_posts": latest_posts,
        "top_posts": top_posts,
        "subscribe_form": subscribe_form,
        "subscribe": subscribe,
        "featured_post": featured_post,
        "website_info": website_info,
    }
    return render(request, "app/index.html", context)


def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
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


def author_page(request, slug):
    author_profile = Profile.objects.get(slug=slug)
    print(request.user.username)
    authors_with_post_count = Profile.objects.annotate(post_count=Count("post")).filter(
        is_author=True
    )
    authors = authors_with_post_count.order_by("-post_count")

    topPosts = Post.objects.filter(author=author_profile).order_by("-view_count")[0:2]
    allPosts = Post.objects.filter(author=author_profile).order_by("-date")[0:]

    context = {
        "author_profile": author_profile,
        "authors": authors,
        "all_posts": allPosts,
        "top_posts": topPosts,
    }
    return render(request, "app/author.html", context)


def profile_page(request, slug):
    user = User.objects.get(username=slug)
    profile = Profile.objects.get(user=user)
    bookmarked_posts = Post.objects.filter(bookmarks=user)
    liked_posts = Post.objects.filter(like=user)
    display_posts = request.POST.get(
        "display_posts"
    )  # Get the value of the button clicked

    if profile.is_author:
        author_posts = Post.objects.filter(author=profile)
    else:
        author_posts = None
    if request.POST:
        profile_form = profileForm(request.POST, request.FILES, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            return HttpResponseRedirect(reverse("profile_page", kwargs={"slug": slug}))
    else:
        profile_form = profileForm(instance=profile)

    if display_posts == "bookmarks":
        display_posts = "bookmarks"  # Set the display_posts value to bookmarks
    elif display_posts == "likes":
        display_posts = "likes"
    elif display_posts == "your_posts":
        display_posts = "your_posts"
    context = {
        "user": user,
        "profile": profile,
        "bookmarked_posts": bookmarked_posts,
        "liked_posts": liked_posts,
        "display_posts": display_posts,
        "profile_form": profile_form,
        "author_posts": author_posts,
    }
    return render(request, "app/yourpage.html", context)


def post_blog(request, slug):
    user_profile = Profile.objects.get(user=slug)
    is_author = user_profile.is_author
    postform = PostForm()
    if request.POST:
        postform = PostForm(request.POST, request.FILES)
        print(postform)
        if postform.is_valid():
            post = postform.save(commit=False)
            print(post)
            post.author = user_profile
            print(post.author)
            post.save()
            return HttpResponseRedirect(reverse("post_page", kwargs={"slug": post.slug}))
        else:
            print('errors', postform.errors)
    context = {"is_author":is_author, "postform":postform, "user_profile":user_profile,}
    return render(request, "app/post_blog.html", context)

def update_blog(request, post_slug):
    post = Post.objects.get(slug=post_slug)
    profile = post.author
    is_author=True
    if request.POST:
        updateBlogForm = PostForm(request.POST, request.FILES ,instance=post)
        if updateBlogForm.is_valid():
            updateBlogForm.save()
            return redirect(reverse("post_page", kwargs={"slug": post_slug}))
    else:
        updateBlogForm = PostForm(instance=post)
        
    context = {"post":post, "postform":updateBlogForm, "is_author":is_author, "user_profile":profile}
    return render(request, "app/post_blog.html", context)

def delete_blog(request, post_slug):
    post = Post.objects.get(slug=post_slug)
    profile = post.author
    delete=True
    is_author=True
    if request.POST:
        post.delete()
        return redirect(reverse("profile_page", kwargs={"slug":profile.username}))
    else:
        updateBlogForm = PostForm(instance=post)
    context = {
        "post":post, 
        "postform":updateBlogForm, 
        "delete":delete, 
        "is_author":is_author, 
        "user_profile":profile
    }
    return render(request, "app/post_blog.html", context)

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
        posts = posts.filter(title__icontains=search_query)

    if sort_by == "famous":
        posts = posts.order_by("-view_count")
    elif sort_by == "alphabetical":
        posts = posts.order_by("title")
    elif sort_by == "newest":
        posts = posts.order_by("-date")
    print(sort_by)

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


def bookmarks(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if post.bookmarks.filter(id=request.user.id).exists():
        post.bookmarks.remove(request.user)
    else:
        post.bookmarks.add(request.user)
    """post = get_object_or_404(Post, slug=slug)
    post = get_object_or_404(Post, id=request.POST.get("post_id"))
    if request.POST and request.user.is_authenticated:
        if post.bookmarks.filter(id=request.user.id).exists():
            post.bookmarks.remove(request.user)
        else:
            post.bookmarks.add(request.user)"""
    return HttpResponseRedirect(reverse("post_page", args=[str(slug)]))


def like_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if post.like.filter(id=request.user.id).exists():
        post.like.remove(request.user)
    else:
        post.like.add(request.user)
    return HttpResponseRedirect(reverse("post_page", args=[str(slug)]))


def registration(request):
    form = NewUserForm()
    if request.POST:
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/")
    context = {"form": form}
    return render(request, "registration/registration.html", context)
