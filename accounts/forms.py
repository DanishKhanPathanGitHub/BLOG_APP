
from django import forms
from accounts.models import Profile, User


class profileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = {"profilePic", "bio"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["profilePic"].widget.attrs["placeholder"] = "Update profile pic"
        self.fields["bio"].widget.attrs["placeholder"] = "Update bio"


class NewUserForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["placeholder"] = "Enter your username..."
        self.fields["email"].widget.attrs["placeholder"] = "Enter your email..."
        self.fields["password"].widget.attrs["placeholder"] = "Enter your password..."  
        self.fields["confirm_password"].widget.attrs["placeholder"] = "Confirm your password..."
        

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        new = User.objects.filter(email=email)
        if new:
            raise forms.ValidationError("email already exists")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if not password or not confirm_password:
            raise forms.ValidationError("Both password fields are required.")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data
