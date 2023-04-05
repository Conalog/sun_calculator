from sun_calculator import get_position, get_times, from_julian, to_julian
from datetime import datetime, timedelta, timezone
import numpy as np

latitude = 37.478897
longitude = 126.953309

print("tz-naive local time result:", get_position(date=datetime.now(), lat=latitude, lng=longitude))  # wrong result
print("tz-aware local time result:", get_position(date=datetime.now().astimezone(), lat=latitude, lng=longitude))
print("tz-naive UTC", get_position(date=datetime.utcnow(), lat=latitude, lng=longitude))
print("tz-aware UTC", get_position(date=datetime.now(tz=timezone.utc), lat=latitude, lng=longitude))


print(np.array((datetime.now(tz=timezone.utc).replace(tzinfo=None),)*2, dtype=np.datetime64).dtype)
print(get_position(
    date=np.array([datetime.utcnow()], dtype=np.datetime64),
    lat=np.array([latitude] * 2),
    lng=longitude
))

for key, val in get_times(date=datetime.now(tz=timezone.utc), lat=latitude, lng=longitude).items():
    print(key, val.astimezone())

print(from_julian(2440588 + 21.))
print(from_julian(2440588 + np.arange(4)))
print(to_julian(from_julian(2440588 + np.arange(4))))

print(get_times(
    date=np.array([datetime.utcnow(), datetime.utcnow() - timedelta(hours=14)], dtype=np.datetime64),
    lat=np.array([latitude]),
    lng=np.array([longitude])
))
