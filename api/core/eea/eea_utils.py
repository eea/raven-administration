from datetime import datetime
from dateutil.tz import tzlocal


class EeaUtils:
    @staticmethod
    def local_datetime():
        now = datetime.now(tz=tzlocal())  # current date and time
        now_str = now.strftime("%Y-%m-%dT%H:%M:%S%z")
        # Correction needed because "%z" gives you timezone offset without colon.
        now_str_corr = "{0}:{1}".format(now_str[:-2], now_str[-2:])
        return now_str_corr
