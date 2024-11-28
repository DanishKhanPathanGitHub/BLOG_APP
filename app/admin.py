from django.contrib import admin
from app.models import Post, Tag, Comments, WebsiteMeta
from accounts.models import User, Profile
# Register your models here.
admin.site.register(Post)
admin.site.register(Tag)
admin.site.register(User)
admin.site.register(Comments)
admin.site.register(Profile)
admin.site.register(WebsiteMeta)

