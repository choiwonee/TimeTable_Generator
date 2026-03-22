import random

# ══════════════════════════════════════════════
#  큐레이션 팔레트 세트 (각 15색)
# ══════════════════════════════════════════════

PALETTES = {
    "🌅 Sunset Energy": [
        "#E63946", "#D62828", "#F4845F", "#CC7700", "#6A9900",
        "#2AAE6E", "#1982C4", "#4267AC", "#6A4C93", "#B5179E",
        "#C9184A", "#E07340", "#3D9E6E", "#2651A7", "#8B1F9E",
    ],
    "🌊 Coastal Vivid": [
        "#0077B6", "#0096C7", "#006E8A", "#E63946", "#E07050",
        "#CC8800", "#2AAE80", "#069890", "#4361EE", "#6B34BE",
        "#9B2D8B", "#D42B72", "#118AB2", "#3A0CA3", "#2E9E90",
    ],
    "🌿 Nature Walk": [
        "#2D6A4F", "#3D8A62", "#4A9A6A", "#6A994E", "#3A5A40",
        "#588157", "#BC4749", "#9C6644", "#A07040", "#774936",
        "#606C38", "#386641", "#B07040", "#BC6C25", "#5A7848",
    ],
    "🍬 Sweet Pop": [
        "#E8445A", "#D43B8C", "#9B35C5", "#5040D0", "#2878D4",
        "#07A09C", "#27A070", "#5E8A00", "#B07800", "#CC5500",
        "#C22860", "#8020A8", "#2460C0", "#059490", "#5A8200",
    ],
    "✨ Retro Neon": [
        "#CC0055", "#D43000", "#A08000", "#6600CC", "#1155CC",
        "#007788", "#008855", "#005588", "#990099", "#AA0033",
        "#0044BB", "#007733", "#AA5500", "#5500AA", "#CC0033",
    ],
    "🍂 Autumn Harvest": [
        "#9C4221", "#7F3A22", "#A0623A", "#9B5525", "#8A6838",
        "#A07845", "#BC6C25", "#C07830", "#556040", "#506440",
        "#2D6A4F", "#4A6B35", "#BC4749", "#9B3A3A", "#6B4226",
    ],
    "💻 Cool Tech": [
        "#1565C0", "#1976D2", "#6366F1", "#7C3AED", "#9333EA",
        "#C026B0", "#DB2777", "#E11D48", "#059669", "#0891B2",
        "#D97706", "#DC2626", "#2563EB", "#0D9488", "#B45309",
    ],
    "❄️ Nordic Mist": [
        "#4A6FA5", "#3D6B8A", "#5E6E9A", "#7A6E9A", "#6A5E8A",
        "#4A7A6A", "#7A5E6E", "#5A6E8A", "#6A5E7A", "#3A6878",
        "#5E5A7A", "#4E6E6A", "#7A5A6A", "#5E7A5A", "#3A5A78",
    ],
}

DEFAULT_PALETTE = "🌅 Sunset Energy"

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