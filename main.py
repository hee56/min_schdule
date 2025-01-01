import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle2, Circle, Download, Calendar } from "lucide-react";
import Papa from 'papaparse';

const DailyChecklist = () => {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [checklist, setChecklist] = useState({});
  const [studyHours, setStudyHours] = useState({});
  const [showCalendar, setShowCalendar] = useState(false);

  // 학습시간 목표
  const targetStudyHours = {
    mwf: 8,
    tt: 9.5,
    saturday: 3,
    sunday: 11
  };

  const getDayType = (date) => {
    const day = date.getDay();
    if (day === 0) return 'sunday';
    if (day === 6) return 'saturday';
    if (day === 1 || day === 3 || day === 5) return 'mwf';
    return 'tt';
  };

  const schedules = {
    mwf: [
      { id: 'wake', label: '기상 시간 (6:00)', time: '6:00', category: 'time' },
      { id: 'sleep', label: '수면 시간 (7:00)', time: '7:00', category: 'time' },
      { id: 'class', label: '수업 (3:30)', time: '3:30', category: 'time' },
      { id: 'meal', label: '식사 및 휴식 (3:00↓)', time: '3:00', category: 'time' },
      { id: 'tkd', label: '태권도 (1:30↓)', time: '1:30', category: 'time' },
      { id: 'study', label: '학습 (8:00↑)', time: '8:00', category: 'study' },
      { id: 'screen', label: '수업 화면 녹화 확인', time: '-', category: 'check' },
      { id: 'focus', label: '전자기기 목적 외 사용 없음', time: '-', category: 'check' },
      { id: 'studyHours', label: '실제 학습시간 (시간)', type: 'number', category: 'input' }
    ],
    tt: [
      // ... (이전과 동일한 구조에 category 추가)
    ],
    saturday: [
      // ... (이전과 동일한 구조에 category 추가)
    ],
    sunday: [
      // ... (이전과 동일한 구조에 category 추가)
    ]
  };

  const formatDate = (date) => {
    return new Intl.DateTimeFormat('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      weekday: 'long',
    }).format(date);
  };

  const handleCheck = (itemId) => {
    const dateKey = selectedDate.toISOString().split('T')[0];
    setChecklist(prev => ({
      ...prev,
      [dateKey]: {
        ...prev[dateKey],
        [itemId]: !prev[dateKey]?.[itemId]
      }
    }));
  };

  const handleStudyHoursChange = (hours) => {
    const dateKey = selectedDate.toISOString().split('T')[0];
    setStudyHours(prev => ({
      ...prev,
      [dateKey]: parseFloat(hours) || 0
    }));
  };

  const isChecked = (itemId) => {
    const dateKey = selectedDate.toISOString().split('T')[0];
    return checklist[dateKey]?.[itemId] || false;
  };

  const evaluateStudyPerformance = (date) => {
    const dateKey = date.toISOString().split('T')[0];
    const actualHours = studyHours[dateKey] || 0;
    const dayType = getDayType(date);
    const targetHours = targetStudyHours[dayType];

    if (actualHours >= targetHours) return 'good';
    if (actualHours === 0) return 'no-data';
    return 'bad';
  };

  const exportToCSV = () => {
    const allDates = Object.keys(checklist);
    const rows = allDates.map(date => {
      const dayType = getDayType(new Date(date));
      return {
        날짜: date,
        요일: new Date(date).toLocaleDateString('ko-KR', { weekday: 'long' }),
        목표학습시간: targetStudyHours[dayType],
        실제학습시간: studyHours[date] || 0,
        평가: evaluateStudyPerformance(new Date(date)),
        ...checklist[date]
      };
    });

    const csv = Papa.unparse(rows);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = '학습체크리스트.csv';
    link.click();
  };

  const generateCalendarDates = () => {
    const startDate = new Date(selectedDate.getFullYear(), selectedDate.getMonth(), 1);
    const endDate = new Date(selectedDate.getFullYear(), selectedDate.getMonth() + 1, 0);
    const dates = [];
    
    for (let date = new Date(startDate); date <= endDate; date.setDate(date.getDate() + 1)) {
      dates.push(new Date(date));
    }
    return dates;
  };

  return (
    <div className="space-y-4 w-full max-w-4xl">
      <Card>
        <CardHeader>
          <CardTitle className="text-center">
            <div className="flex items-center justify-between">
              <button 
                onClick={() => handleDateChange(-1)}
                className="px-4 py-2 text-sm bg-blue-500 text-white rounded"
              >
                이전
              </button>
              <div className="flex items-center space-x-2">
                <span>{formatDate(selectedDate)}</span>
                <Calendar 
                  className="cursor-pointer" 
                  onClick={() => setShowCalendar(!showCalendar)}
                />
              </div>
              <button 
                onClick={() => handleDateChange(1)}
                className="px-4 py-2 text-sm bg-blue-500 text-white rounded"
              >
                다음
              </button>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {showCalendar && (
            <div className="mb-4 grid grid-cols-7 gap-1">
              {['일', '월', '화', '수', '목', '금', '토'].map(day => (
                <div key={day} className="text-center font-bold">{day}</div>
              ))}
              {generateCalendarDates().map((date, index) => {
                const performance = evaluateStudyPerformance(date);
                const colorClass = 
                  performance === 'good' ? 'bg-green-100' :
                  performance === 'bad' ? 'bg-red-100' :
                  performance === 'no-data' ? 'bg-gray-100' : '';
                
                return (
                  <div
                    key={index}
                    onClick={() => setSelectedDate(date)}
                    className={`p-2 text-center cursor-pointer ${colorClass} hover:opacity-75`}
                  >
                    {date.getDate()}
                  </div>
                );
              })}
            </div>
          )}

          <div className="space-y-4">
            {schedules[getDayType(selectedDate)].map((item) => (
              <div key={item.id}>
                {item.category === 'input' ? (
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <span>{item.label}</span>
                    <input
                      type="number"
                      value={studyHours[selectedDate.toISOString().split('T')[0]] || ''}
                      onChange={(e) => handleStudyHoursChange(e.target.value)}
                      className="w-20 p-1 border rounded"
                    />
                  </div>
                ) : (
                  <div 
                    className="flex items-center justify-between p-3 bg-gray-50 rounded hover:bg-gray-100 cursor-pointer"
                    onClick={() => handleCheck(item.id)}
                  >
                    <div className="flex items-center space-x-3">
                      {isChecked(item.id) ? 
                        <CheckCircle2 className="text-green-500" /> : 
                        <Circle className="text-gray-400" />
                      }
                      <span>{item.label}</span>
                    </div>
                    <span className="text-gray-500">{item.time}</span>
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="mt-4 flex justify-between items-center">
            <div className="text-lg font-semibold">
              학습 평가: {' '}
              <span className={
                evaluateStudyPerformance(selectedDate) === 'good' ? 'text-green-500' :
                evaluateStudyPerformance(selectedDate) === 'bad' ? 'text-red-500' :
                'text-gray-500'
              }>
                {evaluateStudyPerformance(selectedDate) === 'good' ? 'GOOD' :
                 evaluateStudyPerformance(selectedDate) === 'bad' ? 'BAD' :
                 '미입력'}
              </span>
            </div>
            <button
              onClick={exportToCSV}
              className="flex items-center space-x-2 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
            >
              <Download size={18} />
              <span>CSV 다운로드</span>
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DailyChecklist;
