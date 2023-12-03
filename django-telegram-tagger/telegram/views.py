import json

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import View, generic

from django_telegram_tagger import helpers
from . import forms, models, FormsMetaClass


# Create your views here.
class IndexView(generic.RedirectView):
    url = reverse_lazy('settings-main-page')

    @helpers.only_logged_in_users(reverse_lazy('login-page'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class SettingsView(generic.FormView):
    def get_form_class(self):
        return self.form_class()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['theme'] = helpers.get_setting('theme')
        return context

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        for k, v in cleaned_data.items():
            setting_defaults = {
                'name': k,
                'value': str(v)
            }
            setting_model, created = models.SettingsModel.objects.get_or_create(setting_defaults, name__exact=k)

            if not created:
                setting_model.value = str(v)
                setting_model.save()

        return self.render_to_response(self.get_context_data(form=form, success=True))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form, success=False))

    def get_initial(self):
        initial = super().get_initial()

        form_class = self.get_form_class()
        for k in form_class.declared_fields:
            value = helpers.get_setting(k)

            if isinstance(form_class.declared_fields[k], forms.forms.BooleanField):
                initial[k] = eval(value)
                continue

            initial[k] = value

        return initial

    @helpers.only_logged_in_users(reverse_lazy('login-page'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class MainSettingsView(SettingsView):
    form_class = FormsMetaClass.get_main_form
    template_name = 'telegram/settings-main.html'


class CommandsSettingsView(SettingsView):
    form_class = FormsMetaClass.get_commands_form
    template_name = 'telegram/settings-commands.html'


class RespondsSettingsView(SettingsView):
    form_class = FormsMetaClass.get_responds_form
    template_name = 'telegram/settings-responds.html'


class ChangeThemeView(View):
    def post(self, request: WSGIRequest):
        data = request.POST

        if 'theme' not in data:
            response = {'ok': False, 'error': 'no key named \'theme\''}
            return HttpResponse(json.dumps(response))

        if not request.user.is_authenticated:
            response = {'ok': False, 'error': 'user is not authorized'}
            return HttpResponse(json.dumps(response))

        theme_defaults = {
            'name': 'theme',
            'value': data['theme']
        }
        theme, created = models.SettingsModel.objects.get_or_create(theme_defaults, name__exact='theme')

        if not created:
            theme.value = data['theme']
            theme.save()

        response = {'ok': True, 'error': ''}
        return HttpResponse(json.dumps(response))
