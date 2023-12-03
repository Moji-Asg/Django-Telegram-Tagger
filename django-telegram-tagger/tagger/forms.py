from django import forms
from django_telegram_tagger import helpers
from telegram import forms as telegram, FormsMetaClass
from .settings import TAGGER_SETTINGS


REQUIRED_ERROR = 'This field is required!'
INVALID_ERROR = 'The input data is not valid!'
MAX_LENGTH_ERROR = 'Maximum character length is {}!'

TAG_SPEED_HELP_TEXT = 'tagger/components/_tag-speed-help-text.html'
MENTION_TAG_HELP_TEXT = 'tagger/components/_mention-tag-help-text.html'
TAG_LIST_HELP_TEXT = 'tagger/components/_tag-list-help-text.html'
REPLY_TAG_HELP_TEXT = 'tagger/components/_reply-tag-help-text.html'
AUTO_TAG_TYPE_HELP_TEXT = 'tagger/components/_auto-tag-type-help-text.html'
AUTO_TAG_CHATS_HELP_TEXT = 'tagger/components/_auto-tag-chats-help-text.html'


class SettingsForm(telegram.SettingsMainForm, metaclass=FormsMetaClass):
    tagger_activation = forms.BooleanField(
        label='Activate Tagger',
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-inline',
                'autocomplete': 'off',
                'js-default': TAGGER_SETTINGS['tagger_activation']
            }
        )
    )

    tag_speed = forms.CharField(
        label='Tag Speed',
        required=True,
        max_length=5,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'area-describedby': 'taggerSpeedHelp',
                'autocomplete': 'off',
                'dir': 'ltr',
                'js-filter': 'double',
                'js-default': TAGGER_SETTINGS['tag_speed']
            }
        ),
        error_messages={
            'required': REQUIRED_ERROR,
            'invalid': INVALID_ERROR,
            'max_length': MAX_LENGTH_ERROR.format(5),
        },
        help_text=TAG_SPEED_HELP_TEXT
    )

    mention_tag_text = forms.CharField(
        label='Mention Tag Text',
        required=True,
        max_length=2048,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'area-describedby': 'mentionTagTextHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'auto',
                'js-default': TAGGER_SETTINGS['mention_tag_text']
            }
        ),
        error_messages={
            'required': REQUIRED_ERROR,
            'max_length': MAX_LENGTH_ERROR.format(2048),
        },
        help_text=MENTION_TAG_HELP_TEXT
    )

    tag_list_text = forms.CharField(
        label='Tag List Text',
        required=True,
        max_length=2048,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'area-describedby': 'tagListTextHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'auto',
                'js-default': TAGGER_SETTINGS['tag_list_text']
            }
        ),
        error_messages={
            'required': REQUIRED_ERROR,
            'max_length': MAX_LENGTH_ERROR.format(2048),
        },
        help_text=TAG_LIST_HELP_TEXT
    )

    reply_tag_text = forms.CharField(
        label='Reply Tag Text',
        required=True,
        max_length=2048,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'area-describedby': 'replyTagTextHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'auto',
                'js-default': TAGGER_SETTINGS['reply_tag_text']
            }
        ),
        error_messages={
            'required': REQUIRED_ERROR,
            'max_length': MAX_LENGTH_ERROR.format(2048),
        },
        help_text=REPLY_TAG_HELP_TEXT
    )

    auto_tag_activation = forms.BooleanField(
        label='Activate Auto Tag',
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-inline',
                'autocomplete': 'off',
                'js-default': TAGGER_SETTINGS['auto_tag_activation']
            }
        )
    )

    auto_tag_type = forms.ChoiceField(
        choices=(
            ('1', 'Regular Tag'),
            ('2', 'Regular Username Tag'),
            ('3', 'Mention Tag'),
            ('4', 'Tag List'),
            ('5', 'Reply Tag')
        ),
        label='Auto Tag Type',
        required=True,
        widget=forms.Select(
            attrs={
                'class': 'form-select',
                'area-describedby': 'autoTagTypeHelp',
                'autocomplete': 'off',
                'js-default': TAGGER_SETTINGS['auto_tag_type']
            }
        ),
        error_messages={
            'required': REQUIRED_ERROR
        },
        help_text=AUTO_TAG_TYPE_HELP_TEXT
    )

    auto_tag_clean = forms.BooleanField(
        label='Auto Cleaning Tags',
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-inline',
                'autocomplete': 'off',
                'js-default': TAGGER_SETTINGS['auto_tag_clean']
            }
        )
    )

    auto_tag_chats = forms.CharField(
        label='Auto Tag Chats',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'area-describedby': 'autoTagChatsHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'ltr',
                'js-default': TAGGER_SETTINGS['auto_tag_chats']
            }
        ),
        error_messages={
            'required': REQUIRED_ERROR
        },
        help_text=AUTO_TAG_CHATS_HELP_TEXT
    )

    def clean_tag_speed(self):
        tag_speed = self.cleaned_data.get('tag_speed')

        if tag_speed:
            if tag_speed.startswith('.'):
                tag_speed = '0' + tag_speed
            elif tag_speed.endswith('.'):
                tag_speed = tag_speed[:-1]

            try:
                speed = float(tag_speed)

                if not (0 < speed <= 10):
                    raise forms.ValidationError
            except:
                raise forms.ValidationError(INVALID_ERROR, 'invalid')

        return tag_speed


class CommandsForm(telegram.SettingsCommandsForm, metaclass=FormsMetaClass):
    tag_command = forms.CharField(
        label='Regular Tag',
        required=True,
        max_length=24,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'area-describedby': 'tagCommandHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'auto',
                'js-default': TAGGER_SETTINGS['tag_command']
            }
        ),
        error_messages={
            'required': REQUIRED_ERROR,
            'max_length': MAX_LENGTH_ERROR
        },
        help_text='Command related to regular tag'
    )

    tag_only_username_command = forms.CharField(
        label='Regular Username Tag',
        required=True,
        max_length=24,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'area-describedby': 'tagOnlyUsernameCommandHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'auto',
                'js-default': TAGGER_SETTINGS['tag_only_username_command']
            }
        ),
        error_messages={
            'required': REQUIRED_ERROR,
            'max_length': MAX_LENGTH_ERROR
        },
        help_text='Command related to regular username tag'
    )

    mention_tag_command = forms.CharField(
        label='Mention Tag',
        required=True,
        max_length=24,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'area-describedby': 'mentionTagCommandHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'auto',
                'js-default': TAGGER_SETTINGS['mention_tag_command']
            }
        ),
        error_messages={
            'required': REQUIRED_ERROR,
            'max_length': MAX_LENGTH_ERROR
        },
        help_text='Command related to mention tag'
    )

    tag_list_command = forms.CharField(
        label='Tag List',
        required=True,
        max_length=24,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'area-describedby': 'tagListCommandHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'auto',
                'js-default': TAGGER_SETTINGS['tag_list_command']
            }
        ),
        error_messages={
            'required': REQUIRED_ERROR,
            'max_length': MAX_LENGTH_ERROR
        },
        help_text='Command related to tag list'
    )

    reply_tag_command = forms.CharField(
        label='Reply Tag',
        required=True,
        max_length=24,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'area-describedby': 'replyTagCommandHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'auto',
                'js-default': TAGGER_SETTINGS['reply_tag_command']
            }
        ),
        error_messages={
            'required': REQUIRED_ERROR,
            'max_length': MAX_LENGTH_ERROR
        },
        help_text='Command related to reply tag'
    )

    clean_tags_command = forms.CharField(
        label='Cleaning Tags',
        required=True,
        max_length=24,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'area-describedby': 'cleanTagsCommandHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'auto',
                'js-default': TAGGER_SETTINGS['clean_tags_command']
            }
        ),
        error_messages={
            'required': REQUIRED_ERROR,
            'max_length': MAX_LENGTH_ERROR
        },
        help_text='Command related to cleaning tags'
    )

    stop_tag_command = forms.CharField(
        label='Stop Tagging',
        required=True,
        max_length=24,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'area-describedby': 'stopTagCommandHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'auto',
                'js-default': TAGGER_SETTINGS['stop_tag_command']
            }
        ),
        error_messages={
            'required': REQUIRED_ERROR,
            'max_length': MAX_LENGTH_ERROR
        },
        help_text='Command relating to stop tagging'
    )


class RespondsForm(telegram.SettingsRespondsForm, metaclass=FormsMetaClass):
    stop_previous_tag_message = telegram.GroupCharField(
        label='Stop tagging first',
        required=False,
        max_length=2048,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'area-describedby': 'stopPreviousTagMessageHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'auto',
                'js-default': TAGGER_SETTINGS['stop_previous_tag_message']
            }
        ),
        error_messages={
            'max_length': MAX_LENGTH_ERROR
        },
        help_text='The text bot tells when bot is tagging and you use another tag command',
        group='global_group'
    )

    tag_start_message = telegram.GroupCharField(
        label='Before regular tag',
        required=False,
        max_length=2048,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'area-describedby': 'tagStartMessageHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'auto',
                'js-default': TAGGER_SETTINGS['tag_start_message']
            }
        ),
        error_messages={
            'max_length': MAX_LENGTH_ERROR
        },
        help_text='The text bot sends before starting regular tag',
        group='tag_group'
    )

    tag_end_message = telegram.GroupCharField(
        label='After regular tag',
        required=False,
        max_length=2048,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'area-describedby': 'tagEndMessageHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'auto',
                'js-default': TAGGER_SETTINGS['tag_end_message']
            }
        ),
        error_messages={
            'max_length': MAX_LENGTH_ERROR
        },
        help_text='The text bot sends after ending regular tag',
        group='tag_group'
    )

    tag_username_start_message = telegram.GroupCharField(
        label='Before regular username tag',
        required=False,
        max_length=2048,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'area-describedby': 'tagUsernameStartMessageHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'auto',
                'js-default': TAGGER_SETTINGS['tag_username_start_message']
            }
        ),
        error_messages={
            'max_length': MAX_LENGTH_ERROR
        },
        help_text='The text bot sends before starting regular username tag',
        group='tag_username_group'
    )

    tag_username_end_message = telegram.GroupCharField(
        label='After regular username tag',
        required=False,
        max_length=2048,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'area-describedby': 'tagUsernameEndMessageHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'auto',
                'js-default': TAGGER_SETTINGS['tag_username_end_message']
            }
        ),
        error_messages={
            'max_length': MAX_LENGTH_ERROR
        },
        help_text='The text bot sends after ending regular username tag',
        group='tag_username_group'
    )

    mention_tag_start_message = telegram.GroupCharField(
        label='Before mention tag',
        required=False,
        max_length=2048,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'area-describedby': 'mentionTagStartMessageHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'auto',
                'js-default': TAGGER_SETTINGS['mention_tag_start_message']
            }
        ),
        error_messages={
            'max_length': MAX_LENGTH_ERROR
        },
        help_text='The text bot sends before starting mention tag',
        group='mention_tag_group'
    )

    mention_tag_end_message = telegram.GroupCharField(
        label='After mention tag',
        required=False,
        max_length=2048,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'area-describedby': 'mentionTagEndMessageHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'auto',
                'js-default': TAGGER_SETTINGS['mention_tag_end_message']
            }
        ),
        error_messages={
            'max_length': MAX_LENGTH_ERROR
        },
        help_text='The text bot sends after ending mention tag',
        group='mention_tag_group'
    )

    tag_list_start_message = telegram.GroupCharField(
        label='Before tag list',
        required=False,
        max_length=2048,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'area-describedby': 'tagListStartMessageHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'auto',
                'js-default': TAGGER_SETTINGS['tag_list_start_message']
            }
        ),
        error_messages={
            'max_length': MAX_LENGTH_ERROR
        },
        help_text='The text bot sends before starting tag list',
        group='tag_list_group'
    )

    tag_list_end_message = telegram.GroupCharField(
        label='After tag list',
        required=False,
        max_length=2048,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'area-describedby': 'tagListEndMessageHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'auto',
                'js-default': TAGGER_SETTINGS['tag_list_end_message']
            }
        ),
        error_messages={
            'max_length': MAX_LENGTH_ERROR
        },
        help_text='The text bot sends after ending tag list',
        group='tag_list_group'
    )

    reply_tag_start_message = telegram.GroupCharField(
        label='Before reply tag',
        required=False,
        max_length=2048,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'area-describedby': 'replyTagStartMessageHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'auto',
                'js-default': TAGGER_SETTINGS['reply_tag_start_message']
            }
        ),
        error_messages={
            'max_length': MAX_LENGTH_ERROR
        },
        help_text='The text bot sends before starting reply tag',
        group='reply_tag_group'
    )

    reply_tag_end_message = telegram.GroupCharField(
        label='After reply tag',
        required=False,
        max_length=2048,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'area-describedby': 'replyTagEndMessageHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'auto',
                'js-default': TAGGER_SETTINGS['reply_tag_end_message']
            }
        ),
        error_messages={
            'max_length': MAX_LENGTH_ERROR
        },
        help_text='The text bot sends after ending reply tag',
        group='reply_tag_group'
    )

    reply_tag_error_message = telegram.GroupCharField(
        label='Data in database is not enough error (reply tag)',
        required=False,
        max_length=2048,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'area-describedby': 'replyTagErrorMessageHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'auto',
                'js-default': TAGGER_SETTINGS['reply_tag_error_message']
            }
        ),
        error_messages={
            'max_length': MAX_LENGTH_ERROR
        },
        help_text='The text bot sends whenever count of users in database is less than 5',
        group='reply_tag_group'
    )

    tag_stop_message = telegram.GroupCharField(
        label='After stop tagging',
        required=False,
        max_length=2048,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'area-describedby': 'tagStopMessageHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'auto',
                'js-default': TAGGER_SETTINGS['tag_stop_message']
            }
        ),
        error_messages={
            'max_length': MAX_LENGTH_ERROR
        },
        help_text='The text bot sends after stopping tagger',
        group='tag_stop_group'
    )

    tag_stop_error_message = telegram.GroupCharField(
        label='Tagger is not tagging',
        required=False,
        max_length=2048,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'area-describedby': 'tagStopErrorMessageHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'auto',
                'js-default': TAGGER_SETTINGS['tag_stop_error_message']
            }
        ),
        error_messages={
            'max_length': MAX_LENGTH_ERROR
        },
        help_text='The text bot sends whenever admin uses stop command while bot is not tagging',
        group='tag_stop_group'
    )

    clean_tags_start_message = telegram.GroupCharField(
        label='Before cleaning tags',
        required=False,
        max_length=2048,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'area-describedby': 'cleanTagsStartMessageHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'auto',
                'js-default': TAGGER_SETTINGS['clean_tags_start_message']
            }
        ),
        error_messages={
            'max_length': MAX_LENGTH_ERROR
        },
        help_text='The text bot sends before cleaning tags',
        group='clean_tags_group'
    )

    clean_tags_end_message = telegram.GroupCharField(
        label='After cleaning tags',
        required=False,
        max_length=2048,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'area-describedby': 'cleanTagsEndMessageHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'auto',
                'js-default': TAGGER_SETTINGS['clean_tags_end_message']
            }
        ),
        error_messages={
            'max_length': MAX_LENGTH_ERROR
        },
        help_text='The text bot sends after cleaning tags',
        group='clean_tags_group'
    )

    clean_tags_error_message = telegram.GroupCharField(
        label='No tags to clean error',
        required=False,
        max_length=2048,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'area-describedby': 'cleanTagsErrorMessageHelp',
                'autocomplete': 'off',
                'spellcheck': 'false',
                'dir': 'auto',
                'js-default': TAGGER_SETTINGS['clean_tags_error_message']
            }
        ),
        error_messages={
            'max_length': MAX_LENGTH_ERROR
        },
        help_text='The text bot sends whenever there is no tags for bot to clean',
        group='clean_tags_group'
    )
