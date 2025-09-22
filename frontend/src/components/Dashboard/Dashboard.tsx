import React, { useEffect } from 'react';
import { useDashboard } from '../../context/DashboardContext';
import Header from '../Layout/Header';
import KPICards from './KPICards';
import SearchFilters from './SearchFilters';
import MachineTable from './MachineTable';
import StatusTrendChart from '../Charts/StatusTrendChart';
import CustomerTrendChart from '../Charts/CustomerTrendChart';
import HourlyTrendChart from '../Charts/HourlyTrendChart';
import { Toast } from 'primereact/toast';
import { useRef } from 'react';

const Dashboard: React.FC = () => {
  const { state, actions } = useDashboard();
  const toast = useRef<Toast>(null);

  // Load initial data when component mounts
  useEffect(() => {
    actions.loadDashboardData(state.selectedDate);
  }, []);

  // Show error toast when there's an error
  useEffect(() => {
    if (state.error) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: state.error,
        life: 5000,
      });
    }
  }, [state.error]);

  return (
    <div className="p-4" style={{ minHeight: '100vh', backgroundColor: '#f8f9fa' }}>
      <Toast ref={toast} />
      
      {/* Header with Date Filter */}
      <div className="mb-4">
        <Header />
      </div>
      
      {/* KPI Cards */}
      <div className="mb-4">
        <KPICards />
      </div>
      
      {/* Search and Filters */}
      <div className="mb-4">
        <SearchFilters />
      </div>
      
      {/* Machine Data Table */}
      <div className="mb-4">
        <MachineTable />
      </div>
      
      {/* Charts Section */}
      <div className="grid">
        {/* Status Trend Chart */}
        <div className="col-12 lg:col-6 mb-4">
          <StatusTrendChart />
        </div>
        
        {/* Customer Trend Chart */}
        <div className="col-12 lg:col-6 mb-4">
          <CustomerTrendChart />
        </div>
        
        {/* Hourly Trend Chart - Full Width */}
        <div className="col-12">
          <HourlyTrendChart />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
