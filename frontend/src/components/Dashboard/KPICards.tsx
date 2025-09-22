import React from 'react';
import { Card } from 'primereact/card';
import { Skeleton } from 'primereact/skeleton';
import { useDashboard } from '../../context/DashboardContext';
import { STATUS_COLORS } from '../../constants/colors';

const KPICards: React.FC = () => {
  const { state } = useDashboard();
  const { kpiStats, filteredMachines, loading } = state;

  // Calculate total machines from filtered results
  const totalMachines = filteredMachines.length;

  // Calculate status counts from filtered machines
  const statusCounts = filteredMachines.reduce((acc, machine) => {
    acc[machine.status] = (acc[machine.status] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const getStatusColor = (status: string) => {
    return STATUS_COLORS[status as keyof typeof STATUS_COLORS] || '#6c757d';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Normal':
        return 'pi pi-check-circle';
      case 'Satisfactory':
        return 'pi pi-info-circle';
      case 'Alert':
        return 'pi pi-exclamation-triangle';
      case 'Unacceptable':
        return 'pi pi-times-circle';
      default:
        return 'pi pi-question-circle';
    }
  };

  if (loading) {
    return (
      <div className="grid">
        <div className="col-12 md:col-6 lg:col-3">
          <Card className="h-full">
            <div className="text-center">
              <Skeleton width="100%" height="2rem" className="mb-2" />
              <Skeleton width="60%" height="3rem" className="mx-auto" />
            </div>
          </Card>
        </div>
        <div className="col-12 md:col-6 lg:col-9">
          <Card className="h-full">
            <Skeleton width="100%" height="8rem" />
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="grid mb-4">
      {/* Total Machines Card */}
      <div className="col-12 md:col-6 lg:col-4">
        <Card className="h-full">
          <div className="text-center p-4">
            <div className="text-600 text-sm font-medium mb-3">Total Machines</div>
            <div className="text-4xl font-bold text-900 mb-2">{totalMachines}</div>
            <div className="text-500 text-sm">
              {filteredMachines.length === state.machines.length 
                ? 'All machines' 
                : `${filteredMachines.length} of ${state.machines.length} machines`
              }
            </div>
          </div>
        </Card>
      </div>

      {/* Status Breakdown Card */}
      <div className="col-12 md:col-6 lg:col-8">
        <Card className="h-full">
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-900 m-0">Machine Status Breakdown</h3>
            <p className="text-600 text-sm m-0 mt-1">Distribution of machines by status</p>
          </div>
          
          <div className="grid">
            {['Normal', 'Satisfactory', 'Alert', 'Unacceptable'].map((status) => {
              const count = statusCounts[status] || 0;
              const percentage = totalMachines > 0 ? ((count / totalMachines) * 100).toFixed(1) : '0';
              
              return (
                <div key={status} className="col-12 sm:col-6 lg:col-3">
                  <div className="flex align-items-center gap-3 p-3 border-round mb-2" 
                       style={{ backgroundColor: `${getStatusColor(status)}15` }}>
                    <i 
                      className={`${getStatusIcon(status)} text-2xl`}
                      style={{ color: getStatusColor(status) }}
                    />
                    <div className="flex-1">
                      <div className="font-semibold text-900">{status}</div>
                      <div className="text-600 text-sm">
                        {count} machines ({percentage}%)
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default KPICards;
