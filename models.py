import random

# ══════════════════════════════════════════════
#  큐레이션 팔레트 세트 (각 10색)
# ══════════════════════════════════════════════

PALETTES = {
    "🌈 무지개": [
        "#E85858", "#F08030", "#E8C020", "#50B840", "#20A878",
        "#2880D0", "#4848C8", "#8040B8", "#C840A0", "#C89870",
    ],
    "🍰 레드벨벳 케이크": [
        "#1A0A10", "#4A1820", "#881828", "#C03030", "#E05858",
        "#F08888", "#F5C8C0", "#C87848", "#5A3018", "#F0E4D8",
    ],
    "🍂 단풍 소풍": [
        "#1E1008", "#5C2C10", "#9A3C18", "#C85820", "#E07820",
        "#F0A028", "#F5C870", "#E8D890", "#5E7028", "#3A4E18",
    ],
    "🍋 레몬 파스타": [
        "#1C2010", "#2A4820", "#4A7830", "#8A9830", "#D4B018",
        "#F0D028", "#F8EC90", "#F5E8C0", "#C87040", "#E8D8A0",
    ],
    "🌲 숲속 오두막": [
        "#0A1008", "#1C3018", "#305C28", "#508038", "#78A858",
        "#A8C880", "#6A4828", "#3C2810", "#C8B888", "#E8DEC0",
    ],
    "🌊 아드리아해": [
        "#060C1E", "#0C2858", "#185098", "#2878C8", "#50A8D8",
        "#90CCE8", "#C8EAF0", "#EAD890", "#C06840", "#1A5848",
    ],
    "🌌 한밤의 은하수": [
        "#050310", "#0C0828", "#201860", "#384098", "#6050C0",
        "#9878D8", "#C0A8E8", "#183C68", "#30789A", "#F0E8C8",
    ],
    "🪻 프로방스 라벤더": [
        "#181028", "#302458", "#584A98", "#8878C0", "#B0A0D8",
        "#D8D0F0", "#7A6878", "#4A5838", "#887860", "#F0E4D0",
    ],
}

DEFAULT_PALETTE = "🌈 무지개"

# ══════════════════════════════════════════════
#  팔레트 색상 순환 큐
# ══════════════════════════════════════════════

_current_palette: str = DEFAULT_PALETTE
_color_queue: list = []


def set_palette(palette_name: str):
    """팔레트를 변경하고 색상 큐를 초기화합니다."""
    global _current_palette, _color_queue
    if palette_name in PALETTES:
        _current_palette = palette_name
    _color_queue = []


def _next_color() -> str:
    """현재 팔레트에서 다음 색상을 순서대로 반환합니다. 다 쓰면 셔플 후 재시작."""
    global _color_queue
    if not _color_queue:
        _color_queue = PALETTES[_current_palette][:]
        random.shuffle(_color_queue)
    return _color_queue.pop()


# ══════════════════════════════════════════════
#  Course 모델
# ══════════════════════════════════════════════

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
        section_name="",
        is_linked=False,
    ):
        self.name = name
        self.section_name = section_name
        self.is_linked = is_linked
        self.day = day
        self.start_period = start_period
        self.end_period = end_period
        self.credits = credits
        self.category = category
        self.is_fixed = False
        self.color = color if color else _next_color()

    def get_periods(self):
        return list(range(self.start_period, self.end_period + 1))

    def display_name(self) -> str:
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
            color=data.get("color"),
            section_name=data.get("section_name", ""),
            is_linked=data.get("is_linked", False),
        )
        course.is_fixed = data.get("is_fixed", False)
        return course