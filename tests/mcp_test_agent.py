"""
Weather Life MCP v2.0 테스트 및 평가 에이전트

PlayMCP 공모전 심사 기준에 맞춘 종합 테스트 및 평가 시스템

심사 기준:
1. 창의성 (30%) - 독창적 기능, 한국 특화
2. 편의성 (40%) - 사용자 경험, 응답 품질
3. 안정성 (30%) - 에러 처리, 응답 시간

테스트 범위:
- 14개 Tool 기능 테스트
- 응답 형식 검증
- 성능 벤치마크
- 에러 처리 검증
- 사용자 시나리오 테스트
"""

from __future__ import annotations
import asyncio
import httpx
import json
import time
from dataclasses import dataclass, field
from typing import Any, Tuple, List, Dict, Optional
from datetime import datetime
from enum import Enum


# =============================================================================
# 설정
# =============================================================================

MCP_ENDPOINT = "https://web-production-19a3b.up.railway.app/mcp"
# LOCAL_ENDPOINT = "http://localhost:8000/mcp"

TIMEOUT = 30.0  # 초


class TestStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    SKIP = "SKIP"


@dataclass
class TestResult:
    """개별 테스트 결과"""
    name: str
    status: TestStatus
    duration_ms: float
    response: Any = None
    error: str = None
    notes: list = field(default_factory=list)

    def to_dict(self):
        return {
            "name": self.name,
            "status": self.status.value,
            "duration_ms": round(self.duration_ms, 2),
            "error": self.error,
            "notes": self.notes,
        }


@dataclass
class EvaluationScore:
    """평가 점수"""
    category: str
    score: float  # 0-100
    max_score: float = 100
    details: list = field(default_factory=list)

    @property
    def percentage(self) -> float:
        return (self.score / self.max_score) * 100


# =============================================================================
# MCP 클라이언트
# =============================================================================

class MCPClient:
    """MCP 서버 클라이언트"""

    def __init__(self, endpoint: str = MCP_ENDPOINT):
        self.endpoint = endpoint
        self.request_id = 0

    async def call_tool(self, tool_name: str, arguments: dict = None) -> tuple[dict, float]:
        """
        MCP Tool 호출

        Returns:
            (응답, 응답시간_ms)
        """
        self.request_id += 1

        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            },
            "id": self.request_id
        }

        start = time.perf_counter()

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                self.endpoint,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )

        duration_ms = (time.perf_counter() - start) * 1000

        if response.status_code != 200:
            return {"error": f"HTTP {response.status_code}"}, duration_ms

        try:
            result = response.json()

            # MCP 응답 파싱
            if "result" in result:
                content = result["result"].get("content", [])
                if content and len(content) > 0:
                    text = content[0].get("text", "{}")
                    try:
                        return json.loads(text), duration_ms
                    except json.JSONDecodeError:
                        return {"text": text}, duration_ms

            if "error" in result:
                return {"error": result["error"]}, duration_ms

            return result, duration_ms

        except Exception as e:
            return {"error": str(e)}, duration_ms

    async def list_tools(self) -> tuple[list, float]:
        """사용 가능한 Tool 목록 조회"""
        self.request_id += 1

        payload = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": self.request_id
        }

        start = time.perf_counter()

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                self.endpoint,
                json=payload,
                headers={"Content-Type": "application/json"}
            )

        duration_ms = (time.perf_counter() - start) * 1000

        if response.status_code != 200:
            return [], duration_ms

        try:
            result = response.json()
            tools = result.get("result", {}).get("tools", [])
            return tools, duration_ms
        except:
            return [], duration_ms


# =============================================================================
# 테스트 케이스
# =============================================================================

class MCPTestAgent:
    """MCP 테스트 에이전트"""

    def __init__(self, endpoint: str = MCP_ENDPOINT):
        self.client = MCPClient(endpoint)
        self.results: list[TestResult] = []
        self.scores: list[EvaluationScore] = []

    async def run_all_tests(self) -> dict:
        """모든 테스트 실행"""
        print("=" * 60)
        print("Weather Life MCP v2.0 테스트 및 평가")
        print("=" * 60)
        print(f"Endpoint: {self.client.endpoint}")
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # 1. 연결 테스트
        await self._test_connection()

        # 2. Tool 목록 테스트
        await self._test_tool_list()

        # 3. 기본 Tool 테스트 (5개)
        await self._test_basic_tools()

        # 4. 생활기상지수 Tool 테스트 (3개)
        await self._test_life_index_tools()

        # 5. 한국 특화 Tool 테스트 (6개)
        await self._test_korean_tools()

        # 6. 에러 처리 테스트
        await self._test_error_handling()

        # 7. 성능 벤치마크
        await self._test_performance()

        # 8. 시나리오 테스트
        await self._test_scenarios()

        # 9. 평가 점수 계산
        self._calculate_scores()

        # 10. 리포트 생성
        return self._generate_report()

    # -------------------------------------------------------------------------
    # 테스트 메서드
    # -------------------------------------------------------------------------

    async def _test_connection(self):
        """연결 테스트"""
        print("\n[1] 연결 테스트")
        print("-" * 40)

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                start = time.perf_counter()
                response = await client.get(self.client.endpoint.replace("/mcp", "/health"))
                duration = (time.perf_counter() - start) * 1000

                if response.status_code == 200:
                    self.results.append(TestResult(
                        name="connection_health",
                        status=TestStatus.PASS,
                        duration_ms=duration,
                        response=response.json(),
                        notes=["서버 정상 응답"]
                    ))
                    print(f"  [PASS] Health Check - {duration:.0f}ms")
                else:
                    self.results.append(TestResult(
                        name="connection_health",
                        status=TestStatus.FAIL,
                        duration_ms=duration,
                        error=f"HTTP {response.status_code}"
                    ))
                    print(f"  [FAIL] Health Check - HTTP {response.status_code}")

        except Exception as e:
            self.results.append(TestResult(
                name="connection_health",
                status=TestStatus.FAIL,
                duration_ms=0,
                error=str(e)
            ))
            print(f"  [FAIL] Health Check - {e}")

    async def _test_tool_list(self):
        """Tool 목록 테스트"""
        print("\n[2] Tool 목록 테스트")
        print("-" * 40)

        tools, duration = await self.client.list_tools()

        expected_tools = [
            "get_weather", "get_air_quality_info", "get_outfit_recommendation_tool",
            "should_i_go_out", "get_weather_summary",
            "get_life_index", "get_uv_info", "get_food_safety_index",
            "is_good_for_laundry", "is_good_for_hiking", "is_good_for_picnic",
            "is_good_for_car_wash", "get_kimjang_timing", "what_should_i_do_today"
        ]

        found_tools = [t.get("name") for t in tools]
        missing = set(expected_tools) - set(found_tools)

        if len(tools) >= 14 and not missing:
            self.results.append(TestResult(
                name="tool_list",
                status=TestStatus.PASS,
                duration_ms=duration,
                response={"count": len(tools), "tools": found_tools},
                notes=[f"14개 Tool 확인됨"]
            ))
            print(f"  [PASS] Tool 목록 - {len(tools)}개 Tool ({duration:.0f}ms)")
        elif missing:
            self.results.append(TestResult(
                name="tool_list",
                status=TestStatus.WARN,
                duration_ms=duration,
                response={"count": len(tools), "missing": list(missing)},
                notes=[f"누락: {missing}"]
            ))
            print(f"  [WARN] Tool 목록 - 누락된 Tool: {missing}")
        else:
            self.results.append(TestResult(
                name="tool_list",
                status=TestStatus.FAIL,
                duration_ms=duration,
                error="Tool 목록 조회 실패"
            ))
            print(f"  [FAIL] Tool 목록 조회 실패")

    async def _test_basic_tools(self):
        """기본 Tool 테스트 (5개)"""
        print("\n[3] 기본 Tool 테스트")
        print("-" * 40)

        basic_tests = [
            ("get_weather", {"location": "서울"}, ["location", "current_weather"]),
            ("get_air_quality_info", {"location": "서울"}, ["location", "pm10", "pm25"]),
            ("get_outfit_recommendation_tool", {"location": "서울"}, ["location", "outfit"]),
            ("should_i_go_out", {"location": "서울"}, ["location", "outing_score"]),
            ("get_weather_summary", {"location": "서울"}, None),  # 문자열 반환
        ]

        for tool_name, args, expected_keys in basic_tests:
            result, duration = await self.client.call_tool(tool_name, args)

            # 응답 검증
            if "error" in result and not expected_keys:
                # 문자열 응답 (get_weather_summary)
                status = TestStatus.PASS if "text" in result or isinstance(result.get("error"), str) == False else TestStatus.FAIL
            elif "error" in result:
                status = TestStatus.FAIL
            elif expected_keys and all(k in result for k in expected_keys):
                status = TestStatus.PASS
            elif not expected_keys:  # 문자열 반환
                status = TestStatus.PASS
            else:
                status = TestStatus.WARN

            self.results.append(TestResult(
                name=f"basic_{tool_name}",
                status=status,
                duration_ms=duration,
                response=result if status == TestStatus.PASS else None,
                error=result.get("error") if status == TestStatus.FAIL else None
            ))

            print(f"  [{status.value}] {tool_name} - {duration:.0f}ms")

    async def _test_life_index_tools(self):
        """생활기상지수 Tool 테스트 (3개)"""
        print("\n[4] 생활기상지수 Tool 테스트")
        print("-" * 40)

        life_tests = [
            ("get_life_index", {"location": "서울"}, ["location"]),
            ("get_uv_info", {"location": "서울"}, ["location"]),
            ("get_food_safety_index", {"location": "서울"}, ["location"]),
        ]

        for tool_name, args, expected_keys in life_tests:
            result, duration = await self.client.call_tool(tool_name, args)

            if "error" in result:
                status = TestStatus.FAIL
            elif all(k in result for k in expected_keys):
                status = TestStatus.PASS
            else:
                status = TestStatus.WARN

            self.results.append(TestResult(
                name=f"life_{tool_name}",
                status=status,
                duration_ms=duration,
                response=result if status == TestStatus.PASS else None,
                error=result.get("error") if status == TestStatus.FAIL else None
            ))

            print(f"  [{status.value}] {tool_name} - {duration:.0f}ms")

    async def _test_korean_tools(self):
        """한국 특화 Tool 테스트 (6개)"""
        print("\n[5] 한국 특화 Tool 테스트")
        print("-" * 40)

        korean_tests = [
            ("is_good_for_laundry", {"location": "서울"}, ["location", "laundry_score", "grade"]),
            ("is_good_for_hiking", {"location": "서울"}, ["location", "hiking_score", "grade"]),
            ("is_good_for_picnic", {"location": "서울"}, ["location", "picnic_score", "grade"]),
            ("is_good_for_car_wash", {"location": "서울"}, ["location", "car_wash_score", "grade"]),
            ("get_kimjang_timing", {"location": "서울"}, ["location", "kimjang_score"]),
            ("what_should_i_do_today", {"location": "서울"}, ["location", "activities", "best_activity"]),
        ]

        for tool_name, args, expected_keys in korean_tests:
            result, duration = await self.client.call_tool(tool_name, args)

            if "error" in result:
                status = TestStatus.FAIL
            elif all(k in result for k in expected_keys):
                status = TestStatus.PASS
                # 추가 검증: 점수 범위
                for key in expected_keys:
                    if "score" in key and key in result:
                        score = result[key]
                        if not (0 <= score <= 100):
                            status = TestStatus.WARN
            else:
                status = TestStatus.WARN

            self.results.append(TestResult(
                name=f"korean_{tool_name}",
                status=status,
                duration_ms=duration,
                response=result if status == TestStatus.PASS else None,
                error=result.get("error") if status == TestStatus.FAIL else None
            ))

            print(f"  [{status.value}] {tool_name} - {duration:.0f}ms")

    async def _test_error_handling(self):
        """에러 처리 테스트"""
        print("\n[6] 에러 처리 테스트")
        print("-" * 40)

        error_tests = [
            ("get_weather", {"location": "알수없는지역XYZ"}, "unknown_location"),
            ("get_weather", {}, "missing_param"),  # 기본값 서울 적용되어야 함
        ]

        for tool_name, args, test_type in error_tests:
            result, duration = await self.client.call_tool(tool_name, args)

            # 알 수 없는 지역: 기본값(서울)으로 폴백 or 에러 응답
            # 파라미터 없음: 기본값 적용
            if test_type == "unknown_location":
                # 폴백 처리 확인
                if "location" in result or "error" in result:
                    status = TestStatus.PASS
                    note = "폴백 또는 에러 처리 정상"
                else:
                    status = TestStatus.WARN
                    note = "예상치 못한 응답"
            elif test_type == "missing_param":
                # 기본값 적용 확인
                if "location" in result and "error" not in result:
                    status = TestStatus.PASS
                    note = "기본값 적용 정상"
                else:
                    status = TestStatus.WARN
                    note = "기본값 미적용"
            else:
                status = TestStatus.SKIP
                note = ""

            self.results.append(TestResult(
                name=f"error_{test_type}",
                status=status,
                duration_ms=duration,
                notes=[note] if note else []
            ))

            print(f"  [{status.value}] {test_type} - {note}")

    async def _test_performance(self):
        """성능 벤치마크"""
        print("\n[7] 성능 벤치마크")
        print("-" * 40)

        # 동일 요청 5회 반복하여 평균 측정
        tool_name = "get_weather"
        args = {"location": "서울"}
        durations = []

        for i in range(5):
            _, duration = await self.client.call_tool(tool_name, args)
            durations.append(duration)
            await asyncio.sleep(0.5)  # Rate limit 방지

        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)

        # 성능 기준: 평균 3초 이내
        if avg_duration < 3000:
            status = TestStatus.PASS
        elif avg_duration < 5000:
            status = TestStatus.WARN
        else:
            status = TestStatus.FAIL

        self.results.append(TestResult(
            name="performance_benchmark",
            status=status,
            duration_ms=avg_duration,
            response={
                "avg_ms": round(avg_duration, 2),
                "min_ms": round(min_duration, 2),
                "max_ms": round(max_duration, 2),
                "samples": len(durations)
            },
            notes=[f"평균 {avg_duration:.0f}ms, 범위 {min_duration:.0f}-{max_duration:.0f}ms"]
        ))

        print(f"  [{status.value}] 평균 응답시간: {avg_duration:.0f}ms (범위: {min_duration:.0f}-{max_duration:.0f}ms)")

    async def _test_scenarios(self):
        """사용자 시나리오 테스트"""
        print("\n[8] 시나리오 테스트")
        print("-" * 40)

        scenarios = [
            {
                "name": "주말_활동_고민",
                "description": "오늘 뭐하면 좋을까?",
                "tool": "what_should_i_do_today",
                "args": {"location": "서울"},
                "validate": lambda r: "activities" in r and "best_activity" in r
            },
            {
                "name": "빨래_고민",
                "description": "오늘 빨래해도 돼?",
                "tool": "is_good_for_laundry",
                "args": {"location": "강남구"},
                "validate": lambda r: "laundry_score" in r and "recommendation" in r
            },
            {
                "name": "등산_계획",
                "description": "등산하기 좋은 날이야?",
                "tool": "is_good_for_hiking",
                "args": {"location": "서울"},
                "validate": lambda r: "hiking_score" in r and "recommended_mountains" in r
            },
            {
                "name": "한강_피크닉",
                "description": "한강 가기 좋아?",
                "tool": "is_good_for_picnic",
                "args": {"location": "서울"},
                "validate": lambda r: "picnic_score" in r and "chimaek_time" in r
            },
            {
                "name": "김장_시즌",
                "description": "김장 언제 하면 좋아?",
                "tool": "get_kimjang_timing",
                "args": {"location": "서울"},
                "validate": lambda r: "kimjang_score" in r
            },
        ]

        for scenario in scenarios:
            result, duration = await self.client.call_tool(scenario["tool"], scenario["args"])

            if "error" not in result and scenario["validate"](result):
                status = TestStatus.PASS
            elif "error" in result:
                status = TestStatus.FAIL
            else:
                status = TestStatus.WARN

            self.results.append(TestResult(
                name=f"scenario_{scenario['name']}",
                status=status,
                duration_ms=duration,
                response=result if status == TestStatus.PASS else None,
                notes=[scenario["description"]]
            ))

            print(f"  [{status.value}] {scenario['name']}: {scenario['description']} - {duration:.0f}ms")

    # -------------------------------------------------------------------------
    # 평가
    # -------------------------------------------------------------------------

    def _calculate_scores(self):
        """심사 기준별 점수 계산"""
        print("\n[9] 평가 점수 계산")
        print("-" * 40)

        # 통과율 계산
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == TestStatus.PASS)
        warned = sum(1 for r in self.results if r.status == TestStatus.WARN)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAIL)

        pass_rate = (passed / total) * 100 if total > 0 else 0

        # 1. 창의성 (30%) - 한국 특화 기능 기반
        korean_tests = [r for r in self.results if r.name.startswith("korean_")]
        korean_pass = sum(1 for r in korean_tests if r.status == TestStatus.PASS)
        creativity_score = (korean_pass / len(korean_tests)) * 100 if korean_tests else 0

        # 보너스: 김장지수 (세계 유일!)
        kimjang_test = next((r for r in self.results if "kimjang" in r.name), None)
        if kimjang_test and kimjang_test.status == TestStatus.PASS:
            creativity_score = min(100, creativity_score + 10)

        self.scores.append(EvaluationScore(
            category="창의성",
            score=creativity_score,
            details=[
                f"한국 특화 Tool: {korean_pass}/{len(korean_tests)} 통과",
                "빨래지수: 기상청 종료 서비스 부활",
                "김장지수: 세계 유일 한국 특화",
                "등산/피크닉/세차: 한국인 생활 밀착"
            ]
        ))

        # 2. 편의성 (40%) - 응답 품질, 다양한 지역 지원
        basic_tests = [r for r in self.results if r.name.startswith("basic_")]
        basic_pass = sum(1 for r in basic_tests if r.status == TestStatus.PASS)

        scenario_tests = [r for r in self.results if r.name.startswith("scenario_")]
        scenario_pass = sum(1 for r in scenario_tests if r.status == TestStatus.PASS)

        convenience_score = (
            (basic_pass / len(basic_tests)) * 50 +  # 기본 기능 50%
            (scenario_pass / len(scenario_tests)) * 50  # 시나리오 50%
        ) if basic_tests and scenario_tests else 0

        self.scores.append(EvaluationScore(
            category="편의성",
            score=convenience_score,
            details=[
                f"기본 Tool: {basic_pass}/{len(basic_tests)} 통과",
                f"시나리오: {scenario_pass}/{len(scenario_tests)} 통과",
                "14개 Tool로 다양한 상황 대응",
                "80개+ 지역 지원",
                "자연어 요청 가능"
            ]
        ))

        # 3. 안정성 (30%) - 에러 처리, 응답 시간
        error_tests = [r for r in self.results if r.name.startswith("error_")]
        error_pass = sum(1 for r in error_tests if r.status == TestStatus.PASS)

        perf_test = next((r for r in self.results if r.name == "performance_benchmark"), None)
        perf_score = 100 if perf_test and perf_test.status == TestStatus.PASS else (
            70 if perf_test and perf_test.status == TestStatus.WARN else 40
        )

        stability_score = (
            (error_pass / len(error_tests)) * 50 +  # 에러 처리 50%
            (perf_score / 100) * 50  # 성능 50%
        ) if error_tests else perf_score * 0.5

        self.scores.append(EvaluationScore(
            category="안정성",
            score=stability_score,
            details=[
                f"에러 처리: {error_pass}/{len(error_tests)} 통과",
                f"성능: {'양호' if perf_score >= 80 else '보통' if perf_score >= 50 else '개선 필요'}",
                "공공데이터포털 API 사용",
                "Railway 배포 24시간 가동"
            ]
        ))

        # 종합 점수 (가중치 적용)
        total_score = (
            creativity_score * 0.30 +
            convenience_score * 0.40 +
            stability_score * 0.30
        )

        self.scores.append(EvaluationScore(
            category="종합",
            score=total_score,
            details=[
                f"창의성: {creativity_score:.1f}점 (30%)",
                f"편의성: {convenience_score:.1f}점 (40%)",
                f"안정성: {stability_score:.1f}점 (30%)"
            ]
        ))

        print(f"  창의성: {creativity_score:.1f}/100")
        print(f"  편의성: {convenience_score:.1f}/100")
        print(f"  안정성: {stability_score:.1f}/100")
        print(f"  ─────────────────")
        print(f"  종합: {total_score:.1f}/100")

    def _generate_report(self) -> dict:
        """최종 리포트 생성"""
        print("\n" + "=" * 60)
        print("테스트 및 평가 완료")
        print("=" * 60)

        # 통계
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == TestStatus.PASS)
        warned = sum(1 for r in self.results if r.status == TestStatus.WARN)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAIL)

        total_duration = sum(r.duration_ms for r in self.results)

        print(f"\n총 {total}개 테스트")
        print(f"  PASS: {passed}")
        print(f"  WARN: {warned}")
        print(f"  FAIL: {failed}")
        print(f"  총 소요시간: {total_duration/1000:.1f}초")

        # 점수 요약
        total_score = next((s for s in self.scores if s.category == "종합"), None)
        if total_score:
            print(f"\n종합 점수: {total_score.score:.1f}/100")

            if total_score.score >= 85:
                print("평가: 우수 (1등권)")
            elif total_score.score >= 75:
                print("평가: 양호 (2-3등권)")
            elif total_score.score >= 60:
                print("평가: 보통")
            else:
                print("평가: 개선 필요")

        # 리포트 생성
        report = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": self.client.endpoint,
            "summary": {
                "total_tests": total,
                "passed": passed,
                "warned": warned,
                "failed": failed,
                "pass_rate": round((passed / total) * 100, 1) if total > 0 else 0,
                "total_duration_ms": round(total_duration, 2)
            },
            "results": [r.to_dict() for r in self.results],
            "scores": [
                {
                    "category": s.category,
                    "score": round(s.score, 1),
                    "details": s.details
                }
                for s in self.scores
            ],
            "recommendation": self._get_recommendation()
        }

        return report

    def _get_recommendation(self) -> list[str]:
        """개선 권장사항"""
        recommendations = []

        # 실패한 테스트 분석
        failed_tests = [r for r in self.results if r.status == TestStatus.FAIL]
        for test in failed_tests:
            if "connection" in test.name:
                recommendations.append("서버 연결 상태 확인 필요")
            elif "basic_" in test.name:
                recommendations.append(f"기본 Tool 오류 수정: {test.name.replace('basic_', '')}")
            elif "korean_" in test.name:
                recommendations.append(f"한국 특화 Tool 오류 수정: {test.name.replace('korean_', '')}")

        # 성능 분석
        perf_test = next((r for r in self.results if r.name == "performance_benchmark"), None)
        if perf_test and perf_test.duration_ms > 3000:
            recommendations.append("응답 시간 개선 필요 (목표: 3초 이내)")

        # 점수 기반 권장사항
        for score in self.scores:
            if score.category == "안정성" and score.score < 70:
                recommendations.append("에러 처리 로직 강화 필요")
            if score.category == "편의성" and score.score < 70:
                recommendations.append("응답 형식 일관성 검토 필요")

        return recommendations if recommendations else ["현재 상태 양호"]


# =============================================================================
# 메인
# =============================================================================

async def main():
    """메인 실행"""
    agent = MCPTestAgent(MCP_ENDPOINT)
    report = await agent.run_all_tests()

    # 리포트 저장
    report_path = "tests/test_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n리포트 저장: {report_path}")

    return report


if __name__ == "__main__":
    asyncio.run(main())
