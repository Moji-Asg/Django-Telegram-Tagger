from django.views import generic
from django_telegram_tagger import helpers


class IndexView(generic.TemplateView):
    template_name = 'main/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['theme'] = helpers.get_setting('theme')
        return context
