from sun_calculator import get_position, get_times, from_julian, to_julian
from datetime import datetime, timezone
import numpy as np

print(get_position(datetime.now(tz=timezone.utc), lat=37.478897, lng=126.953309))
for key, val in get_times(datetime.now(tz=timezone.utc), lat=37.478897, lng=126.953309).items():
    print(key, val.astimezone())

print(np.array((datetime.now(tz=timezone.utc).replace(tzinfo=None),)*2, dtype=np.datetime64).dtype)
print(get_position(np.array((datetime.now(tz=timezone.utc).replace(tzinfo=None),)*2, dtype=np.datetime64), lat=np.array((37.478897, 37.478897)), lng=np.array((126.953309, 126.953309))))
print(from_julian(2440588 + 21.))
print(from_julian(2440588 + np.arange(4)))
print(to_julian(from_julian(2440588 + np.arange(4))))
