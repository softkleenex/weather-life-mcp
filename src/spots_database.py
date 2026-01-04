"""
서울/경기 지역 장소 데이터베이스 (v3.0)

활동별 추천 장소 정보
"""

# =============================================================================
# 데이트 코스
# =============================================================================

DATE_COURSES = {
    "romantic": [
        {
            "name": "북촌 한옥마을 → 삼청동 카페거리",
            "location": "종로구",
            "duration": "3-4시간",
            "feature": "전통 한옥과 현대적 카페가 어우러진 서울 대표 데이트 코스",
            "best_for": "맑은 날, 산책하기 좋은 날씨",
            "spots": ["북촌 한옥마을", "삼청동 카페거리", "국립현대미술관"],
            "tip": "늦은 오후 방문 시 일몰 명소로 유명"
        },
        {
            "name": "경복궁 야간개장 → 광화문",
            "location": "종로구",
            "duration": "2-3시간",
            "feature": "야간에 조명이 켜진 경복궁의 신비로운 분위기",
            "best_for": "저녁, 선선한 날씨",
            "spots": ["경복궁", "광화문광장", "서촌"],
            "tip": "야간개장 기간 확인 필수 (계절별 상이)"
        },
        {
            "name": "반포 한강공원 → 달빛무지개분수",
            "location": "서초구",
            "duration": "2-3시간",
            "feature": "한강 야경과 세계 최장 교량 분수",
            "best_for": "저녁, 여름철",
            "spots": ["반포 한강공원", "세빛둥둥섬", "반포대교"],
            "tip": "분수 운영시간 확인 (4-10월)"
        },
        {
            "name": "남산타워 → 명동",
            "location": "중구/용산구",
            "duration": "3-4시간",
            "feature": "서울 전경과 맛집 거리의 조합",
            "best_for": "맑은 날, 일몰 시간",
            "spots": ["남산타워", "남산공원", "명동"],
            "tip": "케이블카 or 남산 산책로 둘 다 추천"
        },
    ],
    "active": [
        {
            "name": "뚝섬 한강공원 자전거",
            "location": "광진구",
            "duration": "2-3시간",
            "feature": "한강 자전거길 + 수영장(여름)",
            "best_for": "맑고 바람 적은 날",
            "spots": ["뚝섬 한강공원", "자벌레", "뚝섬유원지역"],
            "tip": "자전거 대여소 이용 가능"
        },
        {
            "name": "서울숲 피크닉",
            "location": "성동구",
            "duration": "3-4시간",
            "feature": "도심 속 대형 공원, 사슴 방사장",
            "best_for": "맑은 날, 봄/가을",
            "spots": ["서울숲", "언더스탠드에비뉴", "성수동 카페거리"],
            "tip": "돗자리, 간식 준비하면 완벽"
        },
        {
            "name": "롯데월드 + 석촌호수",
            "location": "송파구",
            "duration": "4-5시간",
            "feature": "테마파크와 벚꽃 명소",
            "best_for": "흐린 날도 OK (실내)",
            "spots": ["롯데월드", "석촌호수", "롯데타워"],
            "tip": "봄 벚꽃 시즌 강추"
        },
    ],
    "cultural": [
        {
            "name": "이태원 → 해방촌",
            "location": "용산구",
            "duration": "3-4시간",
            "feature": "이국적인 분위기와 루프탑 카페",
            "best_for": "저녁, 주말",
            "spots": ["이태원", "경리단길", "해방촌"],
            "tip": "해방촌 뷰 맛집 예약 추천"
        },
        {
            "name": "DDP → 동대문",
            "location": "중구",
            "duration": "2-3시간",
            "feature": "미래적 건축물과 야경",
            "best_for": "저녁, 야경 좋은 날",
            "spots": ["DDP", "동대문역사문화공원", "청계천"],
            "tip": "야간 LED 장미정원 포토존"
        },
    ],
    "food": [
        {
            "name": "망원동 → 연남동",
            "location": "마포구",
            "duration": "3-4시간",
            "feature": "힙한 카페와 맛집 투어",
            "best_for": "아무 날씨나 OK",
            "spots": ["망원시장", "연남동 경의선숲길", "연트럴파크"],
            "tip": "망원시장 먹거리 투어 추천"
        },
        {
            "name": "익선동 → 종로",
            "location": "종로구",
            "duration": "2-3시간",
            "feature": "한옥 골목 카페와 로컬 맛집",
            "best_for": "아무 날씨나 OK",
            "spots": ["익선동 한옥거리", "낙원상가", "종로3가"],
            "tip": "예쁜 한옥 카페 많음"
        },
    ],
}

# =============================================================================
# 등산 코스
# =============================================================================

HIKING_SPOTS = [
    {
        "name": "북한산 (백운대)",
        "location": "서울 강북/경기 고양",
        "difficulty": "중상",
        "duration": "4-5시간",
        "elevation": "836m",
        "feature": "서울 최고봉, 암벽 등반 코스",
        "best_season": "봄/가을",
        "course": "북한산성입구 → 백운대",
        "nearby": ["북한산 두부마을", "우이동 먹자골목"],
        "tip": "암벽 구간 조심, 등산화 필수"
    },
    {
        "name": "관악산",
        "location": "서울 관악구/금천구",
        "difficulty": "중",
        "duration": "3-4시간",
        "elevation": "632m",
        "feature": "서울대 뒷산, 접근성 최고",
        "best_season": "연중",
        "course": "서울대입구 → 연주대",
        "nearby": ["신림동 순대타운", "서울대 카페거리"],
        "tip": "정상 연주대에서 서울 전경 조망"
    },
    {
        "name": "도봉산",
        "location": "서울 도봉구/경기 의정부",
        "difficulty": "중상",
        "duration": "4-5시간",
        "elevation": "740m",
        "feature": "기암괴석과 계곡",
        "best_season": "봄/가을",
        "course": "도봉산역 → 신선대",
        "nearby": ["도봉산 닭한마리", "우이동"],
        "tip": "암벽 구간 많음, 장갑 추천"
    },
    {
        "name": "인왕산",
        "location": "서울 종로구/서대문구",
        "difficulty": "하",
        "duration": "2시간",
        "elevation": "338m",
        "feature": "도심 속 야경 명소",
        "best_season": "연중",
        "course": "사직단 → 정상 → 부암동",
        "nearby": ["부암동 카페거리", "통인시장"],
        "tip": "야간 등산 인기, 서울 야경 최고"
    },
    {
        "name": "아차산",
        "location": "서울 광진구/경기 구리",
        "difficulty": "하",
        "duration": "1.5-2시간",
        "elevation": "287m",
        "feature": "가볍게 오르기 좋은 산",
        "best_season": "연중",
        "course": "아차산역 → 정상 → 고구려정",
        "nearby": ["광나루 한강공원", "건대 맛집거리"],
        "tip": "초보자 추천, 한강 조망"
    },
    {
        "name": "청계산",
        "location": "서울 서초구/경기 성남",
        "difficulty": "중하",
        "duration": "2-3시간",
        "elevation": "618m",
        "feature": "가족 등산 인기 코스",
        "best_season": "연중",
        "course": "원터골입구 → 매봉",
        "nearby": ["판교 카페거리", "양재 꽃시장"],
        "tip": "주말 혼잡, 평일 추천"
    },
]

# =============================================================================
# 캠핑장
# =============================================================================

CAMPING_SPOTS = [
    {
        "name": "가평 자라섬",
        "location": "경기 가평군",
        "distance": "서울에서 1시간",
        "feature": "북한강변 섬 캠핑장, 재즈페스티벌 장소",
        "facilities": ["화장실", "샤워실", "매점", "전기"],
        "type": "오토캠핑",
        "best_for": "가족, 커플",
        "tip": "봄/가을 예약 경쟁 치열"
    },
    {
        "name": "양평 두물머리",
        "location": "경기 양평군",
        "distance": "서울에서 1시간",
        "feature": "남한강+북한강 합류점, 일출 명소",
        "facilities": ["화장실", "주차장"],
        "type": "노지캠핑",
        "best_for": "사진작가, 커플",
        "tip": "새벽 물안개 환상적"
    },
    {
        "name": "포천 산정호수",
        "location": "경기 포천시",
        "distance": "서울에서 1시간 30분",
        "feature": "호수뷰 캠핑, 수상레저",
        "facilities": ["화장실", "샤워실", "매점", "전기"],
        "type": "오토캠핑/글램핑",
        "best_for": "가족",
        "tip": "여름 물놀이 + 캠핑 조합"
    },
    {
        "name": "춘천 남이섬",
        "location": "강원 춘천시",
        "distance": "서울에서 1시간 30분",
        "feature": "메타세쿼이아 길, 사계절 아름다움",
        "facilities": ["글램핑", "풀빌라"],
        "type": "글램핑",
        "best_for": "커플",
        "tip": "배 타고 입장, 겨울 눈 풍경 최고"
    },
    {
        "name": "가평 아침고요수목원 근처",
        "location": "경기 가평군",
        "distance": "서울에서 1시간",
        "feature": "수목원 + 캠핑 조합",
        "facilities": ["화장실", "샤워실", "전기"],
        "type": "오토캠핑",
        "best_for": "가족, 커플",
        "tip": "오색별빛정원전 (겨울) 연계"
    },
]

# =============================================================================
# 피크닉 장소
# =============================================================================

PICNIC_SPOTS = [
    {
        "name": "여의도 한강공원",
        "location": "영등포구",
        "feature": "넓은 잔디밭, 벚꽃 명소, 치맥 성지",
        "facilities": ["편의점", "자전거대여", "화장실", "주차장"],
        "best_for": "치맥, 야경, 봄꽃놀이",
        "chimaek_time": "17:00-21:00",
        "tip": "봄 벚꽃축제 기간 인파 주의"
    },
    {
        "name": "반포 한강공원",
        "location": "서초구",
        "feature": "달빛무지개분수, 세빛둥둥섬",
        "facilities": ["편의점", "자전거대여", "화장실"],
        "best_for": "야경, 분수쇼, 데이트",
        "chimaek_time": "18:00-22:00",
        "tip": "분수 운영시간 확인 (4-10월)"
    },
    {
        "name": "뚝섬 한강공원",
        "location": "광진구",
        "feature": "수영장(여름), 자벌레 전망대",
        "facilities": ["수영장", "자전거대여", "편의점"],
        "best_for": "물놀이, 자전거",
        "chimaek_time": "16:00-21:00",
        "tip": "여름 야외수영장 인기"
    },
    {
        "name": "서울숲",
        "location": "성동구",
        "feature": "사슴 방사장, 넓은 잔디밭",
        "facilities": ["카페", "화장실", "주차장"],
        "best_for": "피크닉, 산책, 가족나들이",
        "chimaek_time": "주류 반입 제한",
        "tip": "돗자리 필수, 성수동 카페 연계"
    },
    {
        "name": "올림픽공원",
        "location": "송파구",
        "feature": "9경 산책로, 들꽃마루",
        "facilities": ["카페", "화장실", "주차장", "자전거대여"],
        "best_for": "산책, 자전거, 피크닉",
        "chimaek_time": "주류 반입 제한",
        "tip": "들꽃마루 가을 핑크뮬리"
    },
]

# =============================================================================
# 드라이브 코스
# =============================================================================

DRIVE_COURSES = [
    {
        "name": "서해안 드라이브 (시화방조제)",
        "location": "경기 시흥/안산",
        "distance": "왕복 약 100km",
        "duration": "3-4시간",
        "feature": "서해 일몰, 바다 위 드라이브",
        "highlights": ["시화방조제", "대부도", "제부도"],
        "best_time": "일몰 시간",
        "tip": "일몰 1시간 전 출발 추천"
    },
    {
        "name": "북한강 드라이브",
        "location": "경기 남양주/가평",
        "distance": "왕복 약 120km",
        "duration": "4-5시간",
        "feature": "강변 드라이브 + 카페거리",
        "highlights": ["팔당댐", "자라섬", "남이섬"],
        "best_time": "오전/오후",
        "tip": "가평 닭갈비 필수"
    },
    {
        "name": "남한강 드라이브",
        "location": "경기 양평/여주",
        "distance": "왕복 약 130km",
        "duration": "4-5시간",
        "feature": "강변 뷰 + 두물머리 일출",
        "highlights": ["두물머리", "세미원", "여주 프리미엄아울렛"],
        "best_time": "새벽(일출) / 오후",
        "tip": "두물머리 새벽 물안개 추천"
    },
    {
        "name": "파주 헤이리 드라이브",
        "location": "경기 파주",
        "distance": "왕복 약 80km",
        "duration": "3-4시간",
        "feature": "예술마을 + 아울렛",
        "highlights": ["헤이리 예술마을", "프로방스", "파주 프리미엄아울렛"],
        "best_time": "낮",
        "tip": "주말 혼잡, 평일 추천"
    },
    {
        "name": "강화도 드라이브",
        "location": "인천 강화군",
        "distance": "왕복 약 140km",
        "duration": "5-6시간",
        "feature": "섬 일주 + 역사탐방",
        "highlights": ["강화평화전망대", "마니산", "전등사"],
        "best_time": "하루종일",
        "tip": "젓갈, 순무김치 기념품"
    },
]

# =============================================================================
# 낚시터
# =============================================================================

FISHING_SPOTS = [
    {
        "name": "팔당댐",
        "location": "경기 남양주/하남",
        "fish_types": ["붕어", "잉어", "쏘가리"],
        "type": "민물낚시",
        "feature": "서울 근교 대표 낚시터",
        "best_season": "봄/가을",
        "tip": "새벽 출조 추천"
    },
    {
        "name": "청평호",
        "location": "경기 가평",
        "fish_types": ["배스", "쏘가리", "붕어"],
        "type": "민물낚시/보트낚시",
        "feature": "배스낚시 명소",
        "best_season": "여름/가을",
        "tip": "보트 대여 가능"
    },
    {
        "name": "소양호",
        "location": "강원 춘천",
        "fish_types": ["빙어", "송어", "배스"],
        "type": "민물낚시/얼음낚시",
        "feature": "겨울 빙어낚시 유명",
        "best_season": "겨울(빙어)/여름",
        "tip": "겨울 빙어축제 연계"
    },
    {
        "name": "시화방조제",
        "location": "경기 시흥/안산",
        "fish_types": ["우럭", "노래미", "숭어"],
        "type": "바다낚시",
        "feature": "방파제 낚시, 접근성 좋음",
        "best_season": "연중",
        "tip": "일몰 드라이브 연계"
    },
    {
        "name": "인천 연안부두",
        "location": "인천 중구",
        "fish_types": ["우럭", "광어", "농어"],
        "type": "선상낚시",
        "feature": "배낚시 출항지",
        "best_season": "봄/가을",
        "tip": "선상낚시 배 예약 필수"
    },
]

# =============================================================================
# 골프장
# =============================================================================

GOLF_COURSES = [
    {
        "name": "남서울CC",
        "location": "경기 성남",
        "distance": "서울에서 30분",
        "holes": 18,
        "feature": "도심 접근성 최고",
        "level": "중급",
        "tip": "예약 경쟁 치열"
    },
    {
        "name": "안양CC",
        "location": "경기 안양",
        "distance": "서울에서 40분",
        "holes": 27,
        "feature": "아름다운 코스 디자인",
        "level": "중급",
        "tip": "주중 추천"
    },
    {
        "name": "용인CC",
        "location": "경기 용인",
        "distance": "서울에서 50분",
        "holes": 27,
        "feature": "자연 경관 우수",
        "level": "중상급",
        "tip": "가을 단풍 최고"
    },
    {
        "name": "가평베네스트",
        "location": "경기 가평",
        "distance": "서울에서 1시간",
        "holes": 27,
        "feature": "리조트형 골프장",
        "level": "중급",
        "tip": "숙박 패키지 인기"
    },
]

# =============================================================================
# 러닝 코스
# =============================================================================

RUNNING_COURSES = [
    {
        "name": "여의도 한강 러닝 코스",
        "location": "영등포구",
        "distance": "5km / 10km",
        "feature": "평탄한 한강변 코스",
        "facilities": ["화장실", "음수대", "편의점"],
        "best_time": "새벽/저녁",
        "tip": "야간 조명 잘 되어있음"
    },
    {
        "name": "반포 한강 러닝 코스",
        "location": "서초구",
        "distance": "5km / 7km",
        "feature": "야경 좋은 코스",
        "facilities": ["화장실", "음수대"],
        "best_time": "저녁",
        "tip": "분수 운영 시간 러닝 추천"
    },
    {
        "name": "올림픽공원 러닝 코스",
        "location": "송파구",
        "distance": "3km / 7km / 9km",
        "feature": "공원 내 순환 코스",
        "facilities": ["화장실", "카페", "주차장"],
        "best_time": "아침/저녁",
        "tip": "9경 둘러보며 러닝"
    },
    {
        "name": "서울숲 러닝 코스",
        "location": "성동구",
        "distance": "3km / 5km",
        "feature": "숲속 러닝",
        "facilities": ["화장실", "카페"],
        "best_time": "아침",
        "tip": "평일 한적함"
    },
    {
        "name": "경의선숲길",
        "location": "마포구",
        "distance": "6km (연남동~홍대)",
        "feature": "도심 속 선형 공원",
        "facilities": ["카페", "화장실"],
        "best_time": "아침",
        "tip": "연남동 → 홍대 코스"
    },
]

# =============================================================================
# 바베큐 장소
# =============================================================================

BBQ_SPOTS = [
    {
        "name": "여의도 한강공원 바베큐존",
        "location": "영등포구",
        "type": "지정구역",
        "feature": "한강 치맥의 성지",
        "facilities": ["화장실", "편의점", "주차장"],
        "reservation": "불필요",
        "tip": "장작불 금지, 가스/숯 OK"
    },
    {
        "name": "뚝섬 한강공원 바베큐존",
        "location": "광진구",
        "type": "지정구역",
        "feature": "수영장 옆 바베큐",
        "facilities": ["화장실", "편의점", "수영장"],
        "reservation": "불필요",
        "tip": "여름 물놀이 + 바베큐"
    },
    {
        "name": "난지 한강공원 바베큐존",
        "location": "마포구",
        "type": "지정구역",
        "feature": "캠핑장 분위기",
        "facilities": ["화장실", "편의점", "주차장"],
        "reservation": "불필요",
        "tip": "노을공원 연계"
    },
    {
        "name": "서울숲 캠핑장",
        "location": "성동구",
        "type": "예약제",
        "feature": "도심 속 캠핑",
        "facilities": ["화장실", "샤워실", "전기"],
        "reservation": "필요 (서울숲 홈페이지)",
        "tip": "주말 예약 빨리 마감"
    },
]


# =============================================================================
# 유틸리티 함수
# =============================================================================

def get_spots_by_weather(activity: str, weather_score: int) -> list:
    """날씨 점수에 따라 적합한 장소 필터링"""
    spots_map = {
        "hiking": HIKING_SPOTS,
        "camping": CAMPING_SPOTS,
        "picnic": PICNIC_SPOTS,
        "drive": DRIVE_COURSES,
        "fishing": FISHING_SPOTS,
        "golf": GOLF_COURSES,
        "running": RUNNING_COURSES,
        "bbq": BBQ_SPOTS,
    }

    spots = spots_map.get(activity, [])

    # 점수에 따라 추천 개수 조절
    if weather_score >= 80:
        return spots[:5]
    elif weather_score >= 60:
        return spots[:3]
    else:
        return spots[:2]


def get_date_course_by_style(style: str, weather_data: dict) -> list:
    """날씨와 스타일에 맞는 데이트 코스 추천"""
    courses = DATE_COURSES.get(style, DATE_COURSES["romantic"])

    # 날씨에 따른 필터링
    rain_prob = weather_data.get("rain_prob", 0)
    temperature = weather_data.get("temperature", 20)

    result = []
    for course in courses:
        # 비 올 때는 실내 위주 추천
        if rain_prob >= 50:
            if "실내" in course.get("best_for", "") or "OK" in course.get("best_for", ""):
                result.append(course)
        else:
            result.append(course)

    return result[:3] if result else courses[:3]
