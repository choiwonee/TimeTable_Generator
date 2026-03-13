import sys
import json
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QLineEdit, QComboBox, 
                               QSpinBox, QPushButton, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QTabWidget, QCheckBox, QMessageBox, 
                               QSplitter, QGroupBox, QFileDialog, QProgressDialog)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor

from constants import DAYS
from models import Course
from logic import ScheduleGenerator
from ui_widgets import TimeTableWidget

# 백그라운드 작업 클래스 (계산 담당)
class ScheduleWorker(QThread):
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, courses, target_credit, empty_days, max_gap):
        super().__init__()
        self.courses = courses
        self.target_credit = target_credit
        self.empty_days = empty_days
        self.max_gap = max_gap

    def run(self):
        try:
            # 안전 장치: 최대 50개까지만 찾음
            gen = ScheduleGenerator(self.courses, self.target_credit, self.empty_days, self.max_gap, max_results=50)
            results = gen.generate()
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TimeTable Manager")
        self.resize(1100, 750)
        self.courses = []
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 상단 툴바
        top_bar = QHBoxLayout()
        save_btn = QPushButton("강의 목록 저장")
        load_btn = QPushButton("강의 목록 불러오기")
        save_btn.clicked.connect(self.save_data)
        load_btn.clicked.connect(self.load_data)
        top_bar.addWidget(save_btn)
        top_bar.addWidget(load_btn)
        top_bar.addStretch()
        main_layout.addLayout(top_bar)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # 좌측 패널
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # 1. 강의 입력
        input_group = QGroupBox("1. 강의 입력")
        input_layout = QVBoxLayout()
        
        row1 = QHBoxLayout()
        self.category_input = QComboBox()
        self.category_input.addItems(["전공", "교양", "기타", "PNP"])
        self.category_input.setFixedWidth(80)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("강의명")
        row1.addWidget(self.category_input)
        row1.addWidget(self.name_input)
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
        self.credit_input.setSuffix("학점")
        
        row2.addWidget(self.day_input)
        row2.addWidget(QLabel("시작:"))
        row2.addWidget(self.start_input)
        row2.addWidget(QLabel("종료:"))
        row2.addWidget(self.end_input)
        row2.addWidget(self.credit_input)
        input_layout.addLayout(row2)
        
        add_btn = QPushButton("추가")
        add_btn.setFixedHeight(35)
        add_btn.clicked.connect(self.add_course)
        input_layout.addWidget(add_btn)
        
        input_group.setLayout(input_layout)
        left_layout.addWidget(input_group)
        
        # 2. 강의 목록
        list_group = QGroupBox("2. 강의 목록 (체크시 고정)")
        list_layout = QVBoxLayout()
        self.course_list_table = QTableWidget(0, 6)
        self.course_list_table.setHorizontalHeaderLabels(["구분", "강의명", "시간", "학점", "고정", "관리"])
        self.course_list_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.course_list_table.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.course_list_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.course_list_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.course_list_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        list_layout.addWidget(self.course_list_table)
        list_group.setLayout(list_layout)
        left_layout.addWidget(list_group)
        
        # 3. 조건 그룹
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
        h_layout.addWidget(QLabel("최대 공강(시간):"))
        h_layout.addWidget(self.max_gap_spin)
        cond_layout.addLayout(h_layout)
        
        cond_layout.addWidget(QLabel("공강 요일:"))
        self.day_off_checks = {}
        d_layout = QHBoxLayout()
        for day in DAYS[:5]:
            chk = QCheckBox(day)
            self.day_off_checks[day] = chk
            d_layout.addWidget(chk)
        cond_layout.addLayout(d_layout)
        
        gen_btn = QPushButton("시간표 생성")
        gen_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; height: 40px;")
        gen_btn.clicked.connect(self.start_generation)
        cond_layout.addWidget(gen_btn)
        
        cond_group.setLayout(cond_layout)
        left_layout.addWidget(cond_group)
        
        self.result_tabs = QTabWidget()
        splitter.addWidget(left_panel)
        splitter.addWidget(self.result_tabs)
        splitter.setSizes([450, 650])
        main_layout.addWidget(splitter)

    def add_course(self):
        name = self.name_input.text().strip()
        if not name: return
        start, end = self.start_input.value(), self.end_input.value()
        if start > end:
            QMessageBox.warning(self, "오류", "시작 교시가 종료 교시보다 늦을 수 없습니다.")
            return
        category = self.category_input.currentText()
        course = Course(name, self.day_input.currentText(), start, end, self.credit_input.value(), category)
        self.courses.append(course)
        self.update_course_list()
        self.name_input.clear()
        self.name_input.setFocus()

    def update_course_list(self):
        self.course_list_table.setRowCount(0)
        for idx, course in enumerate(self.courses):
            self.course_list_table.insertRow(idx)
            self.course_list_table.setItem(idx, 0, QTableWidgetItem(course.category))
            nm = QTableWidgetItem(course.name)
            nm.setForeground(QColor(course.color))
            self.course_list_table.setItem(idx, 1, nm)
            self.course_list_table.setItem(idx, 2, QTableWidgetItem(f"{course.day} {course.start_period}-{course.end_period}"))
            self.course_list_table.setItem(idx, 3, QTableWidgetItem(str(course.credits)))
            chk_w = QWidget()
            chk = QCheckBox()
            chk.setChecked(course.is_fixed)
            chk.stateChanged.connect(lambda s, c=course: setattr(c, 'is_fixed', s == 2))
            l = QHBoxLayout(chk_w)
            l.addWidget(chk)
            l.setAlignment(Qt.AlignCenter)
            l.setContentsMargins(0,0,0,0)
            self.course_list_table.setCellWidget(idx, 4, chk_w)
            btn = QPushButton("삭제")
            btn.clicked.connect(lambda _, c=course: self.delete_course(c))
            self.course_list_table.setCellWidget(idx, 5, btn)

    def delete_course(self, course):
        if course in self.courses:
            self.courses.remove(course)
            self.update_course_list()

    def start_generation(self):
        empty_days = [d for d, c in self.day_off_checks.items() if c.isChecked()]
        
        # 로딩 창 표시
        self.progress_dialog = QProgressDialog("가능한 시간표를 계산 중입니다...", "취소", 0, 0, self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setMinimumDuration(0) 
        self.progress_dialog.show()
        
        # 워커 스레드 생성
        self.worker = ScheduleWorker(self.courses, self.target_credit_spin.value(), empty_days, self.max_gap_spin.value())
        self.worker.finished.connect(self.on_generation_finished)
        self.worker.error.connect(self.on_generation_error)
        self.progress_dialog.canceled.connect(self.worker.terminate)
        self.worker.start()

    def on_generation_finished(self, results):
        self.progress_dialog.close()
        self.result_tabs.clear()
        
        if not results:
            QMessageBox.information(self, "결과 없음", "조건에 맞는 조합이 없습니다.\n(0학점 과목은 '고정' 체크 필수)")
            return
            
        if len(results) >= 50:
            QMessageBox.warning(self, "결과가 너무 많음", 
                                "가능한 조합이 50개 이상입니다.\n시스템 성능을 위해 상위 50개만 표시합니다.\n\n"
                                "조건을 더 구체적으로 설정하세요.")

        for i, schedule in enumerate(results):
            tab = TimeTableWidget()
            tab.load_schedule(schedule)
            
            major_credits = sum(c.credits for c in schedule if c.category == "전공")
            ge_credits = sum(c.credits for c in schedule if c.category == "교양")
            other_credits = sum(c.credits for c in schedule if c.category == "기타")
            pnp_count = sum(1 for c in schedule if c.category == "PNP")
            
            summary_text = f"전공: {major_credits}학점 | 교양: {ge_credits}학점 | 기타: {other_credits}학점"
            if pnp_count > 0:
                summary_text += f" | PNP: {pnp_count}과목"
            
            tab.set_summary(summary_text)
            self.result_tabs.addTab(tab, f"{i+1}번")

    def on_generation_error(self, err_msg):
        self.progress_dialog.close()
        QMessageBox.critical(self, "오류", f"오류가 발생했습니다: {err_msg}")

    def save_data(self):
        path, _ = QFileDialog.getSaveFileName(self, "저장", "", "JSON (*.json)")
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump([c.to_dict() for c in self.courses], f, indent=4, ensure_ascii=False)
                QMessageBox.information(self, "성공", "저장되었습니다.")
            except Exception as e:
                QMessageBox.critical(self, "실패", str(e))

    def load_data(self):
        path, _ = QFileDialog.getOpenFileName(self, "열기", "", "JSON (*.json)")
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.courses = [Course.from_dict(d) for d in json.load(f)]
                self.update_course_list()
                QMessageBox.information(self, "성공", "불러왔습니다.")
            except Exception as e:
                QMessageBox.critical(self, "실패", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())