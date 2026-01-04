# Weather Life MCP API 명세 v3.7.0

## 개요

Weather Life MCP는 날씨, 미세먼지, 옷차림 추천 + **한국 특화 생활지수** + **Kakao Maps 장소 검색**을 제공하는 MCP 서버입니다.

| 항목 | 값 |
|------|-----|
| Transport | Streamable HTTP (Stateless) |
| Endpoint | `https://web-production-19a3b.up.railway.app/mcp` |
| Protocol | MCP (Model Context Protocol) |
| Framework | FastMCP 2.14.1 |
| Version | 3.7.0 |

---

## MCP 요청/응답 형식

### 요청
```bash
curl -X POST https://web-production-19a3b.up.railway.app/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "get_weather",
      "arguments": {"location": "서울"}
    },
    "id": 1
  }'
```

### 응답
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{...}"
      }
    ]
  }
}
```

---

## Tools (30개)

### 기본 Tool (5개)

#### 1. get_weather

현재 날씨와 오늘의 날씨 예보를 조회합니다.

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| location | string | N | "서울" | 지역명 (예: 서울, 강남구, 부산) |

**Response:**

```json
{
  "location": "서울",
  "current_weather": {
    "temperature": -1,
    "humidity": 42,
    "wind_speed": 2.0,
    "precipitation_type": "없음"
  },
  "today_summary": {
    "min_temperature": -5,
    "max_temperature": 3,
    "sky": "맑음",
    "precipitation_probability": 0
  },
  "hourly_forecast": [...]
}
```

---

#### 2. get_weekly_forecast

3일 예보 (오늘/내일/모레)를 조회합니다.

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| location | string | N | "서울" | 지역명 |

**Response:**

```json
{
  "location": "서울",
  "forecast": [
    {"date": "2024-12-29", "min_temp": -3, "max_temp": 5, "sky": "맑음"},
    {"date": "2024-12-30", "min_temp": -2, "max_temp": 6, "sky": "구름많음"},
    {"date": "2024-12-31", "min_temp": -1, "max_temp": 4, "sky": "흐림"}
  ]
}
```

---

#### 3. get_air_quality_info

실시간 미세먼지 정보를 조회합니다.

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| location | string | N | "서울" | 지역명 또는 측정소명 |

**Response:**

```json
{
  "location": "중구",
  "data_time": "2025-12-21 19:00",
  "pm10": {"value": 27, "grade": "좋음", "unit": "ug/m3"},
  "pm25": {"value": 9, "grade": "좋음", "unit": "ug/m3"}
}
```

---

#### 4. get_outfit_recommendation_tool

날씨에 맞는 옷차림을 추천합니다.

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| location | string | N | "서울" | 지역명 |
| temperature | float | N | null | 직접 기온 입력 (선택) |

**Response:**

```json
{
  "location": "서울",
  "temperature": -1,
  "category": "한겨울",
  "outfit": {
    "top": ["히트텍", "두꺼운 니트"],
    "bottom": ["기모 팬츠"],
    "outer": ["롱패딩"],
    "accessories": ["머플러", "장갑", "핫팩"]
  },
  "tip": "최대한 따뜻하게! 동상 주의."
}
```

---

#### 5. should_i_go_out

외출 적합도를 종합적으로 판단합니다.

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| location | string | N | "서울" | 지역명 |

**Response:**

```json
{
  "location": "서울",
  "outing_score": {
    "score": 75,
    "grade": "보통",
    "emoji": "",
    "message": "외출 가능하지만 주의사항이 있어요."
  },
  "outfit": {...},
  "summary": "외출 적합도 75점 (보통)"
}
```

---

### 생활기상지수 Tool (2개)

#### 6. get_uv_info

자외선지수만 조회합니다.

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| location | string | N | "서울" | 지역명 |

**Response:**

```json
{
  "location": "서울",
  "uv_index": 5,
  "level": "높음",
  "recommendation": "자외선 차단제 필수, 모자/선글라스 권장"
}
```

---

#### 7. get_food_safety_index

식중독지수를 조회합니다.

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| location | string | N | "서울" | 지역명 |

**Response:**

```json
{
  "location": "서울",
  "food_poison_index": 75,
  "level": "경고",
  "recommendation": "음식물 상온 보관 금지, 조리 후 빠른 섭취"
}
```

---

### 활동지수 Tool (5개)

#### 8. is_good_for_laundry

빨래하기 좋은 날인지 판단합니다.

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| location | string | N | "서울" | 지역명 |

**Response:**

```json
{
  "location": "서울",
  "laundry_score": 85,
  "grade": "최적",
  "is_good": true,
  "factors": {
    "humidity": {"value": 45, "score": 90},
    "precipitation": {"probability": 10, "score": 90},
    "wind": {"speed": 3.0, "score": 80},
    "temperature": {"value": 15, "score": 85}
  },
  "recommendation": "빨래하기 좋은 날! 오후 3시 전에 널어두세요.",
  "best_time": "10:00-15:00"
}
```

**빨래지수 등급:**

| 점수 | 등급 | 설명 |
|------|------|------|
| 80-100 | 최적 | 빨래 건조 최적 |
| 60-79 | 좋음 | 건조 잘 됨 |
| 40-59 | 보통 | 건조에 시간 걸림 |
| 0-39 | 나쁨 | 실내 건조 권장 |

---

#### 9. is_good_for_hiking

등산하기 좋은 날인지 판단합니다.

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| location | string | N | "서울" | 지역명 |

**Response:**

```json
{
  "location": "서울",
  "hiking_score": 88,
  "grade": "최적",
  "is_good": true,
  "factors": {
    "temperature": {"value": 15, "score": 95},
    "precipitation": {"probability": 0, "score": 100},
    "air_quality": {"pm25": 15, "score": 85},
    "wind": {"speed": 2.0, "score": 90}
  },
  "recommended_mountains": [
    {"name": "북한산", "difficulty": "중", "distance": "서울 근교"},
    {"name": "관악산", "difficulty": "중", "distance": "서울"},
    {"name": "도봉산", "difficulty": "중상", "distance": "서울 북부"}
  ],
  "recommendation": "등산하기 최적! 북한산 추천드려요.",
  "caution": "오후 5시 전 하산 권장"
}
```

---

#### 12. is_good_for_picnic

피크닉/한강 가기 좋은 날인지 판단합니다.

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| location | string | N | "서울" | 지역명 |

**Response:**

```json
{
  "location": "서울",
  "picnic_score": 92,
  "grade": "최적",
  "is_good": true,
  "factors": {
    "temperature": {"value": 22, "score": 100},
    "sky": {"condition": "맑음", "score": 100},
    "precipitation": {"probability": 0, "score": 100},
    "wind": {"speed": 2.0, "score": 90}
  },
  "recommended_spots": [
    {"name": "여의도 한강공원", "feature": "넓은 잔디밭"},
    {"name": "반포 한강공원", "feature": "달빛무지개분수"},
    {"name": "뚝섬 한강공원", "feature": "수영장 인근"}
  ],
  "chimaek_time": "17:00-19:00 (해질녘 치맥 추천!)",
  "recommendation": "피크닉 완벽한 날! 한강 치맥 어때요?"
}
```

---

#### 13. is_good_for_car_wash

세차하기 좋은 날인지 판단합니다.

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| location | string | N | "서울" | 지역명 |

**Response:**

```json
{
  "location": "서울",
  "car_wash_score": 45,
  "grade": "별로",
  "is_good": false,
  "factors": {
    "today_rain": {"probability": 10, "score": 90},
    "tomorrow_rain": {"probability": 80, "score": 20},
    "dust": {"pm10": 45, "score": 70},
    "humidity": {"value": 70, "score": 50}
  },
  "recommendation": "내일 비 예보! 세차는 비 온 뒤로 미루세요.",
  "next_good_day": "모레 (12/26)"
}
```

---

#### 14. is_good_for_exercise

운동하기 좋은 날인지 판단합니다.

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| location | string | N | "서울" | 지역명 |

**Response:**

```json
{
  "location": "서울",
  "exercise_score": 78,
  "grade": "좋음",
  "is_good": true,
  "factors": {
    "temperature": {"value": 18, "score": 90},
    "humidity": {"value": 55, "score": 85},
    "air_quality": {"pm25": 20, "score": 80},
    "wind": {"speed": 2.5, "score": 85}
  },
  "health_risk": "낮음",
  "hydration_recommendation": "시간당 500ml 수분 섭취 권장",
  "recommendation": "운동하기 좋은 날씨입니다!"
}
```

---

### 건강지수 Tool (7개) - 과학적 연구 기반!

#### 13. get_cold_flu_risk

감기/독감 위험도를 분석합니다. (MIT, Yale, PNAS 연구 기반)

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| location | string | N | "서울" | 지역명 |

**Response:**

```json
{
  "location": "서울",
  "cold_flu_risk": {
    "score": 72,
    "grade": "높음",
    "level": "warning"
  },
  "factors": {
    "temperature": {"value": 3, "impact": "높음"},
    "humidity": {"value": 35, "impact": "높음"},
    "temperature_range": {"value": 12, "impact": "중간"}
  },
  "scientific_basis": "MIT/Yale 연구: 저온+저습도=바이러스 생존력 증가",
  "recommendation": "마스크 착용, 실내 가습, 손씻기 권장"
}
```

---

#### 18. get_commute_index

출퇴근 적합도를 교통수단별로 분석합니다.

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| location | string | N | "서울" | 지역명 |

**Response:**

```json
{
  "location": "서울",
  "commute_scores": {
    "car": {"score": 75, "grade": "좋음", "issues": ["결빙 주의"]},
    "public_transit": {"score": 85, "grade": "최적", "issues": []},
    "bicycle": {"score": 45, "grade": "별로", "issues": ["저온", "결빙"]}
  },
  "best_option": "public_transit",
  "weather_impact": "영하권 기온으로 도보/자전거 주의",
  "recommendation": "대중교통 이용 권장"
}
```

---

#### 19. get_allergy_risk

계절별 알레르기 위험도를 분석합니다.

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| location | string | N | "서울" | 지역명 |

**Response:**

```json
{
  "location": "서울",
  "allergy_risk": {
    "score": 65,
    "grade": "보통",
    "level": "caution"
  },
  "allergens": {
    "pollen": {"level": "낮음", "types": []},
    "dust": {"pm10": 45, "level": "보통"},
    "yellow_dust": {"active": false}
  },
  "season_info": "겨울철 - 꽃가루 위험 낮음, 건조로 인한 피부 알레르기 주의",
  "recommendation": "실내 습도 유지, 보습제 사용 권장"
}
```

---

### v2.4 건강/라이프스타일 Tool (4개)

#### 20. get_migraine_risk

편두통 위험도를 분석합니다. (기압/습도 연구 기반)

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| location | string | N | "서울" | 지역명 |

**Response:**

```json
{
  "location": "서울",
  "migraine_risk": {
    "score": 58,
    "grade": "보통",
    "level": "caution"
  },
  "factors": {
    "pressure_change": {"value": -5, "impact": "중간"},
    "humidity": {"value": 65, "impact": "낮음"},
    "temperature_change": {"value": 8, "impact": "중간"}
  },
  "scientific_basis": "기압 급변 시 두통 발생률 증가 연구 기반",
  "recommendation": "두통약 휴대, 충분한 수분 섭취"
}
```

---

#### 21. get_sleep_quality_index

수면 환경 적합도를 분석합니다.

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| location | string | N | "서울" | 지역명 |

**Response:**

```json
{
  "location": "서울",
  "sleep_quality": {
    "score": 82,
    "grade": "좋음"
  },
  "factors": {
    "temperature": {"value": 20, "optimal": "18-22C", "score": 90},
    "humidity": {"value": 50, "optimal": "40-60%", "score": 95},
    "pressure": {"stable": true, "score": 85}
  },
  "recommendation": "적정 온습도입니다. 숙면하기 좋은 환경!",
  "tips": ["취침 1시간 전 환기", "어두운 환경 유지"]
}
```

---

#### 22. get_photography_index

사진 촬영 조건을 분석합니다. (골든아워 계산 포함)

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| location | string | N | "서울" | 지역명 |

**Response:**

```json
{
  "location": "서울",
  "photography_score": 88,
  "grade": "최적",
  "lighting": {
    "current": "좋음",
    "golden_hour_morning": "06:30-07:30",
    "golden_hour_evening": "17:00-18:00",
    "blue_hour": "17:45-18:15"
  },
  "conditions": {
    "sky": "맑음",
    "visibility": "좋음",
    "cloud_cover": 20
  },
  "recommendation": "야외 촬영 최적! 골든아워 활용 추천",
  "best_spots": ["남산타워", "한강공원", "경복궁"]
}
```

---

#### 23. get_joint_pain_risk

관절통 위험도를 분석합니다. (관절염 연구 기반)

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| location | string | N | "서울" | 지역명 |

**Response:**

```json
{
  "location": "서울",
  "joint_pain_risk": {
    "score": 62,
    "grade": "보통",
    "level": "caution"
  },
  "factors": {
    "temperature_drop": {"value": -8, "impact": "높음"},
    "humidity": {"value": 75, "impact": "중간"},
    "pressure_change": {"value": -3, "impact": "낮음"}
  },
  "scientific_basis": "온도 하강과 습도 상승 시 관절통 증가 연구",
  "recommendation": "관절 보온, 스트레칭 권장",
  "tips": ["무릎/손목 보온대 착용", "실내 온도 유지"]
}
```

---

### 레저/스포츠 Tool (3개)

#### 20. get_camping_index

캠핑 적합도를 분석합니다. (낙뢰/강풍 위험도 포함)

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| location | string | N | "서울" | 지역명 |

**Response:**

```json
{
  "location": "서울",
  "camping_score": 82,
  "grade": "최적",
  "is_good": true,
  "factors": {
    "weather": {"condition": "맑음", "score": 95},
    "temperature": {"min": 5, "max": 18, "score": 85},
    "wind": {"speed": 2.5, "score": 90},
    "precipitation": {"probability": 0, "score": 100},
    "lightning_risk": {"level": "없음", "score": 100}
  },
  "warnings": [],
  "gear_recommendation": ["3계절 침낭", "방한복", "핫팩"],
  "recommended_sites": [
    {"name": "가평 캠핑장", "feature": "계곡 인근"},
    {"name": "양평 글램핑", "feature": "편의시설 완비"}
  ],
  "recommendation": "캠핑하기 좋은 날씨! 저녁 기온 하락 대비 필요",
  "fire_safety": "화재 위험 낮음 - 캠프파이어 가능"
}
```

---

#### 21. get_fishing_index

낚시 적합도를 분석합니다. (기압변화 기반)

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| location | string | N | "서울" | 지역명 |

**Response:**

```json
{
  "location": "서울",
  "fishing_score": 78,
  "grade": "좋음",
  "is_good": true,
  "factors": {
    "pressure": {"value": 1018, "trend": "상승", "score": 85},
    "pressure_change": {"value": 3, "impact": "긍정적"},
    "wind": {"speed": 3.0, "direction": "남서", "score": 80},
    "precipitation": {"probability": 5, "score": 95},
    "temperature": {"value": 15, "score": 75}
  },
  "fish_activity": {
    "level": "활발",
    "reason": "기압 상승 중 - 어류 활동 증가"
  },
  "best_time": "06:00-09:00, 16:00-18:00",
  "recommended_spots": [
    {"name": "팔당댐", "fish_type": "붕어, 잉어"},
    {"name": "청평호", "fish_type": "배스"}
  ],
  "recommendation": "낚시하기 좋은 조건! 기압 상승 중으로 입질 기대",
  "gear_tip": "바람 대비 방풍 재킷 필수"
}
```

---

#### 22. get_golf_index

골프 라운딩 적합도를 분석합니다. (바람/볼비행 영향)

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| location | string | N | "서울" | 지역명 |

**Response:**

```json
{
  "location": "서울",
  "golf_score": 85,
  "grade": "최적",
  "is_good": true,
  "factors": {
    "temperature": {"value": 18, "feels_like": 17, "score": 90},
    "wind": {"speed": 2.0, "direction": "북동", "score": 95},
    "precipitation": {"probability": 0, "score": 100},
    "humidity": {"value": 55, "score": 85},
    "uv": {"index": 5, "score": 75}
  },
  "ball_flight_impact": {
    "distance": "정상",
    "direction": "영향 미미",
    "club_recommendation": "평소 클럽 선택"
  },
  "course_condition": {
    "green": "보통",
    "fairway": "양호"
  },
  "recommended_tee_time": "09:00-11:00, 14:00-16:00",
  "recommendation": "골프 라운딩 최적! 바람 영향 적음",
  "gear_tip": "자외선 차단제, 선글라스 권장"
}
```

---

### 장소 검색 Tool (6개) - Kakao Maps 연동! (v3.0 NEW!)

#### 23. get_recommended_spots

활동별 추천 장소를 알려드립니다.

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| location | string | N | "서울" | 지역명 |
| activity | string | N | "all" | hiking/camping/picnic/drive/fishing/golf/running/bbq/all |

---

#### 24. search_nearby_places

주변 장소를 검색합니다. (Kakao Maps API)

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| keyword | string | Y | - | 검색 키워드 (예: "맛집", "카페") |
| location | string | N | "서울" | 검색 중심 지역 |
| radius | integer | N | 2000 | 검색 반경 (미터, 최대 20000) |
| count | integer | N | 5 | 결과 개수 (최대 15) |

**Response:**

```json
{
  "category": "카페",
  "total_count": 1609,
  "places": [
    {
      "name": "공차 강남역점",
      "address": "서울 강남구 강남대로 지하 396",
      "category": "음식점 > 카페 > 공차",
      "phone": "02-569-7344",
      "distance": "15",
      "place_url": "http://place.map.kakao.com/19038749"
    }
  ]
}
```

---

#### 25. get_directions_link

출발지에서 목적지까지 길찾기 링크를 생성합니다.

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| origin | string | Y | - | 출발지 |
| destination | string | Y | - | 목적지 |
| mode | string | N | "car" | car/transit/walk/bike |

---

#### 26. search_restaurant

맛집/음식점을 검색합니다.

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| location | string | N | "서울" | 검색 지역 |
| cuisine | string | N | "" | 음식 종류 (한식, 회, 고기 등) |
| count | integer | N | 5 | 결과 개수 |

---

#### 27. get_place_recommendation

상황/시간에 맞는 장소를 스마트하게 추천합니다.

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| location | string | N | "서울" | 지역 |
| situation | string | N | "혼자" | 혼자/친구/데이트/가족/비즈니스 |
| time_of_day | string | N | "" | 아침/점심/오후/저녁/심야 (빈값=현재시간) |
| count | integer | N | 5 | 결과 개수 |

---

#### 28. get_smart_course

현재 날씨를 분석해서 최적의 코스를 추천합니다!

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| location | string | N | "서울" | 지역 |
| situation | string | N | "데이트" | 데이트/친구/가족/혼자 |

**Response:**

비 오면 실내 위주, 맑으면 야외 포함으로 자동 구성된 3단계 코스를 추천합니다.

---

### v3.7 스마트 분석 Tool (2개) - NEW!

#### 29. get_best_time_for_activity

오늘 하루 중 활동하기 가장 좋은 시간대를 분석합니다!

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| location | string | N | "서울" | 지역명 |
| activity | string | N | "외출" | 활동 종류 (외출/운동/빨래/등산/피크닉) |

**Response:**

```json
{
  "location": "서울",
  "activity": "외출",
  "best_time": {
    "time": "14:00",
    "score": 85,
    "weather": "8°C, 맑음",
    "recommendation": "14:00이 가장 좋아요! (85점)"
  },
  "best_period": {
    "period": "오후",
    "avg_score": 78,
    "recommendation": "오후가 전반적으로 좋아요 (평균 78점)"
  },
  "avoid_time": {
    "time": "06:00",
    "score": 45,
    "reason": "06:00은 피하세요 (45점)"
  },
  "hourly_analysis": [
    {"time": "09:00", "score": 72, "grade": "좋음", "weather": "3°C, 맑음"},
    {"time": "12:00", "score": 80, "grade": "최적", "weather": "6°C, 맑음"}
  ],
  "data_source": {
    "provider": "기상청 단기예보 API",
    "updated_at": "2026-01-04 12:00"
  }
}
```

**사용 예시:**
- "오늘 언제 산책하면 좋을까?"
- "빨래 몇 시에 널면 좋아?"
- "저녁에 나가는 게 나을까, 아침이 나을까?"

---

#### 30. compare_activities

두 활동 중 오늘 날씨에 더 적합한 것을 비교 분석합니다!

**Parameters:**

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| location | string | N | "서울" | 지역명 |
| activity1 | string | N | "캠핑" | 첫 번째 활동 |
| activity2 | string | N | "피크닉" | 두 번째 활동 |

**지원 활동:** 캠핑, 피크닉, 등산, 빨래, 세차, 운동, 러닝, 골프, 낚시

**Response:**

```json
{
  "location": "서울",
  "comparison": {
    "캠핑": {
      "score": 75,
      "grade": "좋음",
      "message": "캠핑하기 좋은 날씨!"
    },
    "피크닉": {
      "score": 82,
      "grade": "최적",
      "message": "피크닉 완벽한 날!"
    }
  },
  "winner": "피크닉",
  "score_difference": 7,
  "recommendation": "오늘은 피크닉가 7점 더 좋아요!",
  "weather_summary": "현재 15°C, 강수확률 10%",
  "data_source": {
    "provider": "기상청 단기예보 API",
    "updated_at": "2026-01-04 12:00"
  }
}
```

**사용 예시:**
- "캠핑 vs 피크닉, 오늘 뭐가 나을까?"
- "등산이랑 러닝 중에 뭐가 좋아?"
- "세차할까 빨래할까?"

---

## Resources (2개)

### weather://locations

지원하는 지역 목록을 반환합니다.

```
지원 지역 (80개+): 강남구, 강동구, 강릉, 강북구, ...
```

### weather://guide

사용 가이드를 반환합니다.

---

## 에러 처리

### 에러 응답 형식

```json
{
  "error": "에러 메시지",
  "location": "요청한 지역명"
}
```

### 주요 에러 코드

| 에러 | 원인 | 해결 방법 |
|------|------|----------|
| API 키 없음 | 환경변수 미설정 | .env 파일에 API 키 설정 |
| HTTP 400/500 | API 서버 오류 | 잠시 후 재시도 |

---

## 데이터 출처

| 데이터 | API | 갱신 주기 |
|--------|-----|----------|
| 날씨 | 기상청 단기예보 | 1시간 |
| 미세먼지 | 에어코리아 대기오염정보 | 1시간 |
| 생활기상지수 | 기상청 생활기상지수 3.0 | 6시간 |
| 장소 검색 | Kakao Maps API | 실시간 |

---

## Rate Limits

| 계정 | 일일 호출 한도 |
|------|---------------|
| 기상청 API | 10,000건 |
| 에어코리아 API | 10,000건 |
| 생활기상지수 API | 10,000건 |
| Kakao Maps API | 300,000건 |
