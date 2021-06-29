from django.shortcuts import render,redirect
from .forms import CreateUserForm,UserUpdateForm, ProfileUpdateForm,gmailUserForm,DictionaryForm,registgmail
from .models import Profile,UserNew,gmailNew
from django.conf import settings
import requests
from django.core.mail import EmailMessage
from django.views import View
from isodate import parse_duration
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def register(request):
    form = CreateUserForm()
    if request.method=='POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            usnm = form.cleaned_data['username']
            eml = form.cleaned_data['email']
            pswd = form.cleaned_data['password1']

            reg = UserNew(username = usnm,email = eml,password = pswd)
            reg.save()
            form.save()
            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('user-login')
        else:
            pswd = request.POST.get('password1')
            pdss = request.POST.get('password2')
            if pswd!=pdss:
                messages.success(request, f'The passwords dont match')
                form = CreateUserForm()
            elif len(pswd)<8:
                messages.success(request, f'The password must be greater than 8 and must include numbers')
                form = CreateUserForm()

            else:
                messages.success(request, f'The password cannot be entirely numeric')
                form = CreateUserForm()

    return render(request,'User/register.html',{'form': form})

def loginUser(request):
	if request.user.is_authenticated:
		return redirect('user-home')
	else:
		if request.method == 'POST':
			username = request.POST.get('username')
			password =request.POST.get('password')

			user = authenticate(request, username=username, password=password)

			if user is not None:
				login(request, user)
				return redirect('user-home')
			else:
				messages.info(request, 'Username OR password is incorrect')

		context = {}
		return render(request, 'User/login.html', context)


def logoutUser(request):
	logout(request)
	return redirect('user-login')



@login_required(login_url='user-login')
def home(request):
    context = {}
    return render(request, 'User/home.html',context)


@login_required
def profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile(user=request.user)
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'User/profile.html', context)

# @login_required
# def gmailus(request):
#     form = gmailUserForm()
#     if request.method=="POST":
#         form = gmailUserForm(request.POST)
#         if form.is_valid():
#             emal = form.cleaned_data['email']
#             subj = form.cleaned_data['subject']
#             msgs = form.cleaned_data['message']
#             regs = gmailNew(email=emal,subject=subj,message=msgs)
#             regs.save()
#             form.save()
#             send_mail(subj,msgs,settings.EMAIL_HOST_USER,[emal],fail_silently=False)
#             messages.success(request, f'The email is sent successfully')
#         else:
#             form = gmailUserForm()
#
#     return render(request,'User/usergmail.html',{'form':form})


class EmailAttachementView(View):
    form_class = registgmail
    template_name = 'User/usergmail.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'email_form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():

            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            email = form.cleaned_data['email']
            files = request.FILES.getlist('attach')
            regs = gmailNew(email=email, subject=subject, message=message)
            regs.save()

            try:
                mail = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [email])
                for f in files:
                    mail.attach(f.name, f.read(), f.content_type)
                mail.send()
                return render(request, self.template_name,
                              {'email_form': form, 'error_message': 'Sent email to %s' % email})
            except:
                return render(request, self.template_name,
                              {'email_form': form, 'error_message': 'Either the attachment is too big or corrupt'})

        return render(request, self.template_name,
                      {'email_form': form, 'error_message': 'Unable to send email. Please try again later'})


@login_required
def facebookus(request):
    return render(request,'User/userfacebook.html')

@login_required
def oxford(request):
    search_result = {}
    if 'word' in request.GET:
        form = DictionaryForm(request.GET)
        if form.is_valid():
            search_result = form.search()
    else:
        form = DictionaryForm()
    return render(request, 'User/oxford.html', {'form': form, 'search_result': search_result})

@login_required
def youtubeview(request):
    videos = []

    if request.method == 'POST':
        search_url = 'https://www.googleapis.com/youtube/v3/search'
        video_url = 'https://www.googleapis.com/youtube/v3/videos'

        search_params = {
            'part': 'snippet',
            'q': request.POST['search'],
            'key': settings.YOUTUBE_DATA_API_KEY,
            'maxResults': 9,
            'type': 'video'
        }

        r = requests.get(search_url, params=search_params)

        results = r.json()['items']

        video_ids = []
        for result in results:
            video_ids.append(result['id']['videoId'])

        if request.POST['submit'] == 'lucky':
            return redirect(f'https://www.youtube.com/watch?v={video_ids[0]}')

        video_params = {
            'key': settings.YOUTUBE_DATA_API_KEY,
            'part': 'snippet,contentDetails',
            'id': ','.join(video_ids),
            'maxResults': 9
        }

        r = requests.get(video_url, params=video_params)

        results = r.json()['items']

        for result in results:
            video_data = {
                'title': result['snippet']['title'],
                'id': result['id'],
                'url': f'https://www.youtube.com/watch?v={result["id"]}',
                'duration': int(parse_duration(result['contentDetails']['duration']).total_seconds() // 60),
                'thumbnail': result['snippet']['thumbnails']['high']['url']
            }

            videos.append(video_data)

    context = {
        'videos': videos
    }

    return render(request, 'User/youtube.html', context)


@login_required
def instagramview(request):
    resultlist = []
    if request.method == 'POST':
        url = "https://easy-instagram-service.p.rapidapi.com/username"

        querystring = {"username": request.POST['search'], "random": "x8n3nsj2"}

        headers = {
            'x-rapidapi-key': "df12ad1e08msh6d8d43e4dbeb269p1e73bcjsn642e41041d36",
            'x-rapidapi-host': "easy-instagram-service.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        results = response.json()
        resultdicts = {
            'full_name': results["full_name"],
            'biography': results["biography"],
            'total_post': results["total_post"],
            'is_verified': results["is_verified"]
        }

        resultlist.append(resultdicts)

        context = {
            'resultlist': resultlist
        }

        return render(request,'User/userinstragram.html', context)

