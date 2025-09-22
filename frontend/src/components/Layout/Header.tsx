import React from 'react';
import { Calendar } from 'primereact/calendar';
import { Card } from 'primereact/card';
import { useDashboard } from '../../context/DashboardContext';
import { format } from 'date-fns';

const Header: React.FC = () => {
  const { state, actions } = useDashboard();

  const handleDateChange = (date: Date | Date[] | null) => {
    if (date && !Array.isArray(date)) {
      actions.setSelectedDate(date);
    }
  };

  return (
    <Card>
      <div className="flex justify-content-between align-items-center">
        <div>
          <h1 className="text-3xl font-bold text-900 m-0">Factory Monitoring Dashboard</h1>
          <p className="text-600 m-0 mt-2 text-lg">
            Real-time monitoring of industrial machines and equipment
          </p>
        </div>
        
        <div className="flex align-items-center gap-3">
          <label htmlFor="date-filter" className="font-semibold text-900 text-lg">
            Select Date:
          </label>
          <Calendar
            id="date-filter"
            value={state.selectedDate}
            onChange={(e) => handleDateChange(e.value)}
            view="month"
            dateFormat="mm/yy"
            showIcon
            icon="pi pi-calendar"
            className="w-14rem"
            placeholder="Select Month"
            showButtonBar
            showOnFocus={false}
          />
        </div>
      </div>
    </Card>
  );
};

export default Header;
