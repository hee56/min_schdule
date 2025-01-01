import streamlit as st
import pandas as pd
import datetime
import calendar
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os

def main():
    st.title('일일 학습 체크리스트')

    # 초기 상태 설정
    if 'checklist_data' not in st.session_state:
        st.session_state.checklist_data = {}
    
    if 'study_hours' not in st.session_state:
        st.session_state.study_hours = {}

    # 날짜 선택
    selected_date = st.date_input("날짜 선택", datetime.now())
    date_key = selected_date.strftime("%Y-%m-%d")

    # 요일별 스케줄 정의
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
    
    # 체크리스트 데이터 초기화
    if date_key not in st.session_state.checklist_data:
        st.session_state.checklist_data[date_key] = {}

    # 체크박스 생성
    for item in current_schedule:
        checked = st.checkbox(
            f"{item['label']} ({item['time']})", 
            key=f"{date_key}_{item['id']}",
            value=st.session_state.checklist_data[date_key].get(item['id'], False)
        )
        st.session_state.checklist_data[date_key][item['id']] = checked

    # 학습 시간 입력
    st.subheader('학습 시간 기록')
    study_hours = st.number_input(
        '실제 학습 시간 (시간)',
        min_value=0.0,
        max_value=24.0,
        value=float(st.session_state.study_hours.get(date_key, 0)),
        step=0.5
    )
    st.session_state.study_hours[date_key] = study_hours

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

    # 월간 캘린더 표시
    st.subheader('월간 학습 현황')
    month_start = selected_date.replace(day=1)
    month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    # 캘린더 데이터 생성
    calendar_data = []
    current_date = month_start
    while current_date <= month_end:
        date_str = current_date.strftime("%Y-%m-%d")
        day_type = get_day_type(current_date)
        actual_hours = st.session_state.study_hours.get(date_str, 0)
        target = target_study_hours[day_type]
        
        if actual_hours >= target:
            status = 'GOOD'
        elif actual_hours > 0:
            status = 'BAD'
        else:
            status = '미입력'
            
        calendar_data.append({
            'date': date_str,
            'day': current_date.day,
            'status': status
        })
        current_date += timedelta(days=1)

    # 캘린더 표시를 위한 데이터프레임 생성
    calendar_df = pd.DataFrame(calendar_data)
    calendar_df['week'] = pd.to_datetime(calendar_df['date']).dt.isocalendar().week
    calendar_df['weekday'] = pd.to_datetime(calendar_df['date']).dt.dayofweek

    # Plotly로 캘린더 히트맵 생성
    weeks = calendar_df['week'].unique()
    weekdays = ['월', '화', '수', '목', '금', '토', '일']
    
    fig = go.Figure(data=go.Heatmap(
        z=[[0 for _ in range(7)] for _ in range(len(weeks))],
        customdata=[['' for _ in range(7)] for _ in range(len(weeks))],
        text=[['' for _ in range(7)] for _ in range(len(weeks))],
        colorscale=[
            [0, 'white'],
            [0.33, '#ffcdd2'],  # Bad - 연한 빨강
            [0.66, '#c8e6c9'],  # Good - 연한 초록
            [1, '#f5f5f5']      # 미입력 - 회색
        ],
        showscale=False
    ))

    # 캘린더 데이터 채우기
    for _, row in calendar_df.iterrows():
        week_idx = list(weeks).index(row['week'])
        day_idx = row['weekday']
        
        if row['status'] == 'GOOD':
            value = 0.66
        elif row['status'] == 'BAD':
            value = 0.33
        else:
            value = 1
            
        fig.data[0].z[week_idx][day_idx] = value
        fig.data[0].text[week_idx][day_idx] = str(row['day'])

    # 캘린더 레이아웃 설정
    fig.update_layout(
        height=300,
        xaxis=dict(
            ticktext=weekdays,
            tickvals=list(range(len(weekdays))),
            showgrid=True
        ),
        yaxis=dict(
            showgrid=True,
            scaleanchor='x'
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # CSV 다운로드 버튼
    if st.button('CSV 다운로드'):
        # 데이터 준비
        data_list = []
        for date_str in st.session_state.checklist_data:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            day_type = get_day_type(date_obj)
            data_list.append({
                '날짜': date_str,
                '요일': date_obj.strftime('%A'),
                '목표학습시간': target_study_hours[day_type],
                '실제학습시간': st.session_state.study_hours.get(date_str, 0),
                **st.session_state.checklist_data[date_str]
            })
        
        df = pd.DataFrame(data_list)
        csv = df.to_csv(index=False)
        st.download_button(
            label="CSV 파일 다운로드",
            data=csv,
            file_name="학습체크리스트.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
