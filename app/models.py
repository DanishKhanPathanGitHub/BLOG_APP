from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profilePic = models.ImageField(null=True, blank=True, upload_to="images/")
    slug = models.CharField(max_length=200, unique=True)
    bio = models.CharField(max_length=400)
    is_author = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.user.username)
        return super(Profile, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.first_name


class Subscribe(models.Model):
    email = models.EmailField(max_length=254)
    date = models.DateTimeField(auto_now=True)


class Tag(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    slug = models.CharField(max_length=200, unique=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        return super(Tag, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Post(models.Model):
    post = models.TextField()
    title = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    image = models.ImageField(null=True, blank=False, upload_to="images/")
    slug = models.CharField(max_length=200, unique=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="post")
    view_count = models.IntegerField(null=True, blank=False)
    is_featured = models.BooleanField(default=False)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    bookmarks = models.ManyToManyField(
        User, blank=True, default=None, related_name="bookmarks"
    )
    like = models.ManyToManyField(User, blank=True, default=None, related_name="likes")

    def like_count(self):
        return self.like.count()
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.title)
        return super(Post, self).save(*args, **kwargs)


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
