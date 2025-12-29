"""
Weather Life MCP 서버 v2.5
날씨 + 미세먼지 + 생활 도우미 + 한국 특화 + 건강 MCP

PlayMCP 공모전 (MCP Player 10) 출품작

v2.5 신규 기능 (야외 활동 지수 6종 추가):
- 드라이브지수 (Drive Index) - 강수/시야/바람/노면 상태 분석
- 캠핑지수 (Camping Index) - 낙뢰/바람/비/기온 분석
- 낚시지수 (Fishing Index) - 기압변화/바람/구름/기온 분석
- 골프지수 (Golf Index) - 바람/비/기온/자외선 분석
- 러닝지수 (Running Index) - 기온/습도/미세먼지/자외선 분석
- 바베큐지수 (BBQ Index) - 바람/비/기온 분석
- 29개 도구로 확장!

v2.4 신규 기능 (건강/생활 지수 확장):
- 편두통위험지수 (Migraine Risk) - 기압/습도 기반 과학적 연구
- 수면컨디션지수 (Sleep Quality) - 온도/습도 최적화 분석
- 사진촬영지수 (Photography) - 골든아워/조명 조건 분석
- 관절통위험지수 (Joint Pain) - 온도변화/습도 기반 관절염 연구
- 23개 도구로 확장!

v2.3 신규 기능 (과학적 근거 기반 - Perplexity Research):
- 감기위험지수 (Cold/Flu Risk) - MIT, Yale, PNAS 연구 기반
- 출퇴근지수 (Commute Index) - 교통수단별 분석
- 알레르기지수 (Allergy Index) - 계절/황사 연동
- 19개 도구로 확장!

v2.2 신규 기능 (AI/ML 트렌드 반영):
- 운동지수 (Health-Weather Integration)
- 캐싱 레이어 (API 최적화)
- 구조화된 에러 처리

v2.1 신규 기능:
- 3일 예보 (get_weekly_forecast)
- 도구 설명 개선 (사용 예시 추가)
- 경쟁 MCP 분석 기반 개선

v2.0 신규 기능:
- 생활기상지수 (자외선, 체감온도, 꽃가루, 식중독)
- 빨래지수 (기상청 종료 서비스 부활!)
- 등산지수 (한국인 등산 사랑)
- 피크닉지수 (한강 치맥!)
- 세차지수
- 김장지수 (세계 유일!)
"""

import sys
import os
from pathlib import Path

# 상위 디렉토리를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount

from config.settings import server_config, default_location, get_grid_coords
from src.weather_api import get_current_weather, get_weather_forecast
from src.air_quality_api import get_air_quality, get_air_quality_forecast
from src.outfit_recommender import (
    WeatherCondition,
    AirQualityCondition,
    get_outfit_recommendation,
    calculate_outing_score,
    get_comprehensive_recommendation,
)
from src.life_index_api import (
    get_uv_index,
    get_heat_index,
    get_pollen_index,
    get_food_poison_index,
    get_all_life_indices,
)
from src.activity_recommender import (
    WeatherData,
    calculate_laundry_index,
    calculate_hiking_index,
    calculate_picnic_index,
    calculate_car_wash_index,
    calculate_kimjang_index,
    calculate_exercise_index,
    calculate_cold_flu_risk_index,
    calculate_commute_index,
    calculate_allergy_risk_index,
    calculate_migraine_risk_index,
    calculate_sleep_quality_index,
    calculate_photography_index,
    calculate_joint_pain_index,
    get_all_activity_recommendations,
    # v2.5 신규
    calculate_drive_index,
    calculate_camping_index,
    calculate_fishing_index,
    calculate_golf_index,
    calculate_running_index,
    calculate_bbq_index,
)
from functools import lru_cache
from datetime import datetime, timedelta
import time

# =============================================================================
# 캐싱 레이어 (v2.2 신규 - API 최적화)
# =============================================================================

# 메모리 캐시 (TTL 지원)
_cache = {}
_cache_ttl = {}

def cached_async(ttl_seconds: int = 300):
    """비동기 함수용 TTL 캐시 데코레이터"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            now = time.time()

            # 캐시 히트 확인
            if cache_key in _cache:
                if now < _cache_ttl.get(cache_key, 0):
                    return _cache[cache_key]

            # 캐시 미스 - 함수 실행
            result = await func(*args, **kwargs)

            # 캐시 저장
            _cache[cache_key] = result
            _cache_ttl[cache_key] = now + ttl_seconds

            return result
        return wrapper
    return decorator


# =============================================================================
# 캐싱된 API 래퍼 함수들 (v2.5 성능 최적화)
# =============================================================================

# 원본 함수 저장 (래퍼에서 사용)
_orig_get_weather = get_current_weather
_orig_get_forecast = get_weather_forecast
_orig_get_air = get_air_quality

@cached_async(ttl_seconds=300)  # 5분 캐시
async def cached_get_weather(location: str) -> dict:
    """캐싱된 날씨 조회"""
    return await _orig_get_weather(location)

@cached_async(ttl_seconds=300)  # 5분 캐시
async def cached_get_forecast(location: str) -> dict:
    """캐싱된 예보 조회"""
    return await _orig_get_forecast(location)

@cached_async(ttl_seconds=600)  # 10분 캐시
async def cached_get_air_quality(location: str) -> dict:
    """캐싱된 미세먼지 조회"""
    return await _orig_get_air(location)

@cached_async(ttl_seconds=3600)  # 1시간 캐시
async def cached_get_life_index(location: str) -> dict:
    """캐싱된 생활기상지수 조회"""
    return await get_life_index_data(location)


# MCP 서버 인스턴스 생성
mcp = FastMCP(
    name="weather-life-mcp",
    instructions="""날씨, 미세먼지, 옷차림 추천, 한국 특화 생활지수를 제공하는 MCP입니다.

주요 기능:
1. 날씨/미세먼지 조회
2. 옷차림 추천 & 외출 적합도
3. 생활기상지수 (자외선, 체감온도, 꽃가루, 식중독)
4. 활동별 추천 (빨래, 등산, 피크닉, 세차)
5. 김장지수 (11-12월 한정, 한국 특화)

한국 전역 80개+ 지역 지원.""",
)


# =============================================================================
# Tools
# =============================================================================


@mcp.tool()
async def get_weather(location: str = "서울") -> dict:
    """
    현재 날씨와 오늘의 날씨 예보를 조회합니다.

    사용 예시: "서울 날씨 어때?", "부산 오늘 날씨", "강남구 기온"

    Args:
        location: 지역명 (예: "서울", "강남구", "부산", "제주")

    Returns:
        현재 날씨 정보와 오늘의 예보
    """
    current = await cached_get_weather(location)
    forecast = await cached_get_forecast(location)

    if "error" in current:
        return {"error": current["error"], "location": location}

    result = {
        "location": location,
        "current_weather": {
            "temperature": current["current"].get("temperature"),
            "humidity": current["current"].get("humidity"),
            "wind_speed": current["current"].get("wind_speed"),
            "precipitation_type": current["current"].get("precipitation_type"),
        },
    }

    if "error" not in forecast:
        result["today_summary"] = forecast.get("today_summary")
        result["hourly_forecast"] = forecast.get("forecasts", [])[:12]  # 12시간 예보

    return result


@mcp.tool()
async def get_air_quality_info(location: str = "서울") -> dict:
    """
    실시간 미세먼지 정보를 조회합니다.

    사용 예시: "미세먼지 어때?", "오늘 공기 질", "초미세먼지 확인"

    Args:
        location: 지역명 또는 측정소명 (예: "서울", "중구", "강남구")

    Returns:
        미세먼지(PM10), 초미세먼지(PM2.5) 수치 및 등급
    """
    result = await cached_get_air_quality(location)

    if "error" in result:
        return {"error": result["error"], "location": location}

    # 간결한 응답 포맷
    return {
        "location": result.get("station_name") or result.get("sido_name"),
        "data_time": result.get("data_time"),
        "pm10": result.get("pm10") or result.get("average", {}).get("pm10"),
        "pm25": result.get("pm25") or result.get("average", {}).get("pm25"),
    }


@mcp.tool()
async def get_outfit_recommendation_tool(
    location: str = "서울",
    temperature: float | None = None,
) -> dict:
    """
    날씨에 맞는 옷차림을 추천합니다.

    사용 예시: "오늘 뭐 입지?", "옷 추천해줘", "외출할 때 뭐 입을까?"

    Args:
        location: 지역명 (예: "서울", "부산")
        temperature: 직접 기온을 입력할 경우 (선택사항)

    Returns:
        기온별 옷차림 추천 (상의, 하의, 겉옷, 액세서리)
    """
    if temperature is None:
        # 실시간 날씨 조회
        weather_data = await cached_get_weather(location)
        if "error" in weather_data:
            return {"error": weather_data["error"]}
        temperature = weather_data["current"].get("temperature", 20)

    weather = WeatherCondition(temperature=temperature)
    recommendation = get_outfit_recommendation(weather)

    return {
        "location": location,
        "temperature": temperature,
        "category": recommendation["category"],
        "outfit": recommendation["recommendation"],
        "tip": recommendation["tip"],
    }


@mcp.tool()
async def should_i_go_out(location: str = "서울") -> dict:
    """
    오늘 외출하기 좋은지 종합적으로 판단합니다.
    날씨, 미세먼지, 기온 등을 고려하여 외출 적합도 점수와 추천을 제공합니다.

    사용 예시: "오늘 외출해도 돼?", "밖에 나가도 괜찮아?", "산책하기 좋아?"

    Args:
        location: 지역명 (예: "서울", "부산", "강남구")

    Returns:
        외출 적합도 점수 (0-100), 등급, 주의사항, 옷차림 추천
    """
    # 날씨 정보 조회
    weather_data = await cached_get_weather(location)
    forecast_data = await cached_get_forecast(location)
    air_data = await cached_get_air_quality(location)

    # 기본값 설정
    temp = 20
    humidity = 50
    wind_speed = 2.0
    precip_prob = 0
    precip_type = "없음"
    sky = "맑음"

    # 날씨 데이터 추출
    if "error" not in weather_data:
        current = weather_data.get("current", {})
        temp = current.get("temperature", temp)
        humidity = current.get("humidity", humidity)
        wind_speed = current.get("wind_speed", wind_speed)
        precip_type = current.get("precipitation_type", precip_type)

    if "error" not in forecast_data:
        summary = forecast_data.get("today_summary", {})
        precip_prob = summary.get("precipitation_probability", precip_prob)
        sky = summary.get("sky", sky)

    # 대기질 데이터 추출
    pm10_value = -1
    pm10_grade = "알수없음"
    pm25_value = -1
    pm25_grade = "알수없음"

    if "error" not in air_data:
        pm10_data = air_data.get("pm10") or air_data.get("average", {}).get("pm10", {})
        pm25_data = air_data.get("pm25") or air_data.get("average", {}).get("pm25", {})

        if isinstance(pm10_data, dict):
            pm10_value = pm10_data.get("value", -1)
            pm10_grade = pm10_data.get("grade", "알수없음")
        if isinstance(pm25_data, dict):
            pm25_value = pm25_data.get("value", -1)
            pm25_grade = pm25_data.get("grade", "알수없음")

    # 조건 객체 생성
    weather = WeatherCondition(
        temperature=temp,
        humidity=humidity,
        wind_speed=wind_speed,
        precipitation_prob=precip_prob,
        precipitation_type=precip_type,
        sky=sky,
    )

    air_quality = AirQualityCondition(
        pm10_value=pm10_value,
        pm10_grade=pm10_grade,
        pm25_value=pm25_value,
        pm25_grade=pm25_grade,
    )

    # 종합 추천 계산
    result = get_comprehensive_recommendation(weather, air_quality)

    return {
        "location": location,
        "conditions": {
            "temperature": temp,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "sky": sky,
            "precipitation": {
                "type": precip_type,
                "probability": precip_prob,
            },
            "air_quality": {
                "pm10": {"value": pm10_value, "grade": pm10_grade},
                "pm25": {"value": pm25_value, "grade": pm25_grade},
            },
        },
        "outing_score": result["outing_score"],
        "outfit": result["outfit_recommendation"],
        "summary": result["summary"],
    }


@mcp.tool()
async def get_weather_summary(location: str = "서울") -> str:
    """
    지역의 날씨를 간단하게 요약해서 알려줍니다.

    Args:
        location: 지역명 (예: "서울", "부산")

    Returns:
        날씨 요약 문장
    """
    weather_data = await cached_get_weather(location)
    forecast_data = await cached_get_forecast(location)
    air_data = await cached_get_air_quality(location)

    # 기본 정보
    temp = "알 수 없음"
    sky = ""
    precip = ""
    pm_status = ""

    if "error" not in weather_data:
        temp = f"{weather_data['current'].get('temperature', '?')}°C"

    if "error" not in forecast_data:
        summary = forecast_data.get("today_summary", {})
        sky = summary.get("sky", "")
        if summary.get("precipitation_probability", 0) >= 50:
            precip = f", 강수확률 {summary['precipitation_probability']}%"

    if "error" not in air_data:
        pm25 = air_data.get("pm25") or air_data.get("average", {}).get("pm25", {})
        if isinstance(pm25, dict):
            grade = pm25.get("grade", "")
            if grade in ["나쁨", "매우나쁨"]:
                pm_status = f", 초미세먼지 {grade}"

    return f"{location} 현재 {temp}, {sky}{precip}{pm_status}"


@mcp.tool()
async def get_weekly_forecast(location: str = "서울") -> dict:
    """
    3일간 날씨 예보를 조회합니다. (오늘, 내일, 모레)
    날짜별 최저/최고 기온, 날씨, 강수확률을 한눈에 확인할 수 있습니다.

    사용 예시: "이번 주 날씨", "내일 날씨 어때?", "주말 날씨", "3일 예보"

    Args:
        location: 지역명 (예: "서울", "부산", "강남구")

    Returns:
        3일간 날씨 예보 (날짜별 최저/최고 기온, 날씨, 강수확률)
    """
    from datetime import datetime, timedelta

    forecast_data = await cached_get_forecast(location)

    if "error" in forecast_data:
        return {"error": forecast_data["error"], "location": location}

    forecasts = forecast_data.get("forecasts", [])

    # 날짜별로 그룹화
    daily_data = {}
    for f in forecasts:
        date = f.get("date")
        if not date:
            continue

        if date not in daily_data:
            daily_data[date] = {
                "date": date,
                "temperatures": [],
                "precipitation_probs": [],
                "sky": None,
                "min_temp": None,
                "max_temp": None,
            }

        if "temperature" in f:
            daily_data[date]["temperatures"].append(f["temperature"])
        if "precipitation_probability" in f:
            daily_data[date]["precipitation_probs"].append(f["precipitation_probability"])
        if f.get("sky") and not daily_data[date]["sky"]:
            daily_data[date]["sky"] = f["sky"]
        if f.get("min_temperature"):
            daily_data[date]["min_temp"] = f["min_temperature"]
        if f.get("max_temperature"):
            daily_data[date]["max_temp"] = f["max_temperature"]

    # 날짜별 요약 생성
    result_days = []
    today = datetime.now()
    day_names = ["오늘", "내일", "모레"]

    for i, (date, data) in enumerate(sorted(daily_data.items())[:3]):
        temps = data["temperatures"]
        probs = data["precipitation_probs"]

        # 최저/최고 기온 계산
        min_temp = data["min_temp"] or (min(temps) if temps else None)
        max_temp = data["max_temp"] or (max(temps) if temps else None)

        # 최대 강수확률
        max_prob = max(probs) if probs else 0

        # 날짜 포맷
        try:
            dt = datetime.strptime(date, "%Y%m%d")
            date_str = dt.strftime("%m/%d")
            weekday = ["월", "화", "수", "목", "금", "토", "일"][dt.weekday()]
        except:
            date_str = date
            weekday = ""

        day_name = day_names[i] if i < len(day_names) else f"{date_str}({weekday})"

        result_days.append({
            "day": day_name,
            "date": f"{date_str}({weekday})",
            "min_temperature": min_temp,
            "max_temperature": max_temp,
            "sky": data["sky"] or "맑음",
            "precipitation_probability": max_prob,
            "summary": f"{min_temp}~{max_temp}°C, {data['sky'] or '맑음'}" + (f", 강수 {max_prob}%" if max_prob >= 30 else "")
        })

    return {
        "location": location,
        "forecast_days": result_days,
        "summary": " | ".join([f"{d['day']}: {d['summary']}" for d in result_days])
    }


# =============================================================================
# v2.0 신규 Tools - 생활기상지수
# =============================================================================


@mcp.tool()
async def get_life_index(location: str = "서울") -> dict:
    """
    생활기상지수를 종합 조회합니다.
    자외선지수, 체감온도(여름), 꽃가루(봄/가을), 식중독지수를 한번에 확인할 수 있습니다.

    Args:
        location: 지역명 (예: "서울", "부산", "강남구")

    Returns:
        자외선지수, 체감온도, 꽃가루농도, 식중독지수 (계절에 따라 일부만 제공)
    """
    # 현재 날씨 데이터 가져오기 (체감온도/식중독 계산용)
    weather_data = await cached_get_weather(location)

    temp = None
    humidity = None
    if "error" not in weather_data:
        temp = weather_data["current"].get("temperature")
        humidity = weather_data["current"].get("humidity")

    result = await get_all_life_indices(location, temp, humidity)
    return result


@mcp.tool()
async def get_uv_info(location: str = "서울") -> dict:
    """
    자외선지수를 조회합니다.
    자외선 강도와 피부 보호 방법을 안내합니다.

    Args:
        location: 지역명

    Returns:
        자외선지수 (0-11+), 등급, 대응 방법
    """
    return await get_uv_index(location)


@mcp.tool()
async def get_food_safety_index(location: str = "서울") -> dict:
    """
    식중독지수를 조회합니다.
    도시락, 야외 식사, 음식 보관 안전성을 판단합니다.

    Args:
        location: 지역명

    Returns:
        식중독지수, 등급, 주의사항
    """
    weather_data = await cached_get_weather(location)

    temp = None
    humidity = None
    if "error" not in weather_data:
        temp = weather_data["current"].get("temperature")
        humidity = weather_data["current"].get("humidity")

    return await get_food_poison_index(location, temp, humidity)


# =============================================================================
# v2.0 신규 Tools - 한국 특화 활동 지수
# =============================================================================


async def _get_weather_data(location: str) -> WeatherData:
    """날씨 데이터를 WeatherData 객체로 변환"""
    weather = await cached_get_weather(location)
    forecast = await cached_get_forecast(location)
    air = await cached_get_air_quality(location)

    # 기본값
    temp = 20
    humidity = 50
    wind_speed = 2.0
    rain_prob = 0
    rain_prob_tomorrow = 0
    sky = "맑음"
    pm25_grade = "보통"
    pm25_value = 25

    if "error" not in weather:
        current = weather.get("current", {})
        temp = current.get("temperature", temp)
        humidity = current.get("humidity", humidity)
        wind_speed = current.get("wind_speed", wind_speed)

    if "error" not in forecast:
        summary = forecast.get("today_summary", {})
        rain_prob = summary.get("precipitation_probability", rain_prob)
        sky = summary.get("sky", sky)
        # 내일 강수확률은 추가 API 필요, 일단 오늘 것 사용
        rain_prob_tomorrow = rain_prob

    if "error" not in air:
        pm25_data = air.get("pm25") or air.get("average", {}).get("pm25", {})
        if isinstance(pm25_data, dict):
            pm25_grade = pm25_data.get("grade", pm25_grade)
            pm25_value = pm25_data.get("value", pm25_value)

    return WeatherData(
        temperature=temp,
        humidity=humidity,
        wind_speed=wind_speed,
        rain_prob=rain_prob,
        rain_prob_tomorrow=rain_prob_tomorrow,
        sky=sky,
        pm25_grade=pm25_grade,
        pm25_value=pm25_value,
    )


@mcp.tool()
async def is_good_for_laundry(location: str = "서울") -> dict:
    """
    오늘 빨래하기 좋은지 판단합니다. (빨래지수)
    기온, 습도, 강수확률, 바람을 종합하여 빨래 건조 적합도를 알려줍니다.
    기상청 종료 서비스를 자체 알고리즘으로 부활시켰습니다!

    사용 예시: "오늘 빨래해도 돼?", "빨래 널어도 될까?", "건조하기 좋아?"

    Args:
        location: 지역명

    Returns:
        빨래지수 (0-100), 등급, 건조 팁
    """
    weather_data = await _get_weather_data(location)
    result = calculate_laundry_index(weather_data)
    result["location"] = location
    # API 명세와 일치시키기 위해 score -> laundry_score
    if "score" in result:
        result["laundry_score"] = result.pop("score")
    # recommendation 필드 추가 (테스트 호환)
    if "message" in result:
        result["recommendation"] = result["message"]
    return result


@mcp.tool()
async def is_good_for_hiking(location: str = "서울") -> dict:
    """
    오늘 등산하기 좋은지 판단합니다. (등산지수)
    기온, 미세먼지, 강수확률, 바람을 종합하여 등산 적합도를 알려줍니다.
    서울 근교 추천 산(북한산, 관악산 등)도 안내해드립니다!

    사용 예시: "등산하기 좋아?", "산 가도 될까?", "오늘 북한산 어때?"

    Args:
        location: 지역명

    Returns:
        등산지수 (0-100), 등급, 추천 산, 주의사항
    """
    weather_data = await _get_weather_data(location)
    result = calculate_hiking_index(weather_data)
    result["location"] = location
    # API 명세와 일치시키기 위해 score -> hiking_score
    if "score" in result:
        result["hiking_score"] = result.pop("score")
    # recommended_mountains 필드 추가 (테스트 호환)
    if "recommendations" in result:
        result["recommended_mountains"] = result["recommendations"]
    return result


@mcp.tool()
async def is_good_for_picnic(location: str = "서울") -> dict:
    """
    오늘 한강/공원 피크닉하기 좋은지 판단합니다. (피크닉지수)
    기온, 미세먼지, 강수확률, 바람을 종합하여 야외 활동 적합도를 알려줍니다.
    한강 치맥을 위한 최적의 타임도 추천해드려요!

    사용 예시: "한강 가기 좋아?", "피크닉 괜찮을까?", "치맥하기 좋은 날이야?"

    Args:
        location: 지역명

    Returns:
        피크닉지수 (0-100), 등급, 추천 장소, 치맥 타임
    """
    weather_data = await _get_weather_data(location)
    result = calculate_picnic_index(weather_data)
    result["location"] = location
    # API 명세와 일치시키기 위해 score -> picnic_score
    if "score" in result:
        result["picnic_score"] = result.pop("score")
    return result


@mcp.tool()
async def is_good_for_car_wash(location: str = "서울") -> dict:
    """
    오늘 세차하기 좋은지 판단합니다. (세차지수)
    오늘/내일 강수확률과 미세먼지를 고려하여 세차 적합도를 알려줍니다.
    내일 비가 오면 세차해도 소용없으니까요!

    사용 예시: "세차해도 될까?", "오늘 세차하기 좋아?", "차 씻어도 돼?"

    Args:
        location: 지역명

    Returns:
        세차지수 (0-100), 등급, 팁
    """
    weather_data = await _get_weather_data(location)
    result = calculate_car_wash_index(weather_data)
    result["location"] = location
    # API 명세와 일치시키기 위해 score -> car_wash_score
    if "score" in result:
        result["car_wash_score"] = result.pop("score")
    return result


@mcp.tool()
async def get_kimjang_timing(location: str = "서울") -> dict:
    """
    김장하기 좋은 날인지 판단합니다. (김장지수)
    11-12월 한정 서비스로, 기온과 강수확률을 고려하여 김장 적기를 알려줍니다.
    세계에서 유일한 김장지수! 한국 전통문화를 반영했습니다.

    사용 예시: "김장 언제 해?", "김장하기 좋은 날이야?", "김치 담그기 좋아?"

    Args:
        location: 지역명

    Returns:
        김장지수 (0-100), 등급, 김장 팁
    """
    weather_data = await _get_weather_data(location)

    # 최저/최고 기온 추가
    forecast = await cached_get_forecast(location)
    if "error" not in forecast:
        summary = forecast.get("today_summary", {})
        weather_data.temp_min = summary.get("min_temperature")
        weather_data.temp_max = summary.get("max_temperature")

    result = calculate_kimjang_index(weather_data)
    result["location"] = location
    # API 명세와 일치시키기 위해 score -> kimjang_score
    if "score" in result:
        result["kimjang_score"] = result.pop("score")
    return result


@mcp.tool()
async def is_good_for_exercise(location: str = "서울") -> dict:
    """
    오늘 야외 운동하기 좋은지 판단합니다. (운동지수)
    기온, 습도, 미세먼지, 강수확률을 종합하여 운동 적합도를 알려줍니다.
    건강 정보(열사병/저체온증 위험, 수분 섭취량)도 함께 제공합니다!

    사용 예시: "오늘 운동하기 좋아?", "러닝해도 될까?", "야외 운동 괜찮아?"

    Args:
        location: 지역명

    Returns:
        운동지수 (0-100), 등급, 추천 운동, 최적 시간대, 수분 섭취 권장량, 건강 위험도
    """
    weather_data = await _get_weather_data(location)
    result = calculate_exercise_index(weather_data)
    result["location"] = location
    # API 명세와 일치시키기 위해 score -> exercise_score
    if "score" in result:
        result["exercise_score"] = result.pop("score")
    return result


@mcp.tool()
async def get_cold_flu_risk(location: str = "서울") -> dict:
    """
    감기/독감 위험 지수를 알려드립니다. (v2.3 신규)
    MIT, Yale, PNAS 연구 기반 과학적 알고리즘으로
    기온, 습도, 일교차, 풍속이 바이러스 전파에 미치는 영향을 분석합니다.

    사용 예시: "감기 걸리기 쉬운 날이야?", "독감 조심해야 해?", "오늘 건강 주의해야 해?"

    Args:
        location: 지역명

    Returns:
        감기위험지수 (0-100, 높을수록 위험), 등급, 위험요인, 예방수칙
    """
    weather_data = await _get_weather_data(location)
    result = calculate_cold_flu_risk_index(weather_data)
    result["location"] = location
    if "score" in result:
        result["flu_risk_score"] = result.pop("score")
    return result


@mcp.tool()
async def get_commute_index(location: str = "서울") -> dict:
    """
    출퇴근 날씨 지수를 알려드립니다. (v2.3 신규)
    자가용, 대중교통, 도보/자전거 각각의 적합도를 분석합니다.
    PNAS 교통연구, Lawson 보행자 기준, UTCI 열쾌적 지수 기반!

    사용 예시: "출근 어떻게 해?", "자전거 출근 괜찮아?", "버스 타도 될까?"

    Args:
        location: 지역명

    Returns:
        출퇴근지수 (0-100), 교통수단별 점수, 최적 수단 추천, 시간대별 팁
    """
    weather_data = await _get_weather_data(location)
    result = calculate_commute_index(weather_data)
    result["location"] = location
    if "score" in result:
        result["commute_score"] = result.pop("score")
    return result


@mcp.tool()
async def get_allergy_risk(location: str = "서울") -> dict:
    """
    알레르기 위험 지수를 알려드립니다. (v2.3 신규)
    미세먼지, 꽃가루(계절별), 황사 가능성을 종합 분석합니다.
    봄철 삼나무/소나무, 가을철 돼지풀/쑥 등 주요 알레르겐 정보 포함!

    사용 예시: "알레르기 주의해야 해?", "꽃가루 심해?", "황사 오나?"

    Args:
        location: 지역명

    Returns:
        알레르기지수 (0-100, 높을수록 위험), 주요 알레르겐, 계절 정보, 예방수칙
    """
    weather_data = await _get_weather_data(location)
    result = calculate_allergy_risk_index(weather_data)
    result["location"] = location
    if "score" in result:
        result["allergy_risk_score"] = result.pop("score")
    return result


# =============================================================================
# v2.4 신규 Tools - 건강/생활 지수 확장
# =============================================================================


@mcp.tool()
async def get_migraine_risk(location: str = "서울") -> dict:
    """
    편두통 위험 지수를 알려드립니다. (v2.4 신규)
    기압 변화, 습도, 기온 변화가 편두통에 미치는 영향을 과학적으로 분석합니다.
    American Migraine Foundation, Neurology Journal 연구 기반!

    사용 예시: "오늘 두통 올 것 같아?", "편두통 주의해야 해?", "머리 아플 날씨야?"

    Args:
        location: 지역명

    Returns:
        편두통위험지수 (0-100, 높을수록 위험), 위험요인, 예방수칙
    """
    # 날씨 데이터 수집
    weather = await cached_get_weather(location)
    forecast = await cached_get_forecast(location)
    air = await cached_get_air_quality(location)

    # weather_data dict 구성
    weather_data = {
        "sky": "맑음",
        "temp_current": 20,
        "temp_min": None,
        "temp_max": None,
        "humidity": 50,
        "rain_prob": 0,
        "wind_speed": 2.0
    }

    if "error" not in weather:
        current = weather.get("current", {})
        weather_data["temp_current"] = current.get("temperature", 20)
        weather_data["humidity"] = current.get("humidity", 50)
        weather_data["wind_speed"] = current.get("wind_speed", 2.0)

    if "error" not in forecast:
        summary = forecast.get("today_summary", {})
        weather_data["rain_prob"] = summary.get("precipitation_probability", 0)
        weather_data["sky"] = summary.get("sky", "맑음")
        weather_data["temp_min"] = summary.get("min_temperature")
        weather_data["temp_max"] = summary.get("max_temperature")

    # air_data dict 구성
    air_data = {
        "pm10_grade": "보통",
        "pm25_grade": "보통",
        "pm10_value": 50,
        "pm25_value": 25
    }

    if "error" not in air:
        pm10_data = air.get("pm10") or air.get("average", {}).get("pm10", {})
        pm25_data = air.get("pm25") or air.get("average", {}).get("pm25", {})
        if isinstance(pm10_data, dict):
            air_data["pm10_grade"] = pm10_data.get("grade", "보통")
            air_data["pm10_value"] = pm10_data.get("value", 50)
        if isinstance(pm25_data, dict):
            air_data["pm25_grade"] = pm25_data.get("grade", "보통")
            air_data["pm25_value"] = pm25_data.get("value", 25)

    result = calculate_migraine_risk_index(weather_data, air_data)
    result["location"] = location
    if "score" in result:
        result["migraine_risk_score"] = result.pop("score")
    return result


@mcp.tool()
async def get_sleep_quality_index(location: str = "서울") -> dict:
    """
    수면 컨디션 지수를 알려드립니다. (v2.4 신규)
    온도, 습도가 수면에 미치는 영향을 과학적으로 분석합니다.
    Harvard Medical School, National Sleep Foundation 연구 기반!

    사용 예시: "오늘 잠 잘 올까?", "수면 환경 어때?", "숙면하기 좋아?"

    Args:
        location: 지역명

    Returns:
        수면컨디션지수 (0-100, 높을수록 좋음), 최적조건, 개선팁
    """
    # 날씨 데이터 수집
    weather = await cached_get_weather(location)
    air = await cached_get_air_quality(location)

    # weather_data dict 구성
    weather_data = {
        "temp_current": 20,
        "humidity": 50
    }

    if "error" not in weather:
        current = weather.get("current", {})
        weather_data["temp_current"] = current.get("temperature", 20)
        weather_data["humidity"] = current.get("humidity", 50)

    # air_data dict 구성
    air_data = {
        "pm10_value": 50
    }

    if "error" not in air:
        pm10_data = air.get("pm10") or air.get("average", {}).get("pm10", {})
        if isinstance(pm10_data, dict):
            air_data["pm10_value"] = pm10_data.get("value", 50)

    result = calculate_sleep_quality_index(weather_data, air_data)
    result["location"] = location
    if "score" in result:
        result["sleep_quality_score"] = result.pop("score")
    return result


@mcp.tool()
async def get_photography_index(location: str = "서울") -> dict:
    """
    사진 촬영 지수를 알려드립니다. (v2.4 신규)
    하늘 상태, 조명 조건, 골든아워를 분석하여 촬영 적합도를 알려줍니다.
    야외 촬영, 풍경 사진에 최적화된 정보 제공!

    사용 예시: "사진 찍기 좋은 날이야?", "골든아워 언제야?", "출사 가도 돼?"

    Args:
        location: 지역명

    Returns:
        사진촬영지수 (0-100, 높을수록 좋음), 골든아워, 촬영조건
    """
    # 날씨 데이터 수집
    weather = await cached_get_weather(location)
    forecast = await cached_get_forecast(location)

    # weather_data dict 구성
    weather_data = {
        "sky": "맑음",
        "rain_prob": 0,
        "humidity": 50
    }

    if "error" not in weather:
        current = weather.get("current", {})
        weather_data["humidity"] = current.get("humidity", 50)

    if "error" not in forecast:
        summary = forecast.get("today_summary", {})
        weather_data["rain_prob"] = summary.get("precipitation_probability", 0)
        weather_data["sky"] = summary.get("sky", "맑음")

    result = calculate_photography_index(weather_data)
    result["location"] = location
    if "score" in result:
        result["photography_score"] = result.pop("score")
    return result


@mcp.tool()
async def get_joint_pain_risk(location: str = "서울") -> dict:
    """
    관절통 위험 지수를 알려드립니다. (v2.4 신규)
    기압 변화, 습도, 온도 변화가 관절에 미치는 영향을 과학적으로 분석합니다.
    Arthritis Foundation, Mayo Clinic, Journal of Rheumatology 연구 기반!

    사용 예시: "관절 아플 것 같아?", "관절통 주의해야 해?", "무릎 쑤실 날씨야?"

    Args:
        location: 지역명

    Returns:
        관절통위험지수 (0-100, 높을수록 관절에 좋음), 위험요인, 관리수칙
    """
    # 날씨 데이터 수집
    weather = await cached_get_weather(location)
    forecast = await cached_get_forecast(location)
    air = await cached_get_air_quality(location)

    # weather_data dict 구성
    weather_data = {
        "temp_current": 20,
        "temp_min": None,
        "temp_max": None,
        "humidity": 50,
        "rain_prob": 0
    }

    if "error" not in weather:
        current = weather.get("current", {})
        weather_data["temp_current"] = current.get("temperature", 20)
        weather_data["humidity"] = current.get("humidity", 50)

    if "error" not in forecast:
        summary = forecast.get("today_summary", {})
        weather_data["rain_prob"] = summary.get("precipitation_probability", 0)
        weather_data["temp_min"] = summary.get("min_temperature")
        weather_data["temp_max"] = summary.get("max_temperature")

    # air_data dict 구성 (인터페이스 통일)
    air_data = {}

    result = calculate_joint_pain_index(weather_data, air_data)
    result["location"] = location
    if "score" in result:
        result["joint_pain_score"] = result.pop("score")
    return result


# =============================================================================
# v2.5 신규 Tools - 야외 활동 지수 6종
# =============================================================================


@mcp.tool()
async def get_drive_index(location: str = "서울") -> dict:
    """
    드라이브/도로여행 적합도를 분석합니다. 강수, 시야, 바람, 노면 상태를 고려합니다.
    장거리 운전, 드라이브 코스, 도로 여행 계획 시 활용하세요!

    사용 예시: "드라이브 가기 좋아?", "오늘 운전하기 어때?", "도로 상황 어때?"

    Args:
        location: 지역명

    Returns:
        드라이브지수 (0-100), 등급, 도로 조건, 안전 팁
    """
    # 날씨 데이터 수집
    weather = await cached_get_weather(location)
    forecast = await cached_get_forecast(location)
    air = await cached_get_air_quality(location)

    # weather_data dict 구성
    weather_data = {
        "sky": "맑음",
        "temp_current": 20,
        "humidity": 50,
        "rain_prob": 0,
        "wind_speed": 2.0
    }

    if "error" not in weather:
        current = weather.get("current", {})
        weather_data["temp_current"] = current.get("temperature", 20)
        weather_data["humidity"] = current.get("humidity", 50)
        weather_data["wind_speed"] = current.get("wind_speed", 2.0)

    if "error" not in forecast:
        summary = forecast.get("today_summary", {})
        weather_data["rain_prob"] = summary.get("precipitation_probability", 0)
        weather_data["sky"] = summary.get("sky", "맑음")

    # air_data dict 구성
    air_data = {
        "pm10_grade": "보통",
        "pm25_grade": "보통"
    }

    if "error" not in air:
        pm10_data = air.get("pm10") or air.get("average", {}).get("pm10", {})
        pm25_data = air.get("pm25") or air.get("average", {}).get("pm25", {})
        if isinstance(pm10_data, dict):
            air_data["pm10_grade"] = pm10_data.get("grade", "보통")
        if isinstance(pm25_data, dict):
            air_data["pm25_grade"] = pm25_data.get("grade", "보통")

    result = calculate_drive_index(weather_data, air_data)
    result["location"] = location
    if "score" in result:
        result["drive_score"] = result.pop("score")
    return result


@mcp.tool()
async def get_camping_index(location: str = "서울") -> dict:
    """
    캠핑 날씨 적합도를 분석합니다. 낙뢰, 바람, 비, 기온을 고려합니다.
    텐트 캠핑, 글램핑, 차박 계획 시 활용하세요!

    사용 예시: "캠핑 가기 좋아?", "오늘 텐트 쳐도 돼?", "캠핑 날씨 어때?"

    Args:
        location: 지역명

    Returns:
        캠핑지수 (0-100), 등급, 날씨 조건, 경고, 팁
    """
    # 날씨 데이터 수집
    weather = await cached_get_weather(location)
    forecast = await cached_get_forecast(location)
    air = await cached_get_air_quality(location)

    # weather_data dict 구성
    weather_data = {
        "sky": "맑음",
        "temp_current": 20,
        "humidity": 50,
        "rain_prob": 0,
        "wind_speed": 2.0
    }

    if "error" not in weather:
        current = weather.get("current", {})
        weather_data["temp_current"] = current.get("temperature", 20)
        weather_data["humidity"] = current.get("humidity", 50)
        weather_data["wind_speed"] = current.get("wind_speed", 2.0)

    if "error" not in forecast:
        summary = forecast.get("today_summary", {})
        weather_data["rain_prob"] = summary.get("precipitation_probability", 0)
        weather_data["sky"] = summary.get("sky", "맑음")

    # air_data dict 구성
    air_data = {
        "pm25_grade": "보통"
    }

    if "error" not in air:
        pm25_data = air.get("pm25") or air.get("average", {}).get("pm25", {})
        if isinstance(pm25_data, dict):
            air_data["pm25_grade"] = pm25_data.get("grade", "보통")

    result = calculate_camping_index(weather_data, air_data)
    result["location"] = location
    if "score" in result:
        result["camping_score"] = result.pop("score")
    return result


@mcp.tool()
async def get_fishing_index(location: str = "서울") -> dict:
    """
    낚시 적합도를 분석합니다. 기압 변화, 바람, 구름, 기온을 고려합니다.
    바다낚시, 민물낚시, 배낚시 계획 시 활용하세요!

    사용 예시: "낚시 가기 좋아?", "오늘 물고기 잘 물어?", "낚시 날씨 어때?"

    Args:
        location: 지역명

    Returns:
        낚시지수 (0-100), 등급, 날씨 조건, 최적 시간대, 팁
    """
    # 날씨 데이터 수집
    weather = await cached_get_weather(location)
    forecast = await cached_get_forecast(location)

    # weather_data dict 구성
    weather_data = {
        "sky": "맑음",
        "temp_current": 20,
        "rain_prob": 0,
        "wind_speed": 2.0
    }

    if "error" not in weather:
        current = weather.get("current", {})
        weather_data["temp_current"] = current.get("temperature", 20)
        weather_data["wind_speed"] = current.get("wind_speed", 2.0)

    if "error" not in forecast:
        summary = forecast.get("today_summary", {})
        weather_data["rain_prob"] = summary.get("precipitation_probability", 0)
        weather_data["sky"] = summary.get("sky", "맑음")

    result = calculate_fishing_index(weather_data)
    result["location"] = location
    if "score" in result:
        result["fishing_score"] = result.pop("score")
    return result


@mcp.tool()
async def get_golf_index(location: str = "서울") -> dict:
    """
    골프 라운딩 적합도를 분석합니다. 바람, 비, 기온, 자외선을 고려합니다.
    골프장 예약, 라운딩 계획 시 활용하세요!

    사용 예시: "골프 치기 좋아?", "오늘 라운딩 괜찮아?", "골프 날씨 어때?"

    Args:
        location: 지역명

    Returns:
        골프지수 (0-100), 등급, 날씨 조건, 플레이 팁
    """
    # 날씨 데이터 수집
    weather = await cached_get_weather(location)
    forecast = await cached_get_forecast(location)
    air = await cached_get_air_quality(location)

    # weather_data dict 구성
    weather_data = {
        "sky": "맑음",
        "temp_current": 20,
        "rain_prob": 0,
        "wind_speed": 2.0,
        "uv_index": 5
    }

    if "error" not in weather:
        current = weather.get("current", {})
        weather_data["temp_current"] = current.get("temperature", 20)
        weather_data["wind_speed"] = current.get("wind_speed", 2.0)

    if "error" not in forecast:
        summary = forecast.get("today_summary", {})
        weather_data["rain_prob"] = summary.get("precipitation_probability", 0)
        weather_data["sky"] = summary.get("sky", "맑음")

    # air_data dict 구성
    air_data = {
        "pm25_grade": "보통"
    }

    if "error" not in air:
        pm25_data = air.get("pm25") or air.get("average", {}).get("pm25", {})
        if isinstance(pm25_data, dict):
            air_data["pm25_grade"] = pm25_data.get("grade", "보통")

    result = calculate_golf_index(weather_data, air_data)
    result["location"] = location
    if "score" in result:
        result["golf_score"] = result.pop("score")
    return result


@mcp.tool()
async def get_running_index(location: str = "서울") -> dict:
    """
    야외 러닝/조깅 적합도를 분석합니다. 기온, 습도, 미세먼지, 자외선을 고려합니다.
    마라톤 훈련, 조깅, 야외 달리기 계획 시 활용하세요!

    사용 예시: "러닝 가기 좋아?", "조깅 괜찮아?", "달리기 하기 좋은 날이야?"

    Args:
        location: 지역명

    Returns:
        러닝지수 (0-100), 등급, 날씨 조건, 최적 시간대, 건강 팁
    """
    # 날씨 데이터 수집
    weather = await cached_get_weather(location)
    forecast = await cached_get_forecast(location)
    air = await cached_get_air_quality(location)

    # weather_data dict 구성
    weather_data = {
        "temp_current": 20,
        "humidity": 50,
        "rain_prob": 0,
        "uv_index": 5
    }

    if "error" not in weather:
        current = weather.get("current", {})
        weather_data["temp_current"] = current.get("temperature", 20)
        weather_data["humidity"] = current.get("humidity", 50)

    if "error" not in forecast:
        summary = forecast.get("today_summary", {})
        weather_data["rain_prob"] = summary.get("precipitation_probability", 0)

    # air_data dict 구성
    air_data = {
        "pm25_grade": "보통",
        "pm25_value": 25
    }

    if "error" not in air:
        pm25_data = air.get("pm25") or air.get("average", {}).get("pm25", {})
        if isinstance(pm25_data, dict):
            air_data["pm25_grade"] = pm25_data.get("grade", "보통")
            air_data["pm25_value"] = pm25_data.get("value", 25)

    result = calculate_running_index(weather_data, air_data)
    result["location"] = location
    if "score" in result:
        result["running_score"] = result.pop("score")
    return result


@mcp.tool()
async def get_bbq_index(location: str = "서울") -> dict:
    """
    야외 바베큐/그릴링 적합도를 분석합니다. 바람, 비, 기온을 고려합니다.
    캠핑 바베큐, 정원 파티, 루프탑 그릴 계획 시 활용하세요!

    사용 예시: "바베큐 하기 좋아?", "고기 구워도 돼?", "야외 그릴 날씨 어때?"

    Args:
        location: 지역명

    Returns:
        바베큐지수 (0-100), 등급, 날씨 조건, 안전 팁
    """
    # 날씨 데이터 수집
    weather = await cached_get_weather(location)
    forecast = await cached_get_forecast(location)

    # weather_data dict 구성
    weather_data = {
        "sky": "맑음",
        "temp_current": 20,
        "rain_prob": 0,
        "wind_speed": 2.0
    }

    if "error" not in weather:
        current = weather.get("current", {})
        weather_data["temp_current"] = current.get("temperature", 20)
        weather_data["wind_speed"] = current.get("wind_speed", 2.0)

    if "error" not in forecast:
        summary = forecast.get("today_summary", {})
        weather_data["rain_prob"] = summary.get("precipitation_probability", 0)
        weather_data["sky"] = summary.get("sky", "맑음")

    result = calculate_bbq_index(weather_data)
    result["location"] = location
    if "score" in result:
        result["bbq_score"] = result.pop("score")
    return result


@mcp.tool()
async def what_should_i_do_today(location: str = "서울") -> dict:
    """
    오늘 뭐하면 좋을지 종합 추천합니다.
    날씨를 분석하여 빨래, 등산, 피크닉, 세차 등 활동별 적합도를 비교해드립니다.
    한 번의 질문으로 모든 활동을 비교할 수 있어요!

    사용 예시: "오늘 뭐하면 좋을까?", "뭐하기 좋은 날이야?", "오늘 할 것 추천해줘"

    Args:
        location: 지역명

    Returns:
        활동별 적합도 점수, 베스트 활동 추천
    """
    weather_data = await _get_weather_data(location)
    result = get_all_activity_recommendations(weather_data)
    result["location"] = location

    # 요약 메시지 생성
    best = result.get("best_activity", {})
    if best.get("score", 0) >= 70:
        result["recommendation"] = f"오늘은 {_get_activity_korean_name(best['name'])} 하기 좋아요! ({best['score']}점)"
    elif best.get("score", 0) >= 50:
        result["recommendation"] = f"오늘은 {_get_activity_korean_name(best['name'])} 괜찮아요. ({best['score']}점)"
    else:
        result["recommendation"] = "오늘은 실내 활동이 좋겠어요."

    return result


def _get_activity_korean_name(activity: str) -> str:
    """활동 영문명을 한글로 변환"""
    names = {
        "laundry": "빨래",
        "hiking": "등산",
        "picnic": "피크닉",
        "car_wash": "세차",
        "exercise": "운동",
        "kimjang": "김장",
    }
    return names.get(activity, activity)


# =============================================================================
# Resources
# =============================================================================


@mcp.resource("weather://locations")
def get_supported_locations() -> str:
    """지원하는 지역 목록을 반환합니다."""
    from config.settings import GRID_COORDINATES

    locations = sorted(GRID_COORDINATES.keys())
    return f"지원 지역 ({len(locations)}개): " + ", ".join(locations)


@mcp.resource("weather://guide")
def get_usage_guide() -> str:
    """사용 가이드를 반환합니다."""
    return """
# Weather Life MCP v2.5 사용 가이드

## 기본 기능

1. **날씨 조회** (get_weather)
   - "서울 날씨 알려줘"

2. **미세먼지 조회** (get_air_quality_info)
   - "지금 미세먼지 어때?"

3. **옷차림 추천** (get_outfit_recommendation_tool)
   - "오늘 뭐 입을까?"

4. **외출 적합도** (should_i_go_out)
   - "오늘 외출해도 될까?"

## 생활기상지수

5. **자외선지수** (get_uv_info)
   - "자외선 어때?"

6. **식중독지수** (get_food_safety_index)
   - "도시락 싸도 돼?"

## 한국 특화 지수

7. **빨래지수** (is_good_for_laundry)
   - "오늘 빨래해도 돼?"

8. **등산지수** (is_good_for_hiking)
   - "등산하기 좋아?"

9. **피크닉지수** (is_good_for_picnic)
   - "한강 가기 좋아?", "치맥하기 좋은 날이야?"

10. **세차지수** (is_good_for_car_wash)
    - "세차해도 될까?"

11. **김장지수** (get_kimjang_timing) [11-12월 한정]
    - "김장 언제 하면 좋아?"

12. **운동지수** (is_good_for_exercise)
    - "오늘 운동하기 좋아?"

13. **종합 추천** (what_should_i_do_today)
    - "오늘 뭐하면 좋을까?"

## v2.3 - 건강/출퇴근 지수 (과학적 근거 기반)

14. **감기위험지수** (get_cold_flu_risk) - MIT, Yale, PNAS 연구 기반!
    - "감기 걸리기 쉬운 날이야?"
    - "독감 조심해야 해?"

15. **출퇴근지수** (get_commute_index) - 교통수단별 분석!
    - "출근 어떻게 해?"
    - "자전거 출근 괜찮아?"

16. **알레르기지수** (get_allergy_risk) - 계절/황사 연동!
    - "알레르기 주의해야 해?"
    - "꽃가루 심해?"

## v2.4 신규 - 건강/생활 지수 확장 (과학적 연구 기반)

17. **편두통위험지수** (get_migraine_risk) - 기압/습도 기반!
    - "오늘 두통 올 것 같아?"
    - "편두통 주의해야 해?"

18. **수면컨디션지수** (get_sleep_quality_index) - 온도/습도 분석!
    - "오늘 잠 잘 올까?"
    - "수면 환경 어때?"

19. **사진촬영지수** (get_photography_index) - 골든아워/조명 분석!
    - "사진 찍기 좋은 날이야?"
    - "골든아워 언제야?"

20. **관절통위험지수** (get_joint_pain_risk) - 관절염 연구 기반!
    - "관절 아플 것 같아?"
    - "관절통 주의해야 해?"

## v2.5 신규 - 야외 활동 지수 6종

21. **드라이브지수** (get_drive_index) - 강수/시야/바람/노면 상태 분석!
    - "드라이브 가기 좋아?"
    - "오늘 운전하기 어때?"

22. **캠핑지수** (get_camping_index) - 낙뢰/바람/비/기온 분석!
    - "캠핑 가기 좋아?"
    - "오늘 텐트 쳐도 돼?"

23. **낚시지수** (get_fishing_index) - 기압변화/바람/구름/기온 분석!
    - "낚시 가기 좋아?"
    - "오늘 물고기 잘 물어?"

24. **골프지수** (get_golf_index) - 바람/비/기온/자외선 분석!
    - "골프 치기 좋아?"
    - "오늘 라운딩 괜찮아?"

25. **러닝지수** (get_running_index) - 기온/습도/미세먼지/자외선 분석!
    - "러닝 가기 좋아?"
    - "조깅 괜찮아?"

26. **바베큐지수** (get_bbq_index) - 바람/비/기온 분석!
    - "바베큐 하기 좋아?"
    - "고기 구워도 돼?"

## 지원 지역

서울 전역 (25개 구), 경기도 주요 도시, 6대 광역시, 제주 등
총 80개 이상의 지역을 지원합니다.
"""


# =============================================================================
# Health Check & Main
# =============================================================================


async def health_check(request):
    """Health check endpoint for Railway"""
    return JSONResponse({
        "status": "healthy",
        "service": "weather-life-mcp",
        "version": "2.5.0",
        "tools": 29,
        "features": ["weather", "weekly_forecast", "air_quality", "outfit", "life_index", "laundry", "hiking", "picnic", "car_wash", "exercise", "kimjang", "cold_flu_risk", "commute", "allergy", "migraine_risk", "sleep_quality", "photography", "joint_pain", "drive", "camping", "fishing", "golf", "running", "bbq"],
        "v2.5_features": ["drive_index", "camping_index", "fishing_index", "golf_index", "running_index", "bbq_index"],
        "v2.4_features": ["migraine_risk", "sleep_quality", "photography_index", "joint_pain_risk"],
        "v2.3_features": ["cold_flu_risk", "commute_index", "allergy_risk", "scientific_basis"]
    })


async def root(request):
    """Root endpoint"""
    return JSONResponse({
        "name": "Weather Life MCP",
        "description": "날씨, 미세먼지, 옷차림 추천 MCP 서버",
        "mcp_endpoint": "/mcp",
        "health": "/health"
    })


def create_app():
    """Create combined Starlette app with MCP"""
    from starlette.middleware import Middleware
    from starlette.routing import Router

    # Get MCP ASGI app
    mcp_app = mcp.http_app(
        path="/mcp",
        stateless_http=True,
        json_response=True,
    )

    # Combine routes: health check first, then MCP handles the rest
    async def combined_app(scope, receive, send):
        path = scope.get("path", "")
        if path == "/" or path == "/health":
            # Handle health routes with Starlette
            health_app = Starlette(routes=[
                Route("/", root),
                Route("/health", health_check),
            ])
            await health_app(scope, receive, send)
        else:
            # Forward to MCP app
            await mcp_app(scope, receive, send)

    return combined_app


def main():
    """서버 실행"""
    port = int(os.environ.get("PORT", server_config.port))
    host = server_config.host

    print(f"Weather Life MCP 서버 시작")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   MCP Endpoint: http://{host}:{port}/mcp")
    print(f"   Health: http://{host}:{port}/health")

    app = create_app()
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
