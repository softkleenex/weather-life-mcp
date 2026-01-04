"""
Weather Life MCP 서버 v3.7
날씨 + 미세먼지 + 생활 도우미 + 한국 특화 + 건강 + 지도 MCP

PlayMCP 공모전 (MCP Player 10) 출품작

v3.7 신규 기능 (스마트 분석):
- 최적 시간대 분석 (get_best_time_for_activity) - "언제 나가면 좋을까?"
- 활동 비교 (compare_activities) - "캠핑 vs 피크닉" 승자 결정
- 28개 → 30개 도구로 확장

v3.6 신규 기능 (실용성 기반 최적화):
- 저사용 도구 제거로 32개 → 28개 최적화
- 김장지수 제거 (11-12월만 사용)
- 러닝지수 제거 (운동지수로 대체)
- 바베큐지수 제거 (피크닉지수로 대체)
- 드라이브지수 제거 (외출적합도로 대체)

v3.5 신규 기능 (도구 통합 최적화):
- 중복 도구 제거로 38개 → 32개 최적화
- get_smart_course로 코스/일정 기능 통합
- get_place_recommendation으로 장소 추천 통합

v3.4 신규 기능 (장소 정보 강화 + 옷차림 세분화):
- 장소 추천 이유 제공 (why_recommend)
- 이동 방법 힌트 (how_to_get_there)
- 알아야 할 것/팁 (notice, tip)
- TPO별 옷차림 (출근/데이트/운동/캐주얼)
- 날씨별 색상 추천

v3.3 신규 기능 (날씨 연동 코스 추천):
- 날씨 기반 코스 추천 (get_smart_course) - 비 오면 실내, 맑으면 야외
- 장소 URL 강조 - 모든 결과에 카카오맵 링크 명확 표시

v3.2 신규 기능 (전국 지원 + 상황별 추천):
- 전국 동적 좌표 조회 (Kakao Geocoding API)
- 상황별 장소 추천 (get_place_recommendation) - 혼자/친구/데이트/가족/비즈니스
- 시간대별 맞춤 추천 - 아침/점심/오후/저녁/심야 자동 감지
- 자연어 추천 (whats_good_here) - "여기서 뭐하면 좋아?"

v3.1 신규 기능 (Kakao Maps API 연동):
- 주변 장소 검색 (search_nearby_places) - 전국 어디든!
- 길찾기 링크 (get_directions_link) - 자동차/대중교통/도보/자전거
- 맛집 검색 (search_restaurant) - 지역별/음식종류별 검색

v3.0 신규 기능 (장소 추천 시스템):
- 데이트 코스 추천 (날씨 기반)
- 활동별 추천 장소 (등산/캠핑/드라이브 등)
- 80개+ 한국 명소 데이터베이스

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
    # v3.0 신규
    calculate_date_course,
    get_activity_spots,
)
from src.kakao_map_api import (
    search_place_by_keyword,
    search_place_by_category,
    geocode,
    get_directions_url,
    get_location_coordinates,
    get_location_coordinates_async,
    get_smart_recommendation,
    get_weather_based_course,
    CATEGORY_CODES,
    SITUATION_CATEGORIES,
    TIME_RECOMMENDATIONS,
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
        "data_source": {
            "provider": "기상청 단기예보 API",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "reliability": "공공데이터포털 인증 API"
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
    situation: str = "",
) -> dict:
    """
    날씨에 맞는 옷차림을 추천합니다! (v3.4 TPO별/색상별 세분화)

    사용 예시:
    - "오늘 뭐 입지?"
    - "데이트할 때 뭐 입을까?"
    - "출근할 때 옷 추천해줘"
    - "운동하러 갈 때 옷차림"

    Args:
        location: 지역명 (예: "서울", "부산")
        temperature: 직접 기온을 입력할 경우 (선택사항)
        situation: 상황 (출근, 데이트, 운동, 캐주얼) - 비어있으면 일반 추천

    Returns:
        기온별/TPO별/색상별 옷차림 추천
    """
    # 실시간 날씨 조회
    weather_data = await cached_get_weather(location)

    if temperature is None:
        if "error" in weather_data:
            return {"error": weather_data["error"]}
        temperature = weather_data["current"].get("temperature", 20)

    # 날씨 조건 구성 (색상 추천을 위해 하늘상태 포함)
    sky = ""
    precip_type = "없음"
    humidity = 50
    wind_speed = 0

    if "error" not in weather_data:
        current = weather_data.get("current", {})
        sky = current.get("sky", "")
        precip_type = current.get("precipitation_type", "없음")
        humidity = current.get("humidity", 50)
        wind_speed = current.get("wind_speed", 0)

    weather = WeatherCondition(
        temperature=temperature,
        sky=sky,
        precipitation_type=precip_type,
        humidity=humidity,
        wind_speed=wind_speed,
    )

    # TPO 매핑
    tpo_map = {
        "출근": "출근", "회사": "출근",
        "데이트": "데이트", "만남": "데이트",
        "운동": "운동", "헬스": "운동",
        "캐주얼": "캐주얼", "일상": "캐주얼", "편한": "캐주얼",
    }
    tpo = tpo_map.get(situation, situation) if situation else ""

    recommendation = get_outfit_recommendation(weather, tpo)

    return {
        "location": location,
        "temperature": temperature,
        "category": recommendation["category"],
        "outfit": recommendation["recommendation"],
        "tip": recommendation["tip"],

        # v3.4 세분화
        "colors": recommendation.get("colors", {}),
        "by_situation": recommendation.get("by_situation", {}),
        "your_situation": recommendation.get("your_situation"),
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


# get_weather_summary 제거됨 - get_weather 사용 권장 (v3.4)


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


# get_life_index 제거됨 - 개별 지수 도구(get_uv_info 등) 사용 권장 (v3.4)


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
        빨래지수 (0-100), 등급, 건조 팁, 점수산출기준
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
    # 데이터 출처 및 업데이트 시간 추가
    result["data_source"] = {
        "weather": "기상청 단기예보 API",
        "air_quality": "에어코리아 대기오염정보 API",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "note": "실시간 데이터 기반 (1시간 내 갱신)"
    }
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


# 김장지수 제거됨 - 11-12월만 사용 가능하여 실용성 낮음 (v3.5)


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


# 드라이브지수 제거됨 - should_i_go_out(외출적합도)로 대체 (v3.6)


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


# 러닝지수 제거됨 - is_good_for_exercise로 대체 (v3.6)


# 바베큐지수 제거됨 - is_good_for_picnic으로 대체 (v3.6)


# what_should_i_do_today 제거됨 - get_smart_course 또는 개별 활동지수 사용 권장 (v3.4)


# =============================================================================
# v3.0 신규: 장소 추천 (카카오맵 연동)
# =============================================================================


# get_date_course 제거됨 - get_smart_course 사용 권장 (v3.4)


@mcp.tool()
async def get_recommended_spots(location: str = "서울", activity: str = "all") -> dict:
    """
    활동별 추천 장소를 알려드립니다.
    현재 날씨를 분석하여 적합한 장소를 추천합니다.

    사용 예시: "등산 어디가 좋아?", "캠핑장 추천해줘", "드라이브 코스 알려줘"

    Args:
        location: 지역명
        activity: 활동 종류
            - hiking: 등산
            - camping: 캠핑
            - picnic: 피크닉
            - drive: 드라이브
            - fishing: 낚시
            - golf: 골프
            - running: 러닝
            - bbq: 바베큐
            - all: 모든 활동 (기본값)

    Returns:
        추천 장소 목록, 날씨 적합도
    """
    from src.spots_database import (
        HIKING_SPOTS, CAMPING_SPOTS, PICNIC_SPOTS,
        DRIVE_COURSES, FISHING_SPOTS, GOLF_COURSES,
        RUNNING_COURSES, BBQ_SPOTS
    )

    weather = await cached_get_weather(location)

    if "error" in weather:
        return {"error": weather["error"], "location": location}

    # 기본 날씨 점수 계산
    temp = weather.get("current_weather", {}).get("temperature", 20)
    rain_prob = weather.get("today_summary", {}).get("precipitation_probability", 0)

    base_score = 100
    if rain_prob >= 50:
        base_score -= 30
    if temp < 0 or temp > 35:
        base_score -= 20

    results = {"location": location, "weather_score": base_score, "activities": {}}

    activity_map = {
        "hiking": ("등산", HIKING_SPOTS),
        "camping": ("캠핑", CAMPING_SPOTS),
        "picnic": ("피크닉", PICNIC_SPOTS),
        "drive": ("드라이브", DRIVE_COURSES),
        "fishing": ("낚시", FISHING_SPOTS),
        "golf": ("골프", GOLF_COURSES),
        "running": ("러닝", RUNNING_COURSES),
        "bbq": ("바베큐", BBQ_SPOTS),
    }

    if activity == "all":
        for key, (name, spots) in activity_map.items():
            count = 3 if base_score >= 70 else 2
            results["activities"][key] = {
                "name": name,
                "spots": spots[:count],
                "total": len(spots)
            }
    elif activity in activity_map:
        name, spots = activity_map[activity]
        count = 5 if base_score >= 70 else 3
        results["activities"][activity] = {
            "name": name,
            "spots": spots[:count],
            "total": len(spots)
        }
    else:
        return {"error": f"지원하지 않는 활동: {activity}", "available": list(activity_map.keys())}

    return results


# =============================================================================
# v3.1 신규: Kakao Maps API 연동
# =============================================================================


@mcp.tool()
async def search_nearby_places(
    keyword: str,
    location: str = "서울",
    radius: int = 2000,
    count: int = 5
) -> dict:
    """
    주변 장소를 검색합니다. (Kakao Maps API)
    전국 어디든 지원! 맛집, 카페, 관광지 등 키워드로 검색할 수 있습니다.

    사용 예시: "강남역 근처 맛집", "전주 한옥마을 카페", "부산 해운대 횟집"

    Args:
        keyword: 검색 키워드 (예: "맛집", "카페", "편의점", "주차장")
        location: 검색 중심 지역 (전국 어디든! 예: "서울", "전주", "속초", "을왕리")
        radius: 검색 반경 (미터, 기본값: 2000, 최대: 20000)
        count: 결과 개수 (기본값: 5, 최대: 15)

    Returns:
        장소 목록 (이름, 주소, 전화번호, 거리, 카카오맵 링크)
    """
    # 지역 좌표 조회 (전국 지원)
    coords = await get_location_coordinates_async(location)
    if not coords:
        return {"error": f"지역을 찾을 수 없습니다: {location}"}

    x, y = coords  # 경도, 위도

    # 카테고리 검색 시도 (한글 키워드가 카테고리에 해당하면)
    if keyword in CATEGORY_CODES:
        result = await search_place_by_category(keyword, x, y, radius, count)
    else:
        # 일반 키워드 검색
        result = await search_place_by_keyword(keyword, x, y, radius, count, "distance")

    if "error" in result:
        return result

    result["search_center"] = location
    result["radius_meters"] = radius

    return result


@mcp.tool()
async def get_directions_link(
    origin: str,
    destination: str,
    mode: str = "car"
) -> dict:
    """
    출발지에서 목적지까지 길찾기 링크를 생성합니다. (Kakao Maps)
    전국 어디든 지원! 자동차, 대중교통, 도보, 자전거 경로를 안내합니다.

    사용 예시: "서울역에서 부산역까지", "전주에서 군산 가는 길", "속초에서 양양까지"

    Args:
        origin: 출발지 (전국 어디든! 예: "서울역", "전주 한옥마을", "해운대")
        destination: 목적지 (전국 어디든! 예: "강남역", "경주 불국사", "제주공항")
        mode: 이동 수단
            - car: 자동차 (기본값)
            - transit: 대중교통
            - walk: 도보
            - bike: 자전거

    Returns:
        카카오맵 길찾기 URL, 이동 수단 정보
    """
    # 출발지 좌표 (전국 지원)
    origin_coords = await get_location_coordinates_async(origin)
    if not origin_coords:
        return {"error": f"출발지를 찾을 수 없습니다: {origin}"}

    # 목적지 좌표 (전국 지원)
    dest_coords = await get_location_coordinates_async(destination)
    if not dest_coords:
        return {"error": f"목적지를 찾을 수 없습니다: {destination}"}

    # 길찾기 URL 생성
    result = get_directions_url(
        origin_name=origin,
        origin_x=origin_coords[0],
        origin_y=origin_coords[1],
        dest_name=destination,
        dest_x=dest_coords[0],
        dest_y=dest_coords[1],
        mode=mode
    )

    return result


@mcp.tool()
async def search_restaurant(
    location: str = "서울",
    cuisine: str = "",
    count: int = 5
) -> dict:
    """
    맛집/음식점을 검색합니다. (Kakao Maps API)
    전국 어디든 지원! 지역과 음식 종류로 맛집을 찾아드립니다.

    사용 예시: "전주 비빔밥", "속초 물회", "제주 흑돼지", "부산 밀면"

    Args:
        location: 검색 지역 (전국 어디든! 예: "전주", "속초", "제주", "부산")
        cuisine: 음식 종류 (예: "한식", "회", "고기", 빈 값이면 전체)
        count: 결과 개수 (기본값: 5)

    Returns:
        맛집 목록 (이름, 주소, 카테고리, 카카오맵 링크)
    """
    # 지역 좌표 조회 (전국 지원)
    coords = await get_location_coordinates_async(location)
    if not coords:
        return {"error": f"지역을 찾을 수 없습니다: {location}"}

    x, y = coords

    # 검색 키워드 구성
    if cuisine:
        keyword = f"{location} {cuisine} 맛집"
    else:
        keyword = f"{location} 맛집"

    result = await search_place_by_keyword(keyword, x, y, 3000, count, "accuracy")

    if "error" in result:
        return result

    result["search_location"] = location
    if cuisine:
        result["cuisine"] = cuisine

    return result


@mcp.tool()
async def get_place_recommendation(
    location: str = "서울",
    situation: str = "혼자",
    time_of_day: str = "",
    count: int = 5
) -> dict:
    """
    상황/시간에 맞는 장소를 스마트하게 추천합니다.
    전국 어디든 지원! 혼자, 친구, 데이트, 가족 등 상황별 맞춤 추천!

    사용 예시:
    - "혼자 갈만한 곳" → situation="혼자"
    - "친구랑 저녁에 뭐하지?" → situation="친구", time_of_day="저녁"
    - "데이트 장소 추천해줘" → situation="데이트"
    - "가족이랑 점심 먹을 곳" → situation="가족", time_of_day="점심"

    Args:
        location: 지역 (전국 어디든! 예: "강남", "전주", "해운대", "제주")
        situation: 상황
            - 혼자: 카페, 서점, 영화관, 미술관 추천
            - 친구: 맛집, 술집, 노래방, 방탈출 추천
            - 데이트: 레스토랑, 루프탑, 와인바 추천
            - 가족: 한식, 뷔페, 박물관, 키즈카페 추천
            - 비즈니스: 호텔, 레스토랑, 회의실 추천
        time_of_day: 시간대 (비어있으면 현재 시간 자동 감지)
            - 아침 (6-10시): 브런치, 베이커리
            - 점심 (11-14시): 맛집, 런치
            - 오후 (14-17시): 카페, 디저트
            - 저녁 (17-21시): 레스토랑, 고기
            - 심야 (21-6시): 술집, 야식
        count: 결과 개수 (기본값: 5)

    Returns:
        상황에 맞는 장소 추천, 분위기 설명, 추천 카테고리
    """
    result = await get_smart_recommendation(
        location=location,
        situation=situation,
        time_of_day=time_of_day,
        count=count
    )

    return result


# whats_good_here 제거됨 - get_place_recommendation 사용 권장 (v3.4)


@mcp.tool()
async def get_smart_course(
    location: str = "서울",
    situation: str = "데이트"
) -> dict:
    """
    현재 날씨를 분석해서 최적의 코스를 추천합니다! (A→B→C 동선)
    비 오면 실내 위주, 맑으면 야외 포함! 날씨 걱정 없이 계획하세요.

    사용 예시:
    - "홍대 데이트 코스 짜줘"
    - "강남에서 친구랑 뭐하지?"
    - "제주도 가족 코스 추천"

    Args:
        location: 지역 (전국 어디든! 예: "홍대", "강남", "제주")
        situation: 상황
            - 데이트: 카페 → 전시회/공원 → 레스토랑
            - 친구: 카페 → 볼링장/맛집 → 술집
            - 가족: 카페 → 박물관/키즈카페 → 식당
            - 혼자: 카페 → 서점/산책 → 맛집

    Returns:
        날씨 기반 3단계 코스 (각 장소 카카오맵 링크 포함)
    """
    # 현재 날씨 조회
    weather = await cached_get_weather(location)
    forecast = await cached_get_forecast(location)

    # 날씨 정보 추출
    sky = "맑음"
    rain_prob = 0
    temperature = 20

    if "error" not in weather:
        current = weather.get("current", {})
        temperature = current.get("temperature", 20)

    if "error" not in forecast:
        summary = forecast.get("today_summary", {})
        rain_prob = summary.get("precipitation_probability", 0)
        sky = summary.get("sky", "맑음")

    # 날씨 기반 코스 추천
    result = await get_weather_based_course(
        location=location,
        situation=situation,
        weather_sky=sky,
        rain_prob=rain_prob,
        temperature=temperature,
    )

    return result


# plan_my_day 제거됨 - get_smart_course 사용 권장 (v3.4)


# =============================================================================
# v3.7 신규 - 독창적 기능 (창의성 개선)
# =============================================================================


@mcp.tool()
async def get_best_time_for_activity(location: str = "서울", activity: str = "외출") -> dict:
    """
    오늘 하루 중 활동하기 가장 좋은 시간대를 분석합니다! (v3.7 신규)
    시간대별 날씨 예보를 분석해서 최적의 타이밍을 알려드려요.

    "언제 나가면 좋을까?" "몇 시가 제일 좋아?" 에 답하는 유일한 MCP!

    사용 예시:
    - "오늘 언제 산책하면 좋을까?"
    - "빨래 몇 시에 널면 좋아?"
    - "저녁에 나가는 게 나을까, 아침이 나을까?"

    Args:
        location: 지역명
        activity: 활동 종류 (외출, 운동, 빨래, 등산, 피크닉)

    Returns:
        시간대별 점수와 최적 시간 추천
    """
    forecast = await cached_get_forecast(location)
    air = await get_air_quality(location)

    if "error" in forecast:
        return {"error": forecast["error"], "location": location}

    hourly = forecast.get("forecasts", [])

    # 시간대별 점수 계산
    time_scores = []
    for h in hourly[:12]:  # 12시간 예보
        score = 100
        factors = []

        temp = h.get("temperature", 20)
        rain_prob = h.get("precipitation_probability", 0)
        sky = h.get("sky", "맑음")
        wind = h.get("wind_speed", 2)

        # 강수확률
        if rain_prob >= 60:
            score -= 50
            factors.append(f"비 {rain_prob}%")
        elif rain_prob >= 30:
            score -= 25
            factors.append(f"비 가능성 {rain_prob}%")

        # 기온 (활동별 최적 기온)
        if activity in ["등산", "운동"]:
            if temp < 0 or temp > 30:
                score -= 30
                factors.append(f"기온 {temp}°C")
            elif 15 <= temp <= 22:
                score += 10
                factors.append(f"기온 최적 {temp}°C")
        elif activity == "빨래":
            if temp < 5:
                score -= 20
                factors.append(f"기온 {temp}°C (건조 느림)")
            elif temp >= 15:
                score += 10
                factors.append(f"기온 {temp}°C (건조 최적)")
        else:  # 외출, 피크닉
            if temp < -5 or temp > 33:
                score -= 40
                factors.append(f"기온 {temp}°C")
            elif 18 <= temp <= 25:
                score += 10

        # 하늘 상태
        if sky == "맑음":
            score += 5
        elif sky == "흐림":
            score -= 10

        # 바람
        if wind > 10:
            score -= 15
            factors.append(f"바람 {wind}m/s")

        score = max(0, min(100, score))

        time_str = f"{h.get('time', '0000')[:2]}:00"
        time_scores.append({
            "time": time_str,
            "score": score,
            "grade": "최적" if score >= 80 else "좋음" if score >= 60 else "보통" if score >= 40 else "나쁨",
            "weather": f"{temp}°C, {sky}",
            "factors": factors if factors else ["양호"]
        })

    # 최적 시간 찾기
    if time_scores:
        best = max(time_scores, key=lambda x: x["score"])
        worst = min(time_scores, key=lambda x: x["score"])
    else:
        best = {"time": "정보없음", "score": 0}
        worst = {"time": "정보없음", "score": 0}

    # 아침/오후/저녁 구분
    morning_scores = [t for t in time_scores if int(t["time"][:2]) < 12]
    afternoon_scores = [t for t in time_scores if 12 <= int(t["time"][:2]) < 18]
    evening_scores = [t for t in time_scores if int(t["time"][:2]) >= 18]

    morning_avg = sum(t["score"] for t in morning_scores) / len(morning_scores) if morning_scores else 0
    afternoon_avg = sum(t["score"] for t in afternoon_scores) / len(afternoon_scores) if afternoon_scores else 0
    evening_avg = sum(t["score"] for t in evening_scores) / len(evening_scores) if evening_scores else 0

    # 추천 시간대 결정
    period_scores = [("아침", morning_avg), ("오후", afternoon_avg), ("저녁", evening_avg)]
    best_period = max(period_scores, key=lambda x: x[1])

    return {
        "location": location,
        "activity": activity,
        "best_time": {
            "time": best["time"],
            "score": best["score"],
            "weather": best.get("weather", ""),
            "recommendation": f"{best['time']}이 가장 좋아요! ({best['score']}점)"
        },
        "best_period": {
            "period": best_period[0],
            "avg_score": round(best_period[1]),
            "recommendation": f"{best_period[0]}이 전반적으로 좋아요 (평균 {round(best_period[1])}점)"
        },
        "avoid_time": {
            "time": worst["time"],
            "score": worst["score"],
            "reason": f"{worst['time']}은 피하세요 ({worst['score']}점)"
        },
        "hourly_analysis": time_scores,
        "data_source": {
            "provider": "기상청 단기예보 API",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
    }


@mcp.tool()
async def compare_activities(location: str = "서울", activity1: str = "캠핑", activity2: str = "피크닉") -> dict:
    """
    두 활동 중 오늘 날씨에 더 적합한 것을 비교 분석합니다! (v3.7 신규)
    "캠핑 갈까 피크닉 갈까?" 같은 고민을 해결해드려요.

    사용 예시:
    - "캠핑 vs 피크닉, 오늘 뭐가 나을까?"
    - "등산이랑 러닝 중에 뭐가 좋아?"
    - "세차할까 빨래할까?"

    Args:
        location: 지역명
        activity1: 첫 번째 활동
        activity2: 두 번째 활동

    Returns:
        두 활동의 비교 분석 및 승자 추천
    """
    weather_data = await _get_weather_data(location)

    # 활동별 점수 계산 함수 매핑
    activity_functions = {
        "캠핑": calculate_camping_index,
        "피크닉": calculate_picnic_index,
        "등산": calculate_hiking_index,
        "빨래": calculate_laundry_index,
        "세차": calculate_car_wash_index,
        "운동": calculate_exercise_index,
        "러닝": calculate_running_index,
        "골프": calculate_golf_index,
        "낚시": calculate_fishing_index,
    }

    # 활동1 점수
    if activity1 in activity_functions:
        result1 = activity_functions[activity1](weather_data)
        score1 = result1.get("score", 50)
        grade1 = result1.get("grade", "보통")
        message1 = result1.get("message", "")
    else:
        score1 = 50
        grade1 = "알수없음"
        message1 = f"{activity1}은 지원하지 않는 활동입니다"

    # 활동2 점수
    if activity2 in activity_functions:
        result2 = activity_functions[activity2](weather_data)
        score2 = result2.get("score", 50)
        grade2 = result2.get("grade", "보통")
        message2 = result2.get("message", "")
    else:
        score2 = 50
        grade2 = "알수없음"
        message2 = f"{activity2}은 지원하지 않는 활동입니다"

    # 승자 결정
    diff = score1 - score2
    if abs(diff) < 10:
        winner = "비슷해요"
        recommendation = f"둘 다 괜찮아요! 더 하고 싶은 걸 하세요."
    elif diff > 0:
        winner = activity1
        recommendation = f"오늘은 {activity1}이 {diff}점 더 좋아요!"
    else:
        winner = activity2
        recommendation = f"오늘은 {activity2}가 {-diff}점 더 좋아요!"

    return {
        "location": location,
        "comparison": {
            activity1: {
                "score": score1,
                "grade": grade1,
                "message": message1
            },
            activity2: {
                "score": score2,
                "grade": grade2,
                "message": message2
            }
        },
        "winner": winner,
        "score_difference": abs(diff),
        "recommendation": recommendation,
        "weather_summary": f"현재 {weather_data.temperature}°C, 강수확률 {weather_data.rain_prob}%",
        "data_source": {
            "provider": "기상청 단기예보 API",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
    }


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
        "version": "3.7.0",
        "tools": 30,
        "features": ["weather", "weekly_forecast", "air_quality", "outfit", "laundry", "hiking", "picnic", "car_wash", "exercise", "cold_flu_risk", "commute", "allergy", "migraine_risk", "sleep_quality", "photography", "joint_pain", "camping", "fishing", "golf", "uv_info", "food_safety", "recommended_spots", "search_nearby_places", "get_directions_link", "search_restaurant", "get_place_recommendation", "get_smart_course", "get_best_time_for_activity", "compare_activities"],
        "v3.7_features": ["get_best_time_for_activity", "compare_activities", "score_breakdown", "data_source_info", "creativity_enhancement"],
        "v3.6_features": ["removed_kimjang", "removed_running", "removed_bbq", "removed_drive", "tool_optimization_32_to_28"],
        "v3.5_features": ["tool_consolidation_38_to_32", "removed_duplicates"],
        "v3.4_features": ["place_info_enriched", "why_recommend", "how_to_get_there", "notice", "hours_info", "outfit_tpo", "outfit_colors"],
        "v3.3_features": ["weather_based_course", "get_smart_course", "kakao_map_url_highlight"],
        "v3.2_features": ["nationwide_support", "dynamic_geocoding", "situation_recommendation", "time_based_recommendation"],
        "v3.1_features": ["kakao_maps_api", "search_nearby_places", "get_directions_link", "search_restaurant"],
        "v3.0_features": ["date_course", "recommended_spots", "spots_database"],
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
