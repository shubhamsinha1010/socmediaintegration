from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
# Create your views here.
from .forms import CreateUserForm,UserUpdateForm, ProfileUpdateForm,gmailUserForm,DictionaryForm
from .models import Profile,UserNew,gmailNew
from django.conf import settings
from django.core.mail import send_mail

from django.contrib import messages
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout

from django.contrib.auth.forms import UserCreationForm

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
            form = CreateUserForm()
    return render(request,'User/register.html',{'form': form})

# def register(request):
#     form = CreateUserForm()
#     if request.method=='POST':
#         form = CreateUserForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, f'Your account has been created! You are now able to log in')
#             return redirect('user-login')
#         else:
#             form = CreateUserForm()
#     return render(request,'User/register.html',{'form': form})

# def loginUser(request):
#     if request.method=='POST':
#         username=request.POST.get('username')
#         password=request.POST.get('password')
#         user = authenticate(request,username=username,password=password)
#         if user is not None:
#             login(request,user)
#             return redirect('user-home')
#         else:
#             messages.info(request,"Username or password is incorrect")
#
#     return render(request,'User/login.html')

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

@login_required
def gmailus(request):
    form = gmailUserForm()
    if request.method=="POST":
        form = gmailUserForm(request.POST)
        if form.is_valid():
            emal = form.cleaned_data['email']
            subj = form.cleaned_data['subject']
            msgs = form.cleaned_data['message']
            regs = gmailNew(email=emal,subject=subj,message=msgs)
            regs.save()
            form.save()
            send_mail(subj,msgs,settings.EMAIL_HOST_USER,[emal],fail_silently=False)
            messages.success(request, f'The email is sent successfully')
        else:
            form = gmailUserForm()

    return render(request,'User/usergmail.html',{'form':form})


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