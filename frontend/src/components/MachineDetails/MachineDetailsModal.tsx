import React, { useState, useEffect } from 'react';
import { Dialog } from 'primereact/dialog';
import { Card } from 'primereact/card';
import { Tag } from 'primereact/tag';
import { Button } from 'primereact/button';
import { ProgressSpinner } from 'primereact/progressspinner';
import { Chart } from 'primereact/chart';
import { useDashboard } from '../../context/DashboardContext';
import { Machine, Bearing, Reading } from '../../types';
import { STATUS_COLORS } from '../../constants/colors';
import { machineAPI } from '../../services/api';

interface MachineDetailsModalProps {
  machine: Machine | null;
  visible: boolean;
  onHide: () => void;
}

const MachineDetailsModal: React.FC<MachineDetailsModalProps> = ({
  machine,
  visible,
  onHide
}) => {
  const [bearings, setBearings] = useState<Bearing[]>([]);
  const [latestReadings, setLatestReadings] = useState<Reading[]>([]);
  const [timeSeriesData, setTimeSeriesData] = useState<any[]>([]);
  const [fftData, setFftData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedBearing, setSelectedBearing] = useState<string | null>(null);

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

  // Load machine details when modal opens
  useEffect(() => {
    if (machine && visible) {
      loadMachineDetails();
    }
  }, [machine, visible]);

  const loadMachineDetails = async () => {
    if (!machine) return;

    setLoading(true);
    try {
      // Load bearings and latest readings
      const [bearingsData, readingsData] = await Promise.all([
        machineAPI.getBearings(machine._id),
        machineAPI.getLatestReadings(machine._id)
      ]);

      setBearings(bearingsData);
      setLatestReadings(readingsData);

      // Set first bearing as selected for charts
      if (bearingsData.length > 0) {
        setSelectedBearing(bearingsData[0]._id);
        loadChartData(bearingsData[0]._id);
      }
    } catch (error) {
      console.error('Error loading machine details:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadChartData = async (bearingId: string) => {
    if (!machine) return;

    try {
      // Load time series data for the selected bearing
      const timeSeries = await machineAPI.getTimeSeries(
        machine._id,
        bearingId,
        'acceleration',
        undefined,
        undefined,
        100
      );

      setTimeSeriesData(timeSeries);

      // Mock FFT data (replace with real API call when available)
      const mockFftData = generateMockFFTData();
      setFftData(mockFftData);
    } catch (error) {
      console.error('Error loading chart data:', error);
    }
  };

  const generateMockFFTData = () => {
    // Generate mock FFT data for demonstration
    const frequencies = Array.from({ length: 50 }, (_, i) => i * 0.5);
    const amplitudes = frequencies.map(freq => 
      Math.exp(-freq / 10) * (1 + 0.5 * Math.sin(freq * 2))
    );
    
    return {
      frequencies,
      amplitudes,
      dominantFrequency: frequencies[amplitudes.indexOf(Math.max(...amplitudes))]
    };
  };

  const handleBearingSelect = (bearingId: string) => {
    setSelectedBearing(bearingId);
    loadChartData(bearingId);
  };

  // Chart configurations
  const trendChartData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Machine Status Trend',
        data: [65, 59, 80, 81, 56, 55, 40],
        borderColor: '#2196F3',
        backgroundColor: 'rgba(33, 150, 243, 0.1)',
        tension: 0.4
      }
    ]
  };

  const timeSeriesChartData = {
    labels: timeSeriesData.map(point => new Date(point.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: 'Acceleration RMS',
        data: timeSeriesData.map(point => point.value),
        borderColor: '#4CAF50',
        backgroundColor: 'rgba(76, 175, 80, 0.1)',
        tension: 0.4
      }
    ]
  };

  const fftChartData = {
    labels: fftData.frequencies?.map(f => f.toFixed(1)) || [],
    datasets: [
      {
        label: 'FFT Amplitude',
        data: fftData.amplitudes || [],
        borderColor: '#FF9800',
        backgroundColor: 'rgba(255, 152, 0, 0.1)',
        tension: 0.4
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: false,
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0,0,0,0.1)',
        }
      },
      x: {
        grid: {
          display: false,
        }
      }
    }
  };

  if (!machine) return null;

  return (
    <Dialog
      header={
        <div className="flex align-items-center gap-3">
          <i className="pi pi-cog text-2xl text-primary"></i>
          <div>
            <h2 className="text-2xl font-bold text-900 m-0">{machine.machineName}</h2>
            <p className="text-600 text-sm m-0 mt-1">
              {machine.customer} • {machine.area} • {machine.subarea}
            </p>
          </div>
        </div>
      }
      visible={visible}
      onHide={onHide}
      style={{ width: '90vw', height: '90vh' }}
      maximizable
      modal
      className="p-fluid"
    >
      <div className="h-full overflow-auto">
        {loading ? (
          <div className="flex align-items-center justify-content-center h-20rem">
            <ProgressSpinner />
          </div>
        ) : (
          <div className="grid">
            {/* Machine Status */}
            <div className="col-12">
              <Card className="mb-3">
                <div className="flex justify-content-between align-items-center">
                  <div>
                    <h3 className="text-lg font-semibold text-900 m-0">Machine Status</h3>
                    <p className="text-600 text-sm m-0 mt-1">Current operational status</p>
                  </div>
                  <Tag
                    value={machine.status}
                    icon={getStatusIcon(machine.status)}
                    style={{ 
                      backgroundColor: getStatusColor(machine.status),
                      color: 'white',
                      border: 'none'
                    }}
                  />
                </div>
              </Card>
            </div>

            {/* Real Time Values - Bearing Details */}
            <div className="col-12">
              <Card className="mb-3">
                <div className="mb-3">
                  <h3 className="text-lg font-semibold text-900 m-0">Real Time Values</h3>
                  <p className="text-600 text-sm m-0 mt-1">Current bearing sensor readings</p>
                </div>
                
                <div className="grid">
                  {bearings.map((bearing) => {
                    const reading = latestReadings.find(r => r.bearingId === bearing._id);
                    return (
                      <div key={bearing._id} className="col-12 md:col-6 lg:col-4">
                        <Card 
                          className={`cursor-pointer transition-colors ${
                            selectedBearing === bearing._id ? 'border-primary' : ''
                          }`}
                          onClick={() => handleBearingSelect(bearing._id)}
                        >
                          <div className="text-center">
                            <h4 className="text-900 font-semibold mb-2">{bearing.bearingLocation}</h4>
                            <Tag
                              value={bearing.status}
                              icon={getStatusIcon(bearing.status)}
                              style={{ 
                                backgroundColor: getStatusColor(bearing.status),
                                color: 'white',
                                border: 'none'
                              }}
                            />
                            
                            {reading && (
                              <div className="mt-3">
                                <div className="grid text-sm">
                                  <div className="col-6">
                                    <div className="text-600">Temperature</div>
                                    <div className="font-semibold">
                                      {reading.temperature ? `${reading.temperature}°C` : 'N/A'}
                                    </div>
                                  </div>
                                  <div className="col-6">
                                    <div className="text-600">Acceleration</div>
                                    <div className="font-semibold">
                                      {reading.acceleration?.rms ? `${reading.acceleration.rms.toFixed(2)}` : 'N/A'}
                                    </div>
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>
                        </Card>
                      </div>
                    );
                  })}
                </div>
              </Card>
            </div>

            {/* Chart 1: Trend Chart */}
            <div className="col-12">
              <Card className="mb-3">
                <div className="mb-3">
                  <h3 className="text-lg font-semibold text-900 m-0">Trend Analysis</h3>
                  <p className="text-600 text-sm m-0 mt-1">Machine performance trend over time</p>
                </div>
                <div style={{ height: '300px' }}>
                  <Chart
                    type="line"
                    data={trendChartData}
                    options={chartOptions}
                    style={{ height: '100%' }}
                  />
                </div>
              </Card>
            </div>

            {/* Chart 2: Time Series Chart */}
            <div className="col-12">
              <Card className="mb-3">
                <div className="mb-3">
                  <h3 className="text-lg font-semibold text-900 m-0">Time Series Analysis</h3>
                  <p className="text-600 text-sm m-0 mt-1">
                    Real-time sensor data for selected bearing
                    {selectedBearing && (
                      <span className="ml-2 text-primary">
                        ({bearings.find(b => b._id === selectedBearing)?.bearingLocation})
                      </span>
                    )}
                  </p>
                </div>
                <div style={{ height: '300px' }}>
                  <Chart
                    type="line"
                    data={timeSeriesChartData}
                    options={chartOptions}
                    style={{ height: '100%' }}
                  />
                </div>
              </Card>
            </div>

            {/* Chart 3: FFT Chart */}
            <div className="col-12">
              <Card className="mb-3">
                <div className="mb-3">
                  <h3 className="text-lg font-semibold text-900 m-0">FFT Analysis</h3>
                  <p className="text-600 text-sm m-0 mt-1">
                    Frequency domain analysis
                    {fftData.dominantFrequency && (
                      <span className="ml-2 text-primary">
                        (Dominant: {fftData.dominantFrequency.toFixed(2)} Hz)
                      </span>
                    )}
                  </p>
                </div>
                <div style={{ height: '300px' }}>
                  <Chart
                    type="line"
                    data={fftChartData}
                    options={chartOptions}
                    style={{ height: '100%' }}
                  />
                </div>
              </Card>
            </div>
          </div>
        )}
      </div>
    </Dialog>
  );
};

export default MachineDetailsModal;
