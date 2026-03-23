# main.py

import sys
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QSpinBox, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QCheckBox, QMessageBox, QSplitter, QGroupBox, QFileDialog,
    QProgressDialog, QDialog, QScrollArea,
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor, QFont, QPalette

from constants import DAYS, DEFAULT_PERIOD_TIMES
from models import Course, PALETTES, DEFAULT_PALETTE, set_palette
from logic import ScheduleGenerator
from ui_widgets import TimeTableWidget


# ══════════════════════════════════════════════
#  백그라운드 계산 스레드
# ══════════════════════════════════════════════

class ScheduleWorker(QThread):
    finished = Signal(str, list)
    error = Signal(str)

    def __init__(self, courses, target_credit, empty_days, max_gap):
        super().__init__()
        self.courses = courses
        self.target_credit = target_credit
        self.empty_days = empty_days
        self.max_gap = max_gap

    def run(self):
        try:
            gen = ScheduleGenerator(
                self.courses, self.target_credit,
                self.empty_days, self.max_gap,
                max_results=50,
            )
            status, results = gen.generate()
            self.finished.emit(status, results)
        except Exception as e:
            self.error.emit(str(e))


# ══════════════════════════════════════════════
#  도움말 다이얼로그
# ══════════════════════════════════════════════

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("사용 방법")
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)
        self.setModal(True)

        # 다크/라이트 모드 감지
        base_color = self.palette().color(QPalette.Base)
        is_dark = base_color.lightness() < 128

        # 팔레트 기반 색상
        if is_dark:
            body_bg      = "rgba(255,255,255,0.06)"
            body_text    = "#d0d0d0"
            divider      = "rgba(255,255,255,0.12)"
        else:
            body_bg      = "#f8f8f8"
            body_text    = "#333333"
            divider      = "#e0e0e0"

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 12)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(24, 20, 24, 8)
        cl.setSpacing(0)

        sections = [
            {
                "step": "Step 1",
                "title": "과목 입력",
                "body": (
                    "① 구분 선택: 전공 / 교양 / 기타 / PNP\n"
                    "② 강의명 입력  (같은 이름 = 같은 과목으로 인식)\n"
                    "③ 요일 / 시작·종료 교시 / 학점 입력\n"
                    "④ [추가] 버튼 또는 Enter"
                ),
            },
            {
                "step": "Step 2",
                "title": "분반 vs 분리수업",
                "body": (
                    "📌  분반  (분리수업 미체크)\n"
                    "같은 강의명으로 여러 시간대를 입력하면\n"
                    "시간표 생성 시 그 중 하나만 자동으로 선택됩니다.\n\n"
                    "    예)  영어회화   화 3-4교시\n"
                    "         영어회화   목 3-4교시\n"
                    "    → 둘 중 하나가 편성됨\n\n"
                    "🔗  분리수업  (분리수업 체크)\n"
                    "같은 강의명의 항목들이 항상 세트로 함께 편성됩니다.\n"
                    "주 2회처럼 여러 시간대가 묶이는 수업에 사용하세요.\n\n"
                    "    예)  대학수학   월 1-2교시  ← 분리수업 체크\n"
                    "         대학수학   목 1-2교시  ← 분리수업 체크\n"
                    "    → 두 시간대가 반드시 함께 편성됨"
                ),
            },
            {
                "step": "Step 3",
                "title": "고정 / PNP",
                "body": (
                    "📌  고정 체크\n"
                    "모든 시간표에 반드시 포함됩니다.\n"
                    "이미 수강 신청한 과목이나 필수 과목에 사용하세요.\n\n"
                    "📌  PNP\n"
                    "학점 목표에 포함되지 않으며,\n"
                    "시간 충돌이 없으면 자동으로 편성됩니다."
                ),
            },
            {
                "step": "Step 4",
                "title": "생성 조건 설정",
                "body": (
                    "• 목표 학점:  완성된 시간표의 총 학점  (PNP 제외)\n"
                    "• 최대 공강:  같은 날 수업 사이 허용할 최대 빈 교시 수\n"
                    "• 공강 요일:  수업을 아예 넣지 않을 요일\n\n"
                    "설정 후 [시간표 생성] 버튼을 누르세요.\n"
                    "조건에 맞는 조합이 최대 50개 탭으로 표시됩니다."
                ),
            },
            {
                "step": "Step 5",
                "title": "결과 저장",
                "body": (
                    "• 이미지로 저장:  원하는 시간표 탭에서 버튼을 눌러 PNG / JPG로 내보내기\n"
                    "• 강의 목록 저장:  입력한 과목 목록을 JSON 파일로 저장\n"
                    "• 강의 목록 불러오기:  저장해 둔 JSON 파일을 불러와 목록 복원\n"
                    "• 교시 시간 설정:  학교별 교시 시작 시간을 직접 입력 가능"
                ),
            },
        ]

        for i, sec in enumerate(sections):
            if i > 0:
                line = QWidget()
                line.setFixedHeight(1)
                line.setStyleSheet(f"background-color: {divider};")
                cl.addWidget(line)
                cl.addSpacing(16)

            # Step 배지 + 제목
            header_w = QWidget()
            header_layout = QHBoxLayout(header_w)
            header_layout.setContentsMargins(0, 0, 0, 0)
            header_layout.setSpacing(8)

            badge = QLabel(sec["step"])
            badge.setFixedHeight(22)
            badge.setStyleSheet(
                "background-color: #4a6fa5; color: white;"
                "font-size: 11px; font-weight: bold;"
                "border-radius: 4px; padding: 0 8px;"
            )
            badge.setAlignment(Qt.AlignCenter)

            title_lbl = QLabel(sec["title"])
            f = QFont()
            f.setPointSize(11)
            f.setBold(True)
            title_lbl.setFont(f)

            header_layout.addWidget(badge)
            header_layout.addWidget(title_lbl)
            header_layout.addStretch()
            cl.addWidget(header_w)
            cl.addSpacing(8)

            # 본문
            body_lbl = QLabel(sec["body"])
            body_lbl.setWordWrap(True)
            body_lbl.setStyleSheet(
                f"font-size: 12px; color: {body_text};"
                f"background-color: {body_bg}; border-radius: 6px; padding: 12px 16px;"
            )
            body_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
            cl.addWidget(body_lbl)
            cl.addSpacing(16)

        cl.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll)

        # 닫기 버튼
        close_btn = QPushButton("닫기")
        close_btn.setFixedHeight(34)
        close_btn.setFixedWidth(100)
        close_btn.setStyleSheet(
            "QPushButton { background-color: #4a6fa5; color: white;"
            "border-radius: 4px; font-size: 13px; }"
            "QPushButton:hover { background-color: #375a8c; }"
        )
        close_btn.clicked.connect(self.accept)

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(24, 0, 24, 0)
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        outer.addLayout(btn_row)


# ══════════════════════════════════════════════
#  교시 시간 설정 다이얼로그
# ══════════════════════════════════════════════

class PeriodSettingsDialog(QDialog):
    def __init__(self, period_times: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("교시 시간 설정")
        self.setMinimumWidth(300)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "각 교시의 시작 시간을 입력하세요 (예: 09:00)\n"
            "비워두면 해당 교시는 교시 번호만 표시됩니다."
        ))

        self.table = QTableWidget(14, 2)
        self.table.setHorizontalHeaderLabels(["교시", "시작 시간"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setFixedHeight(360)

        for i in range(1, 15):
            period_item = QTableWidgetItem(f"{i}교시")
            period_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            period_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i - 1, 0, period_item)
            time_item = QTableWidgetItem(period_times.get(i, ""))
            time_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i - 1, 1, time_item)

        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        reset_btn = QPushButton("기본값으로 초기화")
        ok_btn = QPushButton("확인")
        cancel_btn = QPushButton("취소")
        reset_btn.clicked.connect(self._reset_defaults)
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(reset_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _reset_defaults(self):
        for i in range(1, 15):
            self.table.item(i - 1, 1).setText(DEFAULT_PERIOD_TIMES.get(i, ""))

    def get_period_times(self) -> dict:
        result = {}
        for i in range(1, 15):
            text = self.table.item(i - 1, 1).text().strip()
            if text:
                result[i] = text
        return result


# ══════════════════════════════════════════════
#  과목 편집 다이얼로그
# ══════════════════════════════════════════════

class EditCourseDialog(QDialog):
    def __init__(self, course: "Course", parent=None):
        super().__init__(parent)
        self.setWindowTitle("과목 편집")
        self.setMinimumWidth(340)
        self.setModal(True)
        self.course = course

        layout = QVBoxLayout(self)

        form_layout = QHBoxLayout()
        self.category_cb = QComboBox()
        self.category_cb.addItems(["전공", "교양", "기타", "PNP"])
        self.category_cb.setCurrentText(course.category)
        self.category_cb.setFixedWidth(72)

        self.name_edit = QLineEdit(course.name)
        self.name_edit.setPlaceholderText("강의명 (그룹명)")

        self.section_edit = QLineEdit(course.section_name)
        self.section_edit.setPlaceholderText("분반 (선택)")
        self.section_edit.setFixedWidth(90)

        form_layout.addWidget(self.category_cb)
        form_layout.addWidget(self.name_edit, 1)
        form_layout.addWidget(self.section_edit)
        layout.addLayout(form_layout)

        time_layout = QHBoxLayout()
        self.day_cb = QComboBox()
        self.day_cb.addItems(DAYS)
        self.day_cb.setCurrentText(course.day)

        self.start_spin = QSpinBox()
        self.start_spin.setRange(1, 14)
        self.start_spin.setValue(course.start_period)

        self.end_spin = QSpinBox()
        self.end_spin.setRange(1, 14)
        self.end_spin.setValue(course.end_period)

        self.credit_spin = QSpinBox()
        self.credit_spin.setRange(0, 10)
        self.credit_spin.setValue(course.credits)
        self.credit_spin.setSuffix("학점")

        self.linked_chk = QCheckBox("분리수업")
        self.linked_chk.setChecked(course.is_linked)

        time_layout.addWidget(self.day_cb)
        time_layout.addWidget(QLabel("시작:"))
        time_layout.addWidget(self.start_spin)
        time_layout.addWidget(QLabel("종료:"))
        time_layout.addWidget(self.end_spin)
        time_layout.addWidget(self.credit_spin)
        time_layout.addWidget(self.linked_chk)
        layout.addLayout(time_layout)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("저장")
        cancel_btn = QPushButton("취소")
        ok_btn.clicked.connect(self._save)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _save(self):
        start = self.start_spin.value()
        end = self.end_spin.value()
        if start > end:
            QMessageBox.warning(self, "오류", "시작 교시가 종료 교시보다 늦을 수 없습니다.")
            return
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "오류", "강의명을 입력해주세요.")
            return
        self.accept()

    def get_values(self) -> dict:
        return {
            "name":         self.name_edit.text().strip(),
            "section_name": self.section_edit.text().strip(),
            "category":     self.category_cb.currentText(),
            "day":          self.day_cb.currentText(),
            "start_period": self.start_spin.value(),
            "end_period":   self.end_spin.value(),
            "credits":      self.credit_spin.value(),
            "is_linked":    self.linked_chk.isChecked(),
        }


# ══════════════════════════════════════════════
#  메인 윈도우
# ══════════════════════════════════════════════

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TimeTable Generator")
        self.resize(1100, 750)
        self.courses: list[Course] = []
        self.schedules: list[list] = []   # 생성된 시간표 저장 (팔레트 변경 시 재사용)
        self.period_times: dict = dict(DEFAULT_PERIOD_TIMES)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # ── 상단 툴바 ──
        top_bar = QHBoxLayout()
        save_btn = QPushButton("강의 목록 저장")
        load_btn = QPushButton("강의 목록 불러오기")
        help_btn = QPushButton("?  사용 방법")
        help_btn.setStyleSheet(
            "QPushButton { background-color: #4a6fa5; color: white;"
            "border-radius: 4px; font-weight: bold; padding: 0 12px; }"
            "QPushButton:hover { background-color: #375a8c; }"
        )

        save_btn.clicked.connect(self.save_data)
        load_btn.clicked.connect(self.load_data)
        help_btn.clicked.connect(self.open_help)
        top_bar.addWidget(save_btn)
        top_bar.addWidget(load_btn)
        top_bar.addStretch()
        top_bar.addWidget(help_btn)
        main_layout.addLayout(top_bar)

        splitter = QSplitter(Qt.Horizontal)

        # ── 좌측 패널 ──
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # 1. 강의 입력
        input_group = QGroupBox("1. 강의 입력")
        input_layout = QVBoxLayout()

        row1 = QHBoxLayout()
        self.category_input = QComboBox()
        self.category_input.addItems(["전공", "교양", "기타", "PNP"])
        self.category_input.setFixedWidth(72)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("강의명 (그룹명)")
        self.name_input.returnPressed.connect(self.add_course)

        self.section_input = QLineEdit()
        self.section_input.setPlaceholderText("분반 (선택)")
        self.section_input.setFixedWidth(90)

        row1.addWidget(self.category_input)
        row1.addWidget(self.name_input, 1)
        row1.addWidget(self.section_input)
        input_layout.addLayout(row1)

        row2 = QHBoxLayout()
        self.day_input = QComboBox()
        self.day_input.addItems(DAYS)

        self.start_input = QSpinBox()
        self.start_input.setRange(1, 14)
        self.end_input = QSpinBox()
        self.end_input.setRange(1, 14)

        self.credit_input = QSpinBox()
        self.credit_input.setRange(0, 10)
        self.credit_input.setValue(3)
        self.credit_input.setSuffix("학점")

        self.linked_check = QCheckBox("분리수업")
        self.linked_check.setToolTip(
            "같은 강의명(그룹)에서 여러 요일/시간이 세트로 묶이는 경우 체크하세요.\n"
            "예) 대학수학 월1-2 + 목1-2 → 둘 다 '분리수업' 체크 후 각각 추가"
        )

        self.pnp_hint_label = QLabel("⚠ 학점 목표 미산정")
        self.pnp_hint_label.setStyleSheet(
            "color: #b07800; font-size: 11px; font-weight: bold;"
            "background-color: #fff8e1; border-radius: 3px; padding: 1px 6px;"
        )
        self.pnp_hint_label.setVisible(False)

        row2.addWidget(self.day_input)
        row2.addWidget(QLabel("시작:"))
        row2.addWidget(self.start_input)
        row2.addWidget(QLabel("종료:"))
        row2.addWidget(self.end_input)
        row2.addWidget(self.credit_input)
        row2.addWidget(self.pnp_hint_label)
        row2.addWidget(self.linked_check)
        input_layout.addLayout(row2)

        self.category_input.currentTextChanged.connect(self._on_category_changed)

        # ── 간소화된 안내 문구 (다크/라이트 자동 대응) ──
        hint = QLabel(
            "💡 같은 강의명 = 시간표 생성 시 하나만 선택\n"
            "🔗 분리수업 체크 = 같은 강의명끼리 세트로 묶어서 편성"
        )
        hint.setWordWrap(True)
        _base = hint.palette().color(QPalette.Base)
        _is_dark = _base.lightness() < 128
        if _is_dark:
            _hint_bg   = "rgba(255,255,255,0.06)"
            _hint_text = "#a0a0a0"
        else:
            _hint_bg   = "#f5f5f5"
            _hint_text = "#555555"
        hint.setStyleSheet(
            f"color: {_hint_text}; font-size: 11px; padding: 5px 8px;"
            f"background-color: {_hint_bg}; border-radius: 4px;"
        )
        input_layout.addWidget(hint)

        add_btn = QPushButton("추가")
        add_btn.setFixedHeight(34)
        add_btn.clicked.connect(self.add_course)
        input_layout.addWidget(add_btn)

        input_group.setLayout(input_layout)
        left_layout.addWidget(input_group)

        # 2. 강의 목록
        list_group = QGroupBox("2. 강의 목록  (더블클릭으로 편집 | 체크박스로 고정/분리 변경)")
        list_layout = QVBoxLayout()
        self.course_list_table = QTableWidget(0, 7)
        self.course_list_table.setHorizontalHeaderLabels(
            ["구분", "강의명 [분반]", "시간", "학점", "분리", "고정", "관리"]
        )
        hdr = self.course_list_table.horizontalHeader()
        hdr.setSectionResizeMode(QHeaderView.Stretch)
        hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.course_list_table.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.course_list_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.course_list_table.cellDoubleClicked.connect(self.edit_course_at_row)
        list_layout.addWidget(self.course_list_table)
        list_group.setLayout(list_layout)
        left_layout.addWidget(list_group)

        # 3. 생성 조건
        cond_group = QGroupBox("3. 생성 조건")
        cond_layout = QVBoxLayout()

        self.target_credit_spin = QSpinBox()
        self.target_credit_spin.setRange(1, 30)
        self.target_credit_spin.setValue(18)
        self.target_credit_spin.setPrefix("목표 학점: ")
        cond_layout.addWidget(self.target_credit_spin)

        h_layout = QHBoxLayout()
        self.max_gap_spin = QSpinBox()
        self.max_gap_spin.setValue(3)
        h_layout.addWidget(QLabel("최대 공강(교시):"))
        h_layout.addWidget(self.max_gap_spin)
        cond_layout.addLayout(h_layout)

        cond_layout.addWidget(QLabel("공강 요일:"))
        self.day_off_checks: dict = {}
        d_layout = QHBoxLayout()
        for day in DAYS[:5]:
            chk = QCheckBox(day)
            self.day_off_checks[day] = chk
            d_layout.addWidget(chk)
        cond_layout.addLayout(d_layout)

        gen_btn = QPushButton("시간표 생성")
        gen_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; font-weight: bold; height: 40px;"
        )
        gen_btn.clicked.connect(self.start_generation)
        cond_layout.addWidget(gen_btn)

        cond_group.setLayout(cond_layout)
        left_layout.addWidget(cond_group)

        # ── 우측 패널 (컨트롤 바 + 결과 탭) ──
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)

        # 컨트롤 바 (교시 시간 설정 + 팔레트 선택)
        ctrl_bar = QHBoxLayout()
        ctrl_bar.setSpacing(8)

        settings_btn = QPushButton("⚙  교시 시간 설정")
        settings_btn.clicked.connect(self.open_settings)

        palette_label = QLabel("테마:")
        palette_label.setStyleSheet("font-size: 12px;")
        self.palette_combo = QComboBox()
        self.palette_combo.addItems(list(PALETTES.keys()))
        self.palette_combo.setCurrentText(DEFAULT_PALETTE)
        self.palette_combo.setFixedWidth(185)
        self.palette_combo.setToolTip("과목 추가 시 사용할 색상 팔레트를 선택합니다.")
        self.palette_combo.currentTextChanged.connect(self._on_palette_changed)

        ctrl_bar.addWidget(settings_btn)
        ctrl_bar.addStretch()
        ctrl_bar.addWidget(palette_label)
        ctrl_bar.addWidget(self.palette_combo)
        right_layout.addLayout(ctrl_bar)

        self.result_tabs = QTabWidget()
        right_layout.addWidget(self.result_tabs)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([460, 640])
        main_layout.addWidget(splitter)

    # ══════════════════════════════════════════
    #  팔레트 변경
    # ══════════════════════════════════════════

    def _on_palette_changed(self, name: str):
        set_palette(name)
        self._recolor_courses()
        self.update_course_list()
        self._refresh_result_tabs()

    def _recolor_courses(self):
        """현재 팔레트로 모든 과목 색상을 재배정합니다. 같은 그룹은 같은 색을 공유합니다."""
        from models import _next_color
        group_colors: dict = {}
        for c in self.courses:
            if c.name not in group_colors:
                group_colors[c.name] = _next_color()
            c.color = group_colors[c.name]

    def _refresh_result_tabs(self):
        """현재 열린 시간표 탭을 새 색상으로 다시 그립니다."""
        if not self.schedules:
            return
        current_idx = self.result_tabs.currentIndex()
        self.result_tabs.clear()
        for i, schedule in enumerate(self.schedules):
            tab = TimeTableWidget()
            tab.set_period_times(self.period_times)
            tab.load_schedule(schedule)
            major = ScheduleGenerator._count_credits_by_group([c for c in schedule if c.category == "전공"])
            ge    = ScheduleGenerator._count_credits_by_group([c for c in schedule if c.category == "교양"])
            other = ScheduleGenerator._count_credits_by_group([c for c in schedule if c.category == "기타"])
            pnp_n = len({c.name for c in schedule if c.category == "PNP"})
            total = major + ge + other
            summary = f"총 {total}학점  |  전공: {major}  교양: {ge}  기타: {other}"
            if pnp_n:
                summary += f"  |  PNP: {pnp_n}과목"
            tab.set_summary(summary)
            self.result_tabs.addTab(tab, f"{i + 1}번")
        if 0 <= current_idx < self.result_tabs.count():
            self.result_tabs.setCurrentIndex(current_idx)

    # ══════════════════════════════════════════
    #  도움말
    # ══════════════════════════════════════════

    def open_help(self):
        HelpDialog(self).exec()

    # ══════════════════════════════════════════
    #  강의 추가
    # ══════════════════════════════════════════

    def _find_group_color(self, name: str) -> str | None:
        for c in self.courses:
            if c.name == name:
                return c.color
        return None

    def _on_category_changed(self, text: str):
        self.pnp_hint_label.setVisible(text == "PNP")

    def add_course(self):
        name = self.name_input.text().strip()
        if not name:
            return

        start = self.start_input.value()
        end = self.end_input.value()
        if start > end:
            QMessageBox.warning(self, "오류", "시작 교시가 종료 교시보다 늦을 수 없습니다.")
            return

        day = self.day_input.currentText()
        category = self.category_input.currentText()
        section_name = self.section_input.text().strip()
        is_linked = self.linked_check.isChecked()

        exact_dup = any(
            c.name == name and c.day == day
            and c.start_period == start and c.end_period == end
            for c in self.courses
        )
        if exact_dup:
            QMessageBox.warning(
                self, "중복 과목",
                f"'{name}' ({day} {start}-{end}교시)은 이미 목록에 있습니다.\n"
                "동일한 시간대의 중복 항목은 추가할 수 없습니다."
            )
            return

        same_group = [c for c in self.courses if c.name == name]
        if same_group and is_linked:
            has_non_linked_in_group = any(not c.is_linked for c in same_group)
            if has_non_linked_in_group:
                reply = QMessageBox.question(
                    self, "그룹 혼용 주의",
                    f"'{name}' 그룹에 이미 분반(분리수업 미체크) 항목이 있습니다.\n"
                    "같은 그룹 안에 분반과 분리수업을 함께 쓰면 의도치 않은 결과가 나올 수 있습니다.\n\n"
                    "그래도 추가하시겠습니까?",
                    QMessageBox.Yes | QMessageBox.No,
                )
                if reply == QMessageBox.No:
                    return

        if same_group and not is_linked:
            existing_credits = {c.credits for c in same_group if not c.is_linked}
            new_credit = self.credit_input.value()
            if existing_credits and new_credit not in existing_credits and category != "PNP":
                existing_str = ", ".join(str(v) for v in sorted(existing_credits))
                reply = QMessageBox.question(
                    self, "그룹 학점 불일치",
                    f"'{name}' 그룹의 기존 과목은 [{existing_str}학점]인데\n"
                    f"지금 추가하려는 과목은 [{new_credit}학점]입니다.\n\n"
                    "같은 그룹 내 학점이 다르면 시간표 생성이 불가합니다.\n"
                    "그래도 추가하시겠습니까?",
                    QMessageBox.Yes | QMessageBox.No,
                )
                if reply == QMessageBox.No:
                    return

        has_primary_linked = is_linked and any(
            c.is_linked and c.credits > 0 for c in same_group
        )
        effective_credits = 0 if has_primary_linked else self.credit_input.value()

        group_color = self._find_group_color(name)
        course = Course(
            name, day, start, end,
            effective_credits, category,
            color=group_color,
            section_name=section_name,
            is_linked=is_linked,
        )
        self.courses.append(course)
        self.update_course_list()
        self.name_input.clear()
        self.section_input.clear()
        self.linked_check.setChecked(False)
        self.name_input.setFocus()

    # ══════════════════════════════════════════
    #  강의 목록 갱신 / 삭제
    # ══════════════════════════════════════════

    def update_course_list(self):
        self.course_list_table.setRowCount(0)
        for idx, course in enumerate(self.courses):
            self.course_list_table.insertRow(idx)

            self.course_list_table.setItem(idx, 0, QTableWidgetItem(course.category))

            nm = QTableWidgetItem(course.display_name())
            nm.setForeground(QColor(course.color))
            self.course_list_table.setItem(idx, 1, nm)

            self.course_list_table.setItem(
                idx, 2,
                QTableWidgetItem(f"{course.day} {course.start_period}-{course.end_period}교시"),
            )

            credit_text = f"{course.credits} (미산정)" if course.category == "PNP" else str(course.credits)
            credit_item = QTableWidgetItem(credit_text)
            credit_item.setTextAlignment(Qt.AlignCenter)
            if course.category == "PNP":
                credit_item.setForeground(QColor("#b07800"))
            self.course_list_table.setItem(idx, 3, credit_item)

            linked_w = self._make_centered_checkbox(
                course.is_linked,
                lambda s, c=course: setattr(c, "is_linked", s == 2),
            )
            self.course_list_table.setCellWidget(idx, 4, linked_w)

            fixed_w = self._make_centered_checkbox(
                course.is_fixed,
                lambda s, c=course: setattr(c, "is_fixed", s == 2),
            )
            self.course_list_table.setCellWidget(idx, 5, fixed_w)

            btn = QPushButton("삭제")
            btn.setFixedHeight(26)
            btn.clicked.connect(lambda _, c=course: self.delete_course(c))
            self.course_list_table.setCellWidget(idx, 6, btn)

    @staticmethod
    def _make_centered_checkbox(checked: bool, on_change) -> QWidget:
        w = QWidget()
        chk = QCheckBox()
        chk.setChecked(checked)
        chk.stateChanged.connect(on_change)
        lay = QHBoxLayout(w)
        lay.addWidget(chk)
        lay.setAlignment(Qt.AlignCenter)
        lay.setContentsMargins(0, 0, 0, 0)
        return w

    def edit_course_at_row(self, row: int, _col: int):
        if row < 0 or row >= len(self.courses):
            return
        course = self.courses[row]
        dialog = EditCourseDialog(course, self)
        if dialog.exec() != QDialog.Accepted:
            return

        vals = dialog.get_values()
        new_name = vals["name"]
        new_credit = vals["credits"]
        new_category = vals["category"]

        if (new_name != course.name or vals["day"] != course.day
                or vals["start_period"] != course.start_period
                or vals["end_period"] != course.end_period):
            exact_dup = any(
                c is not course
                and c.name == new_name
                and c.day == vals["day"]
                and c.start_period == vals["start_period"]
                and c.end_period == vals["end_period"]
                for c in self.courses
            )
            if exact_dup:
                QMessageBox.warning(
                    self, "중복 과목",
                    f"'{new_name}' ({vals['day']} {vals['start_period']}-{vals['end_period']}교시)은 "
                    "이미 목록에 있습니다."
                )
                return

        if new_name != course.name or new_credit != course.credits:
            same_group = [
                c for c in self.courses
                if c is not course and c.name == new_name and new_category != "PNP"
            ]
            if same_group:
                existing_credits = {c.credits for c in same_group if c.credits > 0}
                if existing_credits and new_credit not in existing_credits:
                    existing_str = ", ".join(str(v) for v in sorted(existing_credits))
                    reply = QMessageBox.question(
                        self, "그룹 학점 불일치",
                        f"'{new_name}' 그룹의 기존 과목은 [{existing_str}학점]인데\n"
                        f"편집하려는 과목은 [{new_credit}학점]입니다.\n\n"
                        "그래도 저장하시겠습니까?",
                        QMessageBox.Yes | QMessageBox.No,
                    )
                    if reply == QMessageBox.No:
                        return

        if new_name != course.name:
            from models import _next_color
            new_color = self._find_group_color(new_name) or _next_color()
            course.color = new_color

        course.name         = vals["name"]
        course.section_name = vals["section_name"]
        course.category     = vals["category"]
        course.day          = vals["day"]
        course.start_period = vals["start_period"]
        course.end_period   = vals["end_period"]
        course.credits      = vals["credits"]
        course.is_linked    = vals["is_linked"]

        self.update_course_list()

    def delete_course(self, course: Course):
        if course in self.courses:
            self.courses.remove(course)
            self.update_course_list()

    # ══════════════════════════════════════════
    #  시간표 생성
    # ══════════════════════════════════════════

    def start_generation(self):
        from logic import ScheduleGenerator as SG
        fixed_credits = SG._count_credits_by_group(
            [c for c in self.courses if c.is_fixed and c.category != "PNP"]
        )
        target = self.target_credit_spin.value()
        if fixed_credits > target:
            QMessageBox.warning(
                self, "학점 초과",
                f"고정된 과목의 학점 합({fixed_credits}학점)이\n"
                f"목표 학점({target}학점)을 초과합니다.\n\n"
                "목표 학점을 올리거나 고정 과목을 줄여주세요.",
            )
            return

        empty_days = [d for d, c in self.day_off_checks.items() if c.isChecked()]

        self.progress_dialog = QProgressDialog(
            "가능한 시간표를 계산 중입니다...", "취소", 0, 0, self
        )
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.show()

        self.worker = ScheduleWorker(
            self.courses, target, empty_days, self.max_gap_spin.value()
        )
        self.worker.finished.connect(self.on_generation_finished)
        self.worker.error.connect(self.on_generation_error)
        self.progress_dialog.canceled.connect(self.worker.terminate)
        self.worker.start()

    def on_generation_finished(self, status: str, results: list):
        self.progress_dialog.close()

        if status == "credit_mismatch":
            lines = []
            for group_name, credit_set in results:
                credits_str = ", ".join(str(v) for v in sorted(credit_set))
                lines.append(f"  • '{group_name}': {credits_str}학점")
            QMessageBox.critical(
                self, "그룹 내 학점 불일치",
                "같은 그룹(강의명) 내에서 학점이 서로 다른 과목이 있습니다.\n"
                "시간표를 생성하려면 먼저 수정해주세요.\n\n"
                + "\n".join(lines),
            )
            return
        if status == "fixed_conflict":
            QMessageBox.warning(
                self, "고정 과목 충돌",
                "고정된 과목들 사이에 시간 충돌이 있습니다.\n과목 목록을 확인해 주세요.",
            )
            return
        if status == "fixed_empty_day":
            QMessageBox.warning(
                self, "공강 요일 충돌",
                "고정된 과목 중 공강으로 설정한 요일에 수업이 있는 과목이 있습니다.",
            )
            return
        if status == "negative_credits":
            QMessageBox.warning(
                self, "학점 초과",
                "고정된 과목의 학점 합이 목표 학점을 초과합니다.",
            )
            return

        self.result_tabs.clear()
        self.schedules = results   # 팔레트 변경 시 재사용을 위해 저장
        if not results:
            QMessageBox.information(
                self, "결과 없음",
                "조건에 맞는 시간표 조합이 없습니다.\n"
                "목표 학점, 공강 요일, 최대 공강 조건을 완화해 보세요.",
            )
            return

        if len(results) >= 50:
            QMessageBox.warning(
                self, "결과 제한",
                "가능한 조합이 50개 이상입니다. 상위 50개만 표시합니다.\n"
                "조건을 더 구체적으로 설정하세요.",
            )

        for i, schedule in enumerate(results):
            tab = TimeTableWidget()
            tab.set_period_times(self.period_times)
            tab.load_schedule(schedule)

            major = ScheduleGenerator._count_credits_by_group([c for c in schedule if c.category == "전공"])
            ge    = ScheduleGenerator._count_credits_by_group([c for c in schedule if c.category == "교양"])
            other = ScheduleGenerator._count_credits_by_group([c for c in schedule if c.category == "기타"])
            pnp_n = len({c.name for c in schedule if c.category == "PNP"})
            total = major + ge + other

            summary = f"총 {total}학점  |  전공: {major}  교양: {ge}  기타: {other}"
            if pnp_n:
                summary += f"  |  PNP: {pnp_n}과목"
            tab.set_summary(summary)
            self.result_tabs.addTab(tab, f"{i + 1}번")

    def on_generation_error(self, err_msg: str):
        self.progress_dialog.close()
        QMessageBox.critical(self, "오류", f"계산 중 오류가 발생했습니다:\n{err_msg}")

    # ══════════════════════════════════════════
    #  교시 시간 설정
    # ══════════════════════════════════════════

    def open_settings(self):
        dialog = PeriodSettingsDialog(self.period_times, self)
        if dialog.exec() == QDialog.Accepted:
            self.period_times = dialog.get_period_times()
            for i in range(self.result_tabs.count()):
                w = self.result_tabs.widget(i)
                if isinstance(w, TimeTableWidget):
                    w.set_period_times(self.period_times)

    # ══════════════════════════════════════════
    #  저장 / 불러오기
    # ══════════════════════════════════════════

    def save_data(self):
        path, _ = QFileDialog.getSaveFileName(self, "저장", "", "JSON (*.json)")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(
                        [c.to_dict() for c in self.courses],
                        f, indent=4, ensure_ascii=False,
                    )
                QMessageBox.information(self, "성공", "저장되었습니다.")
            except Exception as e:
                QMessageBox.critical(self, "실패", str(e))

    def load_data(self):
        path, _ = QFileDialog.getOpenFileName(self, "열기", "", "JSON (*.json)")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.courses = [Course.from_dict(d) for d in json.load(f)]
                self._normalize_linked_credits()
                self._normalize_group_colors()
                self.update_course_list()
                QMessageBox.information(self, "성공", "불러왔습니다.")
            except Exception as e:
                QMessageBox.critical(self, "실패", str(e))

    def _normalize_linked_credits(self):
        seen_linked: set = set()
        for c in self.courses:
            if not c.is_linked:
                continue
            if c.name in seen_linked:
                c.credits = 0
            else:
                seen_linked.add(c.name)

    def _normalize_group_colors(self):
        """같은 그룹(name)의 과목 색상을 첫 번째 항목 기준으로 통일합니다."""
        group_colors: dict = {}
        for c in self.courses:
            if c.name not in group_colors:
                group_colors[c.name] = c.color
            else:
                c.color = group_colors[c.name]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())