from django.db import models
from django.contrib.auth.models import User
from PIL import Image


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super().save()

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)



class UserNew(models.Model):
    username = models.CharField(max_length=70)
    email = models.EmailField(max_length=70)
    password = models.CharField(max_length=70)


class gmailNew(models.Model):
    email = models.EmailField(max_length=70)
    subject = models.CharField(max_length=70)
    message = models.CharField(max_length=70)


class twitterNew(models.Model):
    usertweet = models.CharField(max_length=100)


class fbautoNew(models.Model):
    faceuser = models.CharField(max_length=100)
    facepassword = models.CharField(max_length=100)
    facepath = models.ImageField(max_length=100)
    facecaption = models.CharField(max_length=100)

