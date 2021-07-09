from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from .models import Profile,gmailNew,twitterNew,fbautoNew
from django.conf import settings
import requests

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

class twitterUserForm(forms.ModelForm):
    class Meta:
        model = twitterNew
        fields = ['usertweet']

class autofacebookUserForm(forms.ModelForm):
    class Meta:
        model = fbautoNew
        fields = ['faceuser','facepassword','facepath','facecaption']


class regist(forms.Form):
    name = forms.CharField(error_messages={'required':'Enter your Username'})
    email = forms.EmailField(error_messages={'required': 'Enter your Email'})
    password = forms.CharField(widget=forms.PasswordInput,error_messages={'required': 'Enter your Password'},min_length=8,max_length=25)

class registgmail(forms.Form):
    email = forms.EmailField(error_messages={'required': 'Enter your Email'})
    subject = forms.CharField(error_messages={'required': 'Enter your Subject'})
    message = forms.CharField(error_messages={'required': 'Enter the Message'})
    attach = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))



class DictionaryForm(forms.Form):
    word = forms.CharField(max_length=100)

    def search(self):
        result = {}
        word = self.cleaned_data['word']
        endpoint = 'https://od-api.oxforddictionaries.com/api/v2/entries/{source_lang}/{word_id}'
        url = endpoint.format(source_lang='en', word_id=word)
        print("OED credentials: {!r}, {!r}".format(settings.OXFORD_APP_ID, settings.OXFORD_APP_KEY), flush=True)
        headers = {'app_id': settings.OXFORD_APP_ID, 'app_key': settings.OXFORD_APP_KEY}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:  # SUCCESS
            result = response.json()
            result['success'] = True
        else:
            result['success'] = False
            if response.status_code == 404:  # NOT FOUND
                result['message'] = 'No entry found for "%s"' % word
            else:
                result['message'] = 'The Oxford API is not available at the moment. Please try again later.'
        return result


class TwitterForm(forms.Form):
    tweet = forms.CharField(max_length=100)


class FacebookAutoForm(forms.Form):
    fbusername = forms.CharField(error_messages={'required': 'Enter the username'})
    fbpassword = forms.CharField(widget=forms.PasswordInput, error_messages={'required': 'Enter your Password'},
                               min_length=8, max_length=25)
    imagepath = forms.ImageField(error_messages={'required': 'Enter the imagepath'})
    caption = forms.CharField(error_messages={'required': 'Enter the caption'})
