import React, { useMemo } from 'react';
import { Chart } from 'primereact/chart';
import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import { useDashboard } from '../../context/DashboardContext';
import { STATUS_COLORS } from '../../constants/colors';
import { format, parseISO } from 'date-fns';

const StatusTrendChart: React.FC = () => {
  const { state } = useDashboard();
  const [viewMode, setViewMode] = React.useState<'monthly' | 'weekly'>('monthly');

  const chartData = useMemo(() => {
    if (!state.statusTrends || state.statusTrends.length === 0) {
      return {
        labels: [],
        datasets: []
      };
    }

    // Sort trends by date
    const sortedTrends = [...state.statusTrends].sort((a, b) => 
      new Date(a.date).getTime() - new Date(b.date).getTime()
    );

    let labels: string[] = [];
    let data: any[] = [];

    if (viewMode === 'monthly') {
      // Show all dates in the month
      labels = sortedTrends.map(trend => format(parseISO(trend.date), 'MMM dd'));
      data = sortedTrends;
    } else {
      // Group by weeks
      const weeklyData = new Map<string, any>();
      
      sortedTrends.forEach(trend => {
        const date = parseISO(trend.date);
        const weekStart = format(date, 'MMM dd');
        const weekKey = `Week of ${weekStart}`;
        
        if (!weeklyData.has(weekKey)) {
          weeklyData.set(weekKey, {
            Normal: 0,
            Satisfactory: 0,
            Alert: 0,
            Unacceptable: 0
          });
        }
        
        const weekData = weeklyData.get(weekKey);
        Object.entries(trend.status_counts).forEach(([status, count]) => {
          weekData[status] += count;
        });
      });
      
      labels = Array.from(weeklyData.keys());
      data = Array.from(weeklyData.values());
    }

    const statuses = ['Normal', 'Satisfactory', 'Alert', 'Unacceptable'];
    
    const datasets = statuses.map(status => ({
      label: status,
      data: data.map(item => item[status] || 0),
      backgroundColor: STATUS_COLORS[status as keyof typeof STATUS_COLORS],
      borderColor: STATUS_COLORS[status as keyof typeof STATUS_COLORS],
      borderWidth: 1,
    }));

    return {
      labels,
      datasets
    };
  }, [state.statusTrends, viewMode]);

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          padding: 20,
        }
      },
      title: {
        display: false,
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
        callbacks: {
          title: (context: any) => {
            return context[0].label;
          },
          label: (context: any) => {
            const label = context.dataset.label || '';
            const value = context.parsed.y;
            const total = context.dataset.data.reduce((sum: number, val: number) => sum + val, 0);
            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : '0';
            return `${label}: ${value} machines (${percentage}%)`;
          }
        }
      }
    },
    scales: {
      x: {
        stacked: true,
        grid: {
          display: false,
        },
        ticks: {
          maxRotation: 45,
          minRotation: 0,
        }
      },
      y: {
        stacked: true,
        beginAtZero: true,
        ticks: {
          stepSize: 1,
        },
        grid: {
          color: 'rgba(0,0,0,0.1)',
        }
      }
    },
    onClick: (event: any, elements: any) => {
      if (elements.length > 0) {
        const element = elements[0];
        const label = chartData.labels[element.index];
        console.log('Clicked on:', label, 'in', viewMode, 'view');
        // TODO: Implement click functionality to show detailed view
      }
    }
  };

  const handleViewToggle = () => {
    setViewMode(prev => prev === 'monthly' ? 'weekly' : 'monthly');
  };

  return (
    <Card className="h-full">
      <div className="flex justify-content-between align-items-center mb-3">
        <div>
          <h3 className="text-lg font-semibold text-900 m-0">Machine Status Trends</h3>
          <p className="text-600 text-sm m-0 mt-1">
            {viewMode === 'monthly' ? 'Daily status distribution' : 'Weekly status distribution'}
          </p>
        </div>
        <Button
          label={viewMode === 'monthly' ? 'Weekly View' : 'Monthly View'}
          icon="pi pi-calendar"
          size="small"
          className="p-button-outlined"
          onClick={handleViewToggle}
        />
      </div>
      
      <div style={{ height: '300px' }}>
        {state.loading ? (
          <div className="flex align-items-center justify-content-center h-full">
            <i className="pi pi-spin pi-spinner text-2xl text-400" />
          </div>
        ) : chartData.labels.length === 0 ? (
          <div className="flex align-items-center justify-content-center h-full">
            <div className="text-center">
              <i className="pi pi-chart-bar text-4xl text-400 mb-3" />
              <h4 className="text-900 mb-2">No Data Available</h4>
              <p className="text-600">No status trend data for the selected period</p>
            </div>
          </div>
        ) : (
          <Chart
            type="bar"
            data={chartData}
            options={chartOptions}
            style={{ height: '100%' }}
          />
        )}
      </div>
    </Card>
  );
};

export default StatusTrendChart;
