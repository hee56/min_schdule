import streamlit as st
import json
import os
from datetime import datetime, timedelta
import calendar

def load_data():
    if os.path.exists('checklist_data.json'):
        with open('checklist_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'checklist': {},
        'study_hours': {},
        'daily_reviews': {}
    }

def save_data(data):
    with open('checklist_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_day_type(date):
    day = date.weekday()
    if day == 6:  # Sunday
        return 'sunday'
    elif day == 5:  # Saturday
        return 'saturday'
    elif day in [0, 2, 4]:  # Monday, Wednesday, Friday
        return 'mwf'
    else:  # Tuesday, Thursday
        return 'tt'

def main():
    st.title('일일 학습 체크리스트')

    # 데이터 로드
    if 'data' not in st.session_state:
        st.session_state.data = load_data()

    # 날짜 선택
    selected_date = st.date_input("날짜 선택", datetime.now())
    date_key = selected_date.strftime("%Y-%m-%d")

    # 요일별 스케줄 정의
    schedules = {
        'mwf': [
            {'id': 'wake', 'label': '기상 시간 (6:00)', 'time': '6:00'},
            {'id': 'sleep', 'label': '수면 시간 (7:00)', 'time': '7:00'},
            {'id': 'class', 'label': '수업 (3:30)', 'time': '3:30'},
            {'id': 'meal', 'label': '식사 및 휴식 (3:00↓)', 'time': '3:00'},
            {'id': 'tkd', 'label': '태권도 (1:30↓)', 'time': '1:30'},
            {'id': 'study', 'label': '학습 (8:00↑)', 'time': '8:00'},
            {'id': 'screen', 'label': '수업 화면 녹화 확인', 'time': '-'},
            {'id': 'focus', 'label': '전자기기 목적 외 사용 없음', 'time': '-'}
        ],
        'tt': [
            {'id': 'wake', 'label': '기상 시간 (6:00)', 'time': '6:00'},
            {'id': 'sleep', 'label': '수면 시간 (7:00)', 'time': '7:00'},
            {'id': 'class', 'label': '수업 (3:30)', 'time': '3:30'},
            {'id': 'meal', 'label': '식사 및 휴식 (3:00↓)', 'time': '3:00'},
            {'id': 'study', 'label': '학습 (9:30↑)', 'time': '9:30'},
            {'id': 'screen', 'label': '수업 화면 녹화 확인', 'time': '-'},
            {'id': 'focus', 'label': '전자기기 목적 외 사용 없음', 'time': '-'}
        ],
        'saturday': [
            {'id': 'wake', 'label': '기상 시간 (6:00)', 'time': '6:00'},
            {'id': 'sleep', 'label': '수면 시간 (7:00)', 'time': '7:00'},
            {'id': 'class', 'label': '수업 (10:30)', 'time': '10:30'},
            {'id': 'meal', 'label': '식사 및 휴식 (3:30)', 'time': '3:30'},
            {'id': 'study', 'label': '학습 (3:00)', 'time': '3:00'},
            {'id': 'screen', 'label': '수업 화면 녹화 확인', 'time': '-'},
            {'id': 'focus', 'label': '전자기기 목적 외 사용 없음', 'time': '-'}
        ],
        'sunday': [
            {'id': 'wake', 'label': '기상 시간 (6:00)', 'time': '6:00'},
            {'id': 'sleep', 'label': '수면 시간 (7:00)', 'time': '7:00'},
            {'id': 'meal', 'label': '식사 및 휴식 (4:00)', 'time': '4:00'},
            {'id': 'study', 'label': '학습 (11:00↑)', 'time': '11:00'},
            {'id': 'focus', 'label': '전자기기 목적 외 사용 없음', 'time': '-'}
        ]
    }

    target_study_hours = {
        'mwf': 8,
        'tt': 9.5,
        'saturday': 3,
        'sunday': 11
    }

    # 체크리스트 표시
    day_type = get_day_type(selected_date)
    current_schedule = schedules[day_type]

    st.subheader('오늘의 체크리스트')
    
    # 데이터 초기화
    if date_key not in st.session_state.data['checklist']:
        st.session_state.data['checklist'][date_key] = {}

    # 체크박스 생성 및 상태 저장
    for item in current_schedule:
        checked = st.checkbox(
            f"{item['label']} ({item['time']})",
            key=f"{date_key}_{item['id']}",
            value=st.session_state.data['checklist'][date_key].get(item['id'], False)
        )
        st.session_state.data['checklist'][date_key][item['id']] = checked

    # 학습 시간 입력
    st.subheader('학습 시간 기록')
    study_hours = st.number_input(
        '실제 학습 시간 (시간)',
        min_value=0.0,
        max_value=24.0,
        value=float(st.session_state.data['study_hours'].get(date_key, 0)),
        step=0.5
    )
    st.session_state.data['study_hours'][date_key] = study_hours

    # 학습 평가
    target_hours = target_study_hours[day_type]
    if study_hours >= target_hours:
        evaluation = 'GOOD'
        color = 'green'
    elif study_hours > 0:
        evaluation = 'BAD'
        color = 'red'
    else:
        evaluation = '미입력'
        color = 'gray'

    st.markdown(f"**학습 평가:** :{color}[{evaluation}]")

    # 일일 총평
    st.subheader('오늘의 총평')
    daily_review = st.text_area(
        "오늘 하루를 돌아보며...",
        value=st.session_state.data['daily_reviews'].get(date_key, ''),
        height=150,
        placeholder="오늘의 성과, 부족한 점, 내일의 계획 등을 기록해보세요."
    )
    st.session_state.data['daily_reviews'][date_key] = daily_review

    # 월간 리뷰 표시
    st.subheader('이번 달 기록 확인')
    month_start = selected_date.replace(day=1)
    month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    current_month_data = {
        date: {
            'study_hours': st.session_state.data['study_hours'].get(date, 0),
            'review': st.session_state.data['daily_reviews'].get(date, '')
        }
        for date in [
            (month_start + timedelta(days=x)).strftime("%Y-%m-%d")
            for x in range((month_end - month_start).days + 1)
        ]
    }

    # 달력 형태로 데이터 표시
    cols = st.columns(7)
    for i, day in enumerate(['일', '월', '화', '수', '목', '금', '토']):
        cols[i].markdown(f"**{day}**")

    # 첫 주 시작 요일까지의 빈 칸 처리
    first_day_weekday = month_start.weekday()
    for i in range((first_day_weekday + 1) % 7):
        cols[i].write("")

    # 날짜별 데이터 표시
    day_count = (first_day_weekday + 1) % 7
    for date, data in current_month_data.items():
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        
        if data['study_hours'] >= target_study_hours[get_day_type(date_obj)]:
            color = 'green'
        elif data['study_hours'] > 0:
            color = 'red'
        else:
            color = 'gray'
            
        cols[day_count].markdown(f"**{date_obj.day}**")
        if data['study_hours'] > 0:
            cols[day_count].markdown(f":{color}[{data['study_hours']}시간]")
        if data['review']:
            cols[day_count].markdown("📝")
            
        day_count = (day_count + 1) % 7

    # 데이터 저장
    save_data(st.session_state.data)

    # 데이터 백업 다운로드 버튼
    if st.button('데이터 백업'):
        json_str = json.dumps(st.session_state.data, ensure_ascii=False, indent=2)
        st.download_button(
            label="JSON 파일 다운로드",
            data=json_str,
            file_name="checklist_backup.json",
            mime="application/json"
        )

if __name__ == "__main__":
    main()
