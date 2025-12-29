"""
옷차림 추천 및 외출 적합도 판단 로직
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class WeatherCondition:
    """날씨 조건"""

    temperature: float  # 현재 기온
    min_temp: Optional[float] = None  # 최저 기온
    max_temp: Optional[float] = None  # 최고 기온
    humidity: Optional[int] = None  # 습도
    wind_speed: Optional[float] = None  # 풍속
    precipitation_prob: Optional[int] = None  # 강수확률
    precipitation_type: Optional[str] = None  # 강수형태
    sky: Optional[str] = None  # 하늘상태


@dataclass
class AirQualityCondition:
    """대기질 조건"""

    pm10_value: float = -1  # 미세먼지
    pm10_grade: str = "알수없음"
    pm25_value: float = -1  # 초미세먼지
    pm25_grade: str = "알수없음"


# 기온별 옷차림 가이드 (v3.4 세분화)
OUTFIT_BY_TEMPERATURE = {
    (28, 100): {
        "category": "한여름",
        "top": ["민소매", "반팔 티셔츠", "린넨 셔츠"],
        "bottom": ["반바지", "린넨 팬츠", "면바지"],
        "outer": [],
        "accessories": ["모자", "선글라스"],
        "tip": "더위 조심! 시원한 소재의 옷을 입으세요.",
        # TPO별 추천 (v3.4)
        "tpo": {
            "출근": {"top": "린넨 셔츠", "bottom": "슬랙스", "tip": "쿨맥스 소재 추천, 재킷은 실내용"},
            "데이트": {"top": "반팔 셔츠", "bottom": "면바지", "tip": "깔끔하면서 시원하게"},
            "운동": {"top": "기능성 반팔", "bottom": "반바지", "tip": "땀 흡수 빠른 소재"},
            "캐주얼": {"top": "반팔 티셔츠", "bottom": "반바지", "tip": "편하게 입으세요"},
        },
        "colors": ["화이트", "하늘색", "베이지", "파스텔톤"],
        "avoid": ["어두운 색", "두꺼운 소재"],
    },
    (23, 27): {
        "category": "초여름/초가을",
        "top": ["반팔 티셔츠", "얇은 셔츠", "블라우스"],
        "bottom": ["면바지", "청바지", "슬랙스"],
        "outer": ["얇은 가디건"],
        "accessories": [],
        "tip": "일교차에 대비해 얇은 겉옷을 챙기세요.",
        "tpo": {
            "출근": {"top": "셔츠", "bottom": "슬랙스", "tip": "가디건을 가방에 챙기세요"},
            "데이트": {"top": "블라우스/셔츠", "bottom": "청바지", "tip": "깔끔한 캐주얼 추천"},
            "운동": {"top": "반팔", "bottom": "트레이닝", "tip": "자외선 차단제 필수"},
            "캐주얼": {"top": "반팔 티", "bottom": "면바지", "tip": "레이어드 하기 좋은 날씨"},
        },
        "colors": ["파스텔", "화이트", "베이지", "연한 색상"],
        "avoid": ["두꺼운 소재"],
    },
    (20, 22): {
        "category": "환절기",
        "top": ["긴팔 티셔츠", "얇은 니트", "맨투맨"],
        "bottom": ["청바지", "슬랙스", "면바지"],
        "outer": ["가디건", "얇은 자켓"],
        "accessories": [],
        "tip": "아침저녁으로 쌀쌀할 수 있어요.",
        "tpo": {
            "출근": {"top": "셔츠+가디건", "bottom": "슬랙스", "tip": "레이어드 스타일 추천"},
            "데이트": {"top": "얇은 니트", "bottom": "청바지", "tip": "자켓 하나 챙기세요"},
            "운동": {"top": "긴팔 기능성", "bottom": "트레이닝", "tip": "운동 후 땀 식으면 쌀쌀"},
            "캐주얼": {"top": "맨투맨", "bottom": "면바지", "tip": "간편하게 입기 좋은 날씨"},
        },
        "colors": ["브라운", "베이지", "카키", "버건디"],
        "avoid": [],
    },
    (17, 19): {
        "category": "선선한 날씨",
        "top": ["니트", "맨투맨", "후드티"],
        "bottom": ["청바지", "슬랙스"],
        "outer": ["자켓", "야상", "트렌치코트"],
        "accessories": [],
        "tip": "겉옷은 필수! 레이어드 스타일 추천.",
        "tpo": {
            "출근": {"top": "셔츠+자켓", "bottom": "슬랙스", "tip": "트렌치코트 추천"},
            "데이트": {"top": "니트", "bottom": "청바지", "tip": "자켓으로 포인트"},
            "운동": {"top": "바람막이", "bottom": "트레이닝", "tip": "운동 전후 체온관리"},
            "캐주얼": {"top": "후드티", "bottom": "청바지", "tip": "편하게 레이어드"},
        },
        "colors": ["브라운", "네이비", "카키", "와인"],
        "avoid": ["얇은 소재만"],
    },
    (12, 16): {
        "category": "쌀쌀한 날씨",
        "top": ["니트", "기모 맨투맨", "셔츠 레이어드"],
        "bottom": ["청바지", "기모 팬츠"],
        "outer": ["자켓", "코트", "가죽자켓"],
        "accessories": ["스카프"],
        "tip": "두꺼운 겉옷을 준비하세요.",
        "tpo": {
            "출근": {"top": "니트+셔츠", "bottom": "슬랙스", "tip": "코트 추천"},
            "데이트": {"top": "니트", "bottom": "청바지", "tip": "가죽자켓으로 스타일업"},
            "운동": {"top": "기모 후드", "bottom": "기모 트레이닝", "tip": "워밍업 충분히"},
            "캐주얼": {"top": "기모 맨투맨", "bottom": "청바지", "tip": "따뜻하고 편하게"},
        },
        "colors": ["네이비", "브라운", "그레이", "블랙"],
        "avoid": ["얇은 니트만"],
    },
    (9, 11): {
        "category": "초겨울",
        "top": ["두꺼운 니트", "기모 후드"],
        "bottom": ["기모 팬츠", "코듀로이"],
        "outer": ["코트", "패딩", "무스탕"],
        "accessories": ["머플러", "장갑"],
        "tip": "보온에 신경 쓰세요.",
        "tpo": {
            "출근": {"top": "두꺼운 니트", "bottom": "울 슬랙스", "tip": "코트 필수"},
            "데이트": {"top": "니트", "bottom": "기모 청바지", "tip": "따뜻하면서 스타일리시하게"},
            "운동": {"top": "기모 후드", "bottom": "기모 트레이닝", "tip": "실내운동 추천"},
            "캐주얼": {"top": "기모 맨투맨", "bottom": "기모 팬츠", "tip": "숏패딩 추천"},
        },
        "colors": ["블랙", "그레이", "네이비", "카멜"],
        "avoid": ["얇은 겉옷"],
    },
    (5, 8): {
        "category": "겨울",
        "top": ["두꺼운 니트", "히트텍"],
        "bottom": ["기모 팬츠", "울 팬츠"],
        "outer": ["두꺼운 코트", "롱패딩", "숏패딩"],
        "accessories": ["머플러", "장갑", "귀마개"],
        "tip": "따뜻하게 입으세요!",
        "tpo": {
            "출근": {"top": "히트텍+니트", "bottom": "울 슬랙스", "tip": "롱코트 추천"},
            "데이트": {"top": "니트", "bottom": "기모 팬츠", "tip": "따뜻하게! 핫팩 챙기세요"},
            "운동": {"top": "기모 후드", "bottom": "기모 트레이닝", "tip": "실내운동 강력 추천"},
            "캐주얼": {"top": "히트텍+후드", "bottom": "기모 팬츠", "tip": "패딩 필수"},
        },
        "colors": ["블랙", "네이비", "그레이", "다크톤"],
        "avoid": ["얇은 소재", "바람 통하는 옷"],
    },
    (-100, 4): {
        "category": "한겨울",
        "top": ["히트텍", "두꺼운 니트", "기모 후드"],
        "bottom": ["기모 팬츠", "발열 내의"],
        "outer": ["롱패딩", "두꺼운 코트"],
        "accessories": ["머플러", "장갑", "귀마개", "핫팩"],
        "tip": "최대한 따뜻하게! 동상 주의.",
        "tpo": {
            "출근": {"top": "히트텍+니트", "bottom": "발열 내의+슬랙스", "tip": "롱패딩 강력 추천"},
            "데이트": {"top": "히트텍+니트", "bottom": "기모 팬츠", "tip": "실내 데이트 추천"},
            "운동": {"top": "히트텍+기모후드", "bottom": "기모 트레이닝", "tip": "실내운동만!"},
            "캐주얼": {"top": "히트텍+후드", "bottom": "기모 팬츠", "tip": "롱패딩+핫팩"},
        },
        "colors": ["블랙", "다크그레이", "네이비"],
        "avoid": ["모든 얇은 옷"],
    },
}


# 날씨별 색상 추천 (v3.4)
WEATHER_COLORS = {
    "맑음": {
        "recommended": ["화이트", "파스텔", "밝은 색상"],
        "tip": "밝은 색으로 화사하게!",
    },
    "흐림": {
        "recommended": ["브라운", "베이지", "따뜻한 톤"],
        "tip": "따뜻한 색상으로 분위기 UP",
    },
    "비": {
        "recommended": ["네이비", "그레이", "어두운 색"],
        "tip": "물 튀어도 티 안 나는 색상 추천",
    },
    "눈": {
        "recommended": ["블랙", "다크톤", "포인트 컬러"],
        "tip": "어두운 베이스에 밝은 액세서리",
    },
}


def get_outfit_recommendation(weather: WeatherCondition, tpo: str = "") -> dict:
    """
    날씨 조건에 따른 옷차림 추천 (v3.4 세분화)

    Args:
        weather: 날씨 조건
        tpo: 상황 (출근, 데이트, 운동, 캐주얼) - 비어있으면 일반 추천

    Returns:
        옷차림 추천 정보 (TPO별/색상별 포함)
    """
    temp = weather.temperature

    # 기온 범위에 맞는 추천 찾기
    recommendation = None
    for (low, high), outfit in OUTFIT_BY_TEMPERATURE.items():
        if low <= temp <= high:
            recommendation = outfit.copy()
            break

    if recommendation is None:
        # 기본값
        recommendation = OUTFIT_BY_TEMPERATURE[(17, 19)].copy()

    # 복사해서 수정 (원본 보존)
    accessories = list(recommendation.get("accessories", []))

    # 추가 조건 반영
    tip = recommendation["tip"]

    # 비/눈 예보 시
    if weather.precipitation_type and weather.precipitation_type != "없음":
        if "비" in weather.precipitation_type:
            accessories.append("우산")
            tip += " 비 예보가 있으니 우산을 챙기세요!"
        elif "눈" in weather.precipitation_type:
            accessories.append("방수 신발")
            tip += " 눈 예보가 있으니 미끄럼 주의!"

    # 강수확률 높을 때
    if weather.precipitation_prob and weather.precipitation_prob >= 60:
        if "우산" not in accessories:
            accessories.append("우산")

    # 바람 강할 때
    if weather.wind_speed and weather.wind_speed >= 5.0:
        tip += " 바람이 강해요, 방풍 자켓 추천!"

    # 습도 높을 때
    if weather.humidity and weather.humidity >= 80:
        tip += " 습도가 높아 불쾌할 수 있어요."

    # 날씨별 색상 추천
    weather_colors = None
    if weather.sky:
        for weather_key in ["맑음", "흐림", "비", "눈"]:
            if weather_key in weather.sky:
                weather_colors = WEATHER_COLORS.get(weather_key)
                break
    if weather.precipitation_type and weather.precipitation_type != "없음":
        if "비" in weather.precipitation_type:
            weather_colors = WEATHER_COLORS.get("비")
        elif "눈" in weather.precipitation_type:
            weather_colors = WEATHER_COLORS.get("눈")

    # TPO별 추천 (v3.4)
    tpo_recommendation = None
    if tpo and tpo in recommendation.get("tpo", {}):
        tpo_recommendation = recommendation["tpo"][tpo]

    result = {
        "temperature": temp,
        "category": recommendation["category"],
        "recommendation": {
            "top": recommendation["top"],
            "bottom": recommendation["bottom"],
            "outer": recommendation["outer"],
            "accessories": accessories,
        },
        "tip": tip,

        # v3.4 세분화된 정보
        "colors": {
            "recommended": recommendation.get("colors", []),
            "avoid": recommendation.get("avoid", []),
            "weather_colors": weather_colors,
        },
        "by_situation": recommendation.get("tpo", {}),
    }

    # TPO가 지정된 경우 해당 추천을 강조
    if tpo_recommendation:
        result["your_situation"] = {
            "tpo": tpo,
            "specific_top": tpo_recommendation["top"],
            "specific_bottom": tpo_recommendation["bottom"],
            "specific_tip": tpo_recommendation["tip"],
        }

    return result


def calculate_outing_score(
    weather: WeatherCondition, air_quality: AirQualityCondition
) -> dict:
    """
    외출 적합도 점수 계산 (0-100)

    Args:
        weather: 날씨 조건
        air_quality: 대기질 조건

    Returns:
        외출 적합도 점수 및 상세 정보
    """
    score = 100
    factors = []

    # 1. 기온 점수 (15~25도가 최적)
    temp = weather.temperature
    if 15 <= temp <= 25:
        temp_score = 100
    elif 10 <= temp < 15 or 25 < temp <= 30:
        temp_score = 80
    elif 5 <= temp < 10 or 30 < temp <= 35:
        temp_score = 60
    elif 0 <= temp < 5 or 35 < temp <= 38:
        temp_score = 40
    else:
        temp_score = 20

    if temp_score < 80:
        factors.append(f"기온 {temp}°C ({_get_temp_desc(temp)})")

    # 2. 강수 점수
    rain_score = 100
    if weather.precipitation_type and weather.precipitation_type != "없음":
        rain_score = 30
        factors.append(f"강수: {weather.precipitation_type}")
    elif weather.precipitation_prob:
        if weather.precipitation_prob >= 80:
            rain_score = 40
            factors.append(f"강수확률 {weather.precipitation_prob}%")
        elif weather.precipitation_prob >= 60:
            rain_score = 60
            factors.append(f"강수확률 {weather.precipitation_prob}%")
        elif weather.precipitation_prob >= 40:
            rain_score = 80

    # 3. 미세먼지 점수
    pm_score = 100
    if air_quality.pm25_grade == "매우나쁨":
        pm_score = 20
        factors.append(f"초미세먼지 매우나쁨 ({air_quality.pm25_value}μg/m³)")
    elif air_quality.pm25_grade == "나쁨":
        pm_score = 50
        factors.append(f"초미세먼지 나쁨 ({air_quality.pm25_value}μg/m³)")
    elif air_quality.pm10_grade == "매우나쁨":
        pm_score = 30
        factors.append(f"미세먼지 매우나쁨 ({air_quality.pm10_value}μg/m³)")
    elif air_quality.pm10_grade == "나쁨":
        pm_score = 60
        factors.append(f"미세먼지 나쁨 ({air_quality.pm10_value}μg/m³)")

    # 4. 바람 점수
    wind_score = 100
    if weather.wind_speed:
        if weather.wind_speed >= 10:
            wind_score = 40
            factors.append(f"강풍 {weather.wind_speed}m/s")
        elif weather.wind_speed >= 7:
            wind_score = 60
            factors.append(f"바람 {weather.wind_speed}m/s")
        elif weather.wind_speed >= 5:
            wind_score = 80

    # 종합 점수 (가중 평균)
    score = int(
        temp_score * 0.25 + rain_score * 0.30 + pm_score * 0.30 + wind_score * 0.15
    )

    # 등급 결정
    if score >= 80:
        grade = "좋음"
        emoji = "😊"
        message = "외출하기 좋은 날이에요!"
    elif score >= 60:
        grade = "보통"
        emoji = "🙂"
        message = "외출 가능하지만 주의사항이 있어요."
    elif score >= 40:
        grade = "나쁨"
        emoji = "😐"
        message = "가능하면 외출을 자제하세요."
    else:
        grade = "매우나쁨"
        emoji = "😷"
        message = "외출을 삼가세요!"

    return {
        "score": score,
        "grade": grade,
        "emoji": emoji,
        "message": message,
        "factors": factors,
        "detail_scores": {
            "temperature": temp_score,
            "precipitation": rain_score,
            "air_quality": pm_score,
            "wind": wind_score,
        },
    }


def _get_temp_desc(temp: float) -> str:
    """기온 설명"""
    if temp >= 35:
        return "폭염"
    elif temp >= 30:
        return "무더움"
    elif temp >= 25:
        return "더움"
    elif temp >= 20:
        return "따뜻함"
    elif temp >= 15:
        return "선선함"
    elif temp >= 10:
        return "쌀쌀함"
    elif temp >= 5:
        return "추움"
    elif temp >= 0:
        return "매우 추움"
    else:
        return "영하"


def get_comprehensive_recommendation(
    weather: WeatherCondition, air_quality: AirQualityCondition
) -> dict:
    """
    종합 추천 정보

    Args:
        weather: 날씨 조건
        air_quality: 대기질 조건

    Returns:
        종합 추천 정보 (외출 적합도 + 옷차림)
    """
    outing = calculate_outing_score(weather, air_quality)
    outfit = get_outfit_recommendation(weather)

    # 대기질 나쁨 시 마스크 추가
    if air_quality.pm10_grade in ["나쁨", "매우나쁨"] or air_quality.pm25_grade in [
        "나쁨",
        "매우나쁨",
    ]:
        if "마스크" not in outfit["recommendation"]["accessories"]:
            outfit["recommendation"]["accessories"].append("마스크")
            outfit["tip"] += " 미세먼지가 나쁘니 마스크를 착용하세요."

    return {
        "outing_score": outing,
        "outfit_recommendation": outfit,
        "summary": f"{outing['emoji']} 외출 적합도 {outing['score']}점 ({outing['grade']}). {outfit['tip']}",
    }
