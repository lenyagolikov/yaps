from datetime import datetime
from typing import Dict, List

from yaps.utils.log_parser.nginx_log import NginxLog


class LogStats:
    @staticmethod
    def get_stats(date: datetime, logs: List[NginxLog]) -> Dict[str, Dict[int, int]]:
        stats = {}
        for log in logs:
            if log.date.date() != date.date() or not log.uri.startswith('/api'):
                continue

            buf = log.uri.split("?")
            uri = buf[0]

            if uri in stats:
                if log.status in stats[uri]:
                    stats[uri][log.status] += 1
                else:
                    stats[uri][log.status] = 1
            else:
                stats[uri] = {log.status: 1}

        return stats

    @staticmethod
    def get_stats_info(date: datetime, stats: Dict[str, Dict[int, int]]) -> str:
        stat_msg = f'Отчет за {date.strftime("%d/%b/%Y")}:\n\n'

        for uri, stat in stats.items():
            uri_stat_msg = f"{uri}:\n"
            for status, count in stat.items():
                uri_stat_msg += f"{status}: {count}\n"
            stat_msg += f"{uri_stat_msg}\n"

        return stat_msg
