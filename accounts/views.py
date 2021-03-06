from django.contrib import messages
from django.contrib.messages import views
from django.db.models.fields import NullBooleanField
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView
from django.views.generic.base import View
from requests.api import request
from .models import User
from .forms import RegisterForm
from .facebookapi import FacebookGraph
from .models import (
    UserProfile,
    FacebookApp,
    FacebookPage,
    AutomatePostCommentsResponse,
)


class RegisterView(SuccessMessageMixin, CreateView):
    model = User
    form_class = RegisterForm
    success_url = '/accounts/login'
    template_name = 'accounts/register.html'
    context_object_name = 'form'
    success_message = 'Your account created successfully!'


class DashboardView(LoginRequiredMixin, View):
    template_name = 'accounts/dashboard.html'
    def get(self, request, *args, **kwargs):
        try:
            profile = UserProfile.objects.get(user = request.user) 
        except:
            profile = UserProfile.objects.create(user = request.user)
        
        # page = profile.facebookpage_set.first()
        # try:
        #     page_id = request.session['page_id']
        # except:
            # page_id = request.session.get('page_id', page.id)

        data = {'profile': profile, 'pages': profile.facebookpage_set.all()}
        return render(request, self.template_name,  data)

class FacebookLoginView(LoginRequiredMixin, View):
    try:
        app = FacebookApp.objects.first()
        app_id = app.app_id
        app_secret = app.app_secret
        redirect_url = app.redirect_url
    except:
        app_id = '482847369816069'
        app_secret = '11b994aa0b08dabbcb04c3b2ade775e7'
        redirect_url = 'https://mhddaghestani.pythonanywhere.com/accounts/facebook-login/'
    def get(self, request, *args, **kwargs):
        # if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user = request.user) 
        except:
            profile = UserProfile.objects.create(user = request.user)
        graph = FacebookGraph(self.app_id, self.app_secret, self.redirect_url)
        
        try:
            profile.facebook_user_code = request.GET['code']
            info = graph.get_user_access_token(request.GET['code'])
            profile.facebook_user_access_token = info['access_token']
            profile.facebook_user_id = info['id']
            profile.facebook_user_name = graph.get_user_name()
            profile.pic_url = graph.get_user_profile_picture()
            profile.save()
            for key, value in graph.get_pages().items():
                try:
                    FacebookPage.objects.get(id = value['id'],)
                except:    
                    page = FacebookPage.objects.create(user_profile = profile, id = value['id'], access_token = value['access_token'], name = value['name'])
                    page.pic_url = graph.picture_url(value['id'], value['access_token'])
                    page.save()
            messages.success(request, 'You signed into facebook successfuly!')
            return HttpResponseRedirect(reverse('accounts:dashboard'))
        except:
            messages.success(request, 'Error signing to facebook, Please try again')
            return HttpResponseRedirect(reverse('accounts:dashboard'))
                    
        # context = request.GET['code']
        # return render(request, 'accounts/facebook-info.html', {'data': context})

class FacebookProfileView(LoginRequiredMixin,View):
    template_name   = 'accounts/facebook-dashboard.html'
    no_pages        = 'accounts/no-pages.html'
    no_account      = 'accounts/no-account.html'
    try:
        app = FacebookApp.objects.first()
        app_id = app.app_id
        app_secret = app.app_secret
        redirect_url = app.redirect_url
    except:
        app_id = '482847369816069'
        app_secret = '11b994aa0b08dabbcb04c3b2ade775e7'
        redirect_url = 'https://mhddaghestani.pythonanywhere.com/accounts/facebook-login/'
    def get(self, request, *args, **kwargs):
        try:
            profile = UserProfile.objects.get(user = request.user) 
        except:
            profile = UserProfile.objects.create(user = request.user)

        if profile.facebookpage_set.all().count() == 0: 
            if  not profile.facebook_user_id == None:
                return render(request, self.no_pages)
            else:
                return render(request, self.no_account)
        
        try:
            page_id = request.COOKIES['page_id']
        except:
            try:
                page = profile.facebookpage_set.first()
                page_id = page.id
            except:
                page_id = ''
        if not page_id == '':
            graph = FacebookGraph(self.app_id, self.app_secret, self.redirect_url)
            page = request.user.userprofile.facebookpage_set.get(id = page_id)
            graph.access_token = page.access_token
            return render(request, self.template_name, {'profile': profile, 'pages': profile.facebookpage_set.all(), 'page_id': page_id, 'posts': graph.get_posts(), 'page': page})
        return render(request, self.template_name, {'profile': profile})


class AddPost(View):
    template_name = 'accounts/add_post.html'
    try:
        app = FacebookApp.objects.first()
        app_id = app.app_id
        app_secret = app.app_secret
        redirect_url = app.redirect_url
    except:
        app_id = '482847369816069'
        app_secret = '11b994aa0b08dabbcb04c3b2ade775e7'
        redirect_url = 'https://mhddaghestani.pythonanywhere.com/accounts/facebook-login/'    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'pages': request.user.userprofile.facebookpage_set.all()})

    def post(self, request, *args, **kwargs):
        page = FacebookPage.objects.get(id = request.POST['page_id'])
        graph = FacebookGraph(self.app_id, self.app_secret, self.redirect_url)
        post_id = graph.add_post(page.id ,request.POST['message'], page.access_token)['id']
        messages.success(request, 'Post add successfuly with id %s' % post_id)
        return HttpResponseRedirect(reverse('accounts:facebook-profile'))


class AutomatePostCommentsResponseView(View):
    template_name = 'accounts/automate_post_comments_response.html'
    try:
        app = FacebookApp.objects.first()
        app_id = app.app_id
        app_secret = app.app_secret
        redirect_url = app.redirect_url
    except:
        app_id = '482847369816069'
        app_secret = '11b994aa0b08dabbcb04c3b2ade775e7'
        redirect_url = 'https://mhddaghestani.pythonanywhere.com/accounts/facebook-login/'
    def get(self, request, post_id, *args, **kwargs):
        page = request.user.userprofile.facebookpage_set.get(id = post_id.split('_')[0])
        graph = FacebookGraph(self.app_id, self.app_secret, self.redirect_url)
        graph.access_token = page.access_token
        post = graph.get_post_details(post_id)
        print(post['created_time'])
        # print(timezone.now())
        # created_time = datetime.strptime(post['created_time'], "%Y-%m-%dT%H:%M:%S%z")
        return render(request, self.template_name, {'post': post, 'page': page,})
    def post(self, request, *args, **kwargs):
        page = request.user.userprofile.facebookpage_set.get(id = request.POST['post_id'].split('_')[0])
        post_id = request.POST['post_id'].split('_')[1]
        try:
            post = AutomatePostCommentsResponse.objects.get(post = post_id)
            messages.success(request, 'An automation for this post is already exist')
            return HttpResponseRedirect(reverse('accounts:facebook-profile'))
        except:
            post = AutomatePostCommentsResponse.objects.create(page = page, post = post_id, response = request.POST['response'],response_privetly = request.POST['response_privetly'], name = request.POST['automation'])
            messages.success(request, 'Automation added successfully')
            return HttpResponseRedirect(reverse('accounts:facebook-profile'))