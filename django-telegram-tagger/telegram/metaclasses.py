from django import forms
from . import telegram, forms as fm


class TelegramMetaClass(type):
    main = telegram.Telegram

    def __new__(cls, cls_name, bases, attrs):
        bases = list(bases)
        if telegram.Telegram in bases:
            bases.remove(telegram.Telegram)

        if cls.main not in bases:
            bases.append(cls.main)

        cls.main = type(cls_name, (*bases,), attrs)

        return cls.main

    @classmethod
    def get_telegram(cls):
        return cls.main


class FormsMetaClass(type):
    __attrs = {}

    def __new__(cls, cls_name, bases, attrs):
        clean_attrs = {k: v for k, v in attrs.items() if not k.startswith('_')}

        if fm.SettingsMainForm in bases:
            if 'main' not in cls.__attrs:
                cls.__attrs['main'] = {}

            cls.__attrs['main'].update(clean_attrs)
        elif fm.SettingsRespondsForm in bases:
            if 'responds' not in cls.__attrs:
                cls.__attrs['responds'] = {}

            cls.__attrs['responds'].update(clean_attrs)
        elif fm.SettingsCommandsForm in bases:
            if 'commands' not in cls.__attrs:
                cls.__attrs['commands'] = {}

            cls.__attrs['commands'].update(clean_attrs)

        return type(cls_name, (forms.Form,), cls.__attrs)

    @classmethod
    def get_main_form(cls):
        new_attrs = {}
        for attr in dir(fm.SettingsMainForm)[::-1]:
            if attr.startswith('_'):
                continue

            new_attrs[attr] = getattr(fm.SettingsMainForm, attr)
        return type('SettingsMainForm', (forms.Form,), {**cls.__attrs.get('main'), **new_attrs})

    @classmethod
    def get_commands_form(cls):
        new_attrs = {}
        for attr in dir(fm.SettingsCommandsForm)[::-1]:
            if attr.startswith('_'):
                continue

            new_attrs[attr] = getattr(fm.SettingsCommandsForm, attr)
        return type('SettingsCommandsForm', (forms.Form,), {**cls.__attrs.get('commands'), **new_attrs})

    @classmethod
    def get_responds_form(cls):
        new_attrs = {}
        for attr in dir(fm.SettingsRespondsForm)[::-1]:
            if attr.startswith('_'):
                continue

            new_attrs[attr] = getattr(fm.SettingsRespondsForm, attr)
        return type('SettingsRespondsForm', (forms.Form,), {**cls.__attrs.get('responds'), **new_attrs})
