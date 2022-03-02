from asyncio import Queue, Task, get_running_loop
from typing import Iterable

from aiohttp.web_app import Application

from yaps.utils import logging
from yaps.utils.alert_bot.bot import ApplicationStatusEventHandler, PGStatusEventHandler, \
    ESStatusEventHandler, UnhandledExceptionEventHandler
from yaps.utils.event.type import EventType

logger = logging.get_logger(__name__)


class EventEngine:
    def __init__(self):
        self.queue = Queue()
        self.handlers = {}

    def register_handler(self, events: Iterable, handler):
        for event in events:
            if event not in self.handlers:
                self.handlers[event] = [handler]
            else:
                self.handlers[event].append(handler)

    async def push(self, event: EventType, *args, **kwargs):
        await self.queue.put((event, args, kwargs))

    async def start(self) -> Task:
        return get_running_loop().create_task(self.__run())

    async def __run(self):
        while True:
            event, args, kwargs = await self.queue.get()
            event_handlers = self.handlers[event]

            for handler in event_handlers:
                await handler(event, *args, **kwargs)


async def create_event_engine(app: Application):
    engine = EventEngine()
    app['event_engine'] = engine

    engine.register_handler([
        EventType.AppUp,
        EventType.AppDown
    ], ApplicationStatusEventHandler())

    engine.register_handler([
        EventType.PGDown,
        EventType.PGAlive,
    ], PGStatusEventHandler())

    engine.register_handler([
        EventType.ESAlive,
        EventType.ESDown
    ], ESStatusEventHandler())

    engine.register_handler([
        EventType.UnhandledException,
    ], UnhandledExceptionEventHandler)

    try:
        task = await engine.start()
        yield
        task.cancel()
    except Exception as err:
        logger.error(err)
