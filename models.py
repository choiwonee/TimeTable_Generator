import random


class Course:
    def __init__(
        self,
        name,
        day,
        start_period,
        end_period,
        credits,
        category="기타",
        color=None,
        section_name="",   # 분반/구분 레이블 (목록 표시용, 선택사항)
        is_linked=False,   # True = 분리수업 세트의 일부
    ):
        self.name = name                 # 그룹명 = 실제 과목명 (시간표에 표시됨)
        self.section_name = section_name
        self.is_linked = is_linked
        self.day = day
        self.start_period = start_period
        self.end_period = end_period
        self.credits = credits
        self.category = category
        self.is_fixed = False

        self.color = color if color else self._generate_dark_pastel_color()

    def _generate_dark_pastel_color(self):
        r = random.randint(50, 160)
        g = random.randint(50, 160)
        b = random.randint(50, 160)
        return f"#{r:02x}{g:02x}{b:02x}"

    def get_periods(self):
        return list(range(self.start_period, self.end_period + 1))

    def display_name(self) -> str:
        """강의 목록에 표시할 이름 (분반 정보 포함)"""
        if self.section_name:
            return f"{self.name}  [{self.section_name}]"
        return self.name

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "section_name": self.section_name,
            "is_linked": self.is_linked,
            "day": self.day,
            "start_period": self.start_period,
            "end_period": self.end_period,
            "credits": self.credits,
            "category": self.category,
            "is_fixed": self.is_fixed,
            "color": self.color,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Course":
        course = cls(
            name=data["name"],
            day=data["day"],
            start_period=data["start_period"],
            end_period=data["end_period"],
            credits=data["credits"],
            category=data.get("category", "기타"),
            color=data["color"],
            section_name=data.get("section_name", ""),
            is_linked=data.get("is_linked", False),
        )
        course.is_fixed = data["is_fixed"]
        return course