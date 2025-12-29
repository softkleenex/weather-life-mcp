"""
Kakao Maps REST API 연동 모듈 (v3.0)

기능:
- 키워드로 장소 검색
- 카테고리별 장소 검색
- 주소 → 좌표 변환
- 길찾기 URL 생성
"""

import os
import httpx
import math
from typing import Optional, List, Dict
from urllib.parse import quote, urlencode


def calculate_distance_between_coords(lat1: float, lon1: float, lat2: float, lon2: float) -> int:
    """
    두 좌표 간 거리 계산 (Haversine 공식)

    Returns:
        거리 (미터)
    """
    R = 6371000  # 지구 반지름 (미터)

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return int(R * c)


async def find_nearest_landmark(x: str, y: str) -> Optional[Dict]:
    """
    주어진 좌표에서 가장 가까운 랜드마크 찾기
    우선순위: 지하철역 > 버스터미널 > 기차역

    Args:
        x: 경도 (longitude)
        y: 위도 (latitude)

    Returns:
        가장 가까운 랜드마크 정보 또는 None
    """
    if not KAKAO_REST_API_KEY:
        return None

    # 검색 우선순위: 지하철역 > 버스터미널
    search_configs = [
        ("SW8", "역", 2000),      # 지하철역, 2km
        ("BT1", "터미널", 5000),  # 버스터미널, 5km
    ]

    try:
        async with httpx.AsyncClient() as client:
            for category_code, suffix_hint, radius in search_configs:
                response = await client.get(
                    f"{KAKAO_LOCAL_API}/search/category.json",
                    headers={"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"},
                    params={
                        "category_group_code": category_code,
                        "x": x,
                        "y": y,
                        "radius": radius,
                        "sort": "distance",
                        "size": 1
                    },
                    timeout=5.0
                )

                if response.status_code == 200:
                    data = response.json()
                    documents = data.get("documents", [])
                    if documents:
                        place = documents[0]
                        name = place.get("place_name", "")
                        return {
                            "name": name,
                            "distance": place.get("distance", ""),
                            "x": place.get("x"),
                            "y": place.get("y")
                        }
    except Exception:
        pass

    return None

# API 키
KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY", "")

# API 엔드포인트
KAKAO_LOCAL_API = "https://dapi.kakao.com/v2/local"
KAKAO_NAVI_URL = "https://map.kakao.com/link"

# 카테고리 코드
CATEGORY_CODES = {
    "대형마트": "MT1",
    "편의점": "CS2",
    "어린이집": "PS3",
    "학교": "SC4",
    "학원": "AC5",
    "주차장": "PK6",
    "주유소": "OL7",
    "지하철역": "SW8",
    "은행": "BK9",
    "문화시설": "CT1",
    "중개업소": "AG2",
    "공공기관": "PO3",
    "관광명소": "AT4",
    "숙박": "AD5",
    "음식점": "FD6",
    "카페": "CE7",
    "병원": "HP8",
    "약국": "PM9",
}


async def search_place_by_keyword(
    keyword: str,
    x: Optional[float] = None,
    y: Optional[float] = None,
    radius: int = 5000,
    size: int = 5,
    sort: str = "accuracy"
) -> Dict:
    """
    키워드로 장소 검색

    Args:
        keyword: 검색 키워드 (예: "강남 맛집", "북한산")
        x: 중심 경도 (longitude)
        y: 중심 위도 (latitude)
        radius: 검색 반경 (미터, 최대 20000)
        size: 결과 개수 (1-15)
        sort: 정렬 기준 (accuracy: 정확도순, distance: 거리순)

    Returns:
        검색 결과 (장소 목록)
    """
    if not KAKAO_REST_API_KEY:
        return {"error": "KAKAO_REST_API_KEY가 설정되지 않았습니다."}

    url = f"{KAKAO_LOCAL_API}/search/keyword.json"

    params = {
        "query": keyword,
        "size": min(size, 15),
        "sort": sort,
    }

    if x and y:
        params["x"] = x
        params["y"] = y
        params["radius"] = min(radius, 20000)

    headers = {
        "Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            # 결과 가공
            places = []
            for doc in data.get("documents", []):
                places.append({
                    "name": doc.get("place_name", ""),
                    "address": doc.get("road_address_name") or doc.get("address_name", ""),
                    "category": doc.get("category_name", ""),
                    "phone": doc.get("phone", ""),
                    "x": doc.get("x", ""),  # 경도
                    "y": doc.get("y", ""),  # 위도
                    "place_url": doc.get("place_url", ""),
                    "distance": doc.get("distance", ""),
                })

            return {
                "keyword": keyword,
                "total_count": data.get("meta", {}).get("total_count", 0),
                "places": places,
            }

    except httpx.HTTPStatusError as e:
        return {"error": f"API 오류: {e.response.status_code}"}
    except Exception as e:
        return {"error": f"요청 실패: {str(e)}"}


async def search_place_by_category(
    category: str,
    x: float,
    y: float,
    radius: int = 2000,
    size: int = 5
) -> Dict:
    """
    카테고리로 주변 장소 검색

    Args:
        category: 카테고리 (음식점, 카페, 편의점, 약국 등)
        x: 중심 경도
        y: 중심 위도
        radius: 검색 반경 (미터)
        size: 결과 개수

    Returns:
        검색 결과
    """
    if not KAKAO_REST_API_KEY:
        return {"error": "KAKAO_REST_API_KEY가 설정되지 않았습니다."}

    # 카테고리 코드 변환
    category_code = CATEGORY_CODES.get(category, "")
    if not category_code:
        # 직접 코드가 입력된 경우
        if category in CATEGORY_CODES.values():
            category_code = category
        else:
            return {
                "error": f"지원하지 않는 카테고리: {category}",
                "available": list(CATEGORY_CODES.keys())
            }

    url = f"{KAKAO_LOCAL_API}/search/category.json"

    params = {
        "category_group_code": category_code,
        "x": x,
        "y": y,
        "radius": min(radius, 20000),
        "size": min(size, 15),
        "sort": "distance",
    }

    headers = {
        "Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            places = []
            for doc in data.get("documents", []):
                places.append({
                    "name": doc.get("place_name", ""),
                    "address": doc.get("road_address_name") or doc.get("address_name", ""),
                    "category": doc.get("category_name", ""),
                    "phone": doc.get("phone", ""),
                    "distance": doc.get("distance", ""),
                    "place_url": doc.get("place_url", ""),
                })

            return {
                "category": category,
                "total_count": data.get("meta", {}).get("total_count", 0),
                "places": places,
            }

    except Exception as e:
        return {"error": f"요청 실패: {str(e)}"}


async def geocode(address: str) -> Dict:
    """
    주소를 좌표로 변환

    Args:
        address: 주소 (예: "서울 종로구 북촌로")

    Returns:
        좌표 정보
    """
    if not KAKAO_REST_API_KEY:
        return {"error": "KAKAO_REST_API_KEY가 설정되지 않았습니다."}

    url = f"{KAKAO_LOCAL_API}/search/address.json"

    params = {"query": address}
    headers = {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            documents = data.get("documents", [])
            if not documents:
                return {"error": "주소를 찾을 수 없습니다.", "address": address}

            doc = documents[0]
            return {
                "address": address,
                "x": doc.get("x", ""),
                "y": doc.get("y", ""),
                "address_type": doc.get("address_type", ""),
            }

    except Exception as e:
        return {"error": f"요청 실패: {str(e)}"}


def get_directions_url(
    origin_name: str,
    origin_x: float,
    origin_y: float,
    dest_name: str,
    dest_x: float,
    dest_y: float,
    mode: str = "car"
) -> Dict:
    """
    길찾기 URL 생성

    Args:
        origin_name: 출발지 이름
        origin_x: 출발지 경도
        origin_y: 출발지 위도
        dest_name: 목적지 이름
        dest_x: 목적지 경도
        dest_y: 목적지 위도
        mode: 이동 수단 (car: 자동차, transit: 대중교통, walk: 도보, bike: 자전거)

    Returns:
        길찾기 URL 정보
    """
    mode_map = {
        "car": "car",
        "자동차": "car",
        "transit": "transit",
        "대중교통": "transit",
        "walk": "walk",
        "도보": "walk",
        "bike": "bike",
        "자전거": "bike",
    }

    transport = mode_map.get(mode, "car")

    # 카카오맵 길찾기 URL 생성
    params = {
        "map_type": "TYPE_MAP",
        "target": "car" if transport == "car" else "walk",
    }

    # 웹/앱 URL
    if transport == "transit":
        # 대중교통
        url = f"https://map.kakao.com/?sName={quote(origin_name)}&eName={quote(dest_name)}&map_type=TYPE_MAP&tab=transit"
    else:
        # 자동차/도보
        url = f"https://map.kakao.com/?sName={quote(origin_name)}&sX={origin_x}&sY={origin_y}&eName={quote(dest_name)}&eX={dest_x}&eY={dest_y}&by={transport}"

    return {
        "mode": transport,
        "mode_korean": {"car": "자동차", "transit": "대중교통", "walk": "도보", "bike": "자전거"}.get(transport, transport),
        "origin": origin_name,
        "destination": dest_name,
        "url": url,
        "message": f"{origin_name}에서 {dest_name}까지 {mode_map.get(mode, '자동차')} 길찾기"
    }


# 한국 전체 주요 지역 좌표
KOREA_COORDINATES = {
    # 서울 주요 지역/랜드마크
    "서울": (126.9780, 37.5665),
    "홍대": (126.9236, 37.5563),
    "홍대입구": (126.9236, 37.5563),
    "이태원": (126.9945, 37.5346),
    "명동": (126.9857, 37.5636),
    "강남역": (127.0276, 37.4979),
    "서울역": (126.9706, 37.5547),
    "잠실": (127.1000, 37.5133),
    "여의도": (126.9246, 37.5219),
    "신촌": (126.9368, 37.5551),
    "건대입구": (127.0704, 37.5402),
    "압구정": (127.0288, 37.5270),
    "신사동": (127.0205, 37.5166),
    "가로수길": (127.0230, 37.5198),
    "성수동": (127.0560, 37.5447),
    "망원동": (126.9052, 37.5556),
    "연남동": (126.9213, 37.5660),
    "합정": (126.9139, 37.5496),
    "상수": (126.9230, 37.5478),
    "을지로": (126.9910, 37.5660),
    "종로": (126.9816, 37.5735),
    "북촌": (126.9850, 37.5825),
    "삼청동": (126.9820, 37.5900),
    "인사동": (126.9850, 37.5740),
    "동대문": (127.0093, 37.5711),
    "청량리": (127.0470, 37.5803),

    # 서울 구
    "강남구": (127.0495, 37.5172),
    "강북구": (127.0255, 37.6396),
    "강서구": (126.8495, 37.5509),
    "관악구": (126.9516, 37.4784),
    "광진구": (127.0857, 37.5384),
    "구로구": (126.8874, 37.4954),
    "금천구": (126.8956, 37.4600),
    "노원구": (127.0569, 37.6542),
    "도봉구": (127.0471, 37.6688),
    "동대문구": (127.0407, 37.5744),
    "동작구": (126.9516, 37.5124),
    "마포구": (126.9090, 37.5663),
    "서대문구": (126.9388, 37.5791),
    "서초구": (127.0327, 37.4837),
    "성동구": (127.0369, 37.5633),
    "성북구": (127.0203, 37.5894),
    "송파구": (127.1059, 37.5048),
    "양천구": (126.8665, 37.5270),
    "영등포구": (126.8983, 37.5264),
    "용산구": (126.9675, 37.5326),
    "은평구": (126.9293, 37.6027),
    "종로구": (126.9816, 37.5735),
    "중구": (126.9996, 37.5640),
    "중랑구": (127.0928, 37.6063),

    # 경기도
    "수원": (127.0286, 37.2636),
    "성남": (127.1378, 37.4201),
    "고양": (126.8320, 37.6584),
    "용인": (127.1775, 37.2410),
    "부천": (126.7660, 37.5034),
    "안산": (126.8468, 37.3219),
    "안양": (126.9526, 37.3943),
    "남양주": (127.2165, 37.6360),
    "화성": (126.8312, 37.1995),
    "평택": (127.0889, 36.9921),
    "의정부": (127.0338, 37.7381),
    "시흥": (126.8030, 37.3800),
    "파주": (126.7800, 37.7600),
    "광명": (126.8664, 37.4786),
    "김포": (126.7156, 37.6152),
    "군포": (126.9350, 37.3614),
    "광주": (127.2553, 37.4295),  # 경기 광주
    "이천": (127.4350, 37.2722),
    "양주": (127.0456, 37.7853),
    "오산": (127.0770, 37.1499),
    "구리": (127.1297, 37.5943),
    "안성": (127.2798, 37.0078),
    "포천": (127.2003, 37.8949),
    "의왕": (126.9683, 37.3449),
    "하남": (127.2146, 37.5393),
    "여주": (127.6375, 37.2983),
    "양평": (127.4875, 37.4917),
    "동두천": (127.0606, 37.9034),
    "과천": (126.9876, 37.4292),
    "가평": (127.5095, 37.8315),
    "연천": (127.0750, 38.0964),

    # 광역시
    "부산": (129.0756, 35.1796),
    "대구": (128.6014, 35.8714),
    "인천": (126.7052, 37.4563),
    "광주광역시": (126.8526, 35.1595),
    "대전": (127.3845, 36.3504),
    "울산": (129.3114, 35.5384),
    "세종": (127.2894, 36.4800),

    # 강원도
    "춘천": (127.7298, 37.8813),
    "원주": (127.9470, 37.3422),
    "강릉": (128.8761, 37.7519),
    "동해": (129.1143, 37.5247),
    "태백": (128.9856, 37.1640),
    "속초": (128.5918, 38.2070),
    "삼척": (129.1658, 37.4500),

    # 충청도
    "청주": (127.4890, 36.6424),
    "충주": (127.9259, 36.9910),
    "제천": (128.1909, 37.1325),
    "천안": (127.1526, 36.8151),
    "공주": (127.1190, 36.4466),
    "보령": (126.6127, 36.3334),
    "아산": (127.0024, 36.7898),
    "서산": (126.4503, 36.7845),
    "논산": (127.0987, 36.1872),
    "당진": (126.6463, 36.8896),

    # 전라도
    "전주": (127.1480, 35.8242),
    "군산": (126.7368, 35.9676),
    "익산": (126.9576, 35.9483),
    "정읍": (126.8561, 35.5699),
    "남원": (127.3903, 35.4164),
    "김제": (126.8809, 35.8037),
    "목포": (126.3922, 34.8118),
    "여수": (127.6622, 34.7604),
    "순천": (127.4875, 34.9506),
    "나주": (126.7108, 35.0159),
    "광양": (127.6958, 34.9407),

    # 경상도
    "포항": (129.3435, 36.0190),
    "경주": (129.2247, 35.8562),
    "김천": (128.1136, 36.1398),
    "안동": (128.7293, 36.5684),
    "구미": (128.3441, 36.1195),
    "영주": (128.6240, 36.8057),
    "영천": (128.9385, 35.9733),
    "상주": (128.1591, 36.4109),
    "문경": (128.1867, 36.5866),
    "경산": (128.7412, 35.8251),
    "창원": (128.6811, 35.2280),
    "진주": (128.1078, 35.1802),
    "통영": (128.4332, 34.8545),
    "사천": (128.0644, 35.0037),
    "김해": (128.8893, 35.2285),
    "밀양": (128.7464, 35.5037),
    "거제": (128.6211, 34.8806),
    "양산": (129.0373, 35.3350),

    # 제주도
    "제주": (126.5312, 33.4996),
    "서귀포": (126.5606, 33.2541),
}


def get_location_coordinates(location: str) -> tuple:
    """지역명으로 좌표 반환 (캐시 조회, 동기)"""
    # 정확한 매칭
    if location in KOREA_COORDINATES:
        return KOREA_COORDINATES[location]

    # 부분 매칭 (예: "서울시" -> "서울")
    for key in KOREA_COORDINATES:
        if key in location or location in key:
            return KOREA_COORDINATES[key]

    # 못 찾으면 None (async 버전에서 API 호출)
    return None


async def get_location_coordinates_async(location: str) -> tuple:
    """
    지역명으로 좌표 반환 (전국 어디든 지원)
    1. 캐시된 좌표 확인
    2. 없으면 Kakao Geocoding API로 동적 조회
    """
    # 1. 캐시 확인
    coords = get_location_coordinates(location)
    if coords:
        return coords

    # 2. Kakao Geocoding API로 동적 조회
    if not KAKAO_REST_API_KEY:
        # API 키 없으면 서울 기본값
        return KOREA_COORDINATES.get("서울")

    result = await geocode(location)
    if "error" not in result and result.get("x") and result.get("y"):
        return (float(result["x"]), float(result["y"]))

    # 3. 키워드 검색으로 시도
    try:
        search_result = await search_place_by_keyword(location, size=1)
        if search_result.get("places"):
            place = search_result["places"][0]
            return (float(place["x"]), float(place["y"]))
    except:
        pass

    # 4. 기본값: 서울
    return KOREA_COORDINATES.get("서울")


# =============================================================================
# 상황별 장소 추천 시스템
# =============================================================================

# 상황별 추천 카테고리
SITUATION_CATEGORIES = {
    "혼자": {
        "keywords": ["카페", "서점", "독서실", "영화관", "미술관", "전시회", "공원"],
        "description": "혼자만의 시간을 보내기 좋은 곳",
    },
    "친구": {
        "keywords": ["맛집", "술집", "호프", "포차", "노래방", "볼링장", "방탈출", "보드게임카페"],
        "description": "친구들과 즐기기 좋은 곳",
    },
    "데이트": {
        "keywords": ["레스토랑", "카페", "영화관", "전시회", "야경", "루프탑", "와인바", "이자카야"],
        "description": "연인과 로맨틱한 시간을 보내기 좋은 곳",
    },
    "가족": {
        "keywords": ["한식", "뷔페", "키즈카페", "놀이공원", "동물원", "박물관", "수족관"],
        "description": "가족과 함께하기 좋은 곳",
    },
    "비즈니스": {
        "keywords": ["레스토랑", "호텔", "카페", "회의실", "코워킹"],
        "description": "비즈니스 미팅에 적합한 곳",
    },
}

# 시간대별 추천
TIME_RECOMMENDATIONS = {
    "아침": {
        "hours": (6, 10),
        "keywords": ["브런치", "모닝커피", "베이커리", "아침식사"],
        "vibe": "상쾌한 하루의 시작",
    },
    "점심": {
        "hours": (11, 14),
        "keywords": ["맛집", "런치", "한식", "일식", "중식"],
        "vibe": "든든한 점심 식사",
    },
    "오후": {
        "hours": (14, 17),
        "keywords": ["카페", "디저트", "전시회", "공원", "산책"],
        "vibe": "여유로운 오후 시간",
    },
    "저녁": {
        "hours": (17, 21),
        "keywords": ["레스토랑", "고기", "파스타", "회", "이자카야"],
        "vibe": "분위기 있는 저녁 식사",
    },
    "심야": {
        "hours": (21, 6),
        "keywords": ["술집", "호프", "포차", "야식", "라멘", "24시"],
        "vibe": "밤을 즐기는 시간",
    },
}

# 날씨별 추천
WEATHER_RECOMMENDATIONS = {
    "맑음": {
        "outdoor": True,
        "keywords": ["공원", "산책", "테라스", "루프탑", "야외"],
        "tip": "야외 활동하기 좋은 날씨예요!",
    },
    "흐림": {
        "outdoor": True,
        "keywords": ["카페", "전시회", "영화관", "쇼핑몰"],
        "tip": "실내외 모두 좋아요",
    },
    "비": {
        "outdoor": False,
        "keywords": ["실내", "영화관", "쇼핑몰", "카페", "북카페"],
        "tip": "실내 활동을 추천해요",
    },
    "눈": {
        "outdoor": False,
        "keywords": ["따뜻한", "국물", "찌개", "라멘", "카페"],
        "tip": "따뜻한 곳에서 포근하게!",
    },
}


def get_korea_time():
    """한국 시간(KST) 반환"""
    from datetime import datetime, timezone, timedelta
    KST = timezone(timedelta(hours=9))
    return datetime.now(KST)


# =============================================================================
# 장소 정보 강화 함수들 (v3.4)
# =============================================================================

def generate_recommendation_reason(category: str, situation: str, time_of_day: str) -> str:
    """
    추천 이유 생성

    Args:
        category: 장소 카테고리 (카페, 음식점 등)
        situation: 상황 (혼자, 친구, 데이트 등)
        time_of_day: 시간대 (아침, 점심, 오후, 저녁, 심야)

    Returns:
        추천 이유 문장
    """
    reasons = {
        # 상황별 이유
        ("데이트", "카페"): "분위기 좋은 공간에서 대화하기 좋아요",
        ("데이트", "음식점"): "특별한 날 기억에 남을 식사를 해보세요",
        ("데이트", "레스토랑"): "로맨틱한 분위기에서 둘만의 시간을",
        ("친구", "카페"): "수다 떨기 좋은 분위기예요",
        ("친구", "음식점"): "맛있는 음식과 함께 즐거운 시간!",
        ("친구", "술집"): "오랜만에 속 터놓고 이야기해요",
        ("혼자", "카페"): "조용히 나만의 시간을 즐기세요",
        ("혼자", "음식점"): "혼밥하기 편한 곳이에요",
        ("혼자", "서점"): "책과 함께 여유로운 시간",
        ("가족", "음식점"): "온 가족이 함께 즐길 수 있어요",
        ("가족", "카페"): "아이들도 좋아하는 공간이에요",

        # 시간대별 이유
        ("아침", "카페"): "상쾌한 아침을 깨워줄 커피 한 잔",
        ("아침", "음식점"): "든든한 아침으로 하루 시작!",
        ("점심", "음식점"): "점심 특선 메뉴가 있어요",
        ("점심", "카페"): "식후 디저트로 딱!",
        ("오후", "카페"): "여유로운 오후 티타임",
        ("오후", "전시"): "문화생활 하기 좋은 시간이에요",
        ("저녁", "음식점"): "분위기 있는 저녁 식사",
        ("저녁", "레스토랑"): "특별한 저녁을 위한 추천",
        ("심야", "음식점"): "야식 맛집! 늦은 시간도 OK",
        ("심야", "술집"): "밤의 분위기를 즐기세요",
    }

    # 상황+카테고리 조합으로 찾기
    for key_cat in ["카페", "음식점", "레스토랑", "술집", "서점", "전시"]:
        if key_cat in category:
            key = (situation, key_cat)
            if key in reasons:
                return reasons[key]
            # 시간대로도 찾기
            key = (time_of_day, key_cat)
            if key in reasons:
                return reasons[key]

    # 기본 이유
    defaults = {
        "데이트": "데이트하기 좋은 분위기예요",
        "친구": "친구들과 즐기기 좋아요",
        "혼자": "혼자 방문하기 편해요",
        "가족": "가족 단위로 방문하기 좋아요",
        "비즈니스": "미팅하기 좋은 환경이에요",
    }
    return defaults.get(situation, "인기 있는 장소예요")


def generate_travel_tip(distance: str) -> str:
    """
    거리 기반 이동 방법 힌트 생성

    Args:
        distance: 거리 문자열 (예: "350", "1200")

    Returns:
        이동 방법 힌트
    """
    try:
        dist = int(distance) if distance else 0
    except (ValueError, TypeError):
        return "카카오맵에서 길찾기를 확인하세요"

    if dist <= 300:
        return "도보 5분 이내, 걸어가기 좋아요"
    elif dist <= 500:
        return "도보 5-10분, 산책하며 가기 좋아요"
    elif dist <= 1000:
        return "도보 10-15분 또는 버스 1정거장"
    elif dist <= 2000:
        return "버스/지하철 이용 추천 (약 10분)"
    elif dist <= 5000:
        return "대중교통 15-20분 소요"
    else:
        return "택시 또는 대중교통 이용 추천"


def generate_notice(category: str) -> Dict[str, str]:
    """
    카테고리별 알아야 할 것 생성

    Args:
        category: 장소 카테고리

    Returns:
        주의사항 딕셔너리
    """
    notices = {
        "카페": {
            "notice": "음료 주문 필수, 노트북 사용 가능 여부 확인",
            "tip": "피크타임(14-17시)엔 웨이팅 있을 수 있어요",
        },
        "음식점": {
            "notice": "예약 가능 여부 미리 확인 추천",
            "tip": "점심(12-13시), 저녁(18-19시)은 대기 시간 있을 수 있어요",
        },
        "레스토랑": {
            "notice": "예약 필수! 드레스코드 확인",
            "tip": "기념일엔 미리 말씀하시면 이벤트 가능할 수 있어요",
        },
        "술집": {
            "notice": "미성년자 출입 불가",
            "tip": "금요일/토요일은 매우 붐벼요",
        },
        "영화관": {
            "notice": "상영 시간표 미리 확인",
            "tip": "팝콘&음료 세트가 더 저렴해요",
        },
        "전시": {
            "notice": "온라인 예매 시 할인 있는 경우 많아요",
            "tip": "평일 오전이 가장 한적해요",
        },
        "공원": {
            "notice": "날씨 변화에 대비하세요",
            "tip": "돗자리, 간식 챙기면 더 좋아요",
        },
        "쇼핑": {
            "notice": "주말은 매우 붐빕니다",
            "tip": "세일 기간 확인하고 방문하세요",
        },
    }

    for key, value in notices.items():
        if key in category:
            return value

    return {
        "notice": "운영시간 확인 후 방문하세요",
        "tip": "카카오맵에서 최신 정보를 확인하세요",
    }


def enrich_place_info(
    place: Dict,
    situation: str = "혼자",
    time_of_day: str = "오후",
    step_num: int = 1,
    prev_place: Optional[Dict] = None,
    is_course: bool = False,
    nearest_landmark: Optional[Dict] = None
) -> Dict:
    """
    장소 정보에 추천 이유, 이동 방법, 알아야 할 것 추가

    Args:
        place: 기본 장소 정보
        situation: 상황
        time_of_day: 시간대
        step_num: 코스에서의 순서
        prev_place: 이전 장소 (코스일 때만)
        is_course: 코스 추천인지 여부
        nearest_landmark: 가장 가까운 랜드마크 (지하철역/버스터미널)

    Returns:
        강화된 장소 정보
    """
    category = place.get("category", "")
    place_url = place.get("place_url", place.get("kakao_map_url", ""))

    # 추천 이유 생성
    reason = generate_recommendation_reason(category, situation, time_of_day)

    # 알아야 할 것
    notice_info = generate_notice(category)

    # 기본 결과
    result = {
        "step": step_num,
        "name": place.get("place_name", place.get("name", "")),
        "address": place.get("road_address_name", place.get("address", "")),
        "category": category,
        "phone": place.get("phone", "카카오맵에서 확인"),
        "kakao_map_url": place_url,
        "why_recommend": reason,
        "notice": notice_info["notice"],
        "tip": notice_info["tip"],
    }

    # 코스일 때: 이전 장소에서의 거리
    if is_course and prev_place:
        try:
            prev_lat = float(prev_place.get("y", 0))
            prev_lon = float(prev_place.get("x", 0))
            curr_lat = float(place.get("y", 0))
            curr_lon = float(place.get("x", 0))

            if prev_lat and prev_lon and curr_lat and curr_lon:
                dist = calculate_distance_between_coords(prev_lat, prev_lon, curr_lat, curr_lon)
                prev_name = prev_place.get("place_name", prev_place.get("name", "이전 장소"))
                result["from_prev_place"] = f"{prev_name}에서"
                result["distance_from_prev"] = f"{dist}m"
                result["travel_tip"] = generate_travel_tip(str(dist))
        except (ValueError, TypeError):
            pass

    # 단일 검색일 때: 가까운 랜드마크에서의 거리
    elif not is_course and nearest_landmark:
        try:
            landmark_name = nearest_landmark.get("name", "")
            landmark_dist = nearest_landmark.get("distance", "")
            if landmark_name and landmark_dist:
                result["nearest_landmark"] = landmark_name
                result["distance_from_landmark"] = f"{landmark_dist}m"
                result["travel_tip"] = generate_travel_tip(landmark_dist)
        except (ValueError, TypeError):
            pass

    return result


def get_current_time_of_day() -> str:
    """현재 한국 시간 기준 시간대 반환"""
    hour = get_korea_time().hour

    if 6 <= hour < 10:
        return "아침"
    elif 10 <= hour < 14:
        return "점심"
    elif 14 <= hour < 17:
        return "오후"
    elif 17 <= hour < 21:
        return "저녁"
    else:  # 21-6시
        return "심야"


async def get_smart_recommendation(
    location: str,
    situation: str = "혼자",
    time_of_day: str = "",
    weather: str = "",
    count: int = 5
) -> Dict:
    """
    상황/시간/날씨에 맞는 스마트 장소 추천

    Args:
        location: 지역명 (전국 어디든)
        situation: 상황 (혼자, 친구, 데이트, 가족, 비즈니스)
        time_of_day: 시간대 (아침, 점심, 오후, 저녁, 심야) - 비어있으면 현재 한국 시간
        weather: 날씨 (맑음, 흐림, 비, 눈) - 비어있으면 무시
        count: 결과 개수

    Returns:
        상황에 맞는 장소 추천
    """
    # 좌표 조회 (전국 지원)
    coords = await get_location_coordinates_async(location)
    if not coords:
        return {"error": f"지역을 찾을 수 없습니다: {location}"}

    x, y = coords

    # 상황별 키워드
    situation_data = SITUATION_CATEGORIES.get(situation, SITUATION_CATEGORIES["혼자"])
    keywords = situation_data["keywords"].copy()

    # 시간대 자동 감지 (한국 시간 기준)
    if not time_of_day:
        time_of_day = get_current_time_of_day()

    time_data = TIME_RECOMMENDATIONS.get(time_of_day, TIME_RECOMMENDATIONS["오후"])

    # 날씨 키워드 추가
    weather_data = None
    if weather:
        weather_data = WEATHER_RECOMMENDATIONS.get(weather)
        if weather_data and not weather_data["outdoor"]:
            # 비/눈일 때 실내 위주
            keywords = [k for k in keywords if k not in ["공원", "산책", "야외", "테라스"]]

    # 검색 키워드 조합 (상황 + 시간대)
    search_keyword = f"{location} {keywords[0]}"
    if time_of_day in ["아침", "점심", "저녁"]:
        search_keyword = f"{location} {time_data['keywords'][0]}"

    # 장소 검색
    result = await search_place_by_keyword(search_keyword, x, y, 3000, count, "accuracy")

    if "error" in result:
        return result

    # 장소에 강화된 정보 추가 (v3.4) + 랜드마크 정보 (v3.6)
    places_with_links = []
    for i, place in enumerate(result.get("places", []), 1):
        # 가장 가까운 랜드마크 찾기 (지하철역 > 버스터미널)
        place_x = place.get("x", "")
        place_y = place.get("y", "")
        nearest_landmark = None
        if place_x and place_y:
            nearest_landmark = await find_nearest_landmark(place_x, place_y)

        enriched = enrich_place_info(place, situation, time_of_day, i, nearest_landmark=nearest_landmark)
        places_with_links.append(enriched)

    # 결과 구성
    return {
        "location": location,
        "situation": situation,
        "situation_description": situation_data["description"],
        "time_of_day": time_of_day,
        "time_vibe": time_data["vibe"],
        "weather": weather or "정보없음",
        "weather_tip": weather_data["tip"] if weather_data else None,
        "recommended_categories": keywords[:5],
        "places": places_with_links,
        "total_found": result.get("total_count", 0),
        "search_keyword": search_keyword,
        "tip": f"각 장소의 '운영시간은 카카오맵에서 확인하세요' 링크를 클릭하세요!",
    }


async def get_weather_based_course(
    location: str,
    situation: str = "데이트",
    weather_sky: str = "",
    rain_prob: int = 0,
    temperature: float = 20,
) -> Dict:
    """
    날씨 기반 코스 추천 (A→B→C 동선)

    Args:
        location: 지역명
        situation: 상황 (혼자, 친구, 데이트, 가족)
        weather_sky: 하늘 상태 (맑음, 구름많음, 흐림)
        rain_prob: 강수확률 (0-100)
        temperature: 현재 기온

    Returns:
        날씨 기반 코스 추천 (순서대로)
    """
    # 좌표 조회
    coords = await get_location_coordinates_async(location)
    if not coords:
        return {"error": f"지역을 찾을 수 없습니다: {location}"}

    x, y = coords

    # 날씨 기반 실내/야외 판단
    is_outdoor_ok = True
    weather_warning = None

    if rain_prob >= 50:
        is_outdoor_ok = False
        weather_warning = f"강수확률 {rain_prob}%! 실내 위주로 추천해요."
    elif temperature < 0:
        weather_warning = f"기온 {temperature}°C! 따뜻한 실내 위주로 추천해요."
        is_outdoor_ok = False
    elif temperature > 33:
        weather_warning = f"기온 {temperature}°C! 에어컨 있는 실내 위주로 추천해요."
        is_outdoor_ok = False
    elif "흐림" in weather_sky:
        weather_warning = "흐린 날씨네요. 실내/야외 모두 괜찮아요."

    # 현재 시간대 파악
    time_of_day = get_current_time_of_day()

    # 코스 구성 (3단계) - 강화된 정보 포함
    course_steps = []
    prev_place_raw = None  # 이전 장소 원본 데이터 (좌표 포함)

    # 1단계: 카페/브런치 (시작)
    step1_keyword = f"{location} 카페" if is_outdoor_ok else f"{location} 북카페"
    step1_result = await search_place_by_keyword(step1_keyword, x, y, 2000, 2, "accuracy")
    if step1_result.get("places"):
        place = step1_result["places"][0]
        enriched = enrich_place_info(place, situation, time_of_day, 1, is_course=True)
        enriched["type"] = "시작"
        enriched["course_tip"] = "여유롭게 대화하며 시작해요"
        course_steps.append(enriched)
        prev_place_raw = place  # 다음 단계를 위해 저장

    # 2단계: 메인 활동
    if situation == "데이트":
        step2_keyword = f"{location} 전시회" if not is_outdoor_ok else f"{location} 공원"
    elif situation == "친구":
        step2_keyword = f"{location} 볼링장" if not is_outdoor_ok else f"{location} 맛집"
    elif situation == "가족":
        step2_keyword = f"{location} 키즈카페" if not is_outdoor_ok else f"{location} 박물관"
    else:
        step2_keyword = f"{location} 서점" if not is_outdoor_ok else f"{location} 산책"

    step2_result = await search_place_by_keyword(step2_keyword, x, y, 3000, 2, "accuracy")
    if step2_result.get("places"):
        place = step2_result["places"][0]
        enriched = enrich_place_info(place, situation, time_of_day, 2, prev_place=prev_place_raw, is_course=True)
        enriched["type"] = "메인"
        enriched["course_tip"] = "오늘의 하이라이트!"
        course_steps.append(enriched)
        prev_place_raw = place  # 다음 단계를 위해 저장

    # 3단계: 식사/마무리
    hour = get_korea_time().hour
    if 11 <= hour < 14:
        step3_keyword = f"{location} 맛집 점심"
    elif 17 <= hour < 21:
        step3_keyword = f"{location} 레스토랑"
    else:
        step3_keyword = f"{location} 맛집"

    step3_result = await search_place_by_keyword(step3_keyword, x, y, 3000, 2, "accuracy")
    if step3_result.get("places"):
        place = step3_result["places"][0]
        enriched = enrich_place_info(place, situation, time_of_day, 3, prev_place=prev_place_raw, is_course=True)
        enriched["type"] = "마무리"
        enriched["course_tip"] = "맛있는 식사로 마무리!"
        course_steps.append(enriched)

    return {
        "location": location,
        "situation": situation,
        "weather": {
            "sky": weather_sky or "정보없음",
            "rain_prob": rain_prob,
            "temperature": temperature,
            "is_outdoor_ok": is_outdoor_ok,
            "warning": weather_warning,
        },
        "course": course_steps,
        "course_summary": " → ".join([s["name"] for s in course_steps]),
        "total_steps": len(course_steps),
        "guide": {
            "how_to_use": "각 장소의 kakao_map_url을 클릭하면 상세 정보/길찾기 가능",
            "what_you_get": "추천이유(why_recommend), 이동방법(how_to_get_there), 알아야 할 것(notice)",
        },
    }
