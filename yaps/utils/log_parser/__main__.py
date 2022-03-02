import asyncio
import logging
from datetime import datetime
from typing import List

from yaps.settings import Config

from yaps.utils.alert_bot.bot import AlertBot
from yaps.utils.log_parser.log_parser import LogParser
from yaps.utils.log_parser.log_stats import LogStats
from yaps.utils.log_parser.nginx_log import NginxLog


def read_logs() -> List[NginxLog]:
    logs = []
    with open(Config.nginx_logs_path, "r") as log_file:
        for log in log_file:
            nginx_log = LogParser.parse_log(log)
            if nginx_log:
                logs.append(nginx_log)

    return logs


def main():
    logs = read_logs()
    logging.info("read %d nginx logs", len(logs))

    now = datetime.now()
    stats = LogStats.get_stats(now, logs)
    info_msg = LogStats.get_stats_info(now, stats)

    alert_bot = AlertBot()
    asyncio.run(alert_bot.send(info_msg))

    logging.info("send info message to telegram bot")


if __name__ == "__main__":
    main()
