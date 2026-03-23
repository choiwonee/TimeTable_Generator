<div align="center">

<br/>

<!-- 앱 아이콘: .ico → .png로 변환 후 GitHub Issues에 업로드하고 아래 URL 교체 -->
<img src="https://github.com/user-attachments/assets/e156d90d-373c-4f37-9899-576d3c9c2a36" height="72" alt="앱 아이콘"/>

# TimeTable Generator

**대학생을 위한 시간표 조합 자동 생성기**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![PySide6](https://img.shields.io/badge/PySide6-Qt%20for%20Python-41CD52?style=flat-square&logo=qt&logoColor=white)](https://doc.qt.io/qtforpython/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)]()

[⬇️ **exe 다운로드 (Windows)**](#-빠른-시작--exe-실행) · [🐍 Python으로 실행](#-python으로-실행) · [📖 사용 방법](#-사용-방법)

<br/>

<img src="https://github.com/user-attachments/assets/8f2c8ca4-be6e-46fc-81f5-1e06d09e6dd6" width="780" alt="프리뷰 이미지"/>

<br/>

</div>

<br/>

---

<br/>

## ⬇️ 빠른 시작 — exe 실행

> Python 설치 없이 바로 실행할 수 있습니다. **Windows 전용.**

**[📦 TimeTable-Generator.exe 다운로드](https://github.com/choiwonee/TimeTable_Generator/releases/latest)**

1. 위 링크에서 `TimeTable-Generator.exe` 다운로드
2. 파일 더블클릭으로 즉시 실행

> **⚠️ Windows 보안 경고가 뜨는 경우**  
> `추가 정보` → `실행` 을 클릭하세요.  
> 개인 개발자 배포 앱에 표시되는 정상적인 경고입니다.

<br/>

---

<br/>

## 🐍 Python으로 실행

소스코드로 직접 실행하거나 macOS / Linux에서 사용할 때 이 방법을 사용하세요.

### 1. 사전 요구사항

```
Python 3.10 이상
```

Python이 없다면 → [python.org/downloads](https://www.python.org/downloads/)

### 2. 저장소 받기

```bash
git clone https://github.com/choiwonee/TimeTable_Generator.git
cd timetable-generator
```

> Git이 없다면 페이지 상단 `Code → Download ZIP` 으로 받아도 됩니다.

### 3. 가상환경 설정

```bash
# 가상환경 생성
python -m venv venv

# 활성화 — macOS / Linux
source venv/bin/activate

# 활성화 — Windows
venv\Scripts\activate
```

### 4. 패키지 설치 및 실행

```bash
pip install -r requirements.txt
python main.py
```

<br/>

---

<br/>

## 📖 사용 방법

>사용 방법은 프로그램 내에서도 확인할 수 있습니다.
<img src="https://github.com/user-attachments/assets/374fde32-fc7e-4b24-a023-2709dbb46c9f" width="197" alt="사용 방법 버튼"/>

### Step 1 — 과목 입력

화면 왼쪽 **① 강의 입력** 영역에서 과목 정보를 입력하고 `추가` 버튼 또는 `Enter` 를 누릅니다.

| 항목 | 설명 |
|---|---|
| **구분** | 전공 / 교양 / 기타 / PNP 선택 |
| **강의명** | 같은 이름으로 입력한 과목은 같은 그룹으로 묶입니다 |
| **분반** | 목록에서 구분할 메모 (선택 사항) |
| **요일 / 교시** | 수업 시간 |
| **학점** | 이수 학점 수 |
| **분리수업** | 주 2회처럼 여러 시간대가 세트인 경우 체크 |

<br/>

추가한 과목을 수정하고 싶다면, 목록을 더블클릭하여 수정할 수 있습니다.

<img src="https://github.com/user-attachments/assets/cef17210-7cee-4c74-a8c8-cc5f5b444962" width="513" alt="목록 수정 창"/>

<br/>

### Step 2 — 분반 vs. 분리수업

같은 강의명으로 등록한 과목들은 한 그룹으로 묶입니다.  
**분리수업 체크 여부**에 따라 동작이 달라집니다.

<details>
<summary><b>📌 분반 (분리수업 미체크)</b> — 여러 시간 중 하나만 선택</summary>

<br/>

같은 강의명으로 여러 시간대를 등록하면, 시간표 생성 시 **그 중 하나만** 자동으로 선택됩니다.

```
예)  영어회화   화 3–4교시
     영어회화   목 3–4교시
→ 둘 중 하나가 자동 편성됨
```

</details>

<details>
<summary><b>🔗 분리수업 (분리수업 체크)</b> — 항상 세트로 함께 편성</summary>

<br/>

같은 강의명의 항목들이 **항상 세트로 함께** 편성됩니다.  
주 2회처럼 여러 시간대가 묶이는 수업에 사용하세요.

```
예)  대학수학   월 1–2교시  ← 분리수업 체크
     대학수학   목 1–2교시  ← 분리수업 체크
→ 두 시간대가 반드시 함께 편성됨
```

</details>

<br/>

### Step 3 — 고정 과목 · PNP 설정

**② 강의 목록** 표에서 설정합니다.

| 기능 | 설명 |
|---|---|
| **고정 체크박스** | 모든 시간표에 반드시 포함. 이미 수강 신청한 과목에 사용 |
| **PNP 구분** | 학점 목표에서 제외. 충돌 없으면 자동으로 편성 |

<br/>

### Step 4 — 생성 조건 설정

**③ 생성 조건** 영역에서 원하는 조건을 설정한 뒤 `시간표 생성` 버튼을 누릅니다.

| 항목 | 설명 |
|---|---|
| **목표 학점** | 완성 시간표의 총 학점 (PNP 제외) |
| **최대 공강** | 같은 날 수업 사이에 허용할 최대 빈 교시 수 |
| **공강 요일** | 수업을 아예 넣지 않을 요일 |

조건에 맞는 조합이 오른쪽에 **최대 50개 탭**으로 표시됩니다.

<br/>

### Step 5 — 결과 확인 및 저장

| 기능 | 방법 |
|---|---|
| **이미지 저장** | 원하는 탭 선택 → `이미지로 저장` → PNG / JPG 내보내기 |
| **과목 목록 저장** | 상단 `강의 목록 저장` → JSON 파일로 저장 |
| **과목 목록 불러오기** | 상단 `강의 목록 불러오기` → 저장한 JSON 복원 |
| **교시 시간 설정** | 우측 상단 `⚙ 교시 시간 설정` → 학교별 교시 시작 시간 입력 |

<br/>

---

<br/>

## 🎨 색상 테마

오른쪽 상단 **테마 선택**에서 시간표 색상 팔레트를 변경할 수 있습니다.

| 테마 | 팔레트 |
|---|---|
| 🌈 무지개 | ![](https://placehold.co/28x20/E85858/E85858.png) ![](https://placehold.co/28x20/F08030/F08030.png) ![](https://placehold.co/28x20/E8C020/E8C020.png) ![](https://placehold.co/28x20/50B840/50B840.png) ![](https://placehold.co/28x20/20A878/20A878.png) ![](https://placehold.co/28x20/2880D0/2880D0.png) ![](https://placehold.co/28x20/4848C8/4848C8.png) ![](https://placehold.co/28x20/8040B8/8040B8.png) ![](https://placehold.co/28x20/C840A0/C840A0.png) ![](https://placehold.co/28x20/C89870/C89870.png) |
| 🍰 레드벨벳 케이크 | ![](https://placehold.co/28x20/1A0A10/1A0A10.png) ![](https://placehold.co/28x20/4A1820/4A1820.png) ![](https://placehold.co/28x20/881828/881828.png) ![](https://placehold.co/28x20/C03030/C03030.png) ![](https://placehold.co/28x20/E05858/E05858.png) ![](https://placehold.co/28x20/F08888/F08888.png) ![](https://placehold.co/28x20/F5C8C0/F5C8C0.png) ![](https://placehold.co/28x20/C87848/C87848.png) ![](https://placehold.co/28x20/5A3018/5A3018.png) ![](https://placehold.co/28x20/F0E4D8/F0E4D8.png) |
| 🍂 단풍 소풍 | ![](https://placehold.co/28x20/1E1008/1E1008.png) ![](https://placehold.co/28x20/5C2C10/5C2C10.png) ![](https://placehold.co/28x20/9A3C18/9A3C18.png) ![](https://placehold.co/28x20/C85820/C85820.png) ![](https://placehold.co/28x20/E07820/E07820.png) ![](https://placehold.co/28x20/F0A028/F0A028.png) ![](https://placehold.co/28x20/F5C870/F5C870.png) ![](https://placehold.co/28x20/E8D890/E8D890.png) ![](https://placehold.co/28x20/5E7028/5E7028.png) ![](https://placehold.co/28x20/3A4E18/3A4E18.png) |
| 🍋 레몬 파스타 | ![](https://placehold.co/28x20/1C2010/1C2010.png) ![](https://placehold.co/28x20/2A4820/2A4820.png) ![](https://placehold.co/28x20/4A7830/4A7830.png) ![](https://placehold.co/28x20/8A9830/8A9830.png) ![](https://placehold.co/28x20/D4B018/D4B018.png) ![](https://placehold.co/28x20/F0D028/F0D028.png) ![](https://placehold.co/28x20/F8EC90/F8EC90.png) ![](https://placehold.co/28x20/F5E8C0/F5E8C0.png) ![](https://placehold.co/28x20/C87040/C87040.png) ![](https://placehold.co/28x20/E8D8A0/E8D8A0.png) |
| 🌲 숲속 오두막 | ![](https://placehold.co/28x20/0A1008/0A1008.png) ![](https://placehold.co/28x20/1C3018/1C3018.png) ![](https://placehold.co/28x20/305C28/305C28.png) ![](https://placehold.co/28x20/508038/508038.png) ![](https://placehold.co/28x20/78A858/78A858.png) ![](https://placehold.co/28x20/A8C880/A8C880.png) ![](https://placehold.co/28x20/6A4828/6A4828.png) ![](https://placehold.co/28x20/3C2810/3C2810.png) ![](https://placehold.co/28x20/C8B888/C8B888.png) ![](https://placehold.co/28x20/E8DEC0/E8DEC0.png) |
| 🌊 아드리아해 | ![](https://placehold.co/28x20/060C1E/060C1E.png) ![](https://placehold.co/28x20/0C2858/0C2858.png) ![](https://placehold.co/28x20/185098/185098.png) ![](https://placehold.co/28x20/2878C8/2878C8.png) ![](https://placehold.co/28x20/50A8D8/50A8D8.png) ![](https://placehold.co/28x20/90CCE8/90CCE8.png) ![](https://placehold.co/28x20/C8EAF0/C8EAF0.png) ![](https://placehold.co/28x20/EAD890/EAD890.png) ![](https://placehold.co/28x20/C06840/C06840.png) ![](https://placehold.co/28x20/1A5848/1A5848.png) |
| 🌌 한밤의 은하수 | ![](https://placehold.co/28x20/050310/050310.png) ![](https://placehold.co/28x20/0C0828/0C0828.png) ![](https://placehold.co/28x20/201860/201860.png) ![](https://placehold.co/28x20/384098/384098.png) ![](https://placehold.co/28x20/6050C0/6050C0.png) ![](https://placehold.co/28x20/9878D8/9878D8.png) ![](https://placehold.co/28x20/C0A8E8/C0A8E8.png) ![](https://placehold.co/28x20/183C68/183C68.png) ![](https://placehold.co/28x20/30789A/30789A.png) ![](https://placehold.co/28x20/F0E8C8/F0E8C8.png) |
| 🪻 프로방스 라벤더 | ![](https://placehold.co/28x20/181028/181028.png) ![](https://placehold.co/28x20/302458/302458.png) ![](https://placehold.co/28x20/584A98/584A98.png) ![](https://placehold.co/28x20/8878C0/8878C0.png) ![](https://placehold.co/28x20/B0A0D8/B0A0D8.png) ![](https://placehold.co/28x20/D8D0F0/D8D0F0.png) ![](https://placehold.co/28x20/7A6878/7A6878.png) ![](https://placehold.co/28x20/4A5838/4A5838.png) ![](https://placehold.co/28x20/887860/887860.png) ![](https://placehold.co/28x20/F0E4D0/F0E4D0.png) |

<br/>

> 앱은 시스템 설정을 자동 감지하여 라이트 / 다크 테마로 전환됩니다.

| ☀️ 라이트 모드 | 🌙 다크 모드 |
|:---:|:---:|
| ![라이트 모드](https://github.com/user-attachments/assets/3727c9d0-4de2-4fbd-a623-18f89a185558) | ![다크 모드](https://github.com/user-attachments/assets/ae928b22-9846-4eda-8817-b5e57d0b0d67) |

<br/>

---

## 📁 파일 구조

```
timetable-generator/
├── main.py          # 메인 윈도우 및 전체 UI
├── logic.py         # 시간표 생성 알고리즘 (DFS + 가지치기)
├── models.py        # Course 데이터 모델 · 색상 팔레트
├── ui_widgets.py    # 시간표 표시 위젯
├── constants.py     # 요일 목록 · 기본 교시 시간
├── requirements.txt
└── README.md
```

---

## 🛠️ 기술 스택

- **Python 3.10+**
- **PySide6** — Qt for Python GUI 프레임워크

---

## 📄 라이선스

이 프로젝트는 [MIT License](LICENSE) 하에 배포됩니다.

---

<div align="center">

만든 사람: **choiwonee** · 문의 및 버그 리포트는 [Issues](https://github.com/yourname/timetable-generator/issues)로 남겨주세요

</div>
