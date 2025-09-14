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
  const [selectedSingleDate, setSelectedSingleDate] = useState<Date | null>(
    selectedDate || null
  );
  const [dateRange, setDateRange] = useState<{ fromDate: Date; toDate: Date } | null>(
    selectedDateRange || null
  );
  const [isSelectingRange, setIsSelectingRange] = useState(false);

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days = [];
    
    // Add days from previous month
    const prevMonth = new Date(year, month - 1, 0);
    const daysInPrevMonth = prevMonth.getDate();
    for (let i = startingDayOfWeek - 1; i >= 0; i--) {
      days.push({
        date: new Date(year, month - 1, daysInPrevMonth - i),
        isCurrentMonth: false,
        isToday: false
      });
    }

    // Add days from current month
    for (let i = 1; i <= daysInMonth; i++) {
      const dayDate = new Date(year, month, i);
      days.push({
        date: dayDate,
        isCurrentMonth: true,
        isToday: dayDate.toDateString() === new Date().toDateString()
      });
    }

    // Add days from next month
    const remainingDays = 42 - days.length; // 6 rows * 7 days
    for (let i = 1; i <= remainingDays; i++) {
      days.push({
        date: new Date(year, month + 1, i),
        isCurrentMonth: false,
        isToday: false
      });
    }

    return days;
  };

  const handleDateClick = (date: Date) => {
    if (!date || !date.getTime()) return;
    
    const clickedDate = new Date(date);
    
    if (isSelectingRange) {
      // Second click - complete the range
      if (dateRange?.fromDate && clickedDate >= dateRange.fromDate) {
        const newRange = { fromDate: dateRange.fromDate, toDate: clickedDate };
        setDateRange(newRange);
        setIsSelectingRange(false);
        
        if (onDateRangeSelect) {
          onDateRangeSelect(newRange.fromDate, newRange.toDate);
        }
      } else if (dateRange?.fromDate && clickedDate < dateRange.fromDate) {
        // If second date is before first, swap them
        const newRange = { fromDate: clickedDate, toDate: dateRange.fromDate };
        setDateRange(newRange);
        setIsSelectingRange(false);
        
        if (onDateRangeSelect) {
          onDateRangeSelect(newRange.fromDate, newRange.toDate);
        }
      }
    } else {
      // First click - start range selection
      setDateRange({ fromDate: clickedDate, toDate: clickedDate });
      setIsSelectingRange(true);
      setSelectedSingleDate(clickedDate);
      
      if (onDateSelect) {
        onDateSelect(clickedDate);
      }
    }
  };

  const isDateSelected = (date: Date) => {
    if (dateRange) {
      const dateTime = date.getTime();
      const fromTime = dateRange.fromDate.getTime();
      const toTime = dateRange.toDate.getTime();
      return dateTime >= fromTime && dateTime <= toTime;
    }
    if (selectedSingleDate) {
      return date.toDateString() === selectedSingleDate.toDateString();
    }
    return false;
  };

  const isRangeStart = (date: Date) => {
    if (!dateRange) return false;
    return date.toDateString() === dateRange.fromDate.toDateString();
  };

  const isRangeEnd = (date: Date) => {
    if (!dateRange) return false;
    return date.toDateString() === dateRange.toDate.toDateString();
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
  const dayNames = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'];

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