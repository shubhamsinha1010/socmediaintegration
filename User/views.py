from django.shortcuts import render,redirect
from .forms import CreateUserForm,UserUpdateForm, ProfileUpdateForm,DictionaryForm,registgmail,twitterUserForm,autofacebookUserForm
from .models import Profile,UserNew,gmailNew,twitterNew,fbautoNew
from django.conf import settings
import requests
from django.core.mail import EmailMessage
from django.views import View
from isodate import parse_duration
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import tweepy
from selenium import webdriver
from time import sleep
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import ElementClickInterceptedException

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
        url = "https://instagram-data1.p.rapidapi.com/user/info"

        querystring = {"username":request.POST['search']}

        headers = {
            'x-rapidapi-key': "fd35b667f9msh57ee2fc0aac17f7p16e3f1jsn6ceffcd0d8c7",
            'x-rapidapi-host': "instagram-data1.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        results = response.json()
        resultdicts = {
            'username': results["username"],
            'totalposts': results["edge_owner_to_timeline_media"]["count"],
            'full_name': results["full_name"],
            'biography': results["biography"],
            'followers': results["edge_followed_by"]["count"],
            'following': results["edge_follow"]["count"],
            'profilepic': results["profile_pic_url"]
        }

        resultlist.append(resultdicts)

    context = {
            'resultlist': resultlist
        }

    return render(request,'User/userinstagram.html', context)

consumer_key='EiCnJUUwjRaCTUaC4vLVagrzu'
consumer_secret='nDBopQND1OedNHCjBHJS27QrFujNxmPKkEtzCzroOFPW7UuVxc'
access_token='1392787081957715976-Xhz8anBqz8qIuKrvckYA9UVvkIqTnz'
access_token_secret='Uk6Tah0TKd8EVgeEtRaWR1YhUTzhnubFwkvSqldfVAp69'


def OAuth():
    try:
        auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
        auth.set_access_token(access_token,access_token_secret)
        return auth

    except Exception as e:
        return None

def tweetapi(request):
    form = twitterUserForm()
    if request.method=='POST':
        form = twitterUserForm(request.POST)
        oauth = OAuth()
        api = tweepy.API(oauth)
        api.update_status(request.POST['search'])

        if form.is_valid():

            twt = form.cleaned_data['usertweet']
            dfsc = twitterNew(usertweet=twt)
            dfsc.save()
            form.save()
            messages.success(request, f'Your tweet has been posted')



    return render(request,'User/twittertweet.html',{'email_forme':form})


def fbauto(request):
    form = autofacebookUserForm()
    if request.method=='POST':
        form = autofacebookUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['faceuser']
            password = form.cleaned_data['facepassword']
            caption = form.cleaned_data['facecaption']
            image_path = form.cleaned_data['myfile']
            print(image_path)


            dser = fbautoNew(faceuser=username,facepassword=password,facecaption=caption,facepath=image_path)
            options = FirefoxOptions()
            options.add_argument("--headless")
            driver = webdriver.Firefox(
                executable_path='/home/shubham/Downloads/geckodriver-v0.29.1-linux64/geckodriver', options=options)

            driver.get('https://www.facebook.com')
            driver.maximize_window()
            driver.find_element_by_xpath('.//*[@id="email"]').send_keys('hackerop.bolte')
            driver.find_element_by_xpath('.//*[@id="pass"]').send_keys('univity2020')
            driver.find_element_by_name('login').click()
            sleep(7)
            driver.find_element_by_class_name('oajrlxb2.b3i9ofy5.qu0x051f.esr5mh6w.e9989ue4.r7d6kgcz.rq0escxv.nhd2j8a9.j83agx80.p7hjln8o.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.cxgpxx05.d1544ag0.sj5x9vvc.tw6a2znq.i1ao9s8h.esuyzwwr.f1sip0of.lzcic4wl.l9j0dhe7.abiwlrkh.p8dawk7l.bp9cbjyn.orhb3f3m.czkt41v7.fmqxjp7s.emzo65vh.btwxx1t3.buofh1pr.idiwt2bm.jifvfom9.kbf60n1y')
            try:
                fjdkf = driver.find_element_by_class_name('m9osqain.a5q79mjw.gy2v8mqq.jm1wdb64.k4urcfbm.qv66sw1b')
                fjif = fjdkf.find_element_by_class_name('a8c37x1j.ni8dbmo4.stjgntxs.l9j0dhe7')
                fjif.click()
                sleep(7)
            except Exception as error:
                print("Error")


            fsdf = driver.find_element_by_class_name('notranslate._5rpu')

            fsdf.send_keys('hellloooo')
            sleep(9)
            driver.find_element_by_css_selector('div[aria-label="Photo/Video"]').click()
            sleep(9)
            driver.find_element_by_xpath(
                '/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/form/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[1]/div/div/input').send_keys('/home/shubham/socialmediaintegration/socialmediaintegration/media/default.jpg')
            sleep(12)
            postbtn = driver.find_elements_by_tag_name('span')
            for i in postbtn:
                if i.text == 'Post':
                    i.click()
            form.save()
            dser.save()
            driver.quit()

    return render(request,'User/facebookautomation.html',{'email_forms':form})





def autfunc(request):
    options = FirefoxOptions()
    options.add_argument("--headless")
    driver=webdriver.Firefox(executable_path='/home/shubham/Downloads/geckodriver-v0.29.1-linux64/geckodriver',options=options)
    driver.get('https://www.facebook.com')

    username='hackerop.bolte'
    password='university2020'

    driver.find_element_by_xpath('.//*[@id="email"]').send_keys(username)
    driver.find_element_by_xpath('.//*[@id="pass"]').send_keys(password)
    driver.find_element_by_name('login').click()
    sleep(11)
    driver.find_element_by_class_name('oajrlxb2.b3i9ofy5.qu0x051f.esr5mh6w.e9989ue4.r7d6kgcz.rq0escxv.nhd2j8a9.j83agx80.p7hjln8o.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.cxgpxx05.d1544ag0.sj5x9vvc.tw6a2znq.i1ao9s8h.esuyzwwr.f1sip0of.lzcic4wl.l9j0dhe7.abiwlrkh.p8dawk7l.bp9cbjyn.orhb3f3m.czkt41v7.fmqxjp7s.emzo65vh.btwxx1t3.buofh1pr.idiwt2bm.jifvfom9.kbf60n1y')
    try:
        fjdkf = driver.find_element_by_class_name('m9osqain.a5q79mjw.gy2v8mqq.jm1wdb64.k4urcfbm.qv66sw1b')
        fjif = fjdkf.find_element_by_class_name('a8c37x1j.ni8dbmo4.stjgntxs.l9j0dhe7')
        fjif.click()
        sleep(11)
    except ElementClickInterceptedException as exception:
        pass
    fsdf = driver.find_element_by_class_name('notranslate._5rpu')
    fsdf.send_keys('helooo')
    sleep(9)
    driver.find_element_by_css_selector('div[aria-label="Photo/Video"]').click()
    sleep(7)
    image_path = '/home/shubham/Desktop/large_rbSbk8j.jpg'
    alabas = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/form/div/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div[1]/div/div/input')
    alabas.send_keys(image_path)
    sleep(9)
    postbtn = driver.find_elements_by_tag_name('span')
    for i in postbtn:
         if i.text=='Post':
            i.click()


