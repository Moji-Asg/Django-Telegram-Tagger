from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views import generic

from django_telegram_tagger import helpers
from . import forms


# Create your views here.
class IndexView(generic.RedirectView):
    url = reverse_lazy('settings-main-page')

    @helpers.only_logged_in_users(reverse_lazy('login-page'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class SignInView(LoginView):
    success_url = reverse_lazy('settings-main-page')
    form_class = forms.AuthForm
    template_name = 'auth/login.html'

    def get_success_url(self):
        return self.success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['theme'] = helpers.get_setting('theme')
        return context


class ForgotPasswordView(generic.TemplateView):
    template_name = 'auth/forgot-password.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['theme'] = helpers.get_setting('theme')
        return context


class SignOutView(LogoutView):
    pass
