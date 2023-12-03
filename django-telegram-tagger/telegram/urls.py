from django.urls import path
from . import views


urlpatterns = [
    path('', views.IndexView.as_view(), name='settings-page'),
    path('main/', views.MainSettingsView.as_view(), name='settings-main-page'),
    path('commands/', views.CommandsSettingsView.as_view(), name='settings-commands-page'),
    path('responds/', views.RespondsSettingsView.as_view(), name='settings-responds-page'),
    path('change-theme/', views.ChangeThemeView.as_view(), name='change-theme'),
]
