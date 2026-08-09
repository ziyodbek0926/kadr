from datetime import date, datetime
from zoneinfo import ZoneInfo

_TASHKENT = ZoneInfo("Asia/Tashkent")


def today_tashkent() -> date:
    return datetime.now(_TASHKENT).date()
