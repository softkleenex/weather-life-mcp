"""
Weather Life MCP 설정 관리
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# .env 파일 로드
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


@dataclass
class APIConfig:
    """공공데이터포털 API 설정"""

    # 기상청 단기예보 API
    weather_api_key: str = os.getenv("WEATHER_API_KEY", "")
    weather_base_url: str = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0"

    # 에어코리아 대기오염정보 API
    air_quality_api_key: str = os.getenv("AIR_QUALITY_API_KEY", "")
    air_quality_base_url: str = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc"

    # 에어코리아 측정소정보 API
    station_info_base_url: str = "http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc"


@dataclass
class ServerConfig:
    """서버 설정"""

    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"


@dataclass
class DefaultLocation:
    """기본 위치 설정"""

    # 기상청 격자 좌표 (서울시청 기준)
    nx: int = int(os.getenv("DEFAULT_NX", "60"))
    ny: int = int(os.getenv("DEFAULT_NY", "127"))

    # 미세먼지 측정소
    station_name: str = os.getenv("DEFAULT_STATION", "중구")


# 전역 설정 인스턴스
api_config = APIConfig()
server_config = ServerConfig()
default_location = DefaultLocation()


# 격자 좌표 매핑 (주요 지역)
GRID_COORDINATES = {
    # 서울
    "서울": (60, 127),
    "강남구": (61, 126),
    "강동구": (62, 126),
    "강북구": (61, 128),
    "강서구": (58, 126),
    "관악구": (59, 125),
    "광진구": (62, 126),
    "구로구": (58, 125),
    "금천구": (59, 124),
    "노원구": (61, 129),
    "도봉구": (61, 129),
    "동대문구": (61, 127),
    "동작구": (59, 125),
    "마포구": (59, 127),
    "서대문구": (59, 127),
    "서초구": (61, 125),
    "성동구": (61, 127),
    "성북구": (61, 127),
    "송파구": (62, 126),
    "양천구": (58, 126),
    "영등포구": (58, 126),
    "용산구": (60, 126),
    "은평구": (59, 128),
    "종로구": (60, 127),
    "중구": (60, 127),
    "중랑구": (62, 128),

    # 경기
    "수원": (60, 121),
    "성남": (63, 124),
    "고양": (57, 128),
    "용인": (64, 119),
    "부천": (56, 125),
    "안산": (57, 121),
    "안양": (59, 123),
    "남양주": (64, 128),
    "화성": (57, 119),
    "평택": (51, 119),
    "의정부": (61, 130),
    "시흥": (57, 123),
    "파주": (56, 131),
    "광명": (58, 125),
    "김포": (55, 128),
    "군포": (59, 122),
    "광주": (65, 123),
    "이천": (68, 121),
    "양주": (61, 131),
    "오산": (62, 118),
    "구리": (62, 127),
    "안성": (65, 115),
    "포천": (64, 134),
    "의왕": (60, 122),
    "하남": (64, 126),
    "여주": (71, 121),
    "양평": (69, 125),
    "동두천": (61, 134),
    "과천": (60, 124),

    # 광역시
    "부산": (98, 76),
    "대구": (89, 90),
    "인천": (55, 124),
    "광주광역시": (58, 74),
    "대전": (67, 100),
    "울산": (102, 84),
    "세종": (66, 103),

    # 기타 주요 도시
    "춘천": (73, 134),
    "원주": (76, 122),
    "강릉": (92, 131),
    "청주": (69, 107),
    "천안": (63, 110),
    "전주": (63, 89),
    "목포": (50, 67),
    "여수": (73, 66),
    "순천": (70, 70),
    "포항": (102, 94),
    "경주": (100, 91),
    "거제": (90, 69),
    "제주": (52, 38),
    "서귀포": (52, 33),
}


# 미세먼지 측정소 매핑 (시도별)
MEASUREMENT_STATIONS = {
    "서울": ["중구", "종로구", "강남구", "송파구", "강서구", "영등포구"],
    "부산": ["중구", "서구", "해운대구", "사하구"],
    "대구": ["중구", "수성구", "달서구"],
    "인천": ["중구", "남동구", "부평구"],
    "광주": ["동구", "서구", "북구"],
    "대전": ["중구", "서구", "유성구"],
    "울산": ["중구", "남구", "북구"],
    "경기": ["수원", "성남", "고양", "용인", "안산"],
}


# 기상 상태 코드 매핑
SKY_CODE = {
    "1": "맑음",
    "3": "구름많음",
    "4": "흐림",
}

PTY_CODE = {
    "0": "없음",
    "1": "비",
    "2": "비/눈",
    "3": "눈",
    "4": "소나기",
    "5": "빗방울",
    "6": "빗방울눈날림",
    "7": "눈날림",
}


# 미세먼지 등급 기준
AIR_QUALITY_GRADE = {
    "pm10": {  # 미세먼지
        "좋음": (0, 30),
        "보통": (31, 80),
        "나쁨": (81, 150),
        "매우나쁨": (151, float("inf")),
    },
    "pm25": {  # 초미세먼지
        "좋음": (0, 15),
        "보통": (16, 35),
        "나쁨": (36, 75),
        "매우나쁨": (76, float("inf")),
    },
}


def get_pm_grade(value: float, pm_type: str = "pm10") -> str:
    """미세먼지 수치를 등급으로 변환"""
    if value < 0:
        return "측정불가"

    grades = AIR_QUALITY_GRADE.get(pm_type, AIR_QUALITY_GRADE["pm10"])
    for grade, (low, high) in grades.items():
        if low <= value <= high:
            return grade
    return "매우나쁨"


def get_grid_coords(location: str) -> tuple[int, int]:
    """지역명으로 격자 좌표 조회"""
    # 정확히 일치하는 경우
    if location in GRID_COORDINATES:
        return GRID_COORDINATES[location]

    # 부분 일치 검색
    for name, coords in GRID_COORDINATES.items():
        if location in name or name in location:
            return coords

    # 기본값 반환 (서울)
    return (default_location.nx, default_location.ny)
