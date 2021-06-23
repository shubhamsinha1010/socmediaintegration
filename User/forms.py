from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from .models import Profile,gmailNew

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','password1','password2']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class gmailUserForm(forms.ModelForm):
    class Meta:
        model = gmailNew
        fields = ['email','subject','message']

class regist(forms.Form):
    name = forms.CharField(error_messages={'required':'Enter your Username'})
    email = forms.EmailField(error_messages={'required': 'Enter your Email'})
    password = forms.CharField(widget=forms.PasswordInput,error_messages={'required': 'Enter your Password'})

class registgmail(forms.Form):
    email = forms.EmailField(error_messages={'required': 'Enter your Email'})
    subject = forms.CharField(error_messages={'required': 'Enter your Subject'})
    message = forms.CharField(error_messages={'required': 'Enter the Message'})