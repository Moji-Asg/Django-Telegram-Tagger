import asyncio
import functools
import inspect
from pyrogram import errors, sync


def run_through_exceptions(func: callable):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if asyncio.iscoroutine(result):
                await result
        except errors.FloodWait as e:
            await asyncio.sleep(e.value)
            result = func(*args, **kwargs)
            if asyncio.iscoroutine(result):
                await result

    cls = type('FloodException', (), {'wrapper': wrapper})
    sync.async_to_sync(cls, 'wrapper')
    return getattr(cls, 'wrapper')


def wrap_methods(source):
    for attr in dir(source):
        method = getattr(source, attr)

        if not attr.startswith('_'):
            if inspect.iscoroutinefunction(method) or inspect.isasyncgenfunction(method):
                new_method = run_through_exceptions(method)
                setattr(source, attr, new_method)
