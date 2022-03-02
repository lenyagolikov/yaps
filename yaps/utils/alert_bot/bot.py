import datetime
import logging
from abc import ABC, abstractmethod

from aiogram import Bot, Dispatcher, types
from aiohttp.web_app import Application

from yaps.settings import Config
from yaps.utils.event.type import EventType


class AlertBot:
    def __init__(
        self,
        bot: Bot = Bot(token=Config.AlertBot.token),
        chat_id: int = Config.AlertBot.chat_id,
    ):
        self.bot = bot
        self.dp = Dispatcher(bot)
        self.chat_id = chat_id

        self.dp.register_message_handler(self.cmd_status, commands="status")
        self.dp.register_message_handler(self.cmd_start, commands="start")

    @classmethod
    async def cmd_status(cls, message: types.Message):
        await message.reply("test status")

    async def cmd_start(self, message: types.Message):
        self.chat_id = message.chat.id
        await message.reply("started")

    async def send(self, msg: str) -> types.Message:
        if self.chat_id:
            return await self.bot.send_message(self.chat_id, self.format_msg(msg))

    async def alert_app_up(self):
        await self.send('[APPLICATION UP]')

    async def alert_app_down(self):
        await self.send('[APPLICATION DOWN]')

    @property
    def dispatcher(self) -> Dispatcher:
        return self.dp

    @classmethod
    def format_msg(cls, msg):
        return f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {msg}'


class AlertBotEventHandler(ABC):
    def __call__(self, *args, **kwargs):
        return self.__handle_event(*args, **kwargs)

    async def __handle_event(self, *args, **kwargs):
        if Config.General.prod:
            return await self.handle_event(*args, **kwargs)

    @abstractmethod
    async def handle_event(self, *args, **kwargs):
        raise NotImplementedError


class PGStatusEventHandler(AlertBotEventHandler):
    prev_pg_status = None

    async def handle_event(self, event_type: EventType, app: Application):
        if event_type == EventType.PGAlive:
            if self.prev_pg_status != event_type:
                await app['alert_bot'].send('[POSTGRESQL ALIVE] Postgres alive')
                self.prev_pg_status = event_type
        elif event_type == EventType.PGDown:
            if self.prev_pg_status != event_type:
                self.prev_pg_status = event_type
                await app['alert_bot'].send('[POSTGRESQL DOWN]: Postgres down:(')


class ESStatusEventHandler(AlertBotEventHandler):
    prev_es_status = None

    async def handle_event(self, event_type: EventType, app: Application):
        if event_type == EventType.ESAlive:
            if self.prev_es_status != event_type:
                await app['alert_bot'].send('[ELASTICSEARCH ALIVE] Elastic search alive')
                self.prev_es_status = event_type
        elif event_type == EventType.ESDown:
            if self.prev_es_status != event_type:
                self.prev_es_status = event_type
                await app['alert_bot'].send('[ELASTICSEARCH DOWN]: Elastic search down:(')


class UnhandledExceptionEventHandler(AlertBotEventHandler):
    async def handle_event(self, event_type: EventType, app: Application, msg: str):
        if event_type == EventType.UnhandledException:
            await app['alert_bot'].send(f'[UNHANDLED EXCEPTION]: {msg}')


class ApplicationStatusEventHandler(AlertBotEventHandler):
    async def handle_event(self, event_type: EventType, app: Application):
        if event_type == EventType.AppUp:
            await app['alert_bot'].alert_app_up()
        elif event_type == EventType.AppDown:
            await app['alert_bot'].alert_app_down()


async def create_alert_bot(token: str, chat_id: int, app: Application):
    logging.info("Registering bot")

    app['alert_bot'] = AlertBot(Bot(token=token), chat_id=chat_id)

    logging.info("Bot registered")

    await app['event_engine'].push(EventType.AppUp, app)

    try:
        logging.info("Polling started")
        yield
    except Exception as err:
        logging.error(err)
