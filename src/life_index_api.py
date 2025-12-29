"""
생활기상지수 API 연동
기상청 생활기상지수 조회서비스 3.0

- 자외선지수 (연중)
- 체감온도 (6-9월)
- 꽃가루농도위험지수 (4-6월, 8-10월)
- 대기정체지수 (연중)
"""

import os
import httpx
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# API 설정
LIFE_INDEX_API_KEY = os.getenv("WEATHER_API_KEY", "")
BASE_URL = "http://apis.data.go.kr/1360000/LivingWthrIdxServiceV4"


# 지역 코드 매핑 (시도별)
AREA_CODES = {
    "서울": "1100000000",
    "부산": "2600000000",
    "대구": "2700000000",
    "인천": "2800000000",
    "광주": "2900000000",
    "대전": "3000000000",
    "울산": "3100000000",
    "세종": "3600000000",
    "경기": "4100000000",
    "강원": "4200000000",
    "충북": "4300000000",
    "충남": "4400000000",
    "전북": "4500000000",
    "전남": "4600000000",
    "경북": "4700000000",
    "경남": "4800000000",
    "제주": "5000000000",
}

# 구 단위 매핑 (서울)
SEOUL_DISTRICT_CODES = {
    "강남구": "1168000000",
    "강동구": "1174000000",
    "강북구": "1130500000",
    "강서구": "1150000000",
    "관악구": "1162000000",
    "광진구": "1121500000",
    "구로구": "1153000000",
    "금천구": "1154500000",
    "노원구": "1135000000",
    "도봉구": "1132000000",
    "동대문구": "1123000000",
    "동작구": "1159000000",
    "마포구": "1144000000",
    "서대문구": "1141000000",
    "서초구": "1165000000",
    "성동구": "1120000000",
    "성북구": "1129000000",
    "송파구": "1171000000",
    "양천구": "1147000000",
    "영등포구": "1156000000",
    "용산구": "1117000000",
    "은평구": "1138000000",
    "종로구": "1111000000",
    "중구": "1114000000",
    "중랑구": "1126000000",
}


def get_area_code(location: str) -> str:
    """지역명을 지역코드로 변환"""
    # 서울 구 단위 체크
    if location in SEOUL_DISTRICT_CODES:
        return SEOUL_DISTRICT_CODES[location]

    # 시도 단위 체크
    for sido, code in AREA_CODES.items():
        if sido in location:
            return code

    # 기본값: 서울
    return AREA_CODES["서울"]


def get_current_time_str() -> str:
    """현재 시간을 API 형식으로 변환 (YYYYMMDDHH)"""
    now = datetime.now()
    # API는 보통 3시간 단위로 데이터 제공
    hour = (now.hour // 3) * 3
    return now.strftime(f"%Y%m%d") + f"{hour:02d}"


# =============================================================================
# 자외선지수
# =============================================================================

UV_INDEX_GRADES = {
    "danger": {"min": 11, "label": "위험", "emoji": "🔴", "advice": "외출 자제, 실내 활동 권장"},
    "very_high": {"min": 8, "label": "매우높음", "emoji": "🟠", "advice": "오전 10시~오후 3시 외출 자제"},
    "high": {"min": 6, "label": "높음", "emoji": "🟡", "advice": "모자, 선글라스, 선크림 필수"},
    "moderate": {"min": 3, "label": "보통", "emoji": "🟢", "advice": "장시간 외출 시 선크림 권장"},
    "low": {"min": 0, "label": "낮음", "emoji": "🔵", "advice": "자외선 걱정 없음"},
}


def get_uv_grade(value: int) -> dict:
    """자외선지수 등급 판정"""
    for grade_key, grade_info in UV_INDEX_GRADES.items():
        if value >= grade_info["min"]:
            return {
                "grade": grade_info["label"],
                "emoji": grade_info["emoji"],
                "advice": grade_info["advice"],
            }
    return UV_INDEX_GRADES["low"]


async def get_uv_index(location: str = "서울") -> dict:
    """
    자외선지수 조회

    Returns:
        {
            "location": "서울",
            "time": "2024-12-24 12:00",
            "uv_index": 3,
            "grade": "보통",
            "emoji": "🟢",
            "advice": "장시간 외출 시 선크림 권장",
            "hourly": [...]
        }
    """
    area_code = get_area_code(location)
    time_str = get_current_time_str()

    params = {
        "serviceKey": LIFE_INDEX_API_KEY,
        "numOfRows": 10,
        "pageNo": 1,
        "dataType": "JSON",
        "areaNo": area_code,
        "time": time_str,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/getUVIdxV4",
                params=params,
            )

            if response.status_code != 200:
                # API 실패 시 계절 기반 추정값 반환
                month = datetime.now().month
                if month in [6, 7, 8]:  # 여름
                    estimated_uv = 8
                elif month in [4, 5, 9, 10]:  # 봄/가을
                    estimated_uv = 5
                else:  # 겨울
                    estimated_uv = 2

                grade_info = get_uv_grade(estimated_uv)
                return {
                    "location": location,
                    "uv_index": estimated_uv,
                    "grade": grade_info["grade"],
                    "emoji": grade_info["emoji"],
                    "advice": grade_info["advice"],
                    "estimated": True,
                    "message": "API 미지원, 계절 기반 추정값",
                }

            data = response.json()

            # 응답 파싱
            items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])

            if not items:
                # API 실패 시 기본값 반환 (계절에 따라 추정)
                month = datetime.now().month
                if month in [6, 7, 8]:  # 여름
                    estimated_uv = 8
                elif month in [4, 5, 9, 10]:  # 봄/가을
                    estimated_uv = 5
                else:  # 겨울
                    estimated_uv = 2

                grade_info = get_uv_grade(estimated_uv)
                return {
                    "location": location,
                    "uv_index": estimated_uv,
                    "grade": grade_info["grade"],
                    "emoji": grade_info["emoji"],
                    "advice": grade_info["advice"],
                    "estimated": True,
                    "message": "실시간 데이터 없음, 계절 기반 추정값",
                }

            # 현재 시간대 데이터 추출
            item = items[0] if isinstance(items, list) else items
            uv_value = int(item.get("h0", item.get("h3", 3)))

            grade_info = get_uv_grade(uv_value)

            return {
                "location": location,
                "uv_index": uv_value,
                "grade": grade_info["grade"],
                "emoji": grade_info["emoji"],
                "advice": grade_info["advice"],
            }

    except Exception as e:
        return {"error": f"자외선지수 조회 실패: {str(e)}"}


# =============================================================================
# 체감온도 (여름철)
# =============================================================================

HEAT_INDEX_GRADES = {
    "danger": {"min": 38, "label": "위험", "emoji": "🔴", "advice": "모든 야외활동 중단"},
    "warning": {"min": 35, "label": "경고", "emoji": "🟠", "advice": "아침/저녁에만 외출"},
    "caution": {"min": 33, "label": "주의", "emoji": "🟡", "advice": "장시간 야외활동 자제"},
    "attention": {"min": 29, "label": "관심", "emoji": "🟢", "advice": "수분 섭취 권장"},
    "normal": {"min": 0, "label": "보통", "emoji": "🔵", "advice": "쾌적한 날씨"},
}


def get_heat_grade(value: float) -> dict:
    """체감온도 등급 판정"""
    for grade_key, grade_info in HEAT_INDEX_GRADES.items():
        if value >= grade_info["min"]:
            return {
                "grade": grade_info["label"],
                "emoji": grade_info["emoji"],
                "advice": grade_info["advice"],
            }
    return HEAT_INDEX_GRADES["normal"]


async def get_heat_index(location: str = "서울", temperature: float = None, humidity: float = None) -> dict:
    """
    체감온도 조회/계산

    여름철(6-9월)에만 의미있는 지수
    API 실패 시 자체 계산
    """
    month = datetime.now().month

    # 여름철 아니면 메시지 반환
    if month not in [5, 6, 7, 8, 9]:
        return {
            "location": location,
            "message": "체감온도는 여름철(5-9월)에만 제공됩니다.",
            "available": False,
        }

    # 온도/습도가 주어지면 자체 계산
    if temperature is not None and humidity is not None:
        # 열지수 공식 (간략화)
        if temperature >= 27:
            heat_index = temperature + 0.5 * (humidity - 50) * 0.1
        else:
            heat_index = temperature

        grade_info = get_heat_grade(heat_index)

        return {
            "location": location,
            "temperature": temperature,
            "humidity": humidity,
            "heat_index": round(heat_index, 1),
            "grade": grade_info["grade"],
            "emoji": grade_info["emoji"],
            "advice": grade_info["advice"],
        }

    # API 호출 시도
    area_code = get_area_code(location)
    time_str = get_current_time_str()

    params = {
        "serviceKey": LIFE_INDEX_API_KEY,
        "numOfRows": 10,
        "pageNo": 1,
        "dataType": "JSON",
        "areaNo": area_code,
        "time": time_str,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/getSenTaIdxV4",
                params=params,
            )

            if response.status_code == 200:
                data = response.json()
                items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])

                if items:
                    item = items[0] if isinstance(items, list) else items
                    heat_value = float(item.get("h0", item.get("h3", 30)))

                    grade_info = get_heat_grade(heat_value)

                    return {
                        "location": location,
                        "heat_index": heat_value,
                        "grade": grade_info["grade"],
                        "emoji": grade_info["emoji"],
                        "advice": grade_info["advice"],
                    }
    except:
        pass

    return {
        "location": location,
        "message": "체감온도 데이터를 가져올 수 없습니다.",
        "available": False,
    }


# =============================================================================
# 꽃가루농도위험지수
# =============================================================================

POLLEN_GRADES = {
    "very_high": {"min": 3, "label": "매우높음", "emoji": "🔴", "advice": "외출 자제, 마스크 필수, 창문 닫기"},
    "high": {"min": 2, "label": "높음", "emoji": "🟠", "advice": "야외활동 자제, 마스크 착용"},
    "moderate": {"min": 1, "label": "보통", "emoji": "🟡", "advice": "알레르기 민감자 주의"},
    "low": {"min": 0, "label": "낮음", "emoji": "🟢", "advice": "꽃가루 걱정 없음"},
}


def get_pollen_grade(value: int) -> dict:
    """꽃가루농도 등급 판정"""
    for grade_key, grade_info in POLLEN_GRADES.items():
        if value >= grade_info["min"]:
            return {
                "grade": grade_info["label"],
                "emoji": grade_info["emoji"],
                "advice": grade_info["advice"],
            }
    return POLLEN_GRADES["low"]


async def get_pollen_index(location: str = "서울") -> dict:
    """
    꽃가루농도위험지수 조회

    서비스 기간:
    - 소나무/참나무: 4-6월
    - 잡초류: 8-10월
    """
    month = datetime.now().month

    # 서비스 기간 체크
    if month in [4, 5, 6]:
        pollen_type = "tree"  # 소나무/참나무
        pollen_name = "소나무/참나무"
    elif month in [8, 9, 10]:
        pollen_type = "weed"  # 잡초류
        pollen_name = "잡초류"
    else:
        return {
            "location": location,
            "message": "꽃가루 정보는 봄(4-6월)과 가을(8-10월)에만 제공됩니다.",
            "available": False,
            "current_month": month,
        }

    area_code = get_area_code(location)
    time_str = datetime.now().strftime("%Y%m%d")

    # API 엔드포인트 선택
    if pollen_type == "tree":
        endpoint = f"{BASE_URL}/getOakPollenRiskIdxV4"  # 참나무
    else:
        endpoint = f"{BASE_URL}/getWeedsPollenRiskndxV4"  # 잡초류

    params = {
        "serviceKey": LIFE_INDEX_API_KEY,
        "numOfRows": 10,
        "pageNo": 1,
        "dataType": "JSON",
        "areaNo": area_code,
        "time": time_str,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(endpoint, params=params)

            if response.status_code == 200:
                data = response.json()
                items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])

                if items:
                    item = items[0] if isinstance(items, list) else items
                    pollen_value = int(item.get("today", 1))

                    grade_info = get_pollen_grade(pollen_value)

                    return {
                        "location": location,
                        "pollen_type": pollen_name,
                        "pollen_index": pollen_value,
                        "grade": grade_info["grade"],
                        "emoji": grade_info["emoji"],
                        "advice": grade_info["advice"],
                    }
    except:
        pass

    # 기본값 반환
    return {
        "location": location,
        "pollen_type": pollen_name,
        "pollen_index": 1,
        "grade": "보통",
        "emoji": "🟡",
        "advice": "알레르기 민감자 주의",
        "estimated": True,
    }


# =============================================================================
# 식중독지수
# =============================================================================

FOOD_POISON_GRADES = {
    "danger": {"min": 86, "label": "위험", "emoji": "🔴", "advice": "도시락 금지, 음식 즉시 냉장"},
    "warning": {"min": 71, "label": "경고", "emoji": "🟠", "advice": "조리 후 2시간 내 섭취"},
    "caution": {"min": 55, "label": "주의", "emoji": "🟡", "advice": "음식 보관 주의"},
    "attention": {"min": 35, "label": "관심", "emoji": "🟢", "advice": "일반적인 주의"},
    "low": {"min": 0, "label": "낮음", "emoji": "🔵", "advice": "식중독 걱정 적음"},
}


def get_food_poison_grade(value: int) -> dict:
    """식중독지수 등급 판정"""
    for grade_key, grade_info in FOOD_POISON_GRADES.items():
        if value >= grade_info["min"]:
            return {
                "grade": grade_info["label"],
                "emoji": grade_info["emoji"],
                "advice": grade_info["advice"],
            }
    return FOOD_POISON_GRADES["low"]


def calculate_food_poison_index(temperature: float, humidity: float) -> int:
    """
    식중독지수 자체 계산

    기온과 습도를 기반으로 계산
    실제 기상청 공식과 유사하게 구현
    """
    # 기본 공식: 기온이 높고 습도가 높을수록 위험
    base_score = 0

    # 기온 영향 (가장 큰 영향)
    if temperature >= 35:
        base_score += 50
    elif temperature >= 30:
        base_score += 40
    elif temperature >= 25:
        base_score += 30
    elif temperature >= 20:
        base_score += 20
    elif temperature >= 15:
        base_score += 10

    # 습도 영향
    if humidity >= 80:
        base_score += 40
    elif humidity >= 70:
        base_score += 30
    elif humidity >= 60:
        base_score += 20
    elif humidity >= 50:
        base_score += 10

    return min(100, max(0, base_score))


async def get_food_poison_index(location: str = "서울", temperature: float = None, humidity: float = None) -> dict:
    """
    식중독지수 조회/계산
    """
    # 온도/습도가 주어지면 자체 계산
    if temperature is not None and humidity is not None:
        index_value = calculate_food_poison_index(temperature, humidity)
        grade_info = get_food_poison_grade(index_value)

        return {
            "location": location,
            "food_poison_index": index_value,
            "grade": grade_info["grade"],
            "emoji": grade_info["emoji"],
            "advice": grade_info["advice"],
            "temperature": temperature,
            "humidity": humidity,
        }

    # API 호출 시도
    area_code = get_area_code(location)
    time_str = get_current_time_str()

    params = {
        "serviceKey": LIFE_INDEX_API_KEY,
        "numOfRows": 10,
        "pageNo": 1,
        "dataType": "JSON",
        "areaNo": area_code,
        "time": time_str,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/getFsnIdxV4",
                params=params,
            )

            if response.status_code == 200:
                data = response.json()
                items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])

                if items:
                    item = items[0] if isinstance(items, list) else items
                    index_value = int(item.get("h0", item.get("today", 50)))

                    grade_info = get_food_poison_grade(index_value)

                    return {
                        "location": location,
                        "food_poison_index": index_value,
                        "grade": grade_info["grade"],
                        "emoji": grade_info["emoji"],
                        "advice": grade_info["advice"],
                    }
    except:
        pass

    # 기본값 (계절 기반)
    month = datetime.now().month
    if month in [6, 7, 8]:
        estimated_index = 70
    elif month in [5, 9]:
        estimated_index = 50
    else:
        estimated_index = 30

    grade_info = get_food_poison_grade(estimated_index)

    return {
        "location": location,
        "food_poison_index": estimated_index,
        "grade": grade_info["grade"],
        "emoji": grade_info["emoji"],
        "advice": grade_info["advice"],
        "estimated": True,
    }


# =============================================================================
# 종합 생활지수 조회
# =============================================================================

async def get_all_life_indices(location: str = "서울", temperature: float = None, humidity: float = None) -> dict:
    """
    모든 생활기상지수 종합 조회
    """
    results = {
        "location": location,
        "indices": {},
    }

    # 자외선지수
    uv = await get_uv_index(location)
    if "error" not in uv:
        results["indices"]["uv"] = uv

    # 체감온도 (여름철)
    heat = await get_heat_index(location, temperature, humidity)
    if heat.get("available", True):
        results["indices"]["heat"] = heat

    # 꽃가루 (봄/가을)
    pollen = await get_pollen_index(location)
    if pollen.get("available", True):
        results["indices"]["pollen"] = pollen

    # 식중독
    food = await get_food_poison_index(location, temperature, humidity)
    if "error" not in food:
        results["indices"]["food_poison"] = food

    return results
