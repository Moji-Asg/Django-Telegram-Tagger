#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import threading
import time

from pyrogram import idle, Client


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_telegram_tagger.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    proc = threading.Thread(
        target=execute_from_command_line,
        args=(sys.argv,),
        daemon=True
    )

    if 'login' in sys.argv:
        cli = Client('app', 3195701, '5f90aac24b411f83faa5f57e18274430', workdir="./db/")
        cli.start()
        print("Session Created!")
        return cli.stop(False)

    if 'runserver' not in sys.argv:
        return proc.run()

    proc.start()

    from django.core.exceptions import AppRegistryNotReady

    while True:
        try:
            from django.apps import apps
            apps.check_apps_ready()
            apps.check_models_ready()
            break
        except AppRegistryNotReady:
            time.sleep(1)

    from telegram import get_telegram
    from django.conf import settings

    obj = get_telegram()

    cli = obj(
        settings.TELEGRAM_SESSION,
        settings.TELEGRAM_API_ID,
        settings.TELEGRAM_API_HASH
    )

    cli.start()

    print('Telegram - Started')

    idle()


if __name__ == '__main__':
    main()
