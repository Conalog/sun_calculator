from sun_calculator import get_times, DEFAULT_TIMES
from datetime import datetime, timedelta, timezone

tz_local = timezone(timedelta(hours=9))
day = datetime(2022, 12, 14, tzinfo=tz_local)
for time_str, time in get_times(day.astimezone(timezone.utc), lat=37.478897, lng=126.953309, times=DEFAULT_TIMES).items():
    print(time_str, time.astimezone(tz_local).isoformat())
