import React, { useMemo } from 'react';
import { Chart } from 'primereact/chart';
import { Card } from 'primereact/card';
import { useDashboard } from '../../context/DashboardContext';
import { STATUS_COLORS } from '../../constants/colors';
import { format, parseISO } from 'date-fns';

const CustomerTrendChart: React.FC = () => {
  const { state } = useDashboard();

  const chartData = useMemo(() => {
    if (!state.statusTrends || state.statusTrends.length === 0) {
      return {
        labels: [],
        datasets: []
      };
    }

    // Group data by customer and date
    const customerData = new Map<string, Map<string, any>>();
    
    // First, collect all unique customers from machines
    const customers = [...new Set(state.machines.map(m => m.customer))];
    
    // Initialize customer data structure
    customers.forEach(customer => {
      customerData.set(customer, new Map());
    });

    // Process status trends to group by customer
    // Note: This is a simplified approach since the API doesn't directly provide customer trends
    // In a real implementation, you might need a separate API endpoint for customer trends
    state.statusTrends.forEach(trend => {
      const date = format(parseISO(trend.date), 'MMM dd');
      
      // For now, we'll distribute the total counts across customers
      // This is a placeholder - in reality, you'd want customer-specific trend data
      customers.forEach((customer, index) => {
        if (!customerData.get(customer)!.has(date)) {
          customerData.get(customer)!.set(date, {
            Normal: 0,
            Satisfactory: 0,
            Alert: 0,
            Unacceptable: 0
          });
        }
        
        const customerTrend = customerData.get(customer)!.get(date);
        const totalForDate = Object.values(trend.status_counts).reduce((sum, count) => sum + count, 0);
        const customerShare = totalForDate / customers.length; // Simplified distribution
        
        Object.entries(trend.status_counts).forEach(([status, count]) => {
          customerTrend[status] += Math.round((count / customers.length) * (index + 1));
        });
      });
    });

    // Get all unique dates
    const allDates = [...new Set(state.statusTrends.map(trend => format(parseISO(trend.date), 'MMM dd')))];
    allDates.sort((a, b) => new Date(a).getTime() - new Date(b).getTime());

    // Create datasets for each customer
    const datasets = customers.map((customer, index) => {
      const customerTrends = customerData.get(customer)!;
      const data = allDates.map(date => {
        const trend = customerTrends.get(date);
        if (!trend) return 0;
        return Object.values(trend).reduce((sum, count) => sum + count, 0);
      });

      return {
        label: customer,
        data,
        backgroundColor: `hsl(${(index * 137.5) % 360}, 70%, 60%)`,
        borderColor: `hsl(${(index * 137.5) % 360}, 70%, 50%)`,
        borderWidth: 1,
      };
    });

    return {
      labels: allDates,
      datasets
    };
  }, [state.statusTrends, state.machines]);

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
            return `${label}: ${value} machines`;
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
        const datasetLabel = chartData.datasets[element.datasetIndex].label;
        console.log('Clicked on:', label, 'for customer:', datasetLabel);
        // TODO: Implement click functionality to show detailed view
      }
    }
  };

  return (
    <Card className="h-full">
      <div className="mb-3">
        <h3 className="text-lg font-semibold text-900 m-0">Customer Machine Trends</h3>
        <p className="text-600 text-sm m-0 mt-1">
          Machine distribution by customer over time
        </p>
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
              <p className="text-600">No customer trend data for the selected period</p>
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

export default CustomerTrendChart;
