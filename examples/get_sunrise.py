from datetime import datetime, timedelta, timezone

from sun_calculator import DEFAULT_TIMES, get_times

tz_local = timezone(timedelta(hours=9))
day = datetime.now(tz=tz_local).replace(hour=12, minute=0, second=0, microsecond=0)
for time_str, time in get_times(
    day.astimezone(timezone.utc), lat=+37.478897, lng=126.953309, times=DEFAULT_TIMES
).items():
    print(time_str, time.astimezone(tz_local).isoformat())
