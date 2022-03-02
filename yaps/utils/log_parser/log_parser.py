import re
from typing import Optional, List
from datetime import datetime

from yaps.utils.log_parser.nginx_log import NginxLog


class LogParser:
    log_re = re.compile(
        r'^([\d\.]+) - - \[([^\]]+)\] "([^"]+)" (\d+) (\d+) "([^"]+)" "([^"]+)"'
    )
    date_format: str = "%d/%b/%Y:%H:%M:%S %z"

    @classmethod
    def parse_log(cls, log: str) -> Optional[NginxLog]:
        matches = re.search(cls.log_re, log)
        method, uri, _ = matches[3].split()
        try:
            return NginxLog(
                ip=matches[1],
                date=datetime.strptime(matches[2], cls.date_format),
                uri=uri,
                method=method,
                status=int(matches[4]),
            )
        except (AttributeError, IndexError, ValueError):
            return None

    @classmethod
    def parse_logs(cls, logs: List[str]) -> List[NginxLog]:
        parsed_logs = []
        for log in logs:
            log_model = cls.parse_log(log)
            if log_model:
                parsed_logs.append(log_model)

        return parsed_logs
