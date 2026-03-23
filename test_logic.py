# test_logic.py

import pytest
from unittest.mock import MagicMock


# ── Course Mock ────────────────────────────────────────────────
class MockCourse:
    def __init__(self, name, day, start, end, credits,
                 category="전공", is_fixed=False, is_linked=False):
        self.name = name
        self.day = day
        self.start_period = start
        self.end_period = end
        self.credits = credits
        self.category = category
        self.is_fixed = is_fixed
        self.is_linked = is_linked
        self.color = "#000000"
        self.section_name = ""

    def get_periods(self):
        return list(range(self.start_period, self.end_period + 1))

    def display_name(self):
        return self.name


# ── ScheduleGenerator import 대신 로직 직접 테스트 ────────────
# constants.py의 DAYS 없이도 동작하도록 mock
import sys
from unittest.mock import patch

DAYS = ["월", "화", "수", "목", "금", "토", "일"]

# constants 모듈 mock
mock_constants = MagicMock()
mock_constants.DAYS = DAYS
sys.modules['constants'] = mock_constants

from logic import ScheduleGenerator


# ═══════════════════════════════════════════════════════════════
#  헬퍼
# ═══════════════════════════════════════════════════════════════

def make_gen(courses, target=18, empty_days=None, max_gap=3):
    return ScheduleGenerator(
        courses,
        target_credits=target,
        empty_days=empty_days or [],
        max_gap=max_gap,
    )


# ═══════════════════════════════════════════════════════════════
#  1. has_conflict
# ═══════════════════════════════════════════════════════════════

class TestHasConflict:
    def test_no_conflict(self):
        courses = [
            MockCourse("A", "월", 1, 3, 3),
            MockCourse("B", "화", 1, 3, 3),
        ]
        gen = make_gen(courses)
        assert gen.has_conflict(courses) is False

    def test_same_day_no_overlap(self):
        courses = [
            MockCourse("A", "월", 1, 3, 3),
            MockCourse("B", "월", 4, 6, 3),
        ]
        gen = make_gen(courses)
        assert gen.has_conflict(courses) is False

    def test_conflict_same_slot(self):
        courses = [
            MockCourse("A", "월", 1, 3, 3),
            MockCourse("B", "월", 3, 5, 3),  # 3교시 겹침
        ]
        gen = make_gen(courses)
        assert gen.has_conflict(courses) is True

    def test_conflict_exact_same_time(self):
        courses = [
            MockCourse("A", "화", 2, 4, 3),
            MockCourse("B", "화", 2, 4, 3),
        ]
        gen = make_gen(courses)
        assert gen.has_conflict(courses) is True

    def test_different_days_no_conflict(self):
        courses = [
            MockCourse("A", "월", 1, 5, 3),
            MockCourse("B", "화", 1, 5, 3),
        ]
        gen = make_gen(courses)
        assert gen.has_conflict(courses) is False


# ═══════════════════════════════════════════════════════════════
#  2. check_empty_days
# ═══════════════════════════════════════════════════════════════

class TestCheckEmptyDays:
    def test_no_empty_days(self):
        courses = [MockCourse("A", "월", 1, 3, 3)]
        gen = make_gen(courses, empty_days=[])
        assert gen.check_empty_days(courses) is True

    def test_course_on_empty_day(self):
        courses = [MockCourse("A", "수", 1, 3, 3)]
        gen = make_gen(courses, empty_days=["수"])
        assert gen.check_empty_days(courses) is False

    def test_course_not_on_empty_day(self):
        courses = [MockCourse("A", "월", 1, 3, 3)]
        gen = make_gen(courses, empty_days=["수", "금"])
        assert gen.check_empty_days(courses) is True

    def test_multiple_courses_one_on_empty_day(self):
        courses = [
            MockCourse("A", "월", 1, 3, 3),
            MockCourse("B", "금", 1, 3, 3),
        ]
        gen = make_gen(courses, empty_days=["금"])
        assert gen.check_empty_days(courses) is False


# ═══════════════════════════════════════════════════════════════
#  3. check_max_gap
# ═══════════════════════════════════════════════════════════════

class TestCheckMaxGap:
    def test_no_gap(self):
        courses = [
            MockCourse("A", "월", 1, 3, 3),
            MockCourse("B", "월", 4, 6, 3),
        ]
        gen = make_gen(courses, max_gap=0)
        assert gen.check_max_gap(courses) is True

    def test_gap_within_limit(self):
        # 월: 1-3, 5-7 → 4교시 공강 1개 → gap=1
        courses = [
            MockCourse("A", "월", 1, 3, 3),
            MockCourse("B", "월", 5, 7, 3),
        ]
        gen = make_gen(courses, max_gap=1)
        assert gen.check_max_gap(courses) is True

    def test_gap_exceeds_limit(self):
        # 월: 1-3, 7-9 → 4,5,6교시 공강 3개 → gap=3 > max_gap=2
        courses = [
            MockCourse("A", "월", 1, 3, 3),
            MockCourse("B", "월", 7, 9, 3),
        ]
        gen = make_gen(courses, max_gap=2)
        assert gen.check_max_gap(courses) is False

    def test_different_days_independent(self):
        # 월에 큰 공강 있어도 화에는 없음 → 각 요일 독립 검사
        courses = [
            MockCourse("A", "월", 1, 2, 3),
            MockCourse("B", "월", 8, 9, 3),  # 월 gap=5
            MockCourse("C", "화", 1, 3, 3),
        ]
        gen = make_gen(courses, max_gap=3)
        assert gen.check_max_gap(courses) is False

    def test_single_course_no_gap(self):
        courses = [MockCourse("A", "월", 1, 3, 3)]
        gen = make_gen(courses, max_gap=0)
        assert gen.check_max_gap(courses) is True


# ═══════════════════════════════════════════════════════════════
#  4. find_credit_mismatches
# ═══════════════════════════════════════════════════════════════

class TestFindCreditMismatches:
    def test_no_mismatch(self):
        courses = [
            MockCourse("자료구조", "월", 1, 3, 3),
            MockCourse("자료구조", "수", 1, 3, 3),
        ]
        result = ScheduleGenerator.find_credit_mismatches(courses)
        assert result == []

    def test_mismatch_detected(self):
        courses = [
            MockCourse("자료구조", "월", 1, 3, 3),
            MockCourse("자료구조", "수", 1, 3, 2),  # 다른 학점
        ]
        result = ScheduleGenerator.find_credit_mismatches(courses)
        assert len(result) == 1
        assert result[0][0] == "자료구조"
        assert result[0][1] == {2, 3}

    def test_pnp_excluded_from_check(self):
        courses = [
            MockCourse("대학체육", "월", 13, 14, 1, category="PNP"),
            MockCourse("대학체육", "수", 13, 14, 2, category="PNP"),
        ]
        result = ScheduleGenerator.find_credit_mismatches(courses)
        assert result == []

    def test_credits_zero_excluded(self):
        # 분리수업 정규화로 credits=0인 슬롯은 무시
        courses = [
            MockCourse("데이터마이닝", "월", 1, 2, 3, is_linked=True),
            MockCourse("데이터마이닝", "목", 1, 2, 0, is_linked=True),
        ]
        result = ScheduleGenerator.find_credit_mismatches(courses)
        assert result == []


# ═══════════════════════════════════════════════════════════════
#  5. _count_credits_by_group
# ═══════════════════════════════════════════════════════════════

class TestCountCreditsByGroup:
    def test_single_group(self):
        courses = [
            MockCourse("A", "월", 1, 3, 3),
            MockCourse("A", "수", 1, 3, 3),
        ]
        assert ScheduleGenerator._count_credits_by_group(courses) == 3

    def test_multiple_groups(self):
        courses = [
            MockCourse("A", "월", 1, 3, 3),
            MockCourse("B", "화", 1, 3, 2),
        ]
        assert ScheduleGenerator._count_credits_by_group(courses) == 5

    def test_linked_course_credits_zero_ignored(self):
        # credits=0 슬롯 있어도 그룹 최댓값(3) 사용
        courses = [
            MockCourse("데이터마이닝", "월", 1, 2, 3, is_linked=True),
            MockCourse("데이터마이닝", "목", 1, 2, 0, is_linked=True),
        ]
        assert ScheduleGenerator._count_credits_by_group(courses) == 3


# ═══════════════════════════════════════════════════════════════
#  6. generate — 통합 시나리오
# ═══════════════════════════════════════════════════════════════

class TestGenerate:
    def test_basic_single_option(self):
        """단일 분반 과목만 있을 때 정확히 1개 결과"""
        courses = [
            MockCourse("A", "월", 1, 3, 3),
            MockCourse("B", "화", 1, 3, 3),
            MockCourse("C", "수", 1, 3, 3),
            MockCourse("D", "목", 1, 3, 3),
            MockCourse("E", "금", 1, 3, 3),
            MockCourse("F", "월", 5, 7, 3),
        ]
        gen = make_gen(courses, target=18)
        status, results = gen.generate()
        assert status == "ok"
        assert len(results) == 1

    def test_fixed_conflict_detected(self):
        """고정 과목 간 충돌 감지"""
        courses = [
            MockCourse("A", "월", 1, 3, 3, is_fixed=True),
            MockCourse("B", "월", 3, 5, 3, is_fixed=True),  # 3교시 충돌
        ]
        gen = make_gen(courses, target=6)
        status, _ = gen.generate()
        assert status == "fixed_conflict"

    def test_fixed_empty_day_detected(self):
        """고정 과목이 공강 요일에 있을 때 감지"""
        courses = [
            MockCourse("A", "수", 1, 3, 3, is_fixed=True),
        ]
        gen = make_gen(courses, target=3, empty_days=["수"])
        status, _ = gen.generate()
        assert status == "fixed_empty_day"

    def test_credit_mismatch_detected(self):
        """같은 그룹 내 학점 불일치 감지"""
        courses = [
            MockCourse("자료구조", "월", 1, 3, 3),
            MockCourse("자료구조", "수", 1, 3, 2),
        ]
        gen = make_gen(courses, target=3)
        status, _ = gen.generate()
        assert status == "credit_mismatch"

    def test_section_selection(self):
        """분반 중 하나만 선택되는지 확인"""
        courses = [
            MockCourse("자료구조", "월", 1, 3, 3),  # A반
            MockCourse("자료구조", "화", 1, 3, 3),  # B반
        ]
        gen = make_gen(courses, target=3)
        status, results = gen.generate()
        assert status == "ok"
        assert len(results) == 2  # 2가지 분반 조합
        for schedule in results:
            names = [c.name for c in schedule]
            assert names.count("자료구조") == 1  # 반드시 하나만

    def test_empty_day_filter(self):
        """공강 요일 과목 제외 확인"""
        courses = [
            MockCourse("A", "월", 1, 3, 3),
            MockCourse("A", "수", 1, 3, 3),  # 공강 요일
        ]
        gen = make_gen(courses, target=3, empty_days=["수"])
        status, results = gen.generate()
        assert status == "ok"
        assert len(results) == 1
        assert results[0][0].day == "월"

    def test_linked_course_as_set(self):
        """분리수업이 세트로 편성되는지 확인"""
        courses = [
            MockCourse("데이터마이닝", "월", 1, 2, 3, is_linked=True),
            MockCourse("데이터마이닝", "목", 1, 2, 0, is_linked=True),
        ]
        gen = make_gen(courses, target=3)
        status, results = gen.generate()
        assert status == "ok"
        assert len(results) == 1
        days = {c.day for c in results[0]}
        assert "월" in days and "목" in days

    def test_linked_partial_fixed(self):
        """분리수업 한 쪽만 고정해도 두 슬롯 모두 포함되는지 확인"""
        courses = [
            MockCourse("데이터마이닝", "월", 1, 2, 3, is_fixed=True, is_linked=True),
            MockCourse("데이터마이닝", "목", 1, 2, 0, is_fixed=False, is_linked=True),
        ]
        gen = make_gen(courses, target=3)
        status, results = gen.generate()
        assert status == "ok"
        assert len(results) >= 1
        for schedule in results:
            days = {c.day for c in schedule}
            assert "월" in days and "목" in days  # 두 슬롯 모두 포함

    def test_pnp_not_counted_in_credits(self):
        """PNP 과목이 학점 목표에서 제외되는지 확인"""
        courses = [
            MockCourse("A", "월", 1, 3, 3),
            MockCourse("B", "화", 1, 3, 3),
            MockCourse("대학체육", "수", 13, 14, 1, category="PNP"),
        ]
        gen = make_gen(courses, target=6)
        status, results = gen.generate()
        assert status == "ok"
        assert len(results) >= 1

    def test_no_results_when_impossible(self):
        """조건에 맞는 조합이 없을 때 빈 결과 반환"""
        courses = [
            MockCourse("A", "월", 1, 3, 3),
        ]
        gen = make_gen(courses, target=9)  # 3학점으로 9학점 불가
        status, results = gen.generate()
        assert status == "ok"
        assert results == []

    def test_negative_credits_when_fixed_exceeds_target(self):
        """고정 과목 학점이 목표 초과 시 감지"""
        courses = [
            MockCourse("A", "월", 1, 3, 3, is_fixed=True),
            MockCourse("B", "화", 1, 3, 3, is_fixed=True),
        ]
        gen = make_gen(courses, target=3)  # 고정 6학점 > 목표 3학점
        status, _ = gen.generate()
        assert status == "negative_credits"

    def test_max_results_limit(self):
        """최대 결과 수 제한 확인"""
        # 분반 3개짜리 과목 여러 개 → 조합 많음
        courses = []
        for day in ["월", "화", "수"]:
            courses.append(MockCourse("A", day, 1, 3, 3))
        for day in ["월", "화", "수"]:
            courses.append(MockCourse("B", day, 5, 7, 3))
        for day in ["목", "금"]:
            courses.append(MockCourse("C", day, 1, 3, 3))
        for day in ["목", "금"]:
            courses.append(MockCourse("D", day, 5, 7, 3))
        for day in ["월", "수", "금"]:
            courses.append(MockCourse("E", day, 9, 11, 3))
        for day in ["화", "목"]:
            courses.append(MockCourse("F", day, 9, 11, 3))

        gen = ScheduleGenerator(courses, target_credits=18,
                                empty_days=[], max_gap=3, max_results=50)
        status, results = gen.generate()
        assert status == "ok"
        assert len(results) <= 50
