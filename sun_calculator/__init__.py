from datetime import datetime, timezone
import numpy as np
from collections import namedtuple
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterable, Any

# shortcuts for easier to read formulas
PI = np.pi
sin = np.sin
cos = np.cos
tan = np.tan
asin = np.arcsin
atan = np.arctan2
acos = np.arccos
rad = PI / 180

# sun times configuration (angle, morning name, evening name)
DEFAULT_TIMES = (
    (-0.833, 'sunrise', 'sunset'),
    (-0.3, 'sunrise_end', 'sunset_start'),
    (-6, 'dawn', 'dusk'),
    (-12, 'nautical_dawn', 'nautical_dusk'),
    (-18, 'night_end', 'night'),
    (6, 'golden_hour_end', 'golden_hour')
) # yapf: disable

# date/time constants and conversions
DAY_IN_MS = 1000 * 60 * 60 * 24
J1970 = 2440588
J2000 = 2451545

AU = 1.49598e11 # m
ECCENTRICITY = 0.0167086


def to_milliseconds(date: 'datetime|np.ndarray') -> 'int|np.ndarray':
    # datetime.datetime
    if isinstance(date, datetime):
        return int(date.timestamp() * 1000)

    # Numpy datetime64
    if np.issubdtype(date.dtype, np.datetime64):
        return date.astype('datetime64[ms]').astype('int64')

    raise ValueError(f'Unknown date type: {type(date)}')


def to_julian(date: 'datetime|np.ndarray') -> 'float|np.ndarray':
    return to_milliseconds(date) / DAY_IN_MS - 0.5 + J1970


def from_julian(j: 'float|np.ndarray') -> 'datetime|np.ndarray':
    ms_date = (j + 0.5 - J1970) * DAY_IN_MS
    # ms_date could be iterable
    try:
        return np.array([
            datetime.utcfromtimestamp(x / 1000)
            if not np.isnan(x) else np.datetime64('NaT') for x in ms_date
        ], dtype=np.datetime64)

    except TypeError:
        return datetime.fromtimestamp(ms_date / 1000, tz=timezone.utc) \
            if not np.isnan(ms_date) else np.datetime64('NaT')


def to_days_since_j2000(date: 'datetime|np.ndarray') -> 'float|np.ndarray':
    return to_julian(date) - J2000


# general calculations for position

# obliquity of the Earth
e = rad * 23.4397

CoordEcliptic = namedtuple("CoordEcliptic", ["longitude", "latitude"])
CoordEquatorial = namedtuple("CoordEcliptic", ["right_ascension", "declination"])
CoordHorizontal = namedtuple("CoordEcliptic", ["azimuth", "altitude"])


def right_ascension(l, b):
    return atan(sin(l) * cos(e) - tan(b) * sin(e), cos(l))


def declination(l, b):
    return asin(sin(b) * cos(e) + cos(b) * sin(e) * sin(l))


def ecliptic2equatorial(coord_ecliptic: 'CoordEcliptic'):
    return CoordEquatorial(right_ascension(*coord_ecliptic), declination(*coord_ecliptic))


def azimuth(ha, phi, dec):
    return atan(sin(ha), cos(ha) * sin(phi) - tan(dec) * cos(phi))


def altitude(ha, phi, dec):
    return asin(sin(phi) * sin(dec) + cos(phi) * cos(dec) * cos(ha))


def sidereal_time(d, lw):
    return rad * (280.16 + 360.9856235 * d) - lw


def astro_refraction(h):
    # the following formula works for positive altitudes only.
    # if h = -0.08901179 a div/0 would occur.
    h = np.maximum(h, 0)

    # formula 16.4 of "Astronomical Algorithms" 2nd edition by Jean Meeus
    # (Willmann-Bell, Richmond) 1998. 1.02 / tan(h + 10.26 / (h + 5.10)) h in
    # degrees, result in arc minutes -> converted to rad:
    return 0.0002967 / np.tan(h + 0.00312536 / (h + 0.08901179))


# general sun calculations


def solar_mean_anomaly(d):
    return rad * (357.5291 + 0.98560028 * d)


def ecliptic_longitude(M):
    # equation of center
    C = rad * (1.9148 * sin(M) + 0.02 * sin(2 * M) + 0.0003 * sin(3 * M))

    # perihelion of the Earth
    P = rad * 102.9372

    return M + C + P + PI


def sun_coords(d):
    M = solar_mean_anomaly(d)
    L = ecliptic_longitude(M)

    return {
        'dec': declination(L, 0),
        'ra': right_ascension(L, 0),
        "distance": AU * (1 - ECCENTRICITY**2.) / (1 + ECCENTRICITY * cos(M))
    }


# calculations for sun times
J0 = 0.0009


def julian_cycle(d, lw):
    return np.round(d - J0 - lw / (2 * PI))


def approx_transit(Ht, lw, n):
    return J0 + (Ht + lw) / (2 * PI) + n


def solar_transit_j(ds, M, L):
    return J2000 + ds + 0.0053 * sin(M) - 0.0069 * sin(2 * L)


def hour_angle(h, phi, d):
    return acos((sin(h) - sin(phi) * sin(d)) / (cos(phi) * cos(d)))


def observer_angle(height):
    return -2.076 * np.sqrt(height) / 60


def get_set_j(h, lw, phi, dec, n, M, L):
    """Get set time for the given sun altitude
    """
    w = hour_angle(h, phi, dec)
    a = approx_transit(w, lw, n)
    return solar_transit_j(a, M, L)


def get_position(date, lng, lat):
    """Calculate sun position for a given date and latitude/longitude
    """
    lw = rad * -lng
    phi = rad * lat
    d = to_days_since_j2000(date)

    c = sun_coords(d)
    H = sidereal_time(d, lw) - c['ra']

    return {
        'azimuth': azimuth(H, phi, c['dec']) / rad + 180.,
        'altitude': altitude(H, phi, c['dec']) / rad,
        "distance": c["distance"]
    }


def get_times(
        date,
        lng,
        lat,
        height=0,
        times: 'Iterable[tuple[float, str, str]]' = None):
    """Calculate sun times

    Calculate sun times for a given date, latitude/longitude, and,
    optionally, the observer height (in meters) relative to the horizon
    """
    # If inputs are vectors (or some list-like type), then coerce them to
    # numpy arrays
    #
    # When inputs are pandas series, then intermediate objects will also be
    # pandas series, and you won't be able to do 2d broadcasting.
    if times is None:
        times = DEFAULT_TIMES
    try:
        len(date)
        len(lat)
        len(lng)
        array_input = True
        date = np.array(date)
        lat = np.array(lat)
        lng = np.array(lng)
    except TypeError:
        array_input = False

    lw = rad * -lng
    phi = rad * lat

    dh = observer_angle(height)

    d = to_days_since_j2000(date)
    n = julian_cycle(d, lw)
    ds = approx_transit(0, lw, n)

    M = solar_mean_anomaly(ds)
    L = ecliptic_longitude(M)
    dec = declination(L, 0)

    Jnoon = solar_transit_j(ds, M, L)

    result = {
        'solar_noon': from_julian(Jnoon),
        'nadir': from_julian(Jnoon - 0.5)}

    angles = np.array([time[0] for time in times])
    h0 = (angles + dh) * rad

    # If array input, add an axis to allow 2d broadcasting
    if array_input:
        h0 = h0[:, np.newaxis]

    # Need to add an axis for 2D broadcasting
    Jset = get_set_j(h0, lw, phi, dec, n, M, L)
    Jrise = Jnoon - (Jset - Jnoon)

    for idx, time in enumerate(times):
        if array_input:
            result[time[1]] = from_julian(Jrise[idx, :])
            result[time[2]] = from_julian(Jset[idx, :])
        else:
            result[time[1]] = from_julian(Jrise[idx])
            result[time[2]] = from_julian(Jset[idx])

    return result
