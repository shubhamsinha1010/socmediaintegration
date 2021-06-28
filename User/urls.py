from django.urls import path
from .views import register,loginUser,logoutUser,home,profile,facebookus,oxford,youtubeview,EmailAttachementView
from django.contrib.auth import views as auth_views

urlpatterns = [

path('', loginUser,name="user-login"),
path('register/', register,name="user-register"),
path('home/', home,name="user-home"),
path('logout/',logoutUser,name="user-logout"),
path('profile/', profile, name='profile'),
path('gmail/', EmailAttachementView.as_view(), name='emailattachment'),
path('oxford/', oxford, name='user-oxford'),
path('youtube/', youtubeview, name='user-youtube'),
path('facebook/', facebookus, name='user-facebook'),
path('change-password/',auth_views.PasswordChangeView.as_view(template_name = 'User/change-password.html',
                success_url = '/'),name = 'change-password'),
# path('password-reset/',passwordreset,name="password-reset"),
# path('password-reset/done/',passwordresetdone,name="password-reset-done"),
# path('password-reset-confirm/<uidb64>/<token>/',passwordresetconfirm,name="password-reset-confirm"),

]