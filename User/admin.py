from django.contrib import admin
from .models import Profile,UserNew,gmailNew,twitterNew,fbautoNew
# Register your models here.

@admin.register(UserNew)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username','email','password')
admin.site.register(Profile)
admin.site.register(gmailNew)
admin.site.register(twitterNew)
admin.site.register(fbautoNew)
