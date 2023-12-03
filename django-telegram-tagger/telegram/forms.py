from django import forms
from django.conf import settings


class GroupCharField(forms.CharField):
    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop('group')

        super().__init__(*args, **kwargs)


class GroupBooleanField(forms.BooleanField):
    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop('group')

        super().__init__(*args, **kwargs)


class GroupChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop('group')

        super().__init__(*args, **kwargs)


ADMINS_LIST_HELP_TEXT = 'telegram/components/_admins-list-help-text.html'

UNEDITABLE_ERROR = 'This field is not editable!'
REQUIRED_ERROR = 'This field is required!'
MAX_LENGTH_ERROR = 'Maximum length is {}!'


class SettingsMainForm:
    admins_list = forms.CharField(
        label='Admins list',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'area-describedby': 'listAdminHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'ltr',
                'js-default': settings.DEFAULT_SETTINGS['admins_list']
            }
        ),
        help_text=ADMINS_LIST_HELP_TEXT
    )


class SettingsCommandsForm:
    settings_command = forms.CharField(
        label='Settings',
        required=True,
        max_length=24,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'area-describedby': 'settingsCommandHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'auto',
                'js-default': settings.DEFAULT_SETTINGS['settings_command']
            }
        ),
        error_messages={
            'required': REQUIRED_ERROR,
            'max_length': MAX_LENGTH_ERROR
        },
        help_text='Enter command related to settings panel'
    )

    set_username_command = forms.CharField(
        label='تنظیم یوزرنیم',
        disabled=True,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'area-describedby': 'setUsernameCommandHelp',
                'dir': 'auto',
                'js-default': settings.DEFAULT_SETTINGS['set_username_command']
            }
        ),
        error_messages={
            'disabled': UNEDITABLE_ERROR
        },
        help_text='Command related to setting username (not editable)'
    )

    set_password_command = forms.CharField(
        label='تنظیم پسورد',
        disabled=True,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'area-describedby': 'setUsernameCommandHelp',
                'dir': 'auto',
                'js-default': settings.DEFAULT_SETTINGS['set_password_command']
            }
        ),
        error_messages={
            'disabled': UNEDITABLE_ERROR
        },
        help_text='Command related to setting password (not editable)'
    )

    help_command = forms.CharField(
        label='راهنما',
        disabled=True,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'area-describedby': 'setUsernameCommandHelp',
                'dir': 'auto',
                'js-default': settings.DEFAULT_SETTINGS['help_command']
            }
        ),
        error_messages={
            'disabled': UNEDITABLE_ERROR
        },
        help_text='Command related to help text (not editable)'
    )


class SettingsRespondsForm:
    pass
