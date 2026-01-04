"""
기상청 단기예보 API 래퍼
https://www.data.go.kr/data/15084084/openapi.do
"""

import httpx
from datetime import datetime, timedelta
from typing import Optional
import sys
from pathlib import Path

# 상위 디렉토리를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import api_config, SKY_CODE, PTY_CODE, get_grid_coords


class WeatherAPI:
    """기상청 단기예보 API 클라이언트"""

    def __init__(self):
        self.api_key = api_config.weather_api_key
        self.base_url = api_config.weather_base_url

    def _get_base_datetime(self) -> tuple[str, str]:
        """
        API 호출을 위한 기준 날짜/시간 계산
        단기예보는 02, 05, 08, 11, 14, 17, 20, 23시에 발표
        """
        now = datetime.now()
        base_times = ["0200", "0500", "0800", "1100", "1400", "1700", "2000", "2300"]

        # 현재 시간보다 이전의 가장 최근 발표 시간 찾기
        current_time = now.strftime("%H%M")

        base_time = "2300"  # 기본값 (전날 23시)
        base_date = (now - timedelta(days=1)).strftime("%Y%m%d")

        for bt in base_times:
            if current_time >= bt:
                base_time = bt
                base_date = now.strftime("%Y%m%d")

        # 발표 후 API 반영까지 약 10분 소요
        if int(current_time) < int(base_time) + 10:
            # 이전 발표 시간 사용
            idx = base_times.index(base_time)
            if idx > 0:
                base_time = base_times[idx - 1]
            else:
                base_time = "2300"
                base_date = (now - timedelta(days=1)).strftime("%Y%m%d")

        return base_date, base_time

    async def get_ultra_short_forecast(
        self, nx: int, ny: int
    ) -> dict:
        """
        초단기실황 조회
        현재 기상 상태를 조회합니다.
        """
        now = datetime.now()
        base_date = now.strftime("%Y%m%d")
        # 정시 기준 (매시 40분 이후 해당 시각 데이터 제공)
        if now.minute < 40:
            base_time = (now - timedelta(hours=1)).strftime("%H00")
        else:
            base_time = now.strftime("%H00")

        params = {
            "serviceKey": self.api_key,
            "numOfRows": 10,
            "pageNo": 1,
            "dataType": "JSON",
            "base_date": base_date,
            "base_time": base_time,
            "nx": nx,
            "ny": ny,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/getUltraSrtNcst",
                params=params,
                timeout=30.0,
            )
            # 에러 처리
            if response.status_code != 200:
                return {"error": f"API 호출 실패: HTTP {response.status_code}"}
            try:
                return self._parse_response(response.json())
            except Exception as e:
                return {"error": f"JSON 파싱 실패: {str(e)}, 응답: {response.text[:200]}"}

    async def get_short_forecast(
        self, nx: int, ny: int, num_of_rows: int = 100
    ) -> dict:
        """
        단기예보 조회
        오늘~모레까지의 예보를 조회합니다.
        """
        base_date, base_time = self._get_base_datetime()

        params = {
            "serviceKey": self.api_key,
            "numOfRows": num_of_rows,
            "pageNo": 1,
            "dataType": "JSON",
            "base_date": base_date,
            "base_time": base_time,
            "nx": nx,
            "ny": ny,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/getVilageFcst",
                params=params,
                timeout=30.0,
            )
            # 에러 처리
            if response.status_code != 200:
                return {"error": f"API 호출 실패: HTTP {response.status_code}"}
            try:
                return self._parse_forecast_response(response.json())
            except Exception as e:
                return {"error": f"JSON 파싱 실패: {str(e)}, 응답: {response.text[:200]}"}

    def _parse_response(self, data: dict) -> dict:
        """초단기실황 응답 파싱"""
        try:
            items = data["response"]["body"]["items"]["item"]
            result = {}

            for item in items:
                category = item["category"]
                value = item["obsrValue"]

                if category == "T1H":  # 기온
                    result["temperature"] = float(value)
                elif category == "RN1":  # 1시간 강수량
                    result["precipitation"] = value
                elif category == "UUU":  # 동서바람성분
                    result["wind_u"] = float(value)
                elif category == "VVV":  # 남북바람성분
                    result["wind_v"] = float(value)
                elif category == "REH":  # 습도
                    result["humidity"] = int(value)
                elif category == "PTY":  # 강수형태
                    result["precipitation_type"] = PTY_CODE.get(value, value)
                elif category == "VEC":  # 풍향
                    result["wind_direction"] = int(value)
                elif category == "WSD":  # 풍속
                    result["wind_speed"] = float(value)

            return result

        except (KeyError, TypeError) as e:
            return {"error": f"응답 파싱 실패: {str(e)}"}

    def _parse_forecast_response(self, data: dict) -> dict:
        """단기예보 응답 파싱"""
        try:
            items = data["response"]["body"]["items"]["item"]

            # 시간대별로 그룹화
            forecasts = {}
            for item in items:
                fcst_date = item["fcstDate"]
                fcst_time = item["fcstTime"]
                key = f"{fcst_date}_{fcst_time}"

                if key not in forecasts:
                    forecasts[key] = {
                        "date": fcst_date,
                        "time": fcst_time,
                    }

                category = item["category"]
                value = item["fcstValue"]

                if category == "TMP":  # 기온
                    forecasts[key]["temperature"] = int(value)
                elif category == "SKY":  # 하늘상태
                    forecasts[key]["sky"] = SKY_CODE.get(value, value)
                elif category == "PTY":  # 강수형태
                    forecasts[key]["precipitation_type"] = PTY_CODE.get(value, value)
                elif category == "POP":  # 강수확률
                    forecasts[key]["precipitation_probability"] = int(value)
                elif category == "REH":  # 습도
                    forecasts[key]["humidity"] = int(value)
                elif category == "WSD":  # 풍속
                    forecasts[key]["wind_speed"] = float(value)
                elif category == "TMN":  # 최저기온
                    forecasts[key]["min_temperature"] = int(value)
                elif category == "TMX":  # 최고기온
                    forecasts[key]["max_temperature"] = int(value)

            # 리스트로 변환 및 정렬
            forecast_list = sorted(forecasts.values(), key=lambda x: f"{x['date']}{x['time']}")

            return {
                "forecasts": forecast_list,
                "count": len(forecast_list),
            }

        except (KeyError, TypeError) as e:
            return {"error": f"응답 파싱 실패: {str(e)}"}


async def get_current_weather(location: str) -> dict:
    """
    특정 지역의 현재 날씨 조회

    Args:
        location: 지역명 (예: "서울", "강남구", "부산")

    Returns:
        현재 날씨 정보
    """
    api = WeatherAPI()
    nx, ny = get_grid_coords(location)

    current = await api.get_ultra_short_forecast(nx, ny)

    if "error" in current:
        return current

    return {
        "location": location,
        "coordinates": {"nx": nx, "ny": ny},
        "current": current,
    }


async def get_weather_forecast(location: str) -> dict:
    """
    특정 지역의 날씨 예보 조회

    Args:
        location: 지역명 (예: "서울", "강남구", "부산")

    Returns:
        날씨 예보 정보
    """
    api = WeatherAPI()
    nx, ny = get_grid_coords(location)

    forecast = await api.get_short_forecast(nx, ny)

    if "error" in forecast:
        return forecast

    # 오늘 날씨 요약
    today = datetime.now().strftime("%Y%m%d")
    today_forecasts = [f for f in forecast["forecasts"] if f["date"] == today]

    # 최저/최고 기온 추출
    temps = [f.get("temperature", 0) for f in today_forecasts if "temperature" in f]
    min_temp = min(temps) if temps else None
    max_temp = max(temps) if temps else None

    # 대표 날씨 (현재 시간대 기준)
    current_hour = datetime.now().strftime("%H00")
    current_forecast = next(
        (f for f in today_forecasts if f["time"] >= current_hour),
        today_forecasts[0] if today_forecasts else None,
    )

    return {
        "location": location,
        "coordinates": {"nx": nx, "ny": ny},
        "today_summary": {
            "min_temperature": min_temp,
            "max_temperature": max_temp,
            "sky": current_forecast.get("sky") if current_forecast else None,
            "precipitation_type": current_forecast.get("precipitation_type") if current_forecast else None,
            "precipitation_probability": current_forecast.get("precipitation_probability") if current_forecast else None,
        },
        "forecasts": forecast["forecasts"][:24],  # 24시간 예보만
    }
