import socket
import sys

from django.shortcuts import redirect
from django.core.exceptions import SynchronousOnlyOperation
from django.apps import apps
from django.conf import settings


def _import_models(app_name: str, model_name: str):
    model = apps.get_model(app_name, model_name)
    return model


def get_setting(name: str):
    SettingsModel = _import_models('telegram', 'SettingsModel')
    try:
        result = SettingsModel.objects.get(name__exact=name)
        return result.value
    except SynchronousOnlyOperation:
        return get_setting_async(name)
    except:
        return settings.DEFAULT_SETTINGS.get(name)


async def get_setting_async(name: str):
    SettingsModel = _import_models('telegram', 'SettingsModel')
    try:
        result = await SettingsModel.objects.aget(name__exact=name)
        return result.value
    except:
        return settings.DEFAULT_SETTINGS.get(name)


def only_logged_in_users(url: str):
    def dispatcher(func: callable):
        def wrapper(*args, **kwargs):
            self = args[0]
            if not self.request.user.is_authenticated:
                return redirect(url)
            return func(*args, **kwargs)

        return wrapper

    return dispatcher


def get_full_url(rel_url: str = None):
    domain = settings.DOMAIN_NAME
    port = None

    if not domain:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        domain = s.getsockname()[0]
        s.close()

        try:
            port = int(sys.argv[2].split(':')[1])
        except:
            port = 8000

    if not port:
        return domain + rel_url if rel_url else domain
    else:
        return domain + ":" + str(port) + rel_url if rel_url else domain + ":" + str(port)
