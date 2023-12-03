import inspect
import re
import typing

from asgiref.sync import sync_to_async
from django.apps import apps
from django.urls import reverse_lazy
from pyrogram import Client, filters, types, methods, handlers

from django_telegram_tagger import helpers
from .helpers import wrap_methods


class Telegram:
    help_context: typing.Dict[str, str] = {
        'set_username_command': 'Set username',
        'set_password_command': 'Set password',
        'settings_command': 'Enter settings panel',
    }

    def __init__(self, session: str, api_id: typing.Union[str, int], api_hash: str):
        self.session = session
        self.api_id = api_id
        self.api_hash = api_hash

        self._wrap_methods()

        self._cli = Client(self.session, self.api_id, self.api_hash, workdir="./db/")

    def add_handlers(self):
        self._cli.add_handler(
            handlers.MessageHandler(
                callback=self.set_username,
                filters=filters.chat('me') & filters.text & self._check_command_filter('set_username_command', r'^{}\s')
            )
        )

        self._cli.add_handler(
            handlers.MessageHandler(
                callback=self.set_password,
                filters=filters.chat('me') & filters.text & self._check_command_filter('set_password_command', r'^{}\s')
            )
        )

        self._cli.add_handler(
            handlers.MessageHandler(
                callback=self.settings,
                filters=filters.text & (filters.me | self._check_admin_filter()) & self._check_command_filter(
                    'settings_command', r'^{}$')
            )
        )

        self._cli.add_handler(
            handlers.MessageHandler(
                callback=self.help,
                filters=filters.text & (filters.me | self._check_admin_filter()) & self._check_command_filter(
                    'help_command', r'^{}$')
            )
        )

    def run(self):
        self.add_handlers()

        self._cli.run()

    def start(self):
        self.add_handlers()

        self._cli.start()

    async def stop(self):
        await self._cli.stop(False)

    async def set_username(self, cli: Client, message: types.Message):
        UsersModel = apps.get_model('telegram', 'UsersModel')
        CustomUserModel = apps.get_model('telegram', 'CustomUserModel')

        user = message.from_user
        username = message.text.split(maxsplit=1)[1]
        set_username_message = await helpers.get_setting('set_username_message')
        set_username_error_message = await helpers.get_setting('set_username_error_message')

        if len(username) > 150:
            return await self._edit_or_reply(message, set_username_error_message)

        user_defaults = {
            'user_id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username
        }
        user_obj, created = await UsersModel.objects.aget_or_create(user_defaults, user_id__exact=user.id)

        if not created:
            for k, v in user_defaults.items():
                setattr(user_obj, k, v)

            await user_obj.asave()

        auth_user_defaults = {
            'user': user_obj,
            'username': username
        }
        auth_user_obj, created = await CustomUserModel.objects.aget_or_create(
            auth_user_defaults,
            user__user_id__exact=user.id
        )

        if not created:
            for k, v in auth_user_defaults.items():
                setattr(auth_user_obj, k, v)

            await auth_user_obj.asave()

        await self._edit_or_reply(message, set_username_message)

    async def set_password(self, cli: Client, message: types.Message):
        CustomUserModel = apps.get_model('telegram', 'CustomUserModel')

        user = message.from_user
        password = message.text.split(maxsplit=1)[1]
        set_password_message = await helpers.get_setting('set_password_message')
        set_password_set_username_first_error_message = await helpers.get_setting(
            'set_password_set_username_first_error_message'
        )
        set_password_invalid_error_message = await helpers.get_setting('set_password_invalid_error_message')

        if len(password) > 128:
            return await self._edit_or_reply(message, set_password_invalid_error_message)

        try:
            auth_user_obj = await CustomUserModel.objects.aget(user__user_id__exact=user.id)
        except:
            return await self._edit_or_reply(message, set_password_set_username_first_error_message)

        auth_user_obj.set_password(password)
        await auth_user_obj.asave()

        await self._edit_or_reply(message, set_password_message)

    async def settings(self, cli: Client, message: types.Message):
        url = reverse_lazy('auth-page')
        full_url = helpers.get_full_url(url)
        settings_message = await helpers.get_setting('settings_message')

        await self._edit_or_reply(message, settings_message.format(full_url))

    async def help(self, cli: Client, message: types.Message):
        help_template = await helpers.get_setting('help_message')

        help_splits = []
        for k, v in self.help_context.items():
            command = await helpers.get_setting(k)
            help_splits.append(help_template.format(command, v))

        help_message = '\n\n'.join(help_splits)

        await self._edit_or_reply(message, help_message)

    @classmethod
    async def _get_admins(cls):
        admins: str = await helpers.get_setting('admins_list')

        admins_list = [int(x) if x.isdigit() else x.lower() if not x.startswith('@') else x.lower()[1:] for x in
                       admins.strip().split()]

        return admins_list

    @classmethod
    def _check_admin_filter(cls):
        async def func(self, cli: Client, update: types.Message):
            if not isinstance(update, types.Message):
                return False

            if not update.from_user:
                return False

            admins_list = await self.cls._get_admins()

            return update.from_user.id in admins_list or \
                (update.from_user.username and update.from_user.username.lower() in admins_list)

        return filters.create(func, cls=cls)

    @classmethod
    def _check_command_filter(cls, command_code: str, regex: str):
        async def func(self, cli: Client, update: types.Message):
            if not isinstance(update, types.Message):
                return False

            if not update.text:
                return False

            command = await helpers.get_setting(self.command_code)

            return bool(re.search(regex.format(command), update.text))

        return filters.create(func, cls=cls, command_code=command_code)

    @classmethod
    async def _edit_or_reply(cls, message: types.Message, text: str):
        if message.outgoing:
            msg = await message.edit_text(
                text=text
            )
        else:
            msg = await message.reply_text(
                text=text
            )

        return msg

    @classmethod
    def _get_gen(cls, gen: typing.AsyncGenerator):
        async def wrapper():
            try:
                try:
                    return await anext(gen)
                except:
                    return await gen.__anext__()
            except StopAsyncIteration:
                return None

        return wrapper

    @classmethod
    async def _chunk_async_gen(cls, generator: typing.AsyncGenerator, size: int):
        chunk = []
        gen = cls._get_gen(generator)

        while True:
            result = await gen()
            if not result:
                break

            try:
                result = iter(result)
                chunk += [x for x in result]
            except TypeError:
                chunk.append(result)

            if len(chunk) == size:
                yield chunk.copy()[0] if size == 1 else chunk.copy()
                chunk.clear()

        if chunk:
            yield chunk.copy()

        yield None

    @staticmethod
    @sync_to_async
    def _get_queryset_value(obj, value):
        return getattr(obj, value)

    @classmethod
    def _chunk_list(cls, _iterable: typing.Iterable, size: int):
        chunk = []
        for i in _iterable:
            try:
                gen = iter(i)
                while True:
                    try:
                        item = next(gen)
                        chunk.append(item)
                    except StopIteration:
                        break

                    if len(chunk) == size:
                        if size == 1:
                            yield chunk[0]
                        else:
                            yield chunk.copy()

                        chunk.clear()
            except TypeError:
                chunk.append(i)

                if len(chunk) == size:
                    if size == 1:
                        yield chunk[0]
                    else:
                        yield chunk.copy()

                    chunk.clear()

        yield chunk

    @classmethod
    def _wrap_methods(cls):
        wrap_methods(methods.Methods)

        for cls_name in dir(types):
            cls_obj = getattr(types, cls_name)

            if inspect.isclass(cls_obj):
                wrap_methods(cls_obj)
