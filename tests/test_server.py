"""
Weather Life MCP 서버 테스트
"""

import pytest
import sys
from pathlib import Path

# 상위 디렉토리를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.outfit_recommender import (
    WeatherCondition,
    AirQualityCondition,
    get_outfit_recommendation,
    calculate_outing_score,
    get_comprehensive_recommendation,
)
from config.settings import get_grid_coords, get_pm_grade


class TestGridCoordinates:
    """격자 좌표 테스트"""

    def test_seoul_coordinates(self):
        """서울 좌표 테스트"""
        nx, ny = get_grid_coords("서울")
        assert nx == 60
        assert ny == 127

    def test_gangnam_coordinates(self):
        """강남구 좌표 테스트"""
        nx, ny = get_grid_coords("강남구")
        assert nx == 61
        assert ny == 126

    def test_busan_coordinates(self):
        """부산 좌표 테스트"""
        nx, ny = get_grid_coords("부산")
        assert nx == 98
        assert ny == 76

    def test_unknown_location_returns_default(self):
        """알 수 없는 지역은 기본값(서울) 반환"""
        nx, ny = get_grid_coords("알수없는지역")
        assert nx == 60  # 서울 기본값
        assert ny == 127


class TestPMGrade:
    """미세먼지 등급 테스트"""

    def test_pm10_good(self):
        """PM10 좋음 등급"""
        assert get_pm_grade(20, "pm10") == "좋음"

    def test_pm10_moderate(self):
        """PM10 보통 등급"""
        assert get_pm_grade(50, "pm10") == "보통"

    def test_pm10_bad(self):
        """PM10 나쁨 등급"""
        assert get_pm_grade(100, "pm10") == "나쁨"

    def test_pm10_very_bad(self):
        """PM10 매우나쁨 등급"""
        assert get_pm_grade(200, "pm10") == "매우나쁨"

    def test_pm25_good(self):
        """PM2.5 좋음 등급"""
        assert get_pm_grade(10, "pm25") == "좋음"

    def test_pm25_bad(self):
        """PM2.5 나쁨 등급"""
        assert get_pm_grade(50, "pm25") == "나쁨"

    def test_invalid_value(self):
        """음수 값은 측정불가"""
        assert get_pm_grade(-1, "pm10") == "측정불가"


class TestOutfitRecommendation:
    """옷차림 추천 테스트"""

    def test_summer_outfit(self):
        """여름 옷차림 (28도 이상)"""
        weather = WeatherCondition(temperature=30)
        result = get_outfit_recommendation(weather)

        assert result["category"] == "한여름"
        assert "반팔" in str(result["recommendation"]["top"])

    def test_winter_outfit(self):
        """겨울 옷차림 (5도 이하)"""
        weather = WeatherCondition(temperature=3)
        result = get_outfit_recommendation(weather)

        assert result["category"] == "한겨울"
        assert "패딩" in str(result["recommendation"]["outer"])

    def test_spring_outfit(self):
        """봄 옷차림 (17-19도)"""
        weather = WeatherCondition(temperature=18)
        result = get_outfit_recommendation(weather)

        assert result["category"] == "선선한 날씨"

    def test_rain_adds_umbrella(self):
        """비 예보시 우산 추가"""
        weather = WeatherCondition(temperature=20, precipitation_type="비")
        result = get_outfit_recommendation(weather)

        assert "우산" in result["recommendation"]["accessories"]

    def test_high_precipitation_prob_adds_umbrella(self):
        """강수확률 높을 때 우산 추가"""
        weather = WeatherCondition(temperature=20, precipitation_prob=80)
        result = get_outfit_recommendation(weather)

        assert "우산" in result["recommendation"]["accessories"]


class TestOutingScore:
    """외출 적합도 점수 테스트"""

    def test_perfect_conditions(self):
        """완벽한 조건 (높은 점수)"""
        weather = WeatherCondition(
            temperature=22,
            humidity=50,
            wind_speed=2.0,
            precipitation_prob=10,
            precipitation_type="없음",
        )
        air_quality = AirQualityCondition(
            pm10_value=20, pm10_grade="좋음", pm25_value=10, pm25_grade="좋음"
        )

        result = calculate_outing_score(weather, air_quality)
        assert result["score"] >= 80
        assert result["grade"] == "좋음"

    def test_bad_air_quality(self):
        """미세먼지 나쁨 (낮은 점수)"""
        weather = WeatherCondition(temperature=22)
        air_quality = AirQualityCondition(
            pm10_value=100, pm10_grade="나쁨", pm25_value=50, pm25_grade="나쁨"
        )

        result = calculate_outing_score(weather, air_quality)
        assert result["score"] < 80
        assert "미세먼지" in str(result["factors"]) or "초미세먼지" in str(result["factors"])

    def test_rainy_day(self):
        """비 오는 날 (낮은 점수)"""
        weather = WeatherCondition(temperature=20, precipitation_type="비")
        air_quality = AirQualityCondition()

        result = calculate_outing_score(weather, air_quality)
        assert result["score"] < 80
        assert "강수" in str(result["factors"])

    def test_extreme_temperature(self):
        """극한 기온 (낮은 점수)"""
        # 폭염
        weather = WeatherCondition(temperature=38)
        air_quality = AirQualityCondition()
        result = calculate_outing_score(weather, air_quality)
        assert result["detail_scores"]["temperature"] < 60

        # 한파
        weather = WeatherCondition(temperature=-10)
        result = calculate_outing_score(weather, air_quality)
        assert result["detail_scores"]["temperature"] < 40


class TestComprehensiveRecommendation:
    """종합 추천 테스트"""

    def test_mask_added_for_bad_air(self):
        """미세먼지 나쁨 시 마스크 추가"""
        weather = WeatherCondition(temperature=20)
        air_quality = AirQualityCondition(
            pm10_value=100, pm10_grade="나쁨", pm25_value=50, pm25_grade="나쁨"
        )

        result = get_comprehensive_recommendation(weather, air_quality)
        accessories = result["outfit_recommendation"]["recommendation"]["accessories"]

        assert "마스크" in accessories

    def test_summary_generated(self):
        """요약 문장 생성 확인"""
        weather = WeatherCondition(temperature=20)
        air_quality = AirQualityCondition()

        result = get_comprehensive_recommendation(weather, air_quality)

        assert "summary" in result
        assert len(result["summary"]) > 0


# =============================================================================
# API 통합 테스트 (실제 API 호출 - 선택적 실행)
# =============================================================================


@pytest.mark.asyncio
@pytest.mark.skip(reason="실제 API 호출 필요, 로컬 테스트 시 skip 해제")
class TestAPIIntegration:
    """API 통합 테스트"""

    async def test_get_weather(self):
        """날씨 API 호출 테스트"""
        from src.weather_api import get_current_weather

        result = await get_current_weather("서울")
        assert "error" not in result or "location" in result

    async def test_get_air_quality(self):
        """미세먼지 API 호출 테스트"""
        from src.air_quality_api import get_air_quality

        result = await get_air_quality("서울")
        assert "error" not in result or "location" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
