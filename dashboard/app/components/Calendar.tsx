"use client";

import { useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { isYesterday } from 'date-fns';

interface CalendarProps {
  onDateSelect?: (date: Date) => void;
  onDateRangeSelect?: (fromDate: Date, toDate: Date) => void;
  selectedDate?: Date | null;
  selectedDateRange?: { fromDate: Date; toDate: Date } | null;
}

const Calendar = ({ onDateSelect, onDateRangeSelect, selectedDate, selectedDateRange }: CalendarProps) => {
  const [currentDate, setCurrentDate] = useState(new Date());
  
  const [selectedSingleDate, setSelectedSingleDate] = useState<Date | null>(() => {
    if (!selectedDate) return null;
    const d = new Date(selectedDate);
    d.setHours(0, 0, 0, 0);
    return d;
  });

  const [dateRange, setDateRange] = useState<{ fromDate: Date; toDate: Date } | null>(() => {
    if (!selectedDateRange) return null;
    const from = new Date(selectedDateRange.fromDate);
    const to = new Date(selectedDateRange.toDate);
    from.setHours(0, 0, 0, 0);
    to.setHours(0, 0, 0, 0);
    return { fromDate: from, toDate: to };
  });

  const [isSelectingRange, setIsSelectingRange] = useState(false);

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    
    const startingDayOfWeek = firstDay.getDay();
    const adjustedStartDay = startingDayOfWeek === 0 ? 6 : startingDayOfWeek - 1;

    const days = [];
    
    const prevMonth = new Date(year, month - 1, 0);
    const daysInPrevMonth = prevMonth.getDate();
    for (let i = adjustedStartDay - 1; i >= 0; i--) {
      const d = new Date(year, month - 1, daysInPrevMonth - i);
      d.setHours(0, 0, 0, 0);
      days.push({ date: d, isCurrentMonth: false, isToday: false });
    }

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    for (let i = 1; i <= daysInMonth; i++) {
      const dayDate = new Date(year, month, i);
      dayDate.setHours(0, 0, 0, 0);
      days.push({
        date: dayDate,
        isCurrentMonth: true,
        isToday: dayDate.getTime() === today.getTime()
      });
    }

    // Días del mes siguiente para completar la cuadrícula de 6 filas (42 días)
    const remainingDays = 42 - days.length;
    for (let i = 1; i <= remainingDays; i++) {
      const d = new Date(year, month + 1, i);
      d.setHours(0, 0, 0, 0);
      days.push({ date: d, isCurrentMonth: false, isToday: false });
    }

    return days;
  };

  const handleDateClick = (date: Date) => {
    if (!date || !date.getTime()) return;
    
    // Normalizamos la fecha clickeada para ignorar horas/minutos/segundos
    const clickedDate = new Date(date);
    clickedDate.setHours(0, 0, 0, 0);
    
    if (isSelectingRange && dateRange?.fromDate) {
      let newRange;
      if (clickedDate >= dateRange.fromDate) {
        newRange = { fromDate: dateRange.fromDate, toDate: clickedDate };
      } else {
        newRange = { fromDate: clickedDate, toDate: dateRange.fromDate };
      }
      
      setDateRange(newRange);
      setIsSelectingRange(false);
      if (onDateRangeSelect) onDateRangeSelect(newRange.fromDate, newRange.toDate);
      
    } else {
      const newRange = { fromDate: clickedDate, toDate: clickedDate };
      setDateRange(newRange);
      setIsSelectingRange(true);
      setSelectedSingleDate(clickedDate);
      if (onDateSelect) onDateSelect(clickedDate);
    }
  };

  const isDateSelected = (date: Date) => {
    const dateTime = date.getTime();
    if (dateRange) {
      const fromTime = dateRange.fromDate.getTime();
      const toTime = dateRange.toDate.getTime();
      return dateTime >= fromTime && dateTime <= toTime;
    }
    if (selectedSingleDate) {
      return dateTime === selectedSingleDate.getTime();
    }
    return false;
  };

  const isRangeStart = (date: Date) => {
    if (!dateRange) return false;
    return date.getTime() === dateRange.fromDate.getTime();
  };

  const isRangeEnd = (date: Date) => {
    if (!dateRange) return false;
    return date.getTime() === dateRange.toDate.getTime();
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentDate);
    if (direction === 'prev') {
      newDate.setMonth(newDate.getMonth() - 1);
    } else {
      newDate.setMonth(newDate.getMonth() + 1);
    }
    setCurrentDate(newDate);
  };

  const formatMonthYear = (date: Date) => {
    return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  };

  const days = getDaysInMonth(currentDate);
  const dayNames = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'];

  return (
    <div className="bg-card border border-border rounded-lg p-6 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={() => navigateMonth('prev')}
          className="p-2 hover:bg-muted rounded-lg transition-colors"
          aria-label="Previous month"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>
        <h2 className="text-lg font-semibold text-foreground">
          {formatMonthYear(currentDate)}
        </h2>
        <button
          onClick={() => navigateMonth('next')}
          className="p-2 hover:bg-muted rounded-lg transition-colors"
          aria-label="Next month"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {/* Days of week */}
      <div className="grid grid-cols-7 gap-1 mb-2">
        {dayNames.map((day) => (
          <div key={day} className="text-center text-sm font-medium text-muted-foreground py-2">
            {day}
          </div>
        ))}
      </div>

      {/* Calendar grid */}
      <div className="grid grid-cols-7 gap-1">
        {days.map((day, index) => {
          const isSelected = isDateSelected(day.date);
          const isStart = isRangeStart(day.date);
          const isEnd = isRangeEnd(day.date);
          
          return (
            <button
              key={index}
              onClick={() => handleDateClick(day.date)}
              className={`
                relative h-10 w-full rounded-lg text-sm font-medium transition-colors
                ${!day.isCurrentMonth 
                  ? 'text-muted-foreground/40' 
                  : 'text-foreground hover:bg-muted'
                }
                ${isSelected 
                  ? isStart || isEnd
                    ? 'bg-primary text-primary-foreground shadow-sm'
                    : 'bg-primary/20 text-primary'
                  : ''
                }
                ${isYesterday(day.date) && !isSelected ? 'ring-2 ring-primary/50' : ''}
              `}
              disabled={!day.isCurrentMonth}
            >
              {day.date.getDate()}
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default Calendar;