from datetime import datetime
from dateutil.tz import tzlocal


class EeaUtils:
    @staticmethod
    def local_datetime():
        now = datetime.now(tz=tzlocal())  # current date and time
        return now.strftime("%Y-%m-%dT%H:%M:%S%z")
