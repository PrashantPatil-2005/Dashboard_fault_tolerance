import React, { useMemo, useState } from 'react';
import { Chart } from 'primereact/chart';
import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import { useDashboard } from '../../context/DashboardContext';

const HourlyTrendChart: React.FC = () => {
  const { state } = useDashboard();
  const [viewMode, setViewMode] = useState<'machines' | 'components'>('machines');

  const chartData = useMemo(() => {
    if (!state.hourlyTrends || state.hourlyTrends.length === 0) {
      return {
        labels: [],
        datasets: []
      };
    }

    // Sort hourly trends by hour
    const sortedTrends = [...state.hourlyTrends].sort((a, b) => a.hour - b.hour);

    const labels = sortedTrends.map(trend => {
      const hour = trend.hour;
      const timeString = hour < 10 ? `0${hour}:00` : `${hour}:00`;
      return timeString;
    });

    const data = sortedTrends.map(trend => trend.count);

    const dataset = {
      label: viewMode === 'machines' ? 'Machine Readings' : 'Component Readings',
      data,
      borderColor: '#2196F3',
      backgroundColor: 'rgba(33, 150, 243, 0.1)',
      borderWidth: 2,
      fill: true,
      tension: 0.4,
      pointBackgroundColor: '#2196F3',
      pointBorderColor: '#ffffff',
      pointBorderWidth: 2,
      pointRadius: 4,
      pointHoverRadius: 6,
    };

    return {
      labels,
      datasets: [dataset]
    };
  }, [state.hourlyTrends, viewMode]);

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
            return `Time: ${context[0].label}`;
          },
          label: (context: any) => {
            const value = context.parsed.y;
            return `${context.dataset.label}: ${value} readings`;
          }
        }
      }
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        ticks: {
          maxRotation: 45,
          minRotation: 0,
        }
      },
      y: {
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
        const time = chartData.labels[element.index];
        console.log('Clicked on time:', time, 'for', viewMode);
        // TODO: Implement click functionality to show detailed view
      }
    }
  };

  const handleViewToggle = () => {
    setViewMode(prev => prev === 'machines' ? 'components' : 'machines');
  };

  return (
    <Card className="h-full">
      <div className="flex justify-content-between align-items-center mb-3">
        <div>
          <h3 className="text-lg font-semibold text-900 m-0">Hourly Reading Trends</h3>
          <p className="text-600 text-sm m-0 mt-1">
            {viewMode === 'machines' 
              ? 'Machine readings per hour for selected date'
              : 'Component readings per hour for selected date'
            }
          </p>
        </div>
        <Button
          label={viewMode === 'machines' ? 'View Components' : 'View Machines'}
          icon="pi pi-refresh"
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
              <i className="pi pi-chart-line text-4xl text-400 mb-3" />
              <h4 className="text-900 mb-2">No Data Available</h4>
              <p className="text-600">No hourly trend data for the selected date</p>
            </div>
          </div>
        ) : (
          <Chart
            type="line"
            data={chartData}
            options={chartOptions}
            style={{ height: '100%' }}
          />
        )}
      </div>
    </Card>
  );
};

export default HourlyTrendChart;
