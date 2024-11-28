from django.urls import path
from app import views

urlpatterns = [
    path("", views.home, name="home"),
    path("post/<slug:slug>", views.post_page, name="post_page"),
    path("tag/<str:name>", views.tag_page, name="tag_page"),
    path("author/<slug:slug>", views.author_page, name="author_page"),
    path("search/", views.search, name="search_page"),
    path("search/<str:sort_by>", views.search, name="search_page"),
    path("profile/<slug:slug>", views.profile_page, name="profile_page"),
    path("about/", views.about, name="about_page"),
    path("bookmarks/<slug:slug>", views.bookmarks, name="bookmarks_page"),
    path("likes/<slug:slug>", views.like_post, name="likes_page"),
    path("post_blog/<slug:slug>", views.post_blog, name="post_blog"),
    path('tags/suggestions/', views.tag_suggestions, name='tag_suggestions'),
    path("update_blog/<slug:post_slug>", views.update_blog, name="update_blog"),
     path("delete_blog/<slug:post_slug>", views.delete_blog, name="delete_blog"),
]
