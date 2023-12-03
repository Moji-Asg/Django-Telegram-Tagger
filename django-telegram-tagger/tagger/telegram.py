import asyncio
import re
import typing

from django.apps import apps
from pyrogram import handlers, filters, types, Client, enums, emoji, errors

from django_telegram_tagger import helpers
from telegram import get_telegram, TelegramMetaClass
from . import settings


class RegExp:
    FIRSTNAME = '{FIRSTNAME}'
    LASTNAME = '{LASTNAME}'
    USERNAME = '{USERNAME}'
    USERID = '{USERID}'

    MENTION_RE = re.compile(r'\{MENTION\((.+?)\)}', flags=re.DOTALL)
    GAMEURL_RE = re.compile(r'\{GAMEURL\((.+?)\)}', flags=re.DOTALL)

    CHECKER_RE = re.compile(
        r'(\{MENTION\((.+?)\)})|(\{GAMEURL\((.+?)\)})|(\{FIRSTNAME})|(\{LASTNAME})|(\{USERNAME})|(\{USERID})'
    )


class WerewolfRE:
    PERSIAN_NORMAL_START = '^یک بازی توسط .+ ساخته شده'
    PERSIAN_CHAOS_START = '^یک بازی با حالت آشوب توسط .+ ساخته شده'
    PERSIAN_FAILED_END = 'چقدر کمین! من با این تعداد بازیکن بازی رو شروع نمیکنم {}'.format(emoji.CRYING_FACE)
    PERSIAN_SUCCESS_END = 'ایول بازی شروع شد' \
                          ' {} یه کم صبر کنین نقشاتونو بهتون بگم'.format(emoji.GRINNING_FACE_WITH_BIG_EYES)

    # ENGLISH_NORMAL_START = r''

    @classmethod
    def combine_all(cls, start: bool):
        data = [f'({getattr(cls, x)})' for x in dir(cls) if
                not callable(x) and x.endswith('_START' if start else '_END')]

        return '|'.join(data)


class Tagger(get_telegram(), metaclass=TelegramMetaClass):
    __stopper: typing.Dict[int, bool] = {}
    __sent_messages: typing.Dict[int, typing.List[int]] = {}
    __running: typing.Dict[int, typing.Callable] = {}
    __autotag: typing.Dict[int, bool] = {}

    def __init__(self, *args, **kwargs):
        self.help_context.update({
            'tag_command': 'Regular Tag',
            'tag_only_username_command': 'Regular Username Tag',
            'mention_tag_command': 'Mention Tag',
            'tag_list_command': 'Tag List',
            'reply_tag_command': 'Reply Tag',
            'stop_tag_command': 'Stop Tagging',
            'clean_tags_command': 'Cleaning Tags'
        })

        super().__init__(*args, **kwargs)

    def add_handlers(self):
        super().add_handlers()

        self._cli.add_handler(
            handlers.MessageHandler(
                callback=self.tag,
                filters=filters.text & (filters.me | self._check_admin_filter()) & self._check_command_filter(
                    'tag_command', r'^{}$') & self._check_tagger_active_filter()
            )
        )

        self._cli.add_handler(
            handlers.MessageHandler(
                callback=self.tag_only_username,
                filters=filters.text & (filters.me | self._check_admin_filter()) & self._check_command_filter(
                    'tag_only_username_command', r'^{}$') & self._check_tagger_active_filter()
            )
        )

        self._cli.add_handler(
            handlers.MessageHandler(
                callback=self.clean_tags,
                filters=filters.text & (filters.me | self._check_admin_filter()) & self._check_command_filter(
                    'clean_tags_command', r'^{}$') & self._check_tagger_active_filter()
            )
        )

        self._cli.add_handler(
            handlers.MessageHandler(
                callback=self.mention_tag,
                filters=filters.text & (filters.me | self._check_admin_filter()) & self._check_command_filter(
                    'mention_tag_command', r'^{}$') & self._check_tagger_active_filter()
            )
        )

        self._cli.add_handler(
            handlers.MessageHandler(
                callback=self.tag_list,
                filters=filters.text & (filters.me | self._check_admin_filter()) & self._check_command_filter(
                    'tag_list_command', r'^{}$') & self._check_tagger_active_filter()
            )
        )

        self._cli.add_handler(
            handlers.MessageHandler(
                callback=self.reply_tag,
                filters=filters.text & (filters.me | self._check_admin_filter()) & self._check_command_filter(
                    'reply_tag_command', r'^{}$') & self._check_tagger_active_filter()
            )
        )

        self._cli.add_handler(
            handlers.MessageHandler(
                callback=self.stop_tag,
                filters=filters.text & (filters.me | self._check_admin_filter()) & self._check_command_filter(
                    'stop_tag_command', r'^{}$') & self._check_tagger_active_filter()
            )
        )

        self._cli.add_handler(
            handlers.MessageHandler(
                callback=self.auto_tag_start,
                filters=filters.user(settings.WEREWOLF_BOTS) & filters.regex(
                    WerewolfRE.combine_all(
                        True)) & self._check_chat_filter() & self._check_auto_tag_active_filter() & self._check_tagger_active_filter()
            )
        )

        self._cli.add_handler(
            handlers.MessageHandler(
                callback=self.auto_tag_stop,
                filters=filters.user(settings.WEREWOLF_BOTS) & filters.regex(
                    WerewolfRE.combine_all(
                        False)) & self._check_chat_filter() & self._check_auto_tag_active_filter() & self._check_tagger_active_filter()
            )
        )

        self._cli.add_handler(
            handlers.MessageHandler(
                callback=self.save_messages,
                filters=filters.group & ~filters.bot & ~filters.me
            )
        )

    async def tag(self, cli: Client, message: types.Message, just_username: bool = False, silent: bool = False):
        chat = message.chat
        reply_msg_id = message.reply_to_message_id
        speed = float(await helpers.get_setting('tag_speed'))
        tag_start_message = await helpers.get_setting('tag_start_message')
        tag_end_message = await helpers.get_setting('tag_end_message')

        if chat.id in self.__running and not just_username:
            return (await self._stop_previous_tag_message(message)) if not silent else None

        if not just_username:
            self.__running[chat.id] = self.tag

        if tag_start_message and not just_username and not silent:
            try:
                start_msg = await self._edit_or_reply(message, tag_start_message)
            except:
                start_msg = None
        else:
            start_msg = None

        gen = self._get_gen(self._chunk_users(chat.id))

        while True:
            if chat.id in self.__stopper and self.__stopper[chat.id]:
                del self.__stopper[chat.id]
                break

            user = await gen()
            if not user:
                self.__stopper[chat.id] = True
                continue

            if just_username:
                if not user.user.username:
                    continue

                try:
                    msg = await cli.send_message(
                        chat_id=chat.id,
                        text='@' + user.user.username,
                        reply_to_message_id=reply_msg_id
                    )
                except:
                    break

                self._add_sent_message(chat.id, msg.id)

                await asyncio.sleep(1 / speed)

                continue

            try:
                msg = await cli.send_message(
                    chat_id=chat.id,
                    text=self._mention_user(user.user.id, user.user.first_name),
                    reply_to_message_id=reply_msg_id
                )
            except:
                break

            self._add_sent_message(chat.id, msg.id)

            await asyncio.sleep(1 / speed)

        if start_msg:
            try:
                await start_msg.delete()
            except:
                pass

        if tag_end_message and not just_username and not silent:
            try:
                await cli.send_message(
                    chat_id=chat.id,
                    text=tag_end_message
                )
            except:
                pass

        if not just_username:
            del self.__running[chat.id]

    async def tag_only_username(self, cli: Client, message: types.Message, silent: bool = False):
        chat = message.chat
        tag_username_start_message = await helpers.get_setting('tag_username_start_message')
        tag_username_end_message = await helpers.get_setting('tag_username_end_message')

        if chat.id in self.__running:
            return (await self._stop_previous_tag_message(message)) if not silent else None

        self.__running[chat.id] = self.tag_only_username

        if tag_username_start_message and not silent:
            try:
                start_msg = await self._edit_or_reply(message, tag_username_start_message)
            except:
                start_msg = None
        else:
            start_msg = None

        try:
            await self.tag(cli, message, just_username=True, silent=silent)
        except:
            pass

        if start_msg:
            try:
                await start_msg.delete()
            except:
                pass

        if tag_username_end_message and not silent:
            try:
                await cli.send_message(
                    chat_id=chat.id,
                    text=tag_username_end_message
                )
            except:
                pass

        del self.__running[chat.id]

    async def clean_tags(self, cli: Client, message: types.Message, silent: bool = False):
        chat = message.chat
        clean_tags_start_message = await helpers.get_setting('clean_tags_start_message')
        clean_tags_end_message = await helpers.get_setting('clean_tags_end_message')
        clean_tags_error_message = await helpers.get_setting('clean_tags_error_message')
        sent_messages = self.__sent_messages.get(chat.id)

        if chat.id in self.__running:
            self.__stopper[chat.id] = True

            while chat.id in self.__running:
                await asyncio.sleep(0.01)

        if sent_messages:
            if clean_tags_start_message and not silent:
                start_msg = await self._edit_or_reply(message, clean_tags_start_message)
            else:
                start_msg = None
        elif not silent:
            return await self._edit_or_reply(message, clean_tags_error_message)
        else:
            return

        if start_msg:
            sent_messages.append(start_msg.id)

        for chunk in self._chunk_list(sent_messages, 100):
            await cli.delete_messages(
                chat_id=chat.id,
                message_ids=chunk
            )

        del self.__sent_messages[chat.id]

        if clean_tags_end_message and not silent:
            await cli.send_message(
                chat_id=chat.id,
                text=clean_tags_end_message
            )

    async def mention_tag(self, cli: Client, message: types.Message, silent: bool = False, game_url: str = None):
        chat = message.chat
        reply_msg_id = message.reply_to_message_id
        speed = float(await helpers.get_setting('tag_speed'))
        mention_tag_text = await helpers.get_setting('mention_tag_text')
        mention_tag_start_text = await helpers.get_setting('mention_tag_start_text')
        mention_tag_end_text = await helpers.get_setting('mention_tag_end_text')

        if chat.id in self.__running:
            return (await self._stop_previous_tag_message(message)) if not silent else None

        self.__running[chat.id] = self.mention_tag

        if mention_tag_start_text and not silent:
            try:
                start_msg = await self._edit_or_reply(message, mention_tag_start_text)
            except:
                start_msg = None
        else:
            start_msg = None

        gen = self._get_gen(self._chunk_users(chat.id))

        while True:
            if chat.id in self.__stopper and self.__stopper[chat.id]:
                del self.__stopper[chat.id]
                break

            user = await gen()
            if not user:
                self.__stopper[chat.id] = True
                continue

            text, _ = self._parse_texts(mention_tag_text, user.user, game_url=game_url)

            try:
                msg = await cli.send_message(
                    chat_id=chat.id,
                    text=text,
                    reply_to_message_id=reply_msg_id,
                    disable_web_page_preview=True
                )
            except:
                break

            self._add_sent_message(chat.id, msg.id)

            await asyncio.sleep(1 / speed)

        if start_msg:
            try:
                await start_msg.delete()
            except:
                pass

        if mention_tag_end_text and not silent:
            try:
                await cli.send_message(
                    chat_id=chat.id,
                    text=mention_tag_end_text
                )
            except:
                pass

        del self.__running[chat.id]

    async def tag_list(self, cli: Client, message: types.Message, silent: bool = False, game_url: str = None):
        chat = message.chat
        reply_msg_id = message.reply_to_message_id
        speed = float(await helpers.get_setting('tag_speed'))
        tag_list_text = await helpers.get_setting('tag_list_text')
        tag_list_start_message = await helpers.get_setting('tag_list_start_message')
        tag_list_end_message = await helpers.get_setting('tag_list_end_message')

        if chat.id in self.__running:
            return (await self._stop_previous_tag_message(message)) if not silent else None

        self.__running[chat.id] = self.tag_list

        if tag_list_start_message and not silent:
            try:
                start_msg = await self._edit_or_reply(message, tag_list_start_message)
            except:
                start_msg = None
        else:
            start_msg = None

        gen = self._get_gen(self._chunk_users(chat.id))

        while True:
            if chat.id in self.__stopper and self.__stopper[chat.id]:
                del self.__stopper[chat.id]
                break

            complete = False
            text = tag_list_text

            while not complete:
                user = await gen()
                if not user:
                    self.__stopper[chat.id] = True
                    gen = self._get_gen(self._chunk_users(chat.id))
                    user = await gen()

                text, complete = self._parse_texts(text, user.user, game_url=game_url, count=1)

            try:
                msg = await cli.send_message(
                    chat_id=chat.id,
                    text=text,
                    reply_to_message_id=reply_msg_id,
                    disable_web_page_preview=True
                )
            except:
                break

            self._add_sent_message(chat.id, msg.id)

            await asyncio.sleep(1 / speed)

        if start_msg:
            try:
                await start_msg.delete()
            except:
                pass

        if tag_list_end_message and not silent:
            try:
                await cli.send_message(
                    chat_id=chat.id,
                    text=tag_list_end_message
                )
            except:
                pass

        del self.__running[chat.id]

    async def reply_tag(self, cli: Client, message: types.Message, silent: bool = False, game_url: str = None):
        UsersMessagesModel = apps.get_model('tagger', 'UsersMessagesModel')

        chat = message.chat
        speed = float(await helpers.get_setting('tag_speed'))
        reply_tag_text = await helpers.get_setting('reply_tag_text')
        reply_tag_start_message = await helpers.get_setting('reply_tag_start_message')
        reply_tag_end_message = await helpers.get_setting('reply_tag_end_message')
        reply_tag_error_message = await helpers.get_setting('reply_tag_error_message')

        if chat.id in self.__running:
            return (await self._stop_previous_tag_message(message)) if not silent else None

        self.__running[chat.id] = self.reply_tag

        users_count = await UsersMessagesModel.objects.acount()
        if users_count < 5:
            del self.__running[chat.id]

            if reply_tag_error_message and not silent:
                return await self._edit_or_reply(message, reply_tag_error_message)
            else:
                return
        else:
            if reply_tag_start_message and not silent:
                try:
                    start_msg = await self._edit_or_reply(message, reply_tag_start_message)
                except:
                    start_msg = None
            else:
                start_msg = None

        while True:
            if chat.id in self.__stopper and self.__stopper[chat.id]:
                del self.__stopper[chat.id]
                break

            gen = self._get_gen(
                self._chunk_async_gen(
                    UsersMessagesModel.objects.filter(chat__chat_id__exact=chat.id).aiterator(),
                    size=50
                )
            )

            while True:
                objs: typing.List[UsersMessagesModel] = await gen()
                if not objs:
                    self.__stopper[chat.id] = True
                    break

                msgs = [await self._get_queryset_value(obj, 'message_id') for obj in objs]
                try:
                    allowed_msgs = [x.id for x in await cli.get_messages(chat.id, msgs) if not x.empty]
                except:
                    break

                for obj in objs:
                    message_id = obj.message_id
                    if message_id not in allowed_msgs:
                        continue

                    user = await self._get_queryset_value(obj, 'user')
                    user = types.User(
                        id=user.user_id,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        username=user.username
                    )

                    text, _ = self._parse_texts(reply_tag_text, user, game_url=game_url, auto_mention=False)

                    try:
                        msg = await cli.send_message(
                            chat_id=chat.id,
                            text=text,
                            reply_to_message_id=message_id,
                            disable_web_page_preview=True
                        )
                    except:
                        break

                    self._add_sent_message(chat.id, msg.id)

                    await asyncio.sleep(1 / speed)

        if start_msg:
            try:
                await start_msg.delete()
            except:
                pass

        if reply_tag_end_message and not silent:
            try:
                await cli.send_message(
                    chat_id=chat.id,
                    text=reply_tag_end_message
                )
            except:
                pass
        
        del self.__running[chat.id]

    async def auto_tag_start(self, cli: Client, message: types.Message):
        chat = message.chat
        auto_tag_type = int(await helpers.get_setting('auto_tag_type'))

        if chat.id in self.__autotag:
            return

        self.__autotag[chat.id] = True

        game_url = message.reply_markup.inline_keyboard[0][0].url
        message.reply_to_message_id = message.id

        options = {
            1: self.tag,
            2: self.tag_only_username,
            3: self.mention_tag,
            4: self.tag_list,
            5: self.reply_tag
        }
        method = options.get(auto_tag_type)

        try:
            await method(
                cli=cli,
                message=message,
                silent=True,
                game_url=game_url
            )
        except:
            await method(
                cli=cli,
                message=message,
                silent=True,
            )

    async def auto_tag_stop(self, cli: Client, message: types.Message):
        chat = message.chat

        if chat.id not in self.__autotag:
            return

        del self.__autotag[chat.id]

        auto_tag_clean = eval(await helpers.get_setting('auto_tag_clean'))

        if chat.id in self.__running:
            self.__stopper[chat.id] = True
            while chat.id in self.__running:
                await asyncio.sleep(0.01)

        if auto_tag_clean:
            await self.clean_tags(cli, message, silent=True)

    async def stop_tag(self, cli: Client, message: types.Message):
        chat = message.chat
        tag_stop_message = await helpers.get_setting('tag_stop_message')
        tag_stop_error_message = await helpers.get_setting('tag_stop_error_message')

        if chat.id not in self.__running:
            return await self._edit_or_reply(message, tag_stop_error_message)

        self.__stopper[chat.id] = True

        while chat.id in self.__running:
            await asyncio.sleep(0.01)

        if tag_stop_message:
            await self._edit_or_reply(message, tag_stop_message)

    async def save_messages(self, cli: Client, message: types.Message):
        UsersModel = apps.get_model('telegram', 'UsersModel')
        ChatsModel = apps.get_model('telegram', 'ChatsModel')
        UsersMessagesModel = apps.get_model('tagger', 'UsersMessagesModel')

        user = message.from_user
        chat = message.chat

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

        chat_defaults = {
            'chat_id': chat.id,
            'title': chat.title,
            'username': chat.username,
            'description': chat.description,
            'invite_link': chat.invite_link
        }
        chat_obj, created = await ChatsModel.objects.aget_or_create(chat_defaults, chat_id__exact=chat.id)

        if not created:
            for k, v in chat_defaults.items():
                setattr(chat_obj, k, v)

            await chat_obj.asave()

        user_message_defaults = {
            'user': user_obj,
            'chat': chat_obj,
            'message_id': message.id
        }
        user_message_obj, created = await UsersMessagesModel.objects.aget_or_create(
            user_message_defaults,
            user__user_id__exact=user.id,
            chat__chat_id__exact=chat.id
        )

        if not created:
            for k, v in user_message_defaults.items():
                setattr(user_message_obj, k, v)

            await user_message_obj.asave()

    @classmethod
    async def _get_auto_tag_chats(cls):
        chats = await helpers.get_setting('auto_tag_chats')
        chats_list = [int(x) for x in chats.strip().split()]
        return chats_list

    @classmethod
    def _check_chat_filter(cls):
        async def func(self, cli: Client, update: types.Message):
            if not isinstance(update, types.Message):
                return False

            return update.chat.id in await self.cls._get_auto_tag_chats()

        return filters.create(func, cls=cls)

    @classmethod
    def _check_auto_tag_active_filter(cls):
        async def func(self, cli: Client, update: types.Message):
            if not isinstance(update, types.Message):
                return False

            auto_tag_activation = eval(await helpers.get_setting('auto_tag_activation'))

            return auto_tag_activation

        return filters.create(func)

    @classmethod
    def _check_tagger_active_filter(cls):
        async def func(self, cli: Client, update: types.Message):
            if not isinstance(update, types.Message):
                return False

            tagger_activation = eval(await helpers.get_setting('tagger_activation'))

            return tagger_activation

        return filters.create(func)

    @classmethod
    def _mention_user(cls, user_id: typing.Union[str, int], text: str):
        return f'<a href="tg://user?id={user_id}">{text}</a>'

    @classmethod
    def _hyperlink_text(cls, url: str, text: str):
        return f'<a href="{url}">{text}</a>'

    @classmethod
    def _add_sent_message(cls, chat_id: int, msg_id: int):
        sent_messages = cls.__sent_messages.get(chat_id, [])
        sent_messages.append(msg_id)
        cls.__sent_messages[chat_id] = sent_messages

    @classmethod
    async def _stop_previous_tag_message(cls, message: types.Message):
        stop_previous_tag_message = await helpers.get_setting('stop_previous_tag_message')
        if stop_previous_tag_message:
            return await cls._edit_or_reply(message, stop_previous_tag_message)

    @classmethod
    def _parse_texts(cls, template: str, user: types.User, game_url: str = None, count: int = None,
                     auto_mention: bool = True):
        first_name = user.first_name or ''
        last_name = user.last_name or ''
        username = user.username or ''
        user_id = user.id or ''

        text = template.replace(
            RegExp.FIRSTNAME,
            first_name,
            count or -1
        ).replace(
            RegExp.LASTNAME,
            last_name,
            count or -1
        ).replace(
            RegExp.USERNAME,
            username,
            count or -1
        ).replace(
            RegExp.USERID,
            str(user_id),
            count or -1
        )

        if RegExp.MENTION_RE.search(text):
            for i, match in enumerate(RegExp.MENTION_RE.finditer(text)):
                if count and i == count:
                    break

                mentioned_user = cls._mention_user(user_id, match.group(1))

                text = RegExp.MENTION_RE.sub(mentioned_user, text, 1)
        else:
            if auto_mention:
                text = cls._mention_user(user_id, text)

        if game_url:
            for match in RegExp.GAMEURL_RE.finditer(text):
                mentioned_game_url = cls._hyperlink_text(game_url, match.group(1))
                text = RegExp.GAMEURL_RE.sub(mentioned_game_url, text, 1)
        else:
            text = RegExp.GAMEURL_RE.sub('', text)

        return text, not bool(RegExp.CHECKER_RE.search(text))

    async def _chunk_users(self, chat_id: int):
        async for chunk in self._cli.get_chat_members(chat_id, filter=enums.ChatMembersFilter.RECENT):
            if chunk.user.is_bot or chunk.user.is_deleted:
                continue

            yield chunk
