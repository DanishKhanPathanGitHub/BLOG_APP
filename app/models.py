from django.db import models

import uuid
from tinymce.models import HTMLField
from accounts.models import User, Profile
# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Post(models.Model):
    content = HTMLField(blank=True, null=True)
    title = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    image = models.ImageField(null=True, blank=True, upload_to="images/")
    slug = models.CharField(max_length=200, unique=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="posts")
    view_count = models.IntegerField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    bookmarks = models.ManyToManyField(
        User, blank=True, default=None, related_name="bookmarks"
    )
    like = models.ManyToManyField(User, blank=True, default=None, related_name="likes")

    def like_count(self):
        return self.like.count()
    
    


class Comments(models.Model):
    content = models.TextField()
    date = models.DateField(auto_now=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="replies",
    )


class WebsiteMeta(models.Model):
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=500)
    About = models.TextField()
