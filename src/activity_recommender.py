"""
한국 특화 활동 추천 시스템

자체 개발 지수:
- 빨래지수 (기상청 서비스 종료 → 부활!)
- 등산지수
- 피크닉지수 (한강/공원)
- 세차지수
- 김장지수 (11-12월 한정)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class WeatherData:
    """날씨 데이터"""
    temperature: float  # 기온 (°C)
    humidity: float  # 습도 (%)
    wind_speed: float  # 풍속 (m/s)
    rain_prob: float  # 강수확률 (%)
    rain_prob_tomorrow: float = 0  # 내일 강수확률
    sky: str = "맑음"  # 하늘 상태
    pm25_grade: str = "보통"  # 초미세먼지 등급
    pm25_value: float = 25  # 초미세먼지 수치
    uv_index: int = 5  # 자외선지수
    temp_min: float = None  # 최저기온
    temp_max: float = None  # 최고기온


# =============================================================================
# 빨래지수 (기상청 서비스 종료 → 자체 부활!)
# =============================================================================

def calculate_laundry_index(weather: WeatherData) -> dict:
    """
    빨래 건조 적합도 계산 (0-100)

    최적 조건:
    - 기온: 15-25°C
    - 습도: 40% 이하
    - 강수확률: 20% 미만
    - 풍속: 2-5m/s (적당한 바람)

    한국 특화:
    - 아파트 베란다 건조 고려
    - 장마철/겨울철 특별 처리
    """
    score = 100
    factors = []
    tips = []

    # 1. 강수확률 (가장 중요!)
    if weather.rain_prob >= 70:
        score -= 60
        factors.append(f"강수확률 {weather.rain_prob}% (빨래 금지)")
    elif weather.rain_prob >= 50:
        score -= 40
        factors.append(f"강수확률 {weather.rain_prob}% (위험)")
    elif weather.rain_prob >= 30:
        score -= 20
        factors.append(f"강수확률 {weather.rain_prob}% (주의)")
        tips.append("오전에 빨래하고 오후 2시 전에 걷으세요")

    # 2. 습도
    if weather.humidity >= 85:
        score -= 35
        factors.append(f"습도 {weather.humidity}% (건조 불가)")
        tips.append("제습기/건조기 사용 권장")
    elif weather.humidity >= 70:
        score -= 25
        factors.append(f"습도 {weather.humidity}% (건조 느림)")
    elif weather.humidity >= 60:
        score -= 10
        factors.append(f"습도 {weather.humidity}%")
    elif weather.humidity <= 40:
        score += 5
        factors.append(f"습도 {weather.humidity}% (건조 최적)")

    # 3. 기온
    if weather.temperature < 5:
        score -= 25
        factors.append(f"기온 {weather.temperature}°C (동파 주의)")
        tips.append("실내 건조 권장")
    elif weather.temperature < 10:
        score -= 15
        factors.append(f"기온 {weather.temperature}°C (건조 느림)")
    elif 15 <= weather.temperature <= 25:
        score += 5
        factors.append(f"기온 {weather.temperature}°C (최적)")

    # 4. 풍속
    if weather.wind_speed < 1:
        score -= 10
        factors.append("바람 없음 (건조 느림)")
    elif weather.wind_speed > 10:
        score -= 15
        factors.append(f"강풍 {weather.wind_speed}m/s (빨래 날아감)")
        tips.append("빨래집게 필수!")
    elif 2 <= weather.wind_speed <= 5:
        score += 5
        factors.append(f"바람 {weather.wind_speed}m/s (최적)")

    # 5. 미세먼지
    if weather.pm25_grade in ["나쁨", "매우나쁨"]:
        score -= 20
        factors.append(f"미세먼지 {weather.pm25_grade}")
        tips.append("실내 건조 권장 (미세먼지)")

    # 점수 보정
    score = max(0, min(100, score))

    # 등급 판정
    if score >= 80:
        grade = "매우좋음"
        emoji = "☀️"
        message = "빨래하기 완벽한 날!"
    elif score >= 60:
        grade = "좋음"
        emoji = "🌤️"
        message = "빨래하기 좋은 날"
    elif score >= 40:
        grade = "보통"
        emoji = "⛅"
        message = "빨래 가능하지만 주의 필요"
    elif score >= 20:
        grade = "나쁨"
        emoji = "🌧️"
        message = "빨래 비추천"
    else:
        grade = "매우나쁨"
        emoji = "❌"
        message = "빨래 금지! 실내 건조하세요"

    return {
        "score": score,
        "grade": grade,
        "emoji": emoji,
        "message": message,
        "factors": factors,
        "tips": tips if tips else ["오후 2시 전에 걷는 것이 좋아요"],
    }


# =============================================================================
# 등산지수 (한국인 등산 사랑 반영!)
# =============================================================================

def calculate_hiking_index(weather: WeatherData) -> dict:
    """
    등산 적합도 계산 (0-100)

    최적 조건:
    - 기온: 15-22°C
    - 습도: 40-60%
    - 강수확률: 20% 미만
    - 풍속: 5m/s 미만
    - 미세먼지: 좋음
    - 자외선: 보통 이하

    한국 특화:
    - 북한산/관악산 등 수도권 등산 고려
    - 일출 등산, 야간 등산 안내
    """
    score = 100
    factors = []
    tips = []
    warnings = []

    # 1. 강수확률 (안전 최우선!)
    if weather.rain_prob >= 60:
        score -= 50
        factors.append(f"강수확률 {weather.rain_prob}%")
        warnings.append("비 예보! 등산 자제")
    elif weather.rain_prob >= 40:
        score -= 30
        factors.append(f"강수확률 {weather.rain_prob}%")
        warnings.append("우비 필수")
    elif weather.rain_prob >= 20:
        score -= 10
        tips.append("가벼운 우비 챙기세요")

    # 2. 기온
    if weather.temperature < 0:
        score -= 30
        factors.append(f"기온 {weather.temperature}°C (혹한)")
        warnings.append("동상 위험! 방한 철저히")
        tips.append("핫팩, 보온병 필수")
    elif weather.temperature < 5:
        score -= 15
        factors.append(f"기온 {weather.temperature}°C (추움)")
        tips.append("방한 장비 필수")
    elif weather.temperature > 30:
        score -= 35
        factors.append(f"기온 {weather.temperature}°C (폭염)")
        warnings.append("열사병 위험! 이른 아침만 추천")
        tips.append("새벽 등산 추천 (5-8시)")
    elif weather.temperature > 28:
        score -= 20
        factors.append(f"기온 {weather.temperature}°C (더움)")
        tips.append("물 충분히, 그늘 코스 추천")
    elif 15 <= weather.temperature <= 22:
        score += 10
        factors.append(f"기온 {weather.temperature}°C (최적)")

    # 3. 미세먼지 (호흡기 건강!)
    if weather.pm25_grade == "매우나쁨":
        score -= 40
        factors.append(f"미세먼지 {weather.pm25_grade}")
        warnings.append("야외 운동 금지!")
    elif weather.pm25_grade == "나쁨":
        score -= 25
        factors.append(f"미세먼지 {weather.pm25_grade}")
        warnings.append("마스크 착용 등산")
    elif weather.pm25_grade == "보통":
        score -= 5
    elif weather.pm25_grade == "좋음":
        score += 5
        factors.append("미세먼지 좋음")

    # 4. 풍속 (산 정상 바람!)
    if weather.wind_speed > 15:
        score -= 30
        factors.append(f"강풍 {weather.wind_speed}m/s")
        warnings.append("정상부 강풍 주의!")
    elif weather.wind_speed > 10:
        score -= 15
        factors.append(f"바람 {weather.wind_speed}m/s")
        tips.append("바람막이 필수")
    elif 3 <= weather.wind_speed <= 7:
        score += 5
        tips.append("시원한 바람이 불어요")

    # 5. 습도
    if weather.humidity > 80:
        score -= 15
        factors.append(f"습도 {weather.humidity}%")
        tips.append("땀이 잘 안 마르니 여벌 옷 챙기세요")
    elif 40 <= weather.humidity <= 60:
        score += 5

    # 6. 자외선
    if weather.uv_index >= 8:
        score -= 10
        tips.append("선크림, 모자 필수!")

    # 점수 보정
    score = max(0, min(100, score))

    # 등급 판정
    if score >= 85:
        grade = "최적"
        emoji = "⛰️"
        message = "등산하기 완벽한 날씨!"
    elif score >= 70:
        grade = "좋음"
        emoji = "🥾"
        message = "등산하기 좋은 날"
    elif score >= 50:
        grade = "보통"
        emoji = "🌤️"
        message = "등산 가능하지만 주의사항 있음"
    elif score >= 30:
        grade = "주의"
        emoji = "⚠️"
        message = "등산 시 주의 필요"
    else:
        grade = "위험"
        emoji = "❌"
        message = "등산 자제 권고"

    # 추천 산 (서울 기준)
    if score >= 70:
        recommendations = ["북한산", "관악산", "도봉산", "수락산"]
    elif score >= 50:
        recommendations = ["인왕산", "안산", "아차산"]  # 비교적 낮은 산
    else:
        recommendations = []

    return {
        "score": score,
        "grade": grade,
        "emoji": emoji,
        "message": message,
        "factors": factors,
        "warnings": warnings,
        "tips": tips if tips else ["등산화 착용, 물 1L 이상 준비"],
        "recommendations": recommendations,
    }


# =============================================================================
# 피크닉지수 (한강/공원)
# =============================================================================

def calculate_picnic_index(weather: WeatherData) -> dict:
    """
    한강/공원 피크닉 적합도 (0-100)

    최적 조건:
    - 기온: 20-26°C
    - 강수확률: 10% 미만
    - 미세먼지: 보통 이상
    - 풍속: 3m/s 이하 (돗자리 날아감 방지)
    - 습도: 70% 미만

    한국 특화:
    - 한강공원 치맥 문화 반영
    - 돗자리, 텐트 설치 고려
    """
    score = 100
    factors = []
    tips = []

    # 1. 강수확률
    if weather.rain_prob >= 50:
        score -= 50
        factors.append(f"강수확률 {weather.rain_prob}%")
        tips.append("실내 카페 추천")
    elif weather.rain_prob >= 30:
        score -= 25
        factors.append(f"강수확률 {weather.rain_prob}%")
        tips.append("돗자리 대신 벤치 이용")
    elif weather.rain_prob >= 10:
        score -= 10

    # 2. 기온 (치맥하기 좋은 온도!)
    if weather.temperature < 10:
        score -= 35
        factors.append(f"기온 {weather.temperature}°C (추움)")
        tips.append("따뜻한 음료 준비")
    elif weather.temperature < 15:
        score -= 20
        tips.append("담요 챙기세요")
    elif weather.temperature > 32:
        score -= 30
        factors.append(f"기온 {weather.temperature}°C (폭염)")
        tips.append("그늘 텐트 필수, 저녁 시간 추천")
    elif weather.temperature > 28:
        score -= 15
        tips.append("양산/그늘막 챙기세요")
    elif 20 <= weather.temperature <= 26:
        score += 10
        factors.append(f"기온 {weather.temperature}°C (최적)")

    # 3. 미세먼지
    if weather.pm25_grade == "매우나쁨":
        score -= 40
        factors.append(f"미세먼지 {weather.pm25_grade}")
    elif weather.pm25_grade == "나쁨":
        score -= 25
        factors.append(f"미세먼지 {weather.pm25_grade}")
    elif weather.pm25_grade == "좋음":
        score += 5

    # 4. 풍속 (돗자리 날아감!)
    if weather.wind_speed > 8:
        score -= 25
        factors.append(f"강풍 {weather.wind_speed}m/s")
        tips.append("텐트/돗자리 고정 필수")
    elif weather.wind_speed > 5:
        score -= 10
        tips.append("돗자리 모서리 고정")
    elif weather.wind_speed < 1:
        if weather.temperature > 25:
            score -= 10
            tips.append("바람 없어서 더울 수 있어요")

    # 5. 습도
    if weather.humidity > 80:
        score -= 15
        factors.append(f"습도 {weather.humidity}%")
        tips.append("끈적끈적할 수 있어요")

    # 점수 보정
    score = max(0, min(100, score))

    # 등급 판정
    if score >= 85:
        grade = "최적"
        emoji = "🧺"
        message = "피크닉 완벽한 날!"
    elif score >= 70:
        grade = "좋음"
        emoji = "🌸"
        message = "피크닉하기 좋은 날"
    elif score >= 50:
        grade = "보통"
        emoji = "🌤️"
        message = "피크닉 가능"
    elif score >= 30:
        grade = "별로"
        emoji = "😐"
        message = "피크닉 비추천"
    else:
        grade = "금지"
        emoji = "❌"
        message = "피크닉 하지 마세요"

    # 추천 장소 (서울)
    if score >= 70:
        spots = ["여의도한강공원", "반포한강공원", "뚝섬한강공원", "망원한강공원"]
    elif score >= 50:
        spots = ["올림픽공원", "서울숲"]  # 그늘 많은 곳
    else:
        spots = []

    # 치맥 타임 추천
    hour = datetime.now().hour
    if score >= 60:
        if weather.temperature > 25:
            chimaek_time = "오후 5-7시 (해질녘)"
        else:
            chimaek_time = "오후 3-6시"
    else:
        chimaek_time = "오늘은 실내 추천"

    return {
        "score": score,
        "grade": grade,
        "emoji": emoji,
        "message": message,
        "factors": factors,
        "tips": tips if tips else ["돗자리, 음료, 간식 챙기세요"],
        "recommended_spots": spots,
        "chimaek_time": chimaek_time,
    }


# =============================================================================
# 세차지수
# =============================================================================

def calculate_car_wash_index(weather: WeatherData) -> dict:
    """
    세차 적합도 계산 (0-100)

    고려 요소:
    - 오늘/내일 강수확률
    - 미세먼지 (세차 후 다시 더러워짐)
    - 황사 여부 (봄철)
    """
    score = 100
    factors = []
    tips = []

    # 1. 오늘 강수확률
    if weather.rain_prob >= 50:
        score -= 50
        factors.append(f"오늘 강수확률 {weather.rain_prob}%")
    elif weather.rain_prob >= 30:
        score -= 25
        factors.append(f"오늘 강수확률 {weather.rain_prob}%")

    # 2. 내일 강수확률 (중요!)
    if weather.rain_prob_tomorrow >= 70:
        score -= 40
        factors.append(f"내일 강수확률 {weather.rain_prob_tomorrow}%")
        tips.append("내일 비 오면 헛수고!")
    elif weather.rain_prob_tomorrow >= 50:
        score -= 25
        factors.append(f"내일 강수확률 {weather.rain_prob_tomorrow}%")
    elif weather.rain_prob_tomorrow >= 30:
        score -= 10

    # 3. 미세먼지
    if weather.pm25_grade == "매우나쁨":
        score -= 35
        factors.append(f"미세먼지 {weather.pm25_grade}")
        tips.append("세차해도 금방 더러워져요")
    elif weather.pm25_grade == "나쁨":
        score -= 20
        factors.append(f"미세먼지 {weather.pm25_grade}")
    elif weather.pm25_grade == "좋음":
        score += 5
        factors.append("미세먼지 좋음")

    # 4. 황사 (봄철)
    month = datetime.now().month
    if month in [3, 4, 5]:
        if weather.pm25_value > 50:
            score -= 20
            factors.append("황사 가능성")
            tips.append("봄철 황사 주의")

    # 5. 기온 (너무 추우면 동결)
    if weather.temperature < 0:
        score -= 30
        factors.append(f"기온 {weather.temperature}°C")
        tips.append("세차 후 물기 동결 주의!")
    elif weather.temperature < 5:
        score -= 15
        tips.append("물기 빨리 닦아주세요")

    # 점수 보정
    score = max(0, min(100, score))

    # 등급 판정
    if score >= 80:
        grade = "최적"
        emoji = "🚗✨"
        message = "세차하기 완벽한 날!"
    elif score >= 60:
        grade = "좋음"
        emoji = "🚙"
        message = "세차하기 좋은 날"
    elif score >= 40:
        grade = "보통"
        emoji = "🚕"
        message = "세차해도 되지만..."
    elif score >= 20:
        grade = "비추"
        emoji = "😐"
        message = "세차 미루세요"
    else:
        grade = "금지"
        emoji = "❌"
        message = "세차하지 마세요!"

    return {
        "score": score,
        "grade": grade,
        "emoji": emoji,
        "message": message,
        "factors": factors,
        "tips": tips if tips else ["오전 세차 후 드라이브 추천!"],
    }


# =============================================================================
# 김장지수 (11-12월 한정, 세계 유일 한국 특화!)
# =============================================================================

def calculate_kimjang_index(weather: WeatherData) -> dict:
    """
    김장 적합도 계산

    최적 조건 (기상청 기준):
    - 평균기온: 4°C 이하
    - 최저기온: 0°C 이하
    - 일교차: 크지 않음
    - 평균기온 4°C 이하가 3일 이상 지속

    작업 조건:
    - 비/눈 없음
    - 야외 작업 가능 온도
    """
    month = datetime.now().month

    # 11-12월만 서비스
    if month not in [10, 11, 12, 1]:
        return {
            "available": False,
            "message": "김장지수는 10월~1월에만 제공됩니다.",
            "tips": ["김장 적기: 보통 11월 중순~12월 초"],
        }

    score = 100
    factors = []
    tips = []

    temp = weather.temperature
    temp_min = weather.temp_min if weather.temp_min else temp - 5
    temp_max = weather.temp_max if weather.temp_max else temp + 5

    # 1. 평균 기온 (가장 중요!)
    if temp <= 0:
        score += 10
        factors.append(f"평균기온 {temp}°C (최적)")
        tips.append("배추 절이기 최적 온도")
    elif temp <= 4:
        score += 5
        factors.append(f"평균기온 {temp}°C (적합)")
    elif temp <= 8:
        score -= 10
        factors.append(f"평균기온 {temp}°C (다소 높음)")
        tips.append("서늘한 곳에서 작업하세요")
    elif temp <= 12:
        score -= 25
        factors.append(f"평균기온 {temp}°C (높음)")
        tips.append("김장 미루는 것 추천")
    else:
        score -= 50
        factors.append(f"평균기온 {temp}°C (부적합)")

    # 2. 최저기온
    if temp_min <= -5:
        score -= 15
        factors.append(f"최저 {temp_min}°C (혹한)")
        tips.append("야외 작업 시 동상 주의")
    elif temp_min <= 0:
        score += 5
        factors.append(f"최저 {temp_min}°C (적합)")

    # 3. 강수확률
    if weather.rain_prob >= 50:
        score -= 40
        factors.append(f"강수확률 {weather.rain_prob}%")
        tips.append("비/눈 오는 날 김장 비추천")
    elif weather.rain_prob >= 30:
        score -= 20

    # 4. 바람 (야외 작업 시)
    if weather.wind_speed > 10:
        score -= 15
        factors.append(f"강풍 {weather.wind_speed}m/s")
        tips.append("실내 작업 권장")
    elif weather.wind_speed > 5:
        score -= 5

    # 점수 보정
    score = max(0, min(100, score))

    # 등급 판정
    if score >= 85:
        grade = "최적"
        emoji = "🥬"
        message = "김장하기 딱 좋은 날씨!"
    elif score >= 70:
        grade = "좋음"
        emoji = "🌶️"
        message = "김장하기 좋은 날"
    elif score >= 50:
        grade = "보통"
        emoji = "👍"
        message = "김장 가능"
    elif score >= 30:
        grade = "별로"
        emoji = "😐"
        message = "김장 미루는 것 추천"
    else:
        grade = "부적합"
        emoji = "❌"
        message = "김장 하지 마세요"

    # 김장 팁
    general_tips = [
        "배추 20포기 기준 소금 3kg",
        "절이는 시간: 8-10시간",
        "양념 재료: 무채, 쪽파, 젓갈, 고춧가루",
        "김장 후 3일간 실온 숙성 후 냉장",
    ]

    return {
        "available": True,
        "score": score,
        "grade": grade,
        "emoji": emoji,
        "message": message,
        "factors": factors,
        "tips": tips if tips else ["서늘한 곳에서 작업하세요"],
        "general_tips": general_tips,
        "weather_summary": {
            "temperature": temp,
            "temp_min": temp_min,
            "temp_max": temp_max,
            "rain_prob": weather.rain_prob,
        },
    }


# =============================================================================
# 운동지수 (Health-Weather Integration, v2.2 신규)
# =============================================================================

def calculate_exercise_index(weather: WeatherData) -> dict:
    """
    야외 운동 적합도 계산 (0-100)

    최적 조건:
    - 기온: 15-22°C
    - 습도: 40-60%
    - 강수확률: 10% 미만
    - 미세먼지: 좋음/보통
    - 풍속: 적당 (2-5m/s)

    Health Integration:
    - 열사병/저체온증 위험도
    - 호흡기 건강 (미세먼지)
    - 수분 섭취 권장량
    - 최적 운동 시간대
    """
    score = 100
    factors = []
    tips = []
    warnings = []

    # 1. 기온 (체온 조절 핵심!)
    if weather.temperature < -5:
        score -= 50
        factors.append(f"기온 {weather.temperature}°C (혹한)")
        warnings.append("저체온증 위험! 실내 운동 권장")
        tips.append("운동 시 방한 장비 필수")
    elif weather.temperature < 5:
        score -= 25
        factors.append(f"기온 {weather.temperature}°C (추움)")
        tips.append("워밍업 충분히, 방한 레이어링")
    elif weather.temperature > 35:
        score -= 60
        factors.append(f"기온 {weather.temperature}°C (극심한 폭염)")
        warnings.append("열사병 위험! 야외 운동 금지")
    elif weather.temperature > 30:
        score -= 35
        factors.append(f"기온 {weather.temperature}°C (폭염)")
        warnings.append("열사병 주의! 이른 아침/저녁만 추천")
        tips.append("물 500ml/30분 섭취, 그늘에서 휴식")
    elif weather.temperature > 28:
        score -= 20
        factors.append(f"기온 {weather.temperature}°C (더움)")
        tips.append("수분 보충 자주, 강도 낮추기")
    elif 15 <= weather.temperature <= 22:
        score += 10
        factors.append(f"기온 {weather.temperature}°C (최적)")

    # 2. 미세먼지 (호흡기 건강!)
    if weather.pm25_grade == "매우나쁨":
        score -= 50
        factors.append(f"미세먼지 {weather.pm25_grade}")
        warnings.append("야외 운동 금지! 실내 운동만")
    elif weather.pm25_grade == "나쁨":
        score -= 30
        factors.append(f"미세먼지 {weather.pm25_grade}")
        warnings.append("격렬한 운동 피하기")
        tips.append("가벼운 운동만, 호흡 깊게 하지 않기")
    elif weather.pm25_grade == "보통":
        score -= 5
    elif weather.pm25_grade == "좋음":
        score += 10
        factors.append("미세먼지 좋음 (호흡 최적)")

    # 3. 강수확률
    if weather.rain_prob >= 60:
        score -= 40
        factors.append(f"강수확률 {weather.rain_prob}%")
        warnings.append("비 예보! 실내 운동 권장")
    elif weather.rain_prob >= 40:
        score -= 25
        factors.append(f"강수확률 {weather.rain_prob}%")
        tips.append("우비/방수 재킷 준비")
    elif weather.rain_prob >= 20:
        score -= 10

    # 4. 습도 (땀 증발 효율)
    if weather.humidity > 85:
        score -= 25
        factors.append(f"습도 {weather.humidity}% (매우 높음)")
        tips.append("땀이 안 마름, 탈수 주의")
        warnings.append("열사병 위험 증가")
    elif weather.humidity > 70:
        score -= 15
        factors.append(f"습도 {weather.humidity}%")
        tips.append("수분 보충 자주")
    elif 40 <= weather.humidity <= 60:
        score += 5
        factors.append(f"습도 {weather.humidity}% (최적)")
    elif weather.humidity < 30:
        score -= 10
        tips.append("호흡기 건조 주의, 물 자주 마시기")

    # 5. 풍속
    if weather.wind_speed > 15:
        score -= 25
        factors.append(f"강풍 {weather.wind_speed}m/s")
        warnings.append("강풍! 자전거/러닝 위험")
    elif weather.wind_speed > 10:
        score -= 15
        tips.append("바람 고려하여 코스 조정")
    elif 2 <= weather.wind_speed <= 5:
        score += 5
        tips.append("시원한 바람이 도움됨")

    # 6. 자외선
    if weather.uv_index >= 8:
        score -= 15
        factors.append(f"자외선 {weather.uv_index} (매우높음)")
        tips.append("선크림 SPF50+, 모자 필수")
        warnings.append("11-15시 야외 운동 피하기")
    elif weather.uv_index >= 6:
        score -= 5
        tips.append("선크림, 선글라스 권장")

    # 점수 보정
    score = max(0, min(100, score))

    # 등급 판정
    if score >= 85:
        grade = "최적"
        emoji = "🏃‍♂️"
        message = "야외 운동 완벽한 날!"
    elif score >= 70:
        grade = "좋음"
        emoji = "🚴"
        message = "야외 운동하기 좋은 날"
    elif score >= 50:
        grade = "보통"
        emoji = "🚶"
        message = "가벼운 운동 추천"
    elif score >= 30:
        grade = "주의"
        emoji = "⚠️"
        message = "운동 시 주의 필요"
    else:
        grade = "위험"
        emoji = "❌"
        message = "야외 운동 자제, 실내 추천"

    # 추천 운동 종류
    if score >= 70:
        if weather.temperature > 25:
            exercises = ["수영", "새벽 러닝", "저녁 자전거"]
        elif weather.temperature < 10:
            exercises = ["빠른 걷기", "러닝", "등산"]
        else:
            exercises = ["러닝", "자전거", "등산", "테니스"]
    elif score >= 50:
        exercises = ["걷기", "가벼운 조깅", "스트레칭"]
    else:
        exercises = ["실내 헬스", "요가", "홈트레이닝"]

    # 최적 운동 시간대
    hour = datetime.now().hour
    if weather.temperature > 28:
        best_time = "05:00-08:00 또는 19:00-21:00"
    elif weather.temperature < 5:
        best_time = "12:00-15:00 (가장 따뜻한 시간)"
    elif weather.uv_index >= 6:
        best_time = "07:00-10:00 또는 17:00-19:00"
    else:
        best_time = "언제든 좋아요!"

    # 수분 섭취 권장량 (1시간 운동 기준)
    if weather.temperature > 30 or weather.humidity > 70:
        hydration = "1L 이상/시간"
    elif weather.temperature > 25:
        hydration = "750ml/시간"
    else:
        hydration = "500ml/시간"

    return {
        "score": score,
        "grade": grade,
        "emoji": emoji,
        "message": message,
        "factors": factors,
        "warnings": warnings,
        "tips": tips if tips else ["즐거운 운동 되세요!"],
        "recommended_exercises": exercises,
        "best_time": best_time,
        "hydration_recommendation": hydration,
        "health_notes": {
            "heat_risk": "높음" if weather.temperature > 30 or (weather.temperature > 25 and weather.humidity > 70) else "보통" if weather.temperature > 25 else "낮음",
            "respiratory_risk": "높음" if weather.pm25_grade in ["나쁨", "매우나쁨"] else "보통" if weather.pm25_grade == "보통" else "낮음",
        }
    }


# =============================================================================
# 종합 활동 추천
# =============================================================================

def get_all_activity_recommendations(weather: WeatherData) -> dict:
    """
    모든 활동별 적합도 종합
    """
    results = {
        "weather_summary": {
            "temperature": weather.temperature,
            "humidity": weather.humidity,
            "rain_prob": weather.rain_prob,
            "pm25_grade": weather.pm25_grade,
        },
        "activities": {},
    }

    # 빨래
    results["activities"]["laundry"] = calculate_laundry_index(weather)

    # 등산
    results["activities"]["hiking"] = calculate_hiking_index(weather)

    # 피크닉
    results["activities"]["picnic"] = calculate_picnic_index(weather)

    # 세차
    results["activities"]["car_wash"] = calculate_car_wash_index(weather)

    # 운동 (v2.2 신규)
    results["activities"]["exercise"] = calculate_exercise_index(weather)

    # 김장 (계절 한정)
    kimjang = calculate_kimjang_index(weather)
    if kimjang.get("available", False):
        results["activities"]["kimjang"] = kimjang

    # 베스트 활동 추천
    best_activity = None
    best_score = 0

    for activity_name, activity_data in results["activities"].items():
        if activity_data.get("score", 0) > best_score:
            best_score = activity_data["score"]
            best_activity = activity_name

    results["best_activity"] = {
        "name": best_activity,
        "score": best_score,
        "message": results["activities"].get(best_activity, {}).get("message", ""),
    }

    return results


def get_weekend_recommendations(
    today_weather: WeatherData,
    tomorrow_weather: WeatherData = None,
) -> dict:
    """
    주말 활동 추천

    오늘과 내일 날씨를 비교하여 최적 활동 추천
    """
    today = get_all_activity_recommendations(today_weather)

    if tomorrow_weather:
        tomorrow = get_all_activity_recommendations(tomorrow_weather)
    else:
        tomorrow = None

    recommendations = {
        "today": today,
        "tomorrow": tomorrow,
        "comparison": [],
    }

    # 비교 분석
    if tomorrow:
        for activity in ["laundry", "hiking", "picnic", "car_wash"]:
            today_score = today["activities"].get(activity, {}).get("score", 0)
            tomorrow_score = tomorrow["activities"].get(activity, {}).get("score", 0)

            if today_score > tomorrow_score + 10:
                recommendations["comparison"].append(
                    f"{activity}: 오늘이 더 좋아요 ({today_score} vs {tomorrow_score})"
                )
            elif tomorrow_score > today_score + 10:
                recommendations["comparison"].append(
                    f"{activity}: 내일이 더 좋아요 ({tomorrow_score} vs {today_score})"
                )

    return recommendations


# =============================================================================
# 감기 위험 지수 (Cold/Flu Risk Index) - 과학적 근거 기반
# =============================================================================

def calculate_cold_flu_risk_index(weather: WeatherData, yesterday_temp: float = None) -> dict:
    """
    감기/독감 위험 지수 계산 (0-100, 높을수록 위험)

    과학적 근거 (Perplexity Research 2024-2025):
    - 기온: 5-20°C에서 바이러스 생존 최적, -5°C 부근에서 전파 최대
    - 습도: 상대습도 40% 미만 시 바이러스 에어로졸 안정성 증가
    - 기온변화: 주간 1°C 이상 급격한 기온 변화 시 면역력 저하
    - 풍속: 점막 건조 유발, 섬모운동 억제

    출처: Yale University, MIT, PNAS, Nature 연구
    """
    risk_score = 0
    factors = []
    recommendations = []

    temp = weather.temperature
    humidity = weather.humidity
    wind_speed = weather.wind_speed

    # 1. 기온 점수 (0-35점)
    # 바이러스 생존 최적: 5-20°C, 전파 최대: -5°C 부근
    if temp < -10:
        temp_score = 25  # 매우 추움 - 실내 밀집 + 점막 건조
        factors.append(f"극저온 ({temp}°C): 실내 밀집 환경 증가")
    elif -10 <= temp < 0:
        temp_score = 35  # 바이러스 전파 최적 구간
        factors.append(f"한파 ({temp}°C): 바이러스 전파 최적 온도대")
    elif 0 <= temp < 5:
        temp_score = 32
        factors.append(f"영하권 ({temp}°C): 바이러스 생존력 강화")
    elif 5 <= temp < 10:
        temp_score = 30  # 바이러스 안정 구간
        factors.append(f"쌀쌀함 ({temp}°C): 바이러스 안정성 높음")
    elif 10 <= temp < 15:
        temp_score = 22
        factors.append(f"선선함 ({temp}°C): 환기 부족 주의")
    elif 15 <= temp < 20:
        temp_score = 15
        factors.append(f"온화함 ({temp}°C): 적정 환기 권장")
    elif 20 <= temp < 25:
        temp_score = 8  # 쾌적 구간
        factors.append(f"쾌적 ({temp}°C): 양호한 조건")
    else:  # 25°C 이상
        temp_score = 5
        factors.append(f"따뜻함 ({temp}°C): 바이러스 활동 저하")

    risk_score += temp_score

    # 2. 습도 점수 (0-30점)
    # 40-60% RH가 최적, 40% 미만은 위험 증가 (MIT 연구)
    if humidity < 30:
        humidity_score = 30
        factors.append(f"매우 건조 ({humidity}%): 에어로졸 전파 위험 최대")
        recommendations.append("가습기 사용 권장 (40-60% 유지)")
    elif 30 <= humidity < 40:
        humidity_score = 25
        factors.append(f"건조 ({humidity}%): 바이러스 에어로졸 안정화")
        recommendations.append("실내 습도 관리 필요")
    elif 40 <= humidity < 60:
        humidity_score = 5  # 최적 구간
        factors.append(f"적정 습도 ({humidity}%): 호흡기 방어 최적")
    elif 60 <= humidity < 80:
        humidity_score = 10
        factors.append(f"높은 습도 ({humidity}%): 환기 필요")
    else:  # 80% 이상
        humidity_score = 15
        factors.append(f"과습 ({humidity}%): 곰팡이 주의, 환기 필수")

    risk_score += humidity_score

    # 3. 기온 변화 점수 (0-20점) - 일교차 기반
    # 연구: 기온 급변 시 면역력 저하 (10°C 이상 변화 시 현저)
    if weather.temp_min is not None and weather.temp_max is not None:
        daily_swing = weather.temp_max - weather.temp_min
        if daily_swing >= 15:
            swing_score = 20
            factors.append(f"극심한 일교차 ({daily_swing:.0f}°C): 면역력 저하 위험")
            recommendations.append("체온 조절 의류 필수")
        elif daily_swing >= 12:
            swing_score = 16
            factors.append(f"큰 일교차 ({daily_swing:.0f}°C): 건강 주의")
        elif daily_swing >= 10:
            swing_score = 12
            factors.append(f"일교차 주의 ({daily_swing:.0f}°C)")
        elif daily_swing >= 7:
            swing_score = 6
            factors.append(f"보통 일교차 ({daily_swing:.0f}°C)")
        else:
            swing_score = 0
        risk_score += swing_score
    elif yesterday_temp is not None:
        # 전일 대비 기온 변화
        temp_change = abs(temp - yesterday_temp)
        if temp_change >= 8:
            swing_score = 18
            factors.append(f"급격한 기온 변화 ({temp_change:.1f}°C 차이)")
            recommendations.append("따뜻하게 입고 면역력 관리")
        elif temp_change >= 5:
            swing_score = 12
            factors.append(f"기온 변화 ({temp_change:.1f}°C 차이)")
        else:
            swing_score = 3
        risk_score += swing_score

    # 4. 풍속 점수 (0-15점)
    # 차가운 바람은 점막 건조, 섬모운동 억제
    if temp < 10:  # 추운 날씨일 때 풍속 영향 증가
        if wind_speed >= 7:
            wind_score = 15
            factors.append(f"강한 찬바람 ({wind_speed}m/s): 점막 건조 위험")
            recommendations.append("마스크/목도리로 호흡기 보호")
        elif wind_speed >= 5:
            wind_score = 12
            factors.append(f"찬바람 ({wind_speed}m/s): 체감온도 급락")
        elif wind_speed >= 3:
            wind_score = 7
            factors.append(f"바람 ({wind_speed}m/s)")
        else:
            wind_score = 2
    else:
        wind_score = min(wind_speed, 8)  # 최대 8점

    risk_score += wind_score

    # 점수 정규화 (0-100)
    risk_score = min(100, max(0, risk_score))

    # 등급 결정
    if risk_score >= 80:
        grade = "매우높음"
        color = "빨강"
        message = "감기/독감 위험이 매우 높습니다. 외출 자제하고 따뜻하게!"
    elif risk_score >= 60:
        grade = "높음"
        color = "주황"
        message = "감기 조심하세요! 손씻기, 마스크 착용 권장"
    elif risk_score >= 40:
        grade = "보통"
        color = "노랑"
        message = "일반적인 건강 관리로 충분합니다"
    elif risk_score >= 20:
        grade = "낮음"
        color = "초록"
        message = "감기 위험이 낮습니다"
    else:
        grade = "매우낮음"
        color = "파랑"
        message = "감기 걱정 없는 쾌적한 날씨입니다"

    # 기본 예방 수칙 추가
    if risk_score >= 40:
        recommendations.extend([
            "손 자주 씻기 (20초 이상)",
            "실내 환기 (2시간마다 10분)",
            "충분한 수분 섭취"
        ])
    if risk_score >= 60:
        recommendations.append("비타민 C, D 섭취 권장")
    if risk_score >= 80:
        recommendations.extend([
            "사람 많은 곳 피하기",
            "충분한 수면 (7-8시간)"
        ])

    return {
        "score": round(risk_score),
        "grade": grade,
        "color": color,
        "message": message,
        "factors": factors,
        "recommendations": list(set(recommendations)),  # 중복 제거
        "detail": {
            "temperature_risk": temp_score,
            "humidity_risk": humidity_score,
            "daily_swing_risk": swing_score if 'swing_score' in dir() else 0,
            "wind_risk": wind_score
        },
        "scientific_basis": "MIT, Yale, PNAS 연구 기반 - 기온, 습도, 일교차가 호흡기 바이러스 전파에 영향"
    }


# =============================================================================
# 출퇴근 지수 (Commute Index) - 다중 교통수단 고려
# =============================================================================

def calculate_commute_index(weather: WeatherData) -> dict:
    """
    출퇴근 적합도 지수 (0-100, 높을수록 좋음)

    과학적 근거 (Transportation Research 2024):
    - 강수: 비 시 치명 사고 34% 증가, 폭우 시 2.46배
    - 풍속: 보행자 6m/s, 자전거 5m/s 이상 불편
    - 기온: UTCI 기준 9-26°C가 쾌적
    - 시정: 0.25마일(400m) 미만은 위험

    교통수단별 점수:
    - 자가용/택시
    - 대중교통 (버스정류장 대기)
    - 도보/자전거
    """
    temp = weather.temperature
    humidity = weather.humidity
    wind_speed = weather.wind_speed
    rain_prob = weather.rain_prob
    sky = weather.sky
    pm25 = weather.pm25_grade

    # 공통 감점 요소 계산
    common_factors = []

    # === 자가용/택시 점수 ===
    car_score = 100
    car_factors = []

    # 강수 영향 (치명사고 증가)
    if rain_prob >= 80 or "비" in sky or "눈" in sky:
        if "눈" in sky:
            car_score -= 35  # 눈은 더 위험
            car_factors.append("적설: 미끄럼 주의")
        else:
            car_score -= 25
            car_factors.append("비: 제동거리 증가")
    elif rain_prob >= 50:
        car_score -= 15
        car_factors.append("비 가능성: 시야 주의")

    # 시정 (안개)
    if "안개" in sky or ("흐림" in sky and humidity >= 90):
        car_score -= 20
        car_factors.append("안개/저시정: 서행 운전")

    # 결빙 위험 (기온 0-4°C + 습도 높음)
    if 0 <= temp <= 4 and humidity >= 80:
        car_score -= 25
        car_factors.append("결빙 위험: 블랙아이스 주의")
    elif temp < 0:
        car_score -= 20
        car_factors.append("영하: 노면 결빙 가능")

    # === 대중교통 점수 (버스정류장 대기 고려) ===
    transit_score = 100
    transit_factors = []

    # 기온 영향 (정류장 대기)
    if temp < -5:
        transit_score -= 30
        transit_factors.append("혹한: 정류장 대기 고통")
    elif temp < 0:
        transit_score -= 20
        transit_factors.append("추위: 따뜻하게 입기")
    elif temp < 5:
        transit_score -= 12
        transit_factors.append("쌀쌀함: 외투 필수")
    elif temp > 33:
        transit_score -= 30
        transit_factors.append("폭염: 정류장 대기 위험")
    elif temp > 30:
        transit_score -= 20
        transit_factors.append("무더위: 수분 보충")
    elif temp > 28:
        transit_score -= 10
        transit_factors.append("더위 주의")

    # 풍속 (Lawson 기준: 정류장 대기 6m/s 이상 불편)
    if wind_speed >= 8:
        transit_score -= 25
        transit_factors.append("강풍: 정류장 대기 힘듦")
    elif wind_speed >= 6:
        transit_score -= 15
        transit_factors.append("바람: 체감온도 하락")
    elif wind_speed >= 4:
        transit_score -= 5

    # 비 (우산 들고 대기)
    if rain_prob >= 80 or "비" in sky:
        transit_score -= 20
        transit_factors.append("비: 우산 필요")
    elif rain_prob >= 50:
        transit_score -= 10
        transit_factors.append("비 가능성")

    # 미세먼지 (호흡)
    if pm25 in ["매우나쁨", "나쁨"]:
        transit_score -= 15
        transit_factors.append(f"미세먼지 {pm25}: 마스크 필수")
    elif pm25 == "보통":
        transit_score -= 5

    # === 도보/자전거 점수 ===
    walk_score = 100
    walk_factors = []

    # 기온 영향 (UTCI 기준 9-26°C 쾌적)
    if temp < 0:
        walk_score -= 35
        walk_factors.append("영하: 도보 고통")
    elif temp < 5:
        walk_score -= 25
        walk_factors.append("추위: 따뜻하게")
    elif temp < 10:
        walk_score -= 15
        walk_factors.append("쌀쌀함")
    elif temp > 33:
        walk_score -= 40
        walk_factors.append("폭염: 도보 자제")
    elif temp > 30:
        walk_score -= 30
        walk_factors.append("무더위: 열사병 주의")
    elif temp > 28:
        walk_score -= 15
        walk_factors.append("더위 주의")

    # 풍속 (자전거는 5m/s 이상 힘듦)
    if wind_speed >= 10:
        walk_score -= 35
        walk_factors.append("강풍: 자전거 위험")
    elif wind_speed >= 7:
        walk_score -= 25
        walk_factors.append("강풍: 도보도 힘듦")
    elif wind_speed >= 5:
        walk_score -= 15
        walk_factors.append("바람: 자전거 힘듦")

    # 비
    if rain_prob >= 80 or "비" in sky:
        walk_score -= 40
        walk_factors.append("비: 도보/자전거 비추천")
    elif rain_prob >= 50:
        walk_score -= 20
        walk_factors.append("비 가능성")

    # 미세먼지 (운동 중 흡입량 증가)
    if pm25 in ["매우나쁨"]:
        walk_score -= 35
        walk_factors.append("미세먼지 매우나쁨: 절대 자제")
    elif pm25 == "나쁨":
        walk_score -= 25
        walk_factors.append("미세먼지 나쁨: 자제 권장")
    elif pm25 == "보통":
        walk_score -= 8

    # 점수 정규화
    car_score = max(0, min(100, car_score))
    transit_score = max(0, min(100, transit_score))
    walk_score = max(0, min(100, walk_score))

    # 종합 점수 (가중 평균)
    overall_score = (car_score * 0.4 + transit_score * 0.35 + walk_score * 0.25)

    # 최적 교통수단 추천
    scores = {"자가용": car_score, "대중교통": transit_score, "도보/자전거": walk_score}
    best_mode = max(scores, key=scores.get)

    # 등급 결정 (종합)
    if overall_score >= 80:
        grade = "좋음"
        message = "출퇴근하기 좋은 날씨입니다"
    elif overall_score >= 60:
        grade = "보통"
        message = "무난한 출퇴근이 가능합니다"
    elif overall_score >= 40:
        grade = "주의"
        message = "출퇴근 시 주의가 필요합니다"
    elif overall_score >= 20:
        grade = "나쁨"
        message = "출퇴근이 힘든 날씨입니다"
    else:
        grade = "매우나쁨"
        message = "가능하면 재택/휴가를 권장합니다"

    # 시간대별 팁
    time_tips = []
    if temp < 5:
        time_tips.append("아침: 체감온도 더 낮음, 따뜻하게")
    if temp > 28:
        time_tips.append("오후: 폭염 피크, 수분 보충")
    if rain_prob >= 50:
        time_tips.append("우산 필수, 여유있게 출발")

    return {
        "score": round(overall_score),
        "grade": grade,
        "message": message,
        "recommended_mode": best_mode,
        "by_mode": {
            "car": {
                "score": car_score,
                "grade": _get_grade(car_score),
                "factors": car_factors
            },
            "transit": {
                "score": transit_score,
                "grade": _get_grade(transit_score),
                "factors": transit_factors
            },
            "walk_bike": {
                "score": walk_score,
                "grade": _get_grade(walk_score),
                "factors": walk_factors
            }
        },
        "time_tips": time_tips,
        "scientific_basis": "PNAS 교통연구, Lawson 보행자 기준, UTCI 열쾌적 지수 기반"
    }


def _get_grade(score: int) -> str:
    """점수를 등급으로 변환"""
    if score >= 80:
        return "좋음"
    elif score >= 60:
        return "보통"
    elif score >= 40:
        return "주의"
    elif score >= 20:
        return "나쁨"
    else:
        return "매우나쁨"


# =============================================================================
# 알레르기 위험 지수 (Allergy Risk Index) - 계절/황사 연동
# =============================================================================

def calculate_allergy_risk_index(weather: WeatherData, season: str = None) -> dict:
    """
    알레르기 위험 지수 (0-100, 높을수록 위험)

    고려 요소:
    - 미세먼지/초미세먼지 (PM10, PM2.5)
    - 계절별 꽃가루 (봄: 삼나무/소나무, 가을: 돼지풀/쑥)
    - 황사 (봄철)
    - 습도 (건조 시 악화)
    - 풍속 (꽃가루/먼지 확산)
    """
    if season is None:
        month = datetime.now().month
        if month in [3, 4, 5]:
            season = "봄"
        elif month in [6, 7, 8]:
            season = "여름"
        elif month in [9, 10, 11]:
            season = "가을"
        else:
            season = "겨울"

    risk_score = 0
    factors = []
    recommendations = []
    allergens = []

    # 1. 미세먼지 점수 (0-40점)
    pm25_grade = weather.pm25_grade
    pm25_value = weather.pm25_value

    if pm25_grade == "매우나쁨":
        pm_score = 40
        factors.append(f"초미세먼지 매우나쁨 ({pm25_value}㎍/㎥)")
        recommendations.append("외출 자제, 마스크 필수 (KF94)")
    elif pm25_grade == "나쁨":
        pm_score = 30
        factors.append(f"초미세먼지 나쁨 ({pm25_value}㎍/㎥)")
        recommendations.append("마스크 착용 권장")
    elif pm25_grade == "보통":
        pm_score = 15
        factors.append(f"초미세먼지 보통 ({pm25_value}㎍/㎥)")
    else:
        pm_score = 5
        factors.append(f"초미세먼지 좋음")

    risk_score += pm_score

    # 2. 계절별 꽃가루 점수 (0-30점)
    if season == "봄":
        allergens = ["삼나무", "소나무", "자작나무", "참나무"]
        pollen_score = 25
        factors.append("봄철 수목 꽃가루 시즌")
        recommendations.append("화분증 주의, 외출 후 세안/양치")
    elif season == "가을":
        allergens = ["돼지풀", "쑥", "환삼덩굴"]
        pollen_score = 22
        factors.append("가을철 잡초 꽃가루 시즌")
        recommendations.append("잡초 꽃가루 주의")
    elif season == "여름":
        allergens = ["잔디"]
        pollen_score = 10
        factors.append("잔디 꽃가루 (약함)")
    else:
        allergens = []
        pollen_score = 5
        factors.append("꽃가루 시즌 아님")

    risk_score += pollen_score

    # 3. 황사 가능성 (봄철, 0-20점)
    if season == "봄":
        # 풍속이 높고 건조하면 황사 위험
        if wind_speed >= 6 and weather.humidity < 40:
            dust_score = 20
            factors.append("황사 가능성 높음")
            allergens.append("황사(모래먼지)")
            recommendations.append("외출 시 보안경, 마스크 착용")
        elif wind_speed >= 4:
            dust_score = 12
            factors.append("황사 주의")
        else:
            dust_score = 5
    else:
        dust_score = 0

    wind_speed = weather.wind_speed
    risk_score += dust_score

    # 4. 습도 점수 (건조 시 악화, 0-10점)
    if weather.humidity < 30:
        humidity_score = 10
        factors.append("매우 건조: 알레르기 증상 악화")
        recommendations.append("가습기 사용, 물 자주 마시기")
    elif weather.humidity < 40:
        humidity_score = 6
        factors.append("건조함")
    else:
        humidity_score = 0

    risk_score += humidity_score

    # 점수 정규화
    risk_score = min(100, max(0, risk_score))

    # 등급 결정
    if risk_score >= 80:
        grade = "매우높음"
        message = "알레르기 환자는 외출 자제"
    elif risk_score >= 60:
        grade = "높음"
        message = "알레르기 약 복용, 마스크 착용"
    elif risk_score >= 40:
        grade = "보통"
        message = "민감군 주의 필요"
    elif risk_score >= 20:
        grade = "낮음"
        message = "대부분 양호"
    else:
        grade = "매우낮음"
        message = "알레르기 걱정 없음"

    return {
        "score": round(risk_score),
        "grade": grade,
        "message": message,
        "season": season,
        "main_allergens": allergens,
        "factors": factors,
        "recommendations": recommendations,
        "detail": {
            "pm_risk": pm_score,
            "pollen_risk": pollen_score,
            "dust_storm_risk": dust_score,
            "humidity_risk": humidity_score
        }
    }


# =============================================================================
# 편두통 위험 지수 (Migraine Risk Index) - v2.4 신규
# =============================================================================

def calculate_migraine_risk_index(weather_data: dict, air_data: dict) -> dict:
    """
    편두통 위험 지수 계산 (0-100, 높을수록 안전)

    과학적 근거:
    - 5hPa 기압 하락 시 편두통 유발 (Neurology 연구)
    - 습도 70% 이상 시 두통 악화
    - 일교차 10도 이상 시 혈관 수축/확장 반복
    - 저기압 접근 시 (강수확률 높음) 편두통 유발

    Args:
        weather_data: 날씨 데이터 (sky, temp_current, temp_min, temp_max, humidity, rain_prob, wind_speed)
        air_data: 대기질 데이터 (pm10_grade, pm25_grade, pm10_value, pm25_value)

    Returns:
        dict: score, grade, risk_factors, advice
    """
    risk_score = 0
    risk_factors = []

    # 날씨 데이터 추출
    sky = weather_data.get("sky", "맑음")
    humidity = weather_data.get("humidity", 50)
    rain_prob = weather_data.get("rain_prob", 0)
    temp_min = weather_data.get("temp_min")
    temp_max = weather_data.get("temp_max")
    temp_current = weather_data.get("temp_current")

    # 일교차 계산
    if temp_min is not None and temp_max is not None:
        temp_diff = temp_max - temp_min
    elif temp_current is not None:
        temp_diff = 8  # 기본값
    else:
        temp_diff = 8

    # 1. 강수확률 (저기압 접근 지표) - 위험도 +40
    if rain_prob > 60:
        risk_score += 40
        risk_factors.append(f"저기압 접근 (강수확률 {rain_prob}%): 기압 하락으로 편두통 유발 가능")

    # 2. 습도 - 위험도 +20
    if humidity > 70:
        risk_score += 20
        risk_factors.append(f"높은 습도 ({humidity}%): 두통 악화 요인")

    # 3. 일교차 - 위험도 +20
    if temp_diff > 10:
        risk_score += 20
        risk_factors.append(f"큰 일교차 ({temp_diff:.0f}도): 혈관 수축/확장 반복")

    # 4. 하늘 상태 - 위험도 +20
    if sky in ["흐림", "비", "눈", "소나기"]:
        risk_score += 20
        risk_factors.append(f"흐린 날씨 ({sky}): 저기압 영향")

    # 점수 계산 (100 - 위험도, 높을수록 안전)
    score = max(0, min(100, 100 - risk_score))

    # 등급 결정
    grade = _get_grade(score)

    # 조언 생성
    if score >= 80:
        advice = "편두통 위험이 낮은 날씨입니다. 평소처럼 활동하세요."
    elif score >= 60:
        advice = "편두통에 민감하신 분은 진통제를 미리 준비하세요."
    elif score >= 40:
        advice = "편두통 위험 주의. 충분한 수분 섭취와 규칙적인 식사를 권장합니다."
    elif score >= 20:
        advice = "편두통 위험 높음. 격렬한 활동을 피하고 휴식을 취하세요."
    else:
        advice = "편두통 위험 매우 높음. 가능하면 조용하고 어두운 곳에서 휴식하세요. 필요시 약 복용."

    return {
        "score": score,
        "grade": grade,
        "risk_factors": risk_factors if risk_factors else ["편두통 유발 요인 없음"],
        "advice": advice
    }


# =============================================================================
# 수면 컨디션 지수 (Sleep Quality Index) - v2.4 신규
# =============================================================================

def calculate_sleep_quality_index(weather_data: dict, air_data: dict) -> dict:
    """
    수면 컨디션 지수 계산 (0-100, 높을수록 좋음)

    과학적 근거:
    - 최적 수면 습도: 40-60% (American Academy of Sleep Medicine)
    - 최적 수면 온도: 18-22도 (Sleep Foundation)
    - 미세먼지는 수면 질 저하 유발 (호흡기 자극)

    Args:
        weather_data: 날씨 데이터 (temp_current, humidity)
        air_data: 대기질 데이터 (pm10_grade, pm10_value)

    Returns:
        dict: score, grade, optimal_conditions, tips
    """
    score = 0
    tips = []

    # 데이터 추출
    temp_current = weather_data.get("temp_current", 20)
    humidity = weather_data.get("humidity", 50)
    pm10_value = air_data.get("pm10_value", 50)

    # 1. 습도 점수 (최대 40점)
    if 40 <= humidity <= 60:
        score += 40
    elif 30 <= humidity < 40 or 60 < humidity <= 70:
        score += 20
        if humidity < 40:
            tips.append("실내가 건조합니다. 가습기 사용을 권장합니다.")
        else:
            tips.append("습도가 다소 높습니다. 환기를 권장합니다.")
    else:
        if humidity < 30:
            tips.append("매우 건조합니다. 가습기 필수, 물 자주 마시기.")
        else:
            tips.append("습도가 너무 높습니다. 제습기 또는 에어컨 사용 권장.")

    # 2. 온도 점수 (최대 40점)
    if 18 <= temp_current <= 22:
        score += 40
    elif 15 <= temp_current < 18 or 22 < temp_current <= 25:
        score += 20
        if temp_current < 18:
            tips.append("다소 쌀쌀합니다. 따뜻한 이불을 준비하세요.")
        else:
            tips.append("약간 따뜻합니다. 시원한 잠옷과 얇은 이불 권장.")
    else:
        if temp_current < 15:
            tips.append("춥습니다. 난방 및 두꺼운 이불 필요.")
        else:
            tips.append("덥습니다. 에어컨 또는 선풍기 사용, 수분 보충 후 취침.")

    # 3. 미세먼지 점수 (최대 20점)
    if pm10_value < 30:
        score += 20
    elif pm10_value < 80:
        score += 10
        tips.append("미세먼지 보통. 취침 전 환기 후 창문 닫기.")
    else:
        tips.append("미세먼지 나쁨. 공기청정기 가동 권장.")

    # 점수 정규화
    score = max(0, min(100, score))

    # 등급 결정
    grade = _get_grade(score)

    # 기본 팁 추가
    if not tips:
        tips.append("쾌적한 수면 환경입니다. 좋은 밤 되세요!")

    # 최적 조건 정보
    optimal_conditions = {
        "optimal_temperature": "18-22도",
        "optimal_humidity": "40-60%",
        "current_temperature": f"{temp_current}도",
        "current_humidity": f"{humidity}%"
    }

    return {
        "score": score,
        "grade": grade,
        "optimal_conditions": optimal_conditions,
        "tips": tips
    }


# =============================================================================
# 사진 촬영 지수 (Photography Index) - v2.4 신규
# =============================================================================

def calculate_photography_index(weather_data: dict) -> dict:
    """
    사진 촬영 적합도 지수 (0-100, 높을수록 좋음)

    고려 요소:
    - 하늘 상태: 맑음 최적, 구름많음도 드라마틱한 하늘로 좋음
    - 강수확률: 낮을수록 좋음
    - 습도: 40-70% 최적 (공기 선명도)
    - 골든아워: 일출 후 1시간, 일몰 전 1시간이 최적

    Args:
        weather_data: 날씨 데이터 (sky, rain_prob, humidity)

    Returns:
        dict: score, grade, best_times, conditions
    """
    score = 0

    # 데이터 추출
    sky = weather_data.get("sky", "맑음")
    rain_prob = weather_data.get("rain_prob", 0)
    humidity = weather_data.get("humidity", 50)

    # 1. 하늘 상태 (최대 50점)
    if sky == "맑음":
        score += 50
        sky_condition = "맑은 하늘 - 선명한 사진 촬영 최적"
    elif sky in ["구름많음", "구름 많음"]:
        score += 30
        sky_condition = "구름 많음 - 드라마틱한 하늘 연출 가능"
    elif sky == "흐림":
        score += 10
        sky_condition = "흐림 - 소프트 라이팅, 인물사진 적합"
    else:
        score += 5
        sky_condition = f"{sky} - 촬영 조건 불리"

    # 2. 강수확률 (최대 30점)
    if rain_prob < 20:
        score += 30
        rain_condition = "강수 걱정 없음"
    elif rain_prob < 40:
        score += 20
        rain_condition = "비 가능성 낮음"
    elif rain_prob < 60:
        score += 10
        rain_condition = "비 올 수 있음 - 방수 커버 준비"
    else:
        score += 0
        rain_condition = "비 예상 - 실내 촬영 권장"

    # 3. 습도 (최대 20점) - 공기 선명도
    if 40 <= humidity <= 70:
        score += 20
        humidity_condition = "적정 습도 - 공기 선명도 좋음"
    elif 30 <= humidity < 40 or 70 < humidity <= 80:
        score += 10
        humidity_condition = "습도 보통"
    else:
        score += 0
        if humidity < 30:
            humidity_condition = "건조함 - 먼지 주의"
        else:
            humidity_condition = "습함 - 렌즈 김 서림 주의"

    # 점수 정규화
    score = max(0, min(100, score))

    # 등급 결정
    grade = _get_grade(score)

    # 골든아워 정보
    best_times = [
        "일출 후 1시간 (골든아워): 따뜻한 색감, 긴 그림자",
        "일몰 전 1시간 (골든아워): 황금빛 조명, 드라마틱한 하늘",
        "블루아워 (일몰 직후): 파란빛 하늘, 도시 야경"
    ]

    # 조건 정보
    conditions = {
        "sky": sky_condition,
        "rain": rain_condition,
        "humidity": humidity_condition,
        "recommendation": "야외 촬영 적합" if score >= 60 else "실내 촬영 권장" if score < 40 else "촬영 가능하나 주의 필요"
    }

    return {
        "score": score,
        "grade": grade,
        "best_times": best_times,
        "conditions": conditions
    }


# =============================================================================
# 관절통 지수 (Joint Pain Index) - v2.4 신규
# =============================================================================

def calculate_joint_pain_index(weather_data: dict, air_data: dict) -> dict:
    """
    관절통 위험 지수 계산 (0-100, 높을수록 관절에 좋음)

    과학적 근거:
    - 10도 이상 온도 하락 + 습도 60% 이상 = 관절통 증가 (Rheumatology 연구)
    - 저기압 접근 시 관절 내 압력 변화로 통증 유발
    - 습도 높을수록 관절 주변 조직 부종

    Args:
        weather_data: 날씨 데이터 (temp_min, temp_max, humidity, rain_prob)
        air_data: 대기질 데이터 (사용하지 않지만 인터페이스 통일)

    Returns:
        dict: score, grade, risk_factors, advice
    """
    risk_score = 0
    risk_factors = []

    # 데이터 추출
    temp_min = weather_data.get("temp_min")
    temp_max = weather_data.get("temp_max")
    temp_current = weather_data.get("temp_current")
    humidity = weather_data.get("humidity", 50)
    rain_prob = weather_data.get("rain_prob", 0)

    # 일교차 계산
    if temp_min is not None and temp_max is not None:
        temp_diff = temp_max - temp_min
    elif temp_current is not None:
        temp_diff = 8  # 기본값
    else:
        temp_diff = 8

    # 1. 일교차 - 위험도 +30
    if temp_diff > 10:
        risk_score += 30
        risk_factors.append(f"큰 일교차 ({temp_diff:.0f}도): 관절 온도 변화 스트레스")

    # 2. 습도 - 위험도 +30 또는 +20
    if humidity > 70:
        risk_score += 30
        risk_factors.append(f"높은 습도 ({humidity}%): 관절 주변 조직 부종 가능")
    elif humidity > 60:
        risk_score += 20
        risk_factors.append(f"다소 높은 습도 ({humidity}%): 관절 불편감 증가")

    # 3. 강수확률 (저기압) - 위험도 +20
    if rain_prob > 50:
        risk_score += 20
        risk_factors.append(f"저기압 접근 (강수확률 {rain_prob}%): 관절 내 압력 변화")

    # 점수 계산 (100 - 위험도, 높을수록 관절에 좋음)
    score = max(0, min(100, 100 - risk_score))

    # 등급 결정
    grade = _get_grade(score)

    # 조언 생성
    if score >= 80:
        advice = "관절에 좋은 날씨입니다. 가벼운 운동을 권장합니다."
    elif score >= 60:
        advice = "관절 상태 양호. 무리한 활동은 피하세요."
    elif score >= 40:
        advice = "관절통 주의. 보온에 신경 쓰고 스트레칭을 자주 하세요."
    elif score >= 20:
        advice = "관절통 위험 높음. 따뜻하게 하고 무리한 활동을 피하세요. 온찜질 권장."
    else:
        advice = "관절통 위험 매우 높음. 보온 필수, 관절 보호대 착용 권장. 필요시 진통제 준비."

    return {
        "score": score,
        "grade": grade,
        "risk_factors": risk_factors if risk_factors else ["관절통 유발 요인 없음"],
        "advice": advice
    }


# =============================================================================
# v2.5 신규 - 야외 활동 지수 6종
# =============================================================================


def calculate_drive_index(weather_data: dict, air_data: dict = None) -> dict:
    """
    드라이브지수 - 도로 여행 안전성 및 쾌적도 계산 (0-100, 높을수록 좋음)

    도로 주행 안전성과 드라이브 쾌적도를 종합 평가합니다.

    핵심 요소:
    - 강수 (critical): 비/눈 시 제동거리 증가, 시야 저하
    - 시정: 안개, 황사 등 저시정 상태
    - 바람: 고속도로에서 대형 차량 전복 위험
    - 결빙: 기온 0도 이하 + 습기 시 블랙아이스 위험

    Args:
        weather_data: 날씨 데이터 (sky, temp_current, humidity, rain_prob, wind_speed)
        air_data: 대기질 데이터 (선택사항, 시정 영향)

    Returns:
        dict: score, grade, grade_kr, factors, recommendations, warnings
    """
    score = 100
    factors = []
    recommendations = []
    warnings = []

    # 데이터 추출
    sky = weather_data.get("sky", "맑음")
    temp_current = weather_data.get("temp_current", 15)
    humidity = weather_data.get("humidity", 50)
    rain_prob = weather_data.get("rain_prob", 0)
    wind_speed = weather_data.get("wind_speed", 0)

    # air_data 처리
    if air_data is None:
        air_data = {}
    pm10_grade = air_data.get("pm10_grade", "보통")

    # 1. 강수 (가장 중요! 치명사고 직결) - 최대 -50점
    if rain_prob >= 80 or "비" in sky or "소나기" in sky:
        score -= 40
        factors.append(f"강수 예상 (강수확률 {rain_prob}%): 제동거리 증가, 시야 저하")
        warnings.append("비 오는 날 운전: 제동거리 1.5배 증가, 감속 운행 필수")
        recommendations.append("와이퍼 상태 점검, 서행 운전")
    elif rain_prob >= 50:
        score -= 25
        factors.append(f"비 가능성 (강수확률 {rain_prob}%)")
        recommendations.append("우산 및 와이퍼 점검")
    elif rain_prob >= 30:
        score -= 10
        factors.append(f"강수 주의 (강수확률 {rain_prob}%)")

    # 눈은 더 위험
    if "눈" in sky:
        score -= 50
        factors.append("적설 예상: 미끄럼 사고 위험 매우 높음")
        warnings.append("눈길 운전: 급제동/급가속 금지, 차간거리 2배 유지")
        recommendations.append("스노우 체인 또는 스노우 타이어 필수")

    # 2. 결빙 위험 (기온 0도 이하 + 습기) - 최대 -35점
    if temp_current <= 0:
        if rain_prob > 0 or humidity >= 80:
            score -= 35
            factors.append(f"결빙 위험 (기온 {temp_current}도, 습도 {humidity}%)")
            warnings.append("블랙아이스 주의! 교량/터널 출입구/그늘진 도로 특히 위험")
            recommendations.append("새벽/야간 운전 자제, 급제동 금지")
        else:
            score -= 20
            factors.append(f"영하 기온 ({temp_current}도): 도로 결빙 가능")
            recommendations.append("급제동/급가속 자제")
    elif temp_current <= 4:
        if humidity >= 80:
            score -= 15
            factors.append(f"결빙 주의 (기온 {temp_current}도, 습도 높음)")

    # 3. 시정/안개 - 최대 -30점
    if "안개" in sky or ("흐림" in sky and humidity >= 95):
        score -= 30
        factors.append("안개/저시정: 시야 확보 어려움")
        warnings.append("안개 시 전조등 켜고 서행, 비상등 금지")
        recommendations.append("안개등 사용, 차간거리 충분히 확보")
    elif humidity >= 90 and ("흐림" in sky or "구름" in sky):
        score -= 15
        factors.append("시정 저하 가능성 (높은 습도)")

    # 4. 풍속 (고속도로 위험) - 최대 -25점
    if wind_speed >= 15:
        score -= 25
        factors.append(f"강풍 ({wind_speed}m/s): 차량 흔들림 심각")
        warnings.append("강풍 시 대형 차량/트레일러 전복 위험, 핸들 꽉 잡기")
        recommendations.append("고속도로 대신 국도 이용 권장")
    elif wind_speed >= 10:
        score -= 15
        factors.append(f"바람 강함 ({wind_speed}m/s): 차선 이탈 주의")
        recommendations.append("급핸들 조작 자제, 옆차선 대형차 주의")
    elif wind_speed >= 7:
        score -= 5
        factors.append(f"바람 있음 ({wind_speed}m/s)")

    # 5. 기온 (극한 조건) - 최대 -15점
    if temp_current >= 35:
        score -= 15
        factors.append(f"폭염 ({temp_current}도): 타이어 펑크/과열 위험")
        recommendations.append("타이어 공기압 점검, 냉각수 확인")
    elif temp_current <= -10:
        score -= 15
        factors.append(f"혹한 ({temp_current}도): 배터리/시동 문제 가능")
        recommendations.append("배터리 상태 점검, 예열 충분히")

    # 6. 미세먼지/황사 - 최대 -15점
    if pm10_grade in ["매우나쁨", "나쁨"]:
        score -= 15
        factors.append(f"미세먼지 {pm10_grade}: 시야 저하")
        recommendations.append("외기 차단, 에어컨 내부순환 모드")

    # 점수 정규화
    score = max(0, min(100, score))

    # 등급 결정
    grade = _get_grade(score)
    grade_kr_map = {
        "좋음": "매우좋음",
        "보통": "좋음",
        "주의": "보통",
        "나쁨": "주의",
        "매우나쁨": "위험"
    }
    grade_kr = grade_kr_map.get(grade, "보통")

    # 기본 권장사항
    if not recommendations:
        recommendations.append("쾌적한 드라이브 날씨입니다. 안전 운전하세요!")

    if not factors:
        factors.append("도로 주행 조건 양호")

    return {
        "score": score,
        "grade": grade,
        "grade_kr": grade_kr,
        "factors": factors,
        "recommendations": recommendations,
        "warnings": warnings
    }


def calculate_camping_index(weather_data: dict, air_data: dict = None) -> dict:
    """
    캠핑지수 - 야외 캠핑 적합도 계산 (0-100, 높을수록 좋음)

    야외 캠핑의 안전성과 쾌적도를 종합 평가합니다.

    핵심 요소:
    - 낙뢰 (critical disqualifier): 치명적 위험, 즉시 score 0 반환
    - 바람: 15m/s 이상 텐트 파손, 화재 위험
    - 강수: 침수, 장비 손상
    - 기온: 쾌적 범위 15-25도

    Args:
        weather_data: 날씨 데이터 (sky, temp_current, humidity, rain_prob, wind_speed)
        air_data: 대기질 데이터 (선택사항)

    Returns:
        dict: score, grade, grade_kr, factors, recommendations, warnings
    """
    factors = []
    recommendations = []
    warnings = []

    # 데이터 추출
    sky = weather_data.get("sky", "맑음")
    temp_current = weather_data.get("temp_current", 20)
    humidity = weather_data.get("humidity", 50)
    rain_prob = weather_data.get("rain_prob", 0)
    wind_speed = weather_data.get("wind_speed", 0)

    # air_data 처리
    if air_data is None:
        air_data = {}
    pm25_grade = air_data.get("pm25_grade", "보통")

    # 낙뢰 체크 (Critical Disqualifier)
    lightning_keywords = ["천둥", "번개", "뇌우", "낙뢰"]
    has_lightning = any(kw in sky for kw in lightning_keywords)

    if has_lightning:
        return {
            "score": 0,
            "grade": "매우나쁨",
            "grade_kr": "위험",
            "factors": ["낙뢰 위험: 캠핑 절대 금지"],
            "recommendations": ["즉시 실내로 대피하세요", "차량 내부가 텐트보다 안전합니다"],
            "warnings": ["낙뢰는 치명적입니다! 야외 활동 즉시 중단"]
        }

    score = 100

    # 높은 강수확률도 뇌우 가능성 시사 (70% 이상 + 흐림/비)
    if rain_prob >= 70 and ("흐림" in sky or "비" in sky):
        factors.append("뇌우 가능성 있음: 캠핑 주의")
        warnings.append("갑작스러운 낙뢰 대비 필요, 실내 대피 계획 수립")

    # 1. 풍속 (텐트 안전, 화재 위험) - 최대 -50점
    if wind_speed >= 15:
        score -= 50
        factors.append(f"강풍 ({wind_speed}m/s): 텐트 설치 위험, 화재 위험")
        warnings.append("강풍 시 텐트 파손/비산 위험! 캠핑 자제 권고")
        recommendations.append("바람막이 설치 필수, 텐트 고정 철저히")
    elif wind_speed >= 10:
        score -= 30
        factors.append(f"바람 강함 ({wind_speed}m/s): 텐트 고정 주의")
        recommendations.append("텐트 팩 깊이 박기, 가이라인 필수")
    elif wind_speed >= 7:
        score -= 15
        factors.append(f"바람 있음 ({wind_speed}m/s)")
        recommendations.append("텐트 고정 확인")
    elif wind_speed >= 5:
        score -= 5
        factors.append(f"약한 바람 ({wind_speed}m/s)")

    # 2. 강수 - 최대 -40점
    if rain_prob >= 80 or "비" in sky or "눈" in sky:
        score -= 40
        factors.append(f"강수 예상 (강수확률 {rain_prob}%): 캠핑 부적합")
        warnings.append("비/눈 예보 시 캠핑 취소 또는 대피 준비")
        recommendations.append("방수 타프 필수, 침수 위험 지역 피하기")
    elif rain_prob >= 50:
        score -= 25
        factors.append(f"비 가능성 (강수확률 {rain_prob}%)")
        recommendations.append("타프 설치, 우비 준비")
    elif rain_prob >= 30:
        score -= 10
        factors.append(f"강수 주의 (강수확률 {rain_prob}%)")
        recommendations.append("방수 장비 점검")

    # 3. 기온 - 최대 -30점
    if temp_current < 0:
        score -= 30
        factors.append(f"영하 ({temp_current}도): 동계 캠핑 장비 필수")
        warnings.append("저체온증 위험! 동계용 침낭(-20도 이상) 필요")
        recommendations.append("핫팩, 난로, 따뜻한 음료 준비")
    elif temp_current < 5:
        score -= 20
        factors.append(f"추움 ({temp_current}도): 방한 장비 필요")
        recommendations.append("동계 침낭, 두꺼운 매트 권장")
    elif temp_current < 10:
        score -= 10
        factors.append(f"쌀쌀함 ({temp_current}도)")
        recommendations.append("긴 옷, 여분의 담요 준비")
    elif temp_current > 32:
        score -= 25
        factors.append(f"무더위 ({temp_current}도): 열사병 주의")
        warnings.append("폭염 시 그늘 확보, 수분 섭취 필수")
        recommendations.append("그늘진 사이트 선택, 선풍기/부채 준비")
    elif temp_current > 28:
        score -= 10
        factors.append(f"더움 ({temp_current}도)")
        recommendations.append("통풍 좋은 텐트, 시원한 음료 준비")
    elif 15 <= temp_current <= 25:
        score += 5  # 최적 기온 보너스
        factors.append(f"쾌적한 기온 ({temp_current}도): 캠핑 최적")

    # 4. 습도 - 최대 -10점
    if humidity >= 85:
        score -= 10
        factors.append(f"높은 습도 ({humidity}%): 결로 발생, 장비 젖음")
        recommendations.append("텐트 환기, 제습제 준비")
    elif humidity >= 75:
        score -= 5
        factors.append(f"습도 높음 ({humidity}%)")

    # 5. 미세먼지 (선택사항)
    if pm25_grade in ["매우나쁨", "나쁨"]:
        score -= 15
        factors.append(f"미세먼지 {pm25_grade}: 야외 활동 불리")
        recommendations.append("마스크 준비, 텐트 내 공기청정기 고려")

    # 점수 정규화
    score = max(0, min(100, score))

    # 등급 결정
    grade = _get_grade(score)
    grade_kr_map = {
        "좋음": "최적",
        "보통": "좋음",
        "주의": "보통",
        "나쁨": "주의",
        "매우나쁨": "위험"
    }
    grade_kr = grade_kr_map.get(grade, "보통")

    # 기본 권장사항
    if not recommendations:
        recommendations.append("캠핑하기 좋은 날씨입니다! 즐거운 캠핑 되세요.")

    if not factors:
        factors.append("캠핑 조건 양호")

    return {
        "score": score,
        "grade": grade,
        "grade_kr": grade_kr,
        "factors": factors,
        "recommendations": recommendations,
        "warnings": warnings
    }


def calculate_fishing_index(weather_data: dict) -> dict:
    """
    낚시지수 - 낚시 적합도 계산 (0-100, 높을수록 좋음)

    낚시 조건과 어류 활성도를 종합 평가합니다.

    핵심 요소:
    - 기압 변화 (rain_prob 프록시): 기압 하강 시 물고기 활성 증가
    - 바람: 10m/s 이상 소형 선박 위험 (풍랑주의보급)
    - 구름: 흐린 날 포식어 활동 증가
    - 가벼운 비: 물 표면 자극으로 오히려 좋을 수 있음

    Args:
        weather_data: 날씨 데이터 (sky, temp_current, rain_prob, wind_speed)

    Returns:
        dict: score, grade, grade_kr, factors, recommendations, warnings
    """
    factors = []
    recommendations = []
    warnings = []

    # 데이터 추출
    sky = weather_data.get("sky", "맑음")
    temp_current = weather_data.get("temp_current", 20)
    rain_prob = weather_data.get("rain_prob", 0)
    wind_speed = weather_data.get("wind_speed", 0)

    # 1. 풍속 (안전 최우선!) - Critical check
    if wind_speed >= 14:
        return {
            "score": 0,
            "grade": "매우나쁨",
            "grade_kr": "위험",
            "factors": [f"폭풍급 바람 ({wind_speed}m/s): 낚시 금지"],
            "recommendations": ["낚시 취소하세요. 안전이 최우선입니다."],
            "warnings": ["풍랑주의보급 바람! 선박 출항 금지, 갯바위 위험"]
        }

    score = 70  # 기본 점수 (보통)

    if wind_speed >= 10:
        score -= 35
        factors.append(f"강풍 ({wind_speed}m/s): 소형 선박 위험")
        warnings.append("소형 선박 조업 주의보급, 갯바위 낚시 위험")
        recommendations.append("방파제 또는 민물 낚시 권장")
    elif wind_speed >= 7:
        score -= 20
        factors.append(f"바람 강함 ({wind_speed}m/s): 캐스팅 어려움")
        recommendations.append("바람 방향 고려하여 포인트 선정")
    elif wind_speed >= 5:
        score -= 10
        factors.append(f"약간의 바람 ({wind_speed}m/s)")
    elif wind_speed < 2:
        score -= 5
        factors.append("무풍: 수면 정적, 입질 저조 가능")

    # 2. 기압 변화 (강수확률로 추정) - 낚시에 유리할 수 있음
    if 40 <= rain_prob <= 70:
        score += 10
        factors.append(f"기압 하강 중 (강수확률 {rain_prob}%): 물고기 활성 증가!")
        recommendations.append("입질 좋은 타이밍, 적극적으로 노려보세요")
    elif rain_prob > 70:
        score -= 10
        factors.append(f"비 예상 (강수확률 {rain_prob}%): 장비 보호 필요")
        recommendations.append("우비, 방수 가방 필수")

    # 3. 하늘 상태 - 포식어에 유리
    if sky in ["흐림", "구름많음", "구름 많음"]:
        score += 10
        factors.append(f"흐린 하늘 ({sky}): 포식어 활동 증가")
        recommendations.append("루어 낚시 적합, 큰 물고기 기대")
    elif sky == "맑음":
        score += 5
        factors.append("맑은 날씨: 쾌적한 낚시 환경")
        recommendations.append("자외선 차단, 그늘 확보")
    elif "비" in sky:
        if "소나기" in sky:
            score -= 15
            factors.append("소나기 예상: 급작스러운 비 주의")
            warnings.append("갑작스러운 소나기 대비 대피처 확인")
        else:
            score -= 5
            factors.append("가벼운 비: 오히려 입질 좋을 수 있음")
            recommendations.append("방수 장비 착용, 미끼 효과 기대")

    # 4. 기온 - 어종별 활성 온도
    if temp_current < 0:
        score -= 25
        factors.append(f"영하 ({temp_current}도): 혹한 낚시")
        warnings.append("동상 주의! 방한 철저히")
        recommendations.append("핫팩, 보온병, 방한장갑 필수")
    elif temp_current < 5:
        score -= 15
        factors.append(f"추움 ({temp_current}도): 어류 활동 저하")
        recommendations.append("깊은 수심 노리기, 저활성 미끼 사용")
    elif temp_current > 30:
        score -= 15
        factors.append(f"무더위 ({temp_current}도): 열사병 주의")
        warnings.append("그늘 확보, 수분 섭취 필수")
        recommendations.append("이른 아침 또는 저녁 낚시 권장")
    elif temp_current > 25:
        score -= 5
        factors.append(f"더움 ({temp_current}도)")
        recommendations.append("얕은 수심 그늘진 곳 탐색")
    elif 15 <= temp_current <= 22:
        score += 5
        factors.append(f"쾌적한 기온 ({temp_current}도): 최적의 낚시 컨디션")

    # 점수 정규화
    score = max(0, min(100, score))

    # 등급 결정
    grade = _get_grade(score)
    grade_kr_map = {
        "좋음": "최적",
        "보통": "좋음",
        "주의": "보통",
        "나쁨": "주의",
        "매우나쁨": "위험"
    }
    grade_kr = grade_kr_map.get(grade, "보통")

    # 기본 권장사항
    if not recommendations:
        recommendations.append("낚시하기 좋은 날입니다! 대어를 기대하세요.")

    if not factors:
        factors.append("낚시 조건 양호")

    return {
        "score": score,
        "grade": grade,
        "grade_kr": grade_kr,
        "factors": factors,
        "recommendations": recommendations,
        "warnings": warnings
    }


def calculate_golf_index(weather_data: dict, air_data: dict = None) -> dict:
    """
    골프지수 - 골프 플레이 적합도 계산 (0-100, 높을수록 좋음)

    골프 플레이 조건을 종합 평가합니다.

    핵심 요소:
    - 바람 (critical): 9m/s 이상 볼 궤적 심각한 편차
    - 비: 그립 미끄러움, 비거리 감소
    - 기온: 최적 18-26도 (추위 시 볼 압축률 저하)
    - 자외선: 장시간 야외 노출

    Args:
        weather_data: 날씨 데이터 (sky, temp_current, humidity, rain_prob, wind_speed, uv_index)
        air_data: 대기질 데이터 (선택사항)

    Returns:
        dict: score, grade, grade_kr, factors, recommendations, warnings
    """
    score = 100
    factors = []
    recommendations = []
    warnings = []

    # 데이터 추출
    sky = weather_data.get("sky", "맑음")
    temp_current = weather_data.get("temp_current", 20)
    humidity = weather_data.get("humidity", 50)
    rain_prob = weather_data.get("rain_prob", 0)
    wind_speed = weather_data.get("wind_speed", 0)
    uv_index = weather_data.get("uv_index", 5)

    # air_data 처리
    if air_data is None:
        air_data = {}
    pm25_grade = air_data.get("pm25_grade", "보통")

    # 1. 바람 (볼 궤적에 치명적!) - 최대 -40점
    if wind_speed >= 12:
        score -= 40
        factors.append(f"강풍 ({wind_speed}m/s): 정상적인 플레이 불가")
        warnings.append("강풍으로 볼 컨트롤 불가능! 골프 취소 권장")
    elif wind_speed >= 9:
        score -= 30
        factors.append(f"강한 바람 ({wind_speed}m/s): 볼 궤적 큰 편차")
        warnings.append("클럽 선택 2-3클럽 조정 필요")
        recommendations.append("낮은 탄도 샷 구사, 바람 방향 필수 확인")
    elif wind_speed >= 6:
        score -= 20
        factors.append(f"바람 있음 ({wind_speed}m/s): 볼 편차 발생")
        recommendations.append("풍향 고려하여 에임 조정")
    elif wind_speed >= 4:
        score -= 10
        factors.append(f"약한 바람 ({wind_speed}m/s)")
        recommendations.append("바람 방향 체크 습관화")
    elif wind_speed < 2:
        factors.append("무풍: 최적의 샷 컨디션")

    # 2. 강수 (그립 & 비거리) - 최대 -40점
    if rain_prob >= 80 or "비" in sky:
        score -= 40
        factors.append(f"비 예상 (강수확률 {rain_prob}%): 플레이 불리")
        warnings.append("비 오면 그립 미끄러움, 비거리 10-15% 감소")
        recommendations.append("우산, 타월 여분 준비, 레인 글러브 착용")
    elif rain_prob >= 50:
        score -= 25
        factors.append(f"비 가능성 (강수확률 {rain_prob}%)")
        recommendations.append("우비, 방수 모자 준비")
    elif rain_prob >= 30:
        score -= 10
        factors.append(f"강수 주의 (강수확률 {rain_prob}%)")

    # 3. 기온 (볼 압축률, 체력) - 최대 -25점
    if temp_current < 10:
        score -= 25
        factors.append(f"추움 ({temp_current}도): 볼 압축률 저하, 비거리 감소")
        warnings.append("추위로 근육 경직 주의, 워밍업 필수")
        recommendations.append("핫팩, 따뜻한 음료, 레이어드 착용")
    elif temp_current < 15:
        score -= 15
        factors.append(f"쌀쌀함 ({temp_current}도)")
        recommendations.append("워밍업 충분히, 방풍 자켓")
    elif temp_current > 32:
        score -= 25
        factors.append(f"폭염 ({temp_current}도): 체력 소모 심각")
        warnings.append("열사병 주의! 수분 섭취 필수")
        recommendations.append("쿨링 타월, 전해질 음료, 그늘 휴식")
    elif temp_current > 28:
        score -= 10
        factors.append(f"더움 ({temp_current}도)")
        recommendations.append("수분 보충 자주, 양산/모자 착용")
    elif 18 <= temp_current <= 26:
        score += 5
        factors.append(f"쾌적한 기온 ({temp_current}도): 골프 최적 컨디션")

    # 4. 자외선 (장시간 야외) - 최대 -15점
    if uv_index >= 8:
        score -= 15
        factors.append(f"자외선 매우 높음 (지수 {uv_index})")
        warnings.append("강한 자외선! 피부/눈 보호 필수")
        recommendations.append("선크림 SPF50+, 선글라스, 모자 필수")
    elif uv_index >= 6:
        score -= 10
        factors.append(f"자외선 높음 (지수 {uv_index})")
        recommendations.append("선크림, 모자 착용 권장")
    elif uv_index >= 3:
        score -= 5
        factors.append(f"자외선 보통 (지수 {uv_index})")

    # 5. 습도 - 최대 -10점
    if humidity >= 80:
        score -= 10
        factors.append(f"높은 습도 ({humidity}%): 그립 미끄러움")
        recommendations.append("그립 타월 자주 사용, 글러브 여분 준비")
    elif humidity >= 70:
        score -= 5
        factors.append(f"습도 높음 ({humidity}%)")

    # 6. 미세먼지 (선택사항)
    if pm25_grade in ["매우나쁨", "나쁨"]:
        score -= 15
        factors.append(f"미세먼지 {pm25_grade}: 호흡기 주의")
        recommendations.append("마스크 준비, 격렬한 움직임 자제")

    # 점수 정규화
    score = max(0, min(100, score))

    # 등급 결정
    grade = _get_grade(score)
    grade_kr_map = {
        "좋음": "최적",
        "보통": "좋음",
        "주의": "보통",
        "나쁨": "주의",
        "매우나쁨": "위험"
    }
    grade_kr = grade_kr_map.get(grade, "보통")

    # 기본 권장사항
    if not recommendations:
        recommendations.append("골프하기 완벽한 날씨입니다! 좋은 스코어 기대하세요.")

    if not factors:
        factors.append("골프 조건 최적")

    return {
        "score": score,
        "grade": grade,
        "grade_kr": grade_kr,
        "factors": factors,
        "recommendations": recommendations,
        "warnings": warnings
    }


def calculate_running_index(weather_data: dict, air_data: dict) -> dict:
    """
    러닝지수 - 야외 러닝 적합도 계산 (0-100, 높을수록 좋음)

    야외 러닝 조건을 종합 평가합니다.

    핵심 요소:
    - AQI (critical): 150 초과 시 야외 운동 금지 (EPA 기준)
    - 기온: 10-18도 최적 (마라톤 연구 기반)
    - 습도+고온: 열사병 위험 급증
    - 자외선: 장시간 노출 위험

    Args:
        weather_data: 날씨 데이터 (temp_current, humidity, rain_prob, wind_speed, uv_index)
        air_data: 대기질 데이터 (pm25_grade, pm25_value, pm10_value)

    Returns:
        dict: score, grade, grade_kr, factors, recommendations, warnings
    """
    factors = []
    recommendations = []
    warnings = []

    # 데이터 추출
    temp_current = weather_data.get("temp_current", 20)
    humidity = weather_data.get("humidity", 50)
    rain_prob = weather_data.get("rain_prob", 0)
    wind_speed = weather_data.get("wind_speed", 0)
    uv_index = weather_data.get("uv_index", 5)

    # 대기질 데이터 추출
    pm25_grade = air_data.get("pm25_grade", "보통") if air_data else "보통"
    pm25_value = air_data.get("pm25_value", 25) if air_data else 25

    # AQI 추정 (PM2.5 기준 간이 계산)
    # 한국 기준: 좋음 0-15, 보통 16-35, 나쁨 36-75, 매우나쁨 76+
    if pm25_value <= 15:
        aqi_estimate = pm25_value * 3  # ~45
    elif pm25_value <= 35:
        aqi_estimate = 50 + (pm25_value - 15) * 2.5  # 50-100
    elif pm25_value <= 75:
        aqi_estimate = 100 + (pm25_value - 35) * 1.25  # 100-150
    else:
        aqi_estimate = 150 + (pm25_value - 75)  # 150+

    # 1. 대기질 (Critical!) - AQI 150 초과 시 실내 운동
    if aqi_estimate > 150 or pm25_grade == "매우나쁨":
        return {
            "score": 0,
            "grade": "매우나쁨",
            "grade_kr": "위험",
            "factors": [f"미세먼지 매우나쁨 (PM2.5: {pm25_value}ug/m3): 야외 운동 금지"],
            "recommendations": ["실내 러닝머신 또는 홈트레이닝으로 대체하세요"],
            "warnings": ["EPA 기준 AQI 150 초과! 야외 격렬한 운동 시 폐 손상 위험"]
        }

    score = 100

    if pm25_grade == "나쁨" or aqi_estimate > 100:
        score -= 30
        factors.append(f"미세먼지 나쁨 (PM2.5: {pm25_value}ug/m3): 운동 강도 낮추기")
        warnings.append("호흡량 증가로 미세먼지 흡입 증가, 가벼운 조깅만 권장")
        recommendations.append("마스크 착용 러닝 또는 실내 운동 권장")
    elif pm25_grade == "보통":
        score -= 10
        factors.append(f"미세먼지 보통 (PM2.5: {pm25_value}ug/m3)")
        recommendations.append("장시간 러닝 피하기")
    else:
        factors.append(f"미세먼지 좋음 (PM2.5: {pm25_value}ug/m3): 호흡 쾌적")

    # 2. 기온 + 습도 복합 (열사병 위험)
    heat_index = temp_current + (humidity / 100) * 10  # 간이 열지수

    if temp_current > 32 or heat_index > 40:
        score -= 40
        factors.append(f"폭염 ({temp_current}도, 습도 {humidity}%): 열사병 위험 매우 높음")
        warnings.append("열사병 위험! 야외 러닝 절대 자제, 실내 운동 권장")
    elif temp_current > 28 or heat_index > 35:
        score -= 25
        factors.append(f"더움 ({temp_current}도, 습도 {humidity}%): 열사병 주의")
        warnings.append("충분한 수분 섭취, 이른 아침/저녁 시간 선택")
        recommendations.append("10-15분마다 물 마시기, 그늘 코스 선택")
    elif temp_current > 25:
        score -= 15
        factors.append(f"다소 더움 ({temp_current}도)")
        recommendations.append("수분 보충 자주, 강도 조절")
    elif temp_current < 0:
        score -= 20
        factors.append(f"영하 ({temp_current}도): 동상, 호흡기 자극")
        warnings.append("찬 공기 흡입 시 기관지 자극 주의")
        recommendations.append("넥워머로 호흡기 보호, 레이어드 착용")
    elif temp_current < 5:
        score -= 10
        factors.append(f"추움 ({temp_current}도)")
        recommendations.append("워밍업 충분히, 보온 레이어")
    elif 10 <= temp_current <= 18:
        score += 10
        factors.append(f"최적 기온 ({temp_current}도): 러닝 최고의 컨디션")

    # 3. 습도 단독 평가 (땀 증발)
    if humidity >= 80:
        score -= 15
        factors.append(f"높은 습도 ({humidity}%): 땀 증발 어려움")
        recommendations.append("속건 소재 착용, 페이스 조절")
    elif humidity >= 70:
        score -= 10
        factors.append(f"습도 높음 ({humidity}%)")

    # 4. 강수
    if rain_prob >= 70:
        score -= 20
        factors.append(f"비 예상 (강수확률 {rain_prob}%): 미끄럼 주의")
        recommendations.append("트레일 러닝 자제, 방수 재킷 착용")
    elif rain_prob >= 40:
        score -= 10
        factors.append(f"비 가능성 (강수확률 {rain_prob}%)")

    # 5. 자외선
    if uv_index >= 8:
        score -= 10
        factors.append(f"자외선 매우 높음 (지수 {uv_index})")
        warnings.append("강한 자외선! 11-15시 피하기")
        recommendations.append("선크림 SPF50+, 모자, 선글라스")
    elif uv_index >= 6:
        score -= 5
        factors.append(f"자외선 높음 (지수 {uv_index})")
        recommendations.append("선크림, 모자 권장")

    # 6. 바람
    if wind_speed >= 10:
        score -= 15
        factors.append(f"강풍 ({wind_speed}m/s): 러닝 저항 증가")
        recommendations.append("바람 등지고 출발, 마무리는 맞바람으로")
    elif wind_speed >= 6:
        score -= 5
        factors.append(f"바람 있음 ({wind_speed}m/s)")

    # 점수 정규화
    score = max(0, min(100, score))

    # 등급 결정
    grade = _get_grade(score)
    grade_kr_map = {
        "좋음": "최적",
        "보통": "좋음",
        "주의": "보통",
        "나쁨": "주의",
        "매우나쁨": "위험"
    }
    grade_kr = grade_kr_map.get(grade, "보통")

    # 기본 권장사항
    if not recommendations:
        recommendations.append("러닝하기 완벽한 날씨입니다! 즐거운 러닝 되세요.")

    if not factors:
        factors.append("러닝 조건 최적")

    return {
        "score": score,
        "grade": grade,
        "grade_kr": grade_kr,
        "factors": factors,
        "recommendations": recommendations,
        "warnings": warnings
    }


def calculate_bbq_index(weather_data: dict) -> dict:
    """
    바베큐지수 - 야외 바베큐 적합도 계산 (0-100, 높을수록 좋음)

    야외 그릴링 조건을 종합 평가합니다.

    핵심 요소:
    - 바람 (critical): 8m/s 이상 화재 위험
    - 비: 화덕 운용 어려움
    - 기온: 쾌적한 야외 식사 온도 18-28도

    Args:
        weather_data: 날씨 데이터 (sky, temp_current, humidity, rain_prob, wind_speed)

    Returns:
        dict: score, grade, grade_kr, factors, recommendations, warnings
    """
    score = 100
    factors = []
    recommendations = []
    warnings = []

    # 데이터 추출
    sky = weather_data.get("sky", "맑음")
    temp_current = weather_data.get("temp_current", 22)
    humidity = weather_data.get("humidity", 50)
    rain_prob = weather_data.get("rain_prob", 0)
    wind_speed = weather_data.get("wind_speed", 0)

    # 1. 바람 (화재 안전 Critical!) - 최대 -50점
    if wind_speed >= 12:
        score -= 50
        factors.append(f"강풍 ({wind_speed}m/s): 화재 위험 매우 높음")
        warnings.append("강풍 시 바베큐 금지! 불씨 비산으로 화재 발생 위험")
        recommendations.append("실내 그릴 또는 다른 날로 연기")
    elif wind_speed >= 8:
        score -= 35
        factors.append(f"바람 강함 ({wind_speed}m/s): 화재 주의")
        warnings.append("바람막이 설치 필수, 불꽃 관리 철저히")
        recommendations.append("바람막이 설치, 소화기 준비")
    elif wind_speed >= 5:
        score -= 20
        factors.append(f"바람 있음 ({wind_speed}m/s): 불꽃 흔들림")
        recommendations.append("그릴 뚜껑 활용, 바람 방향 고려")
    elif wind_speed >= 3:
        score -= 10
        factors.append(f"약한 바람 ({wind_speed}m/s)")
    else:
        factors.append("무풍: 그릴 온도 유지 최적")

    # 2. 강수 (화덕 운용) - 최대 -40점
    if rain_prob >= 80 or "비" in sky:
        score -= 40
        factors.append(f"비 예상 (강수확률 {rain_prob}%): 바베큐 부적합")
        warnings.append("비 오면 그릴 운용 어려움, 화상 위험 증가")
        recommendations.append("지붕 있는 장소 또는 다른 날로 연기")
    elif rain_prob >= 50:
        score -= 25
        factors.append(f"비 가능성 (강수확률 {rain_prob}%)")
        recommendations.append("타프/차양막 준비, 그릴 커버")
    elif rain_prob >= 30:
        score -= 10
        factors.append(f"강수 주의 (강수확률 {rain_prob}%)")
        recommendations.append("우비, 그릴 커버 준비")

    # 3. 기온 - 최대 -20점
    if temp_current < 5:
        score -= 20
        factors.append(f"추움 ({temp_current}도): 야외 활동 불편")
        recommendations.append("핫팩, 난로 준비, 따뜻한 음료")
    elif temp_current < 10:
        score -= 10
        factors.append(f"쌀쌀함 ({temp_current}도)")
        recommendations.append("겉옷 준비, 그릴 옆에서 따뜻하게")
    elif temp_current > 35:
        score -= 20
        factors.append(f"폭염 ({temp_current}도): 열사병 + 화기 위험")
        warnings.append("폭염 + 화기 사용으로 열사병 위험 급증")
        recommendations.append("그늘 확보, 충분한 수분, 저녁 시간 권장")
    elif temp_current > 30:
        score -= 10
        factors.append(f"더움 ({temp_current}도)")
        recommendations.append("그늘막 설치, 시원한 음료 준비")
    elif 18 <= temp_current <= 28:
        score += 10
        factors.append(f"쾌적한 기온 ({temp_current}도): 바베큐 최적")

    # 4. 습도 (불 피우기 영향)
    if humidity >= 85:
        score -= 10
        factors.append(f"높은 습도 ({humidity}%): 착화 어려울 수 있음")
        recommendations.append("점화제 충분히 준비")
    elif humidity <= 30:
        score -= 5
        factors.append(f"매우 건조 ({humidity}%): 화재 확산 주의")
        warnings.append("건조한 날씨에 화재 확산 빠름, 물 준비 필수")

    # 점수 정규화
    score = max(0, min(100, score))

    # 등급 결정
    grade = _get_grade(score)
    grade_kr_map = {
        "좋음": "최적",
        "보통": "좋음",
        "주의": "보통",
        "나쁨": "주의",
        "매우나쁨": "위험"
    }
    grade_kr = grade_kr_map.get(grade, "보통")

    # 기본 권장사항
    if not recommendations:
        recommendations.append("바베큐하기 완벽한 날씨입니다! 맛있는 고기 드세요.")

    if not factors:
        factors.append("바베큐 조건 최적")

    return {
        "score": score,
        "grade": grade,
        "grade_kr": grade_kr,
        "factors": factors,
        "recommendations": recommendations,
        "warnings": warnings
    }
