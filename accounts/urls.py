from accounts.forms import RegisterForm
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import (
    RegisterView,
    DashboardView,
    FacebookLoginView,
    FacebookProfileView,
    AddPost,
    AutomatePostCommentsResponseView,
)

app_name = 'accounts'
urlpatterns = [
    path('login/', LoginView.as_view(template_name = 'accounts/login.html'), name= 'login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('dashboard', DashboardView.as_view(), name='dashboard'),
    path('facebook-login/', FacebookLoginView.as_view(), name='facebook-login'),
    path('facebook/', FacebookProfileView.as_view(), name='facebook-profile'),
    path('add-post/', AddPost.as_view(), name='add-post'),
    path('add-automate-response/<str:post_id>/', AutomatePostCommentsResponseView.as_view(), name='response'),
]
