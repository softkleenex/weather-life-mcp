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


# 기온별 옷차림 가이드
OUTFIT_BY_TEMPERATURE = {
    (28, 100): {
        "category": "한여름",
        "top": ["민소매", "반팔 티셔츠", "린넨 셔츠"],
        "bottom": ["반바지", "린넨 팬츠", "면바지"],
        "outer": [],
        "accessories": ["모자", "선글라스"],
        "tip": "더위 조심! 시원한 소재의 옷을 입으세요.",
    },
    (23, 27): {
        "category": "초여름/초가을",
        "top": ["반팔 티셔츠", "얇은 셔츠", "블라우스"],
        "bottom": ["면바지", "청바지", "슬랙스"],
        "outer": ["얇은 가디건"],
        "accessories": [],
        "tip": "일교차에 대비해 얇은 겉옷을 챙기세요.",
    },
    (20, 22): {
        "category": "환절기",
        "top": ["긴팔 티셔츠", "얇은 니트", "맨투맨"],
        "bottom": ["청바지", "슬랙스", "면바지"],
        "outer": ["가디건", "얇은 자켓"],
        "accessories": [],
        "tip": "아침저녁으로 쌀쌀할 수 있어요.",
    },
    (17, 19): {
        "category": "선선한 날씨",
        "top": ["니트", "맨투맨", "후드티"],
        "bottom": ["청바지", "슬랙스"],
        "outer": ["자켓", "야상", "트렌치코트"],
        "accessories": [],
        "tip": "겉옷은 필수! 레이어드 스타일 추천.",
    },
    (12, 16): {
        "category": "쌀쌀한 날씨",
        "top": ["니트", "기모 맨투맨", "셔츠 레이어드"],
        "bottom": ["청바지", "기모 팬츠"],
        "outer": ["자켓", "코트", "가죽자켓"],
        "accessories": ["스카프"],
        "tip": "두꺼운 겉옷을 준비하세요.",
    },
    (9, 11): {
        "category": "초겨울",
        "top": ["두꺼운 니트", "기모 후드"],
        "bottom": ["기모 팬츠", "코듀로이"],
        "outer": ["코트", "패딩", "무스탕"],
        "accessories": ["머플러", "장갑"],
        "tip": "보온에 신경 쓰세요.",
    },
    (5, 8): {
        "category": "겨울",
        "top": ["두꺼운 니트", "히트텍"],
        "bottom": ["기모 팬츠", "울 팬츠"],
        "outer": ["두꺼운 코트", "롱패딩", "숏패딩"],
        "accessories": ["머플러", "장갑", "귀마개"],
        "tip": "따뜻하게 입으세요!",
    },
    (-100, 4): {
        "category": "한겨울",
        "top": ["히트텍", "두꺼운 니트", "기모 후드"],
        "bottom": ["기모 팬츠", "발열 내의"],
        "outer": ["롱패딩", "두꺼운 코트"],
        "accessories": ["머플러", "장갑", "귀마개", "핫팩"],
        "tip": "최대한 따뜻하게! 동상 주의.",
    },
}


def get_outfit_recommendation(weather: WeatherCondition) -> dict:
    """
    날씨 조건에 따른 옷차림 추천

    Args:
        weather: 날씨 조건

    Returns:
        옷차림 추천 정보
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

    # 추가 조건 반영

    # 비/눈 예보 시
    if weather.precipitation_type and weather.precipitation_type != "없음":
        if "비" in weather.precipitation_type:
            recommendation["accessories"].append("우산")
            recommendation["tip"] += " 비 예보가 있으니 우산을 챙기세요!"
        elif "눈" in weather.precipitation_type:
            recommendation["accessories"].append("방수 신발")
            recommendation["tip"] += " 눈 예보가 있으니 미끄럼 주의!"

    # 강수확률 높을 때
    if weather.precipitation_prob and weather.precipitation_prob >= 60:
        if "우산" not in recommendation["accessories"]:
            recommendation["accessories"].append("우산")

    # 바람 강할 때
    if weather.wind_speed and weather.wind_speed >= 5.0:
        recommendation["tip"] += " 바람이 강해요, 방풍 자켓 추천!"

    # 습도 높을 때
    if weather.humidity and weather.humidity >= 80:
        recommendation["tip"] += " 습도가 높아 불쾌할 수 있어요."

    return {
        "temperature": temp,
        "category": recommendation["category"],
        "recommendation": {
            "top": recommendation["top"],
            "bottom": recommendation["bottom"],
            "outer": recommendation["outer"],
            "accessories": recommendation["accessories"],
        },
        "tip": recommendation["tip"],
    }


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
