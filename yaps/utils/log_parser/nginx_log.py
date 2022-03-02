from datetime import datetime
from typing import NamedTuple


class NginxLog(NamedTuple):
    ip: str
    uri: str
    date: datetime
    method: str
    status: int
