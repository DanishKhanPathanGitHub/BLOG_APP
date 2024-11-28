import uuid
from django import forms
from app.models import Comments, Profile, Post
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from tinymce.widgets import TinyMCE
from django.utils.text import slugify

class PostForm(forms.ModelForm):
    tags = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter tags, separated by commas',
            'class': 'tag-input-field',
        })
    )
    class Meta:
        model = Post
        fields = {"content","title", "image", "tags"}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs["placeholder"] = "Enter your title for your post"
        self.fields['content'] = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
        self.fields["image"].widget.attrs["placeholder"] = "upload image for your blog"

    def save(self, *args, **kwargs):
        try:
            prev_title = Post.objects.get(id=self.instance.id).title
            print(prev_title)
            if prev_title != self.instance.title:
                print('inside if')

                slug = str(uuid.uuid4()) + self.cleaned_data['title']
                self.slug = slugify(slug)
        except: 
            print("inside except")
            slug = str(uuid.uuid4()) + self.cleaned_data['title']
            self.instance.slug = slugify(slug)
       
        return super().save(*args, **kwargs)

class commentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = {"content"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["content"].widget.attrs["placeholder"] = "tyepe your comment..."


