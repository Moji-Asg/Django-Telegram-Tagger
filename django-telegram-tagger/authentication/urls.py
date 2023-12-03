from django.urls import path
from . import views


urlpatterns = [
    path('', views.IndexView.as_view(), name='auth-page'),
    path('login/', views.SignInView.as_view(), name='login-page'),
    path('logout/', views.SignOutView.as_view(), name='logout-page'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password-page')
]
