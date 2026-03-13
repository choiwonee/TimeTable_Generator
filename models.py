import random

class Course:
    def __init__(self, name, day, start_period, end_period, credits, category="기타", color=None):
        # 강의 객체 초기화 (category 추가됨)
        self.name = name
        self.day = day
        self.start_period = start_period
        self.end_period = end_period
        self.credits = credits
        self.category = category
        self.is_fixed = False
        
        if color:
            self.color = color
        else:
            # 하얀 글씨가 잘 보이도록 진한 파스텔톤(RGB 50~160) 생성
            self.color = self._generate_dark_pastel_color()

    def _generate_dark_pastel_color(self):
        r = random.randint(50, 160)
        g = random.randint(50, 160)
        b = random.randint(50, 160)
        return f"#{r:02x}{g:02x}{b:02x}"

    def get_periods(self):
        return list(range(self.start_period, self.end_period + 1))

    def to_dict(self):
        return {
            "name": self.name,
            "day": self.day,
            "start_period": self.start_period,
            "end_period": self.end_period,
            "credits": self.credits,
            "category": self.category,
            "is_fixed": self.is_fixed,
            "color": self.color
        }

    @classmethod
    def from_dict(cls, data):
        # 구버전 json 파일 호환성을 위해 category가 없으면 '기타'로 설정
        category = data.get("category", "기타")
        course = cls(
            data["name"], data["day"], 
            data["start_period"], data["end_period"], 
            data["credits"], category, data["color"]
        )
        course.is_fixed = data["is_fixed"]
        return course