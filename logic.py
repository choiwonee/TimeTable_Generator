# logic.py

from collections import OrderedDict
from constants import DAYS


class ScheduleGenerator:
    def __init__(self, all_courses, target_credits, empty_days, max_gap, max_results=50):
        self.all_courses = all_courses
        self.target_credits = target_credits
        self.empty_days = set(empty_days)
        self.max_gap = max_gap
        self.max_results = max_results

    def generate(self):
        """
        시간표 조합을 생성합니다.

        반환: (status: str, results: list)
          "ok"               — 정상. results에 Course 리스트의 리스트.
          "fixed_conflict"   — 고정 과목 간 시간 충돌.
          "fixed_empty_day"  — 고정 과목이 공강 요일에 존재.
          "negative_credits" — 고정 과목 학점 합 > 목표 학점.

        ── 그룹(name) 기반 선택 규칙 ──
          • is_linked=True  슬롯들 → 하나의 '세트 옵션' (전부 함께 선택)
          • is_linked=False 슬롯들 → 각각 독립 '분반 옵션' (하나만 선택)
          학점은 그룹당 1회만 카운트.

        ── PNP ──
          학점 목표에서 제외. 미고정 PNP는 조합 확정 후 충돌 없으면 자동 포함.

        ── 성능 ──
          학점 내림차순 정렬 + 접미 누적합 기반 DFS 가지치기.
        """
        fixed = [c for c in self.all_courses if c.is_fixed]
        optional = [c for c in self.all_courses if not c.is_fixed]

        # 그룹 내 학점 불일치 검사 (전체 과목 대상)
        mismatches = self.find_credit_mismatches(self.all_courses)
        if mismatches:
            return "credit_mismatch", mismatches  # mismatches = [(그룹명, {학점값...}), ...]

        if self.has_conflict(fixed):
            return "fixed_conflict", []
        if not self.check_empty_days(fixed):
            return "fixed_empty_day", []

        fixed_credits = self._count_credits_by_group(
            [c for c in fixed if c.category != "PNP"]
        )
        needed = self.target_credits - fixed_credits
        if needed < 0:
            return "negative_credits", []

        opt_pnp = [c for c in optional if c.category == "PNP"]
        opt_normal = [c for c in optional if c.category != "PNP"]

        # 그룹 구성 (입력 순서 유지)
        groups: OrderedDict = OrderedDict()
        for c in opt_normal:
            groups.setdefault(c.name, []).append(c)

        # 각 그룹 → 옵션 목록 변환
        group_options: list = []
        for group_name, courses in groups.items():
            # 분리수업 정규화 후 0이 저장된 슬롯이 있을 수 있으므로 max 사용
            credits = max(c.credits for c in courses)
            linked = tuple(c for c in courses if c.is_linked)
            non_linked = [c for c in courses if not c.is_linked]
            options = []
            if linked:
                options.append(linked)
            for c in non_linked:
                options.append((c,))
            group_options.append((credits, options))

        group_options.sort(key=lambda x: -x[0])

        n = len(group_options)
        suffix_sum = [0] * (n + 1)
        for i in range(n - 1, -1, -1):
            suffix_sum[i] = suffix_sum[i + 1] + group_options[i][0]

        results: list = []
        fixed_occ: set = set(
            (c.day, p) for c in fixed for p in c.get_periods()
        )
        chosen_slots: list = []
        chosen_occ: set = set()

        def dfs(idx: int, rem: int) -> None:
            if len(results) >= self.max_results:
                return
            if rem == 0:
                base = fixed + [c for slot in chosen_slots for c in slot]
                self._append_with_pnp(base, fixed_occ | chosen_occ, opt_pnp, results)
                return
            if idx >= n or suffix_sum[idx] < rem:
                return

            credits, options = group_options[idx]

            # 이 그룹 건너뜀
            dfs(idx + 1, rem)
            if len(results) >= self.max_results:
                return

            # 이 그룹에서 옵션 하나 선택
            if credits <= rem:
                for option in options:
                    if len(results) >= self.max_results:
                        return
                    if any(c.day in self.empty_days for c in option):
                        continue
                    new_slots = set(
                        (c.day, p) for c in option for p in c.get_periods()
                    )
                    if new_slots & (fixed_occ | chosen_occ):
                        continue
                    chosen_slots.append(list(option))
                    chosen_occ.update(new_slots)
                    dfs(idx + 1, rem - credits)
                    chosen_slots.pop()
                    chosen_occ.difference_update(new_slots)

        dfs(0, needed)
        return "ok", results

    @staticmethod
    def find_credit_mismatches(courses: list) -> list:
        """
        같은 그룹(name) 안에서 학점 값이 2가지 이상인 경우를 반환합니다.
        반환: [(그룹명, frozenset({학점값, ...})), ...]  — 빈 리스트 = 문제 없음
        """
        from collections import defaultdict
        group_credits: dict = defaultdict(set)
        for c in courses:
            if c.category != "PNP":
                group_credits[c.name].add(c.credits)
        return [
            (name, credits)
            for name, credits in group_credits.items()
            if len(credits) > 1
        ]

    @staticmethod
    def _count_credits_by_group(courses: list) -> int:
        seen: set = set()
        total = 0
        for c in courses:
            if c.name not in seen:
                total += c.credits
                seen.add(c.name)
        return total

    def _append_with_pnp(self, base, occupied, pnp_courses, results):
        schedule = list(base)
        occ = set(occupied)
        for p in pnp_courses:
            if p.day in self.empty_days:
                continue
            slots = set((p.day, period) for period in p.get_periods())
            if not (slots & occ):
                schedule.append(p)
                occ.update(slots)
        if self.check_max_gap(schedule):
            results.append(schedule)

    def has_conflict(self, courses: list) -> bool:
        occupied: set = set()
        for c in courses:
            for p in c.get_periods():
                slot = (c.day, p)
                if slot in occupied:
                    return True
                occupied.add(slot)
        return False

    def check_empty_days(self, courses: list) -> bool:
        return all(c.day not in self.empty_days for c in courses)

    def check_max_gap(self, courses: list) -> bool:
        day_periods: dict = {day: set() for day in DAYS}
        for c in courses:
            if c.day in day_periods:
                day_periods[c.day].update(c.get_periods())
        for day in DAYS:
            periods = sorted(day_periods[day])
            for i in range(len(periods) - 1):
                if periods[i + 1] - periods[i] - 1 > self.max_gap:
                    return False
        return True