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
from typing import Optional, List, Dict
from urllib.parse import quote, urlencode

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
    """지역명으로 좌표 반환 (한국 전체)"""
    # 정확한 매칭
    if location in KOREA_COORDINATES:
        return KOREA_COORDINATES[location]

    # 부분 매칭 (예: "서울시" -> "서울")
    for key in KOREA_COORDINATES:
        if key in location or location in key:
            return KOREA_COORDINATES[key]

    # 기본값: 서울
    return KOREA_COORDINATES.get("서울")
