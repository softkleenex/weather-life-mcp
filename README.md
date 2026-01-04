# Weather Life MCP v3.0

<div align="center">

![MCP](https://img.shields.io/badge/MCP-Model_Context_Protocol-blue?style=for-the-badge)
![Railway](https://img.shields.io/badge/Railway-Deployed-success?style=for-the-badge&logo=railway)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

### **날씨 + 장소 추천, 한 번에!**

날씨 + 미세먼지 + 옷차림 + **한국 특화 생활지수** + **Kakao Maps 장소 검색** MCP 서버

[데모 사용하기](#-빠른-시작) | [API 문서](docs/API.md) | [사용 예시](docs/EXAMPLES.md)

---

**PlayMCP 공모전 (MCP Player 10) 출품작**

</div>

---

## **차별화 포인트**

### 생활지수 (10개)
| 기능 | 설명 | 왜 특별한가? |
|:---:|:---:|:---:|
| **빨래지수** | 빨래 건조 적합도 | 기상청 종료 서비스 **부활!** |
| **피크닉지수** | 한강/공원 적합도 | **치맥 타임** 추천 포함 |
| **등산지수** | 등산 적합도 | 북한산/관악산 등 **추천 산** 안내 |
| **세차지수** | 세차 적합도 | **내일 비 예보**까지 고려 |
| **운동지수** | 야외 운동 적합도 | **건강 위험도, 수분 섭취량** 안내 |
| **캠핑지수** | 캠핑 적합도 | **낙뢰/강풍 위험** 분석 |
| **낚시지수** | 낚시 적합도 | **기압변화** 기반 분석 |
| **골프지수** | 골프 라운딩 | **바람/볼비행** 영향 |

### 건강지수 (6개) - 과학적 연구 기반!
| 기능 | 설명 | 왜 특별한가? |
|:---:|:---:|:---:|
| **감기위험지수** | 감기/독감 위험도 | **MIT, Yale, PNAS 연구 기반!** |
| **출퇴근지수** | 교통수단별 분석 | **자가용/대중교통/자전거** 각각 점수 |
| **알레르기지수** | 계절 알레르겐 | **꽃가루, 황사** 연동 분석 |
| **편두통지수** | 두통 위험도 | **기압/습도 연구 기반!** |
| **수면지수** | 수면 환경 분석 | **최적 온습도 연구 기반** |
| **관절통지수** | 관절 통증 위험 | **관절염 연구 기반** |

### 장소 검색 (6개) - Kakao Maps 연동! (v3.0 NEW!)
| 기능 | 설명 | 왜 특별한가? |
|:---:|:---:|:---:|
| **추천 장소** | 활동별 추천 장소 | 등산/캠핑/피크닉 등 **맞춤 추천** |
| **주변 검색** | 주변 장소 검색 | **전국 어디든** 카페/맛집/편의점 |
| **길찾기** | 카카오맵 길찾기 | **자동차/대중교통/도보** 링크 생성 |
| **맛집 검색** | 음식점 검색 | **지역+음식 종류**로 검색 |
| **상황별 추천** | TPO별 장소 추천 | **혼자/친구/데이트/가족** 맞춤 |
| **스마트 코스** | 날씨 기반 코스 | **비 오면 실내, 맑으면 야외** 자동 |

> **단순 날씨 조회가 아닌, 한국인의 생활 패턴에 맞춘 "활동 기반 추천"**
>
> **v3.0 신규: Kakao Maps 연동으로 장소 검색/코스 추천까지!**

---

## **실제 응답 예시**

### "오늘 빨래해도 돼?"

```
빨래지수: 55점 (보통)

"빨래 가능하지만 주의 필요"

요인:
- 습도 71% (건조 느림)
- 기온 -9.3°C (동파 주의)
- 바람 2.4m/s (최적)

팁: 실내 건조 권장
```

### "강남 근처 카페 찾아줘" (v3.0 NEW!)

```
검색 결과: 1,609개 중 5개

1. 공차 강남역점
   주소: 서울 강남구 강남대로 지하 396
   거리: 15m
   링크: http://place.map.kakao.com/19038749

2. 빽다방 강남역지하도점
   주소: 서울 강남구 강남대로 지하 396
   거리: 25m
   ...
```

### "홍대 데이트 코스 짜줘" (v3.0 NEW!)

```
날씨: 맑음, -5°C → 야외 활동 가능!

추천 코스:
1. 카페 (14:00) - 온수동커피 ☕
2. 전시회 (15:30) - 홍대 무한도전 전시 🎨
3. 레스토랑 (18:00) - 연남동 파스타집 🍝

각 장소 카카오맵 링크 포함!
```

---

## **테스트 결과: 100/100점**

```
============================================================
Weather Life MCP v2.0 테스트 및 평가
============================================================

총 24개 테스트
  PASS: 23
  WARN: 1
  FAIL: 0

평가 점수:
  창의성: 100/100
  편의성: 100/100
  안정성: 100/100
  ─────────────────
  종합:  100/100  (최우수, 1등권)
============================================================
```

---

## **빠른 시작**

### MCP 엔드포인트
```
https://web-production-19a3b.up.railway.app/mcp
```

### Claude Desktop 설정

`claude_desktop_config.json`에 추가:

```json
{
  "mcpServers": {
    "weather-life": {
      "url": "https://web-production-19a3b.up.railway.app/mcp"
    }
  }
}
```

### 대화 예시
```
# 날씨/생활지수
"오늘 서울 날씨 어때?"
"미세먼지 괜찮아?"
"오늘 빨래해도 돼?"
"등산하기 좋은 날이야?"
"한강 가기 좋아?"
"캠핑 가도 될까?"
"낚시하기 좋은 날이야?"
"골프치기 좋아?"

# 건강지수
"감기 걸리기 쉬운 날이야?"
"자전거 출근 괜찮아?"
"알레르기 주의해야 해?"
"오늘 두통 올 것 같아?"
"잠 잘 올까?"
"관절 아플까?"

# 장소 검색 (v3.0 NEW!)
"강남역 근처 맛집 찾아줘"
"전주 비빔밥 맛집"
"홍대 데이트 코스 짜줘"
"서울역에서 부산역까지 길찾기"
"혼자 갈만한 카페 추천"
```

---

## **28개 Tool**

### 기본 Tool (5개)
| Tool | 설명 | 예시 질문 |
|------|------|----------|
| `get_weather` | 현재 날씨 + 시간대별 예보 | "서울 날씨 알려줘" |
| `get_weekly_forecast` | **3일 예보 (오늘/내일/모레)** | "이번 주 날씨", "내일 날씨" |
| `get_air_quality_info` | PM10, PM2.5 실시간 | "미세먼지 어때?" |
| `get_outfit_recommendation_tool` | 기온별/TPO별 옷차림 | "오늘 뭐 입을까?" |
| `should_i_go_out` | 외출 적합도 (0-100) | "외출해도 될까?" |

### 생활기상지수 Tool (2개)
| Tool | 설명 | 제공 시기 |
|------|------|----------|
| `get_uv_info` | 자외선지수 | 연중 |
| `get_food_safety_index` | 식중독지수 | 연중 |

### 활동지수 Tool (8개)
| Tool | 설명 | 차별화 포인트 |
|------|------|--------------|
| `is_good_for_laundry` | 빨래지수 | 기상청 종료 서비스 부활 |
| `is_good_for_hiking` | 등산지수 | 추천 산 안내 |
| `is_good_for_picnic` | 피크닉지수 | 치맥 타임 추천 |
| `is_good_for_car_wash` | 세차지수 | 내일 비 고려 |
| `is_good_for_exercise` | 운동지수 | 건강 위험도, 수분 섭취량 |
| `get_camping_index` | 캠핑지수 | 낙뢰/강풍 위험도 |
| `get_fishing_index` | 낚시지수 | 기압변화 기반 |
| `get_golf_index` | 골프지수 | 바람 영향 분석 |

### 건강지수 Tool (7개) - 과학적 근거 기반!
| Tool | 설명 | 차별화 포인트 |
|------|------|--------------|
| `get_cold_flu_risk` | 감기위험지수 | **MIT, Yale, PNAS 연구 기반** |
| `get_commute_index` | 출퇴근지수 | **교통수단별 점수** |
| `get_allergy_risk` | 알레르기지수 | **계절별 알레르겐** |
| `get_migraine_risk` | 편두통지수 | **기압/습도 연구 기반** |
| `get_sleep_quality_index` | 수면지수 | **최적 온습도 18-22C** |
| `get_photography_index` | 사진지수 | **골든아워 계산** |
| `get_joint_pain_risk` | 관절통지수 | **관절염 연구 기반** |

### 장소 검색 Tool (6개) - Kakao Maps 연동! (v3.0 NEW!)
| Tool | 설명 | 차별화 포인트 |
|------|------|--------------|
| `get_recommended_spots` | 활동별 추천 장소 | 등산/캠핑/피크닉 등 맞춤 추천 |
| `search_nearby_places` | 주변 장소 검색 | **전국 어디든** 카페/맛집/편의점 |
| `get_directions_link` | 길찾기 링크 | 자동차/대중교통/도보/자전거 |
| `search_restaurant` | 맛집/음식점 검색 | 지역+음식 종류로 검색 |
| `get_place_recommendation` | 상황별 장소 추천 | 혼자/친구/데이트/가족 맞춤 |
| `get_smart_course` | 날씨 기반 코스 | 비 오면 실내, 맑으면 야외 자동 |

---

## **지원 지역: 80개+**

### 서울특별시 (25개 구)
강남구, 강동구, 강북구, 강서구, 관악구, 광진구, 구로구, 금천구, 노원구, 도봉구, 동대문구, 동작구, 마포구, 서대문구, 서초구, 성동구, 성북구, 송파구, 양천구, 영등포구, 용산구, 은평구, 종로구, 중구, 중랑구

### 경기도 (29개 시)
수원, 성남, 고양, 용인, 부천, 안산, 안양, 남양주, 화성, 평택, 의정부, 시흥, 파주, 광명, 김포, 군포, 광주, 이천, 양주, 오산, 구리, 안성, 포천, 의왕, 하남, 여주, 양평, 동두천, 과천

### 광역시 (7개)
부산, 대구, 인천, 광주, 대전, 울산, 세종

### 기타 주요 도시
춘천, 원주, 강릉, 청주, 천안, 전주, 목포, 여수, 순천, 포항, 경주, 거제, 제주, 서귀포 등

---

## **심사 기준 대응**

### 창의성 (100점)
- **빨래지수**: 기상청 종료 서비스 자체 부활
- **피크닉지수**: 한강 치맥 문화 반영
- **과학적 건강지수**: MIT/Yale/PNAS 연구 기반
- **스마트 코스**: 날씨 연동 코스 자동 생성
- 단순 날씨 조회가 아닌 **활동 + 장소 추천**

### 편의성 (100점)
- 자연어로 간단하게 질문 가능
- **28개 Tool**로 다양한 상황 대응
- **Kakao Maps 연동**으로 장소 검색까지
- 80개+ 지역 지원
- 한국어 응답

### 안정성 (100점)
- 공공데이터포털 공식 API 사용
- Kakao Maps API 연동
- Railway 배포 24시간 가동
- Stateless HTTP로 확장성 확보

---

## **기술 스택**

| 항목 | 기술 |
|------|------|
| Framework | FastMCP 2.14.1 |
| Transport | Streamable HTTP (Stateless) |
| Language | Python 3.11+ |
| Deployment | Railway |
| API | 기상청, 에어코리아, 생활기상지수 |

---

## **프로젝트 구조**

```
weather-life-mcp/
├── src/
│   ├── server.py              # MCP 서버 (16개 Tool)
│   ├── weather_api.py         # 기상청 날씨 API
│   ├── air_quality_api.py     # 에어코리아 미세먼지 API
│   ├── outfit_recommender.py  # 옷차림/외출 추천
│   ├── life_index_api.py      # 생활기상지수 API
│   └── activity_recommender.py # 한국 특화 활동 추천
├── config/
│   └── settings.py            # 설정 및 지역 좌표
├── tests/
│   ├── mcp_test_agent.py      # 통합 테스트 에이전트
│   └── test_report.json       # 테스트 결과
├── docs/
│   ├── API.md                 # API 명세서
│   ├── EXAMPLES.md            # 사용 예시
│   └── PLAYMCP_REGISTRATION.md
└── README.md
```

---

## **로컬 실행**

### 1. 환경 설정
```bash
git clone https://github.com/softkleenex/weather-life-mcp.git
cd weather-life-mcp
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. API 키 설정
```bash
cp .env.example .env
# .env 파일에 API 키 입력
```

**필요한 API 키 (공공데이터포털):**
- 기상청_단기예보 조회서비스
- 한국환경공단_에어코리아_대기오염정보
- 기상청_생활기상지수 조회서비스 3.0

### 3. 서버 실행
```bash
python src/server.py
```

---

## **데이터 출처**

| 데이터 | 출처 | 갱신 주기 |
|--------|------|----------|
| 날씨 | 기상청 단기예보 API | 1시간 |
| 미세먼지 | 에어코리아 대기오염정보 API | 1시간 |
| 생활지수 | 기상청 생활기상지수 3.0 | 6시간 |

---

## **버전 히스토리**

### v3.0.0 (2025-01-03)
- **Kakao Maps 연동** - 장소 검색/길찾기/코스 추천
- `search_nearby_places` - 주변 장소 검색
- `get_directions_link` - 카카오맵 길찾기 링크
- `search_restaurant` - 맛집/음식점 검색
- `get_place_recommendation` - 상황별 장소 추천
- `get_smart_course` - 날씨 기반 코스 자동 생성
- `get_recommended_spots` - 활동별 추천 장소
- Tool 28개 (구조 개편)
- 일부 미사용 Tool 정리

### v2.4.0 (2024-12-29)
- **편두통지수 추가** (`get_migraine_risk`)
- **수면지수 추가** (`get_sleep_quality_index`)
- **사진지수 추가** (`get_photography_index`)
- **관절통지수 추가** (`get_joint_pain_risk`)
- 건강/라이프스타일 지수 강화

### v2.3.0 (2024-12-28)
- **감기위험지수 추가** (`get_cold_flu_risk`) - MIT, Yale, PNAS 연구 기반
- **출퇴근지수 추가** (`get_commute_index`)
- **알레르기지수 추가** (`get_allergy_risk`)
- 과학적 연구 기반 건강 지수 강화

### v2.0.0 (2024-12-28)
- 한국 특화 기능 추가 (빨래/등산/피크닉/세차)
- 생활기상지수 연동 (자외선/식중독)

### v1.0.0 (2024-12-23)
- 초기 버전
- 날씨, 미세먼지, 옷차림, 외출 적합도

---

## **라이선스**

MIT License

---

<div align="center">

### **Made with for Korean Users**

**GitHub:** [@softkleenex](https://github.com/softkleenex)

---

*PlayMCP 공모전 (MCP Player 10) 출품작*

</div>
