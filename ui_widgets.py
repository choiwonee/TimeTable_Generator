from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from constants import DAYS

class TimeTableWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # 레이아웃 설정
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 1. 상단 요약 라벨 (학점 정보 표시용)
        self.summary_label = QLabel("학점 계산 중...")
        self.summary_label.setAlignment(Qt.AlignCenter)
        self.summary_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #333; background-color: #f0f0f0; padding: 8px; border-radius: 5px;")
        layout.addWidget(self.summary_label)
        
        # 2. 시간표 테이블
        self.table = QTableWidget(14, 7)
        self.table.setHorizontalHeaderLabels(DAYS)
        self.table.setVerticalHeaderLabels([f"{i}교시" for i in range(1, 15)])
        
        # 헤더 정렬 및 크기 조정
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setDefaultAlignment(Qt.AlignCenter) # 교시 중앙 정렬
        
        # 수정 불가 설정
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.table)

    def set_summary(self, text):
        # 상단 라벨 텍스트 변경 메서드
        self.summary_label.setText(text)

    def load_schedule(self, courses):
        # 시간표 렌더링
        self.table.clearContents()
        
        for course in courses:
            try:
                col_idx = DAYS.index(course.day)
                for period in course.get_periods():
                    row_idx = period - 1
                    if 0 <= row_idx < 14:
                        item = QTableWidgetItem(course.name)
                        item.setTextAlignment(Qt.AlignCenter)
                        
                        # 배경색 및 글자색(흰색) 적용
                        item.setBackground(QColor(course.color))
                        item.setForeground(Qt.white)
                        
                        self.table.setItem(row_idx, col_idx, item)
            except ValueError:
                pass