"""
에어코리아 대기오염정보 API 래퍼
https://www.data.go.kr/data/15073861/openapi.do
"""

import httpx
from typing import Optional
import sys
from pathlib import Path

# 상위 디렉토리를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import api_config, get_pm_grade


class AirQualityAPI:
    """에어코리아 대기오염정보 API 클라이언트"""

    def __init__(self):
        self.api_key = api_config.air_quality_api_key
        self.base_url = api_config.air_quality_base_url
        self.station_url = api_config.station_info_base_url

    async def get_realtime_by_station(self, station_name: str) -> dict:
        """
        측정소별 실시간 대기오염 정보 조회

        Args:
            station_name: 측정소명 (예: "중구", "강남구")
        """
        params = {
            "serviceKey": self.api_key,
            "returnType": "json",
            "numOfRows": 1,
            "pageNo": 1,
            "stationName": station_name,
            "dataTerm": "DAILY",
            "ver": "1.3",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/getMsrstnAcctoRltmMesureDnsty",
                params=params,
                timeout=30.0,
            )
            return self._parse_station_response(response.json(), station_name)

    async def get_realtime_by_sido(self, sido_name: str) -> dict:
        """
        시도별 실시간 대기오염 정보 조회

        Args:
            sido_name: 시도명 (예: "서울", "경기", "부산")
        """
        params = {
            "serviceKey": self.api_key,
            "returnType": "json",
            "numOfRows": 100,
            "pageNo": 1,
            "sidoName": sido_name,
            "ver": "1.3",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/getCtprvnRltmMesureDnsty",
                params=params,
                timeout=30.0,
            )
            return self._parse_sido_response(response.json(), sido_name)

    async def get_forecast(self, search_date: Optional[str] = None) -> dict:
        """
        대기질 예보 조회

        Args:
            search_date: 조회 날짜 (YYYY-MM-DD), None이면 오늘
        """
        from datetime import datetime

        if search_date is None:
            search_date = datetime.now().strftime("%Y-%m-%d")

        params = {
            "serviceKey": self.api_key,
            "returnType": "json",
            "numOfRows": 100,
            "pageNo": 1,
            "searchDate": search_date,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/getMinuDustFrcstDspth",
                params=params,
                timeout=30.0,
            )
            return self._parse_forecast_response(response.json())

    async def get_nearby_station(self, tm_x: float, tm_y: float) -> dict:
        """
        좌표 기반 가까운 측정소 조회

        Args:
            tm_x: TM X 좌표
            tm_y: TM Y 좌표
        """
        params = {
            "serviceKey": self.api_key,
            "returnType": "json",
            "tmX": tm_x,
            "tmY": tm_y,
            "ver": "1.1",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.station_url}/getNearbyMsrstnList",
                params=params,
                timeout=30.0,
            )
            return self._parse_nearby_station_response(response.json())

    def _parse_station_response(self, data: dict, station_name: str) -> dict:
        """측정소별 응답 파싱"""
        try:
            items = data["response"]["body"]["items"]

            if not items:
                return {"error": f"'{station_name}' 측정소 데이터를 찾을 수 없습니다."}

            item = items[0]

            # 수치 파싱 (문자열 또는 "-" 처리)
            def safe_float(val, default=-1):
                try:
                    if val is None or val == "-" or val == "":
                        return default
                    return float(val)
                except (ValueError, TypeError):
                    return default

            pm10 = safe_float(item.get("pm10Value"))
            pm25 = safe_float(item.get("pm25Value"))

            return {
                "station_name": station_name,
                "data_time": item.get("dataTime"),
                "pm10": {
                    "value": pm10,
                    "grade": get_pm_grade(pm10, "pm10"),
                    "unit": "μg/m³",
                },
                "pm25": {
                    "value": pm25,
                    "grade": get_pm_grade(pm25, "pm25"),
                    "unit": "μg/m³",
                },
                "o3": {
                    "value": safe_float(item.get("o3Value")),
                    "unit": "ppm",
                },
                "no2": {
                    "value": safe_float(item.get("no2Value")),
                    "unit": "ppm",
                },
                "co": {
                    "value": safe_float(item.get("coValue")),
                    "unit": "ppm",
                },
                "so2": {
                    "value": safe_float(item.get("so2Value")),
                    "unit": "ppm",
                },
                "khai": {  # 통합대기환경지수
                    "value": safe_float(item.get("khaiValue")),
                    "grade": item.get("khaiGrade"),
                },
            }

        except (KeyError, TypeError, IndexError) as e:
            return {"error": f"응답 파싱 실패: {str(e)}"}

    def _parse_sido_response(self, data: dict, sido_name: str) -> dict:
        """시도별 응답 파싱"""
        try:
            items = data["response"]["body"]["items"]

            if not items:
                return {"error": f"'{sido_name}' 지역 데이터를 찾을 수 없습니다."}

            # 평균값 계산
            pm10_values = []
            pm25_values = []

            stations = []
            for item in items:
                try:
                    pm10 = float(item.get("pm10Value", 0) or 0)
                    pm25 = float(item.get("pm25Value", 0) or 0)

                    if pm10 > 0:
                        pm10_values.append(pm10)
                    if pm25 > 0:
                        pm25_values.append(pm25)

                    stations.append({
                        "station_name": item.get("stationName"),
                        "pm10": pm10,
                        "pm25": pm25,
                    })
                except (ValueError, TypeError):
                    continue

            avg_pm10 = sum(pm10_values) / len(pm10_values) if pm10_values else -1
            avg_pm25 = sum(pm25_values) / len(pm25_values) if pm25_values else -1

            return {
                "sido_name": sido_name,
                "station_count": len(stations),
                "average": {
                    "pm10": {
                        "value": round(avg_pm10, 1),
                        "grade": get_pm_grade(avg_pm10, "pm10"),
                    },
                    "pm25": {
                        "value": round(avg_pm25, 1),
                        "grade": get_pm_grade(avg_pm25, "pm25"),
                    },
                },
                "stations": stations[:10],  # 상위 10개만
            }

        except (KeyError, TypeError) as e:
            return {"error": f"응답 파싱 실패: {str(e)}"}

    def _parse_forecast_response(self, data: dict) -> dict:
        """예보 응답 파싱"""
        try:
            items = data["response"]["body"]["items"]

            if not items:
                return {"error": "예보 데이터를 찾을 수 없습니다."}

            forecasts = []
            for item in items:
                forecasts.append({
                    "inform_code": item.get("informCode"),  # PM10, PM25, O3
                    "inform_date": item.get("informData"),
                    "inform_cause": item.get("informCause"),
                    "inform_overall": item.get("informOverall"),
                    "inform_grade": item.get("informGrade"),
                })

            return {
                "forecasts": forecasts,
                "count": len(forecasts),
            }

        except (KeyError, TypeError) as e:
            return {"error": f"응답 파싱 실패: {str(e)}"}

    def _parse_nearby_station_response(self, data: dict) -> dict:
        """근처 측정소 응답 파싱"""
        try:
            items = data["response"]["body"]["items"]

            if not items:
                return {"error": "근처 측정소를 찾을 수 없습니다."}

            stations = []
            for item in items:
                stations.append({
                    "station_name": item.get("stationName"),
                    "addr": item.get("addr"),
                    "tm": item.get("tm"),  # 거리 (km)
                })

            return {
                "stations": stations,
                "nearest": stations[0] if stations else None,
            }

        except (KeyError, TypeError) as e:
            return {"error": f"응답 파싱 실패: {str(e)}"}


async def get_air_quality(location: str) -> dict:
    """
    특정 지역의 대기질 정보 조회

    Args:
        location: 지역명 또는 측정소명

    Returns:
        대기질 정보
    """
    api = AirQualityAPI()

    # 먼저 측정소명으로 시도
    result = await api.get_realtime_by_station(location)

    if "error" not in result:
        return result

    # 시도명으로 시도
    sido_map = {
        "서울": "서울",
        "부산": "부산",
        "대구": "대구",
        "인천": "인천",
        "광주": "광주",
        "대전": "대전",
        "울산": "울산",
        "세종": "세종",
        "경기": "경기",
        "강원": "강원",
        "충북": "충북",
        "충남": "충남",
        "전북": "전북",
        "전남": "전남",
        "경북": "경북",
        "경남": "경남",
        "제주": "제주",
    }

    for key, sido in sido_map.items():
        if key in location:
            return await api.get_realtime_by_sido(sido)

    # 기본값: 서울
    return await api.get_realtime_by_sido("서울")


async def get_air_quality_forecast() -> dict:
    """
    대기질 예보 조회

    Returns:
        대기질 예보 정보
    """
    api = AirQualityAPI()
    return await api.get_forecast()
