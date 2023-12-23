from django import forms
from app.models import Comments, Subscribe, Profile, Post
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class commentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = {"content"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["content"].widget.attrs["placeholder"] = "tyepe your comment..."


class subscribeForm(forms.ModelForm):
    class Meta:
        model = Subscribe
        fields = "__all__"
        labels = {"email": _("")}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs["placeholder"] = "Enter your email..."


class profileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = {"profilePic", "bio"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["profilePic"].widget.attrs["placeholder"] = "Update profile pic"
        self.fields["bio"].widget.attrs["placeholder"] = "Update bio"


class NewUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = {"username", "email", "password1", "password2"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["placeholder"] = "Enter your username..."
        self.fields["email"].widget.attrs["placeholder"] = "Enter your email..."
        self.fields["password1"].widget.attrs["placeholder"] = "Enter your password..."
        self.fields["password2"].widget.attrs[
            "placeholder"
        ] = "Enter your password again..."

    def clean_username(self):
        username = self.cleaned_data["username"].lower()
        new = User.objects.filter(username=username)
        if new:
            raise forms.ValidationError("username already exists")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        new = User.objects.filter(email=email)
        if new:
            raise forms.ValidationError("email already exists")
        return email

    def clean_password(self):
        password1 = self.cleaned_data["password1"]
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError("password doesn't match")
        return password2

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = {"post","title", "image",}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs["placeholder"] = "Enter your title for your post"
        self.fields["post"].widget.attrs["placeholder"] = "Write your blog..."
        self.fields["image"].widget.attrs["placeholder"] = "upload image for your blog"
