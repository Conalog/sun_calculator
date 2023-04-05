# 개요

- 태양의 위치(고도, 방위각, 거리)를 계산해주는 모듈
    
    관측자 위치 기준으로 천체의 위치를 나타내는 [지평좌표계](https://en.wikipedia.org/wiki/Horizontal_coordinate_system) 참조
    
- 일출&일몰 시간 계산 가능
- `numpy.array`로 복수의 값을 인풋으로 넣을 수 있음

# 사용법 예시

- 특정 경위도에서 현재 태양의 위치 계산

    ```python
    import sun_calculator
    import datetime
    
    latitude = 37.478897
    longitude = 126.953309
    
    # tz-naive local time result (wrong)
    print(sun_calculator.get_position(date=datetime.datetime.now(), lat=latitude, lng=longitude))
    
    # tz-aware local time result (correct)
    print(sun_calculator.get_position(date=datetime.datetime.now().astimezone(), lat=latitude, lng=longitude))
    
    # tz-naive UTC result (correct)
    print(sun_calculator.get_position(date=datetime.datetime.utcnow(), lat=latitude, lng=longitude))
    
    # tz-aware UTC result (correct)
    print(sun_calculator.get_position(date=datetime.datetime.now(tz=datetime.timezone.utc), lat=latitude, lng=longitude))
    ```
    
    - timezone-naive한 경우 UTC로 가정
    - 결과 형식
        
        ```json
        {
          "azimuth": "float", 
          "altitude": "float", 
          "distance": "float"
        }
        ```
        
        - 고도와 방위각은 °, 거리는 m 단위
- 복수의 시각+경도+위도 조합에서의 태양의 위치 계산

    ```python
    import sun_calculator
    import datetime
    import numpy as np
    
    latitude = 37.478897
    longitude = 126.953309
    
    print(sun_calculator.get_position(
        date=np.array([datetime.datetime.utcnow(), datetime.datetime.utcnow() + datetime.timedelta(hours=4)], dtype=np.datetime64),
        lat=latitude,
        lng=longitude
    ))
    
    print(sun_calculator.get_position(
        date=np.array([datetime.datetime.utcnow(), datetime.datetime.utcnow() + datetime.timedelta(hours=4)], dtype=np.datetime64),
        lat=np.array([latitude]),
        lng=np.array([longitude])
    ))
    
    print(sun_calculator.get_position(
        date=np.array([datetime.datetime.utcnow()], dtype=np.datetime64),
        lat=np.array([latitude] * 2),
        lng=longitude
    ))
    ```
    
    - **`numpy`의 `datetime64`는 tz-naive하기 때문에 UTC 시각을 사용하여야 함**
    - `numpy`에서 broadcast할 수 있는 형태면 다 가능하지만, 아웃풋이 의도치 않은 형태를 가질 수 있으므로 같은 dimension을 쓰는 것을 추천
    - 결과 형식
        
        ```json
        {
          "azimuth": "numpy.ndarray", 
          "altitude": "numpy.ndarray", 
          "distance": "numpy.ndarray"
        }
        ```
        
- 특정 위치에서의 주요 이벤트 시각

    ```python
    import sun_calculator
    import datetime
    
    latitude = 37.478897
    longitude = 126.953309
    
    tz_local = datetime.timezone(datetime.timedelta(hours=9))
    day = datetime.datetime.now(tz=tz_local).replace(hour=12, minute=0, second=0, microsecond=0)
    
    for key, val in sun_calculator.get_times(date=day.astimezone(datetime.timezone.utc), lat=latitude, lng=longitude).items():
        print(key, val.astimezone())
    
    ```
    
    - 일출&일몰 시각 등 주요 이벤트의 시각 계산
    - 주어진 시각에서 (전후 상관 없이) “가장 가까운 태양의 남중 시각”를 기준으로 계산되기 때문에, 특정일의 이벤트 시각을 알고 싶은 경우 **정오의 `datetime`을 넣어주는 것이 좋음**
    - 결과 형식
        
        ```json
        {
            "solar_noon": "datetime",
            "solar_midnight": "datetime",
            "sunrise": "datetime",
            "sunset": "datetime",
            "sunrise_end": "datetime",
            "sunset_start": "datetime",
            "dawn": "datetime",
            "dusk": "datetime",
            "nautical_dawn": "datetime",
            "nautical_dusk": "datetime",
            "night_end": "datetime",
            "night_start": "datetime",
            "golden_hour_end": "datetime",
            "golden_hour_start": "datetime"
        }
        ```
        
        - tz-aware한 UTC `datetime`을 리턴
        - 각 시각의 정의
            - solar noon, solar midnight: 태양의 자오선 통과 시각
            - sunrise, sunset: 태양의 지평선 통과 시각 (고도=-0.833, 대기에 의한 굴절 효과 고려)
            - sunrise_end, sunset_start: 태양이 지평선에 접하는 시각 (고도=-0.3)
            - dawn, dusk: 시민 박명 시작/끝 (고도=-6)
            - nautical_dawn, nautical_dusk: 항해박명 시작/끝 (고도=-12)
            - night_end, night_start: 천문박명 시작/끝 (고도=-18)
            - golden_hour_end, golden_hour_start: 일몰 직전 / 일출 직후 (고도=6, 촬영 용어)