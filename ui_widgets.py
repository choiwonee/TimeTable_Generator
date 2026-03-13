# ui_widgets.py

from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView,
    QWidget, QVBoxLayout, QLabel,
    QPushButton, QFileDialog, QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from constants import DAYS


class TimeTableWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.period_times: dict = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(6)

        # 상단 요약 라벨
        self.summary_label = QLabel("학점 계산 중...")
        self.summary_label.setAlignment(Qt.AlignCenter)
        self.summary_label.setStyleSheet(
            "font-weight: bold; font-size: 14px; color: #333;"
            "background-color: #f0f0f0; padding: 8px; border-radius: 5px;"
        )
        layout.addWidget(self.summary_label)

        # 시간표 테이블
        self.table = QTableWidget(14, 7)
        self.table.setHorizontalHeaderLabels(DAYS)
        self.table.setVerticalHeaderLabels([f"{i}교시" for i in range(1, 15)])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.table.verticalHeader().setMinimumWidth(72)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        # 이미지 내보내기 버튼
        export_btn = QPushButton("이미지로 저장")
        export_btn.setFixedHeight(32)
        export_btn.setStyleSheet(
            "QPushButton { background-color: #5c85d6; color: white;"
            "border-radius: 4px; font-size: 13px; }"
            "QPushButton:hover { background-color: #3d6bbf; }"
        )
        export_btn.clicked.connect(self.export_image)
        layout.addWidget(export_btn)

    def set_summary(self, text: str):
        self.summary_label.setText(text)

    def set_period_times(self, period_times: dict):
        """교시별 시작 시간 설정 후 세로 헤더 갱신"""
        self.period_times = period_times
        self._refresh_period_headers()

    def load_schedule(self, courses: list):
        self.table.clearContents()
        for course in courses:
            try:
                col_idx = DAYS.index(course.day)
                for period in course.get_periods():
                    row_idx = period - 1
                    if 0 <= row_idx < 14:
                        item = QTableWidgetItem(course.display_name())
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setBackground(QColor(course.color))
                        item.setForeground(QColor("white"))
                        self.table.setItem(row_idx, col_idx, item)
            except ValueError:
                pass

    def export_image(self):
        """요약 라벨과 시간표 테이블만 이미지로 저장합니다 (버튼 제외)."""
        path, _ = QFileDialog.getSaveFileName(
            self, "이미지로 저장", "시간표.png",
            "PNG 이미지 (*.png);;JPG 이미지 (*.jpg)",
        )
        if not path:
            return

        # summary_label + table 두 위젯의 영역만 합쳐서 캡처
        from PySide6.QtCore import QRect, QPoint
        top = self.summary_label.mapTo(self, QPoint(0, 0))
        bottom_widget = self.table
        bottom_right = bottom_widget.mapTo(self, QPoint(
            bottom_widget.width(), bottom_widget.height()
        ))
        capture_rect = QRect(top, bottom_right)

        pixmap = self.grab(capture_rect)
        if pixmap.save(path):
            QMessageBox.information(self, "저장 완료", f"이미지가 저장되었습니다:\n{path}")
        else:
            QMessageBox.warning(self, "저장 실패", "이미지 저장에 실패했습니다.")

    def _refresh_period_headers(self):
        labels = []
        for i in range(1, 15):
            t = self.period_times.get(i, "")
            labels.append(f"{i}교시\n{t}" if t else f"{i}교시")
        self.table.setVerticalHeaderLabels(labels)