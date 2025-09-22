// API Response Types
export interface Machine {
  _id: string;
  machineName: string;
  customer: string;
  area: string;
  subarea: string;
  machineType?: string;
  status: 'Normal' | 'Satisfactory' | 'Alert' | 'Unacceptable';
  ingestedDate?: string;
}

export interface Bearing {
  _id: string;
  machineId: string;
  bearingLocation: string;
  bearingType?: string;
  position?: string;
  status: 'Normal' | 'Satisfactory' | 'Alert' | 'Unacceptable';
}

export interface Reading {
  _id: string;
  machineId: string;
  bearingId: string;
  timestamp: string;
  status: 'Normal' | 'Satisfactory' | 'Alert' | 'Unacceptable';
  Axis_Id: string;
  acceleration?: {
    rms?: number;
    peak?: number;
    crestFactor?: number;
    kurtosis?: number;
  };
  velocity?: {
    rms?: number;
    peak?: number;
    crestFactor?: number;
  };
  temperature?: number;
  fftData?: {
    frequencies: number[];
    amplitudes: number[];
    dominantFrequency?: number;
  };
}

export interface KPIStats {
  total_readings: number;
  status_counts: {
    Normal: number;
    Satisfactory: number;
    Alert: number;
    Unacceptable: number;
  };
}

export interface HourlyTrend {
  hour: number;
  count: number;
}

export interface StatusTrend {
  date: string;
  status_counts: {
    Normal: number;
    Satisfactory: number;
    Alert: number;
    Unacceptable: number;
  };
}

// Dashboard State Types
export interface DashboardState {
  selectedDate: Date;
  machines: Machine[];
  filteredMachines: Machine[];
  kpiStats: KPIStats | null;
  statusTrends: StatusTrend[];
  hourlyTrends: HourlyTrend[];
  loading: boolean;
  error: string | null;
  searchFilters: {
    customer: string;
    area: string;
    subarea: string;
    machineName: string;
    status: string;
  };
}

// Chart Data Types
export interface ChartDataPoint {
  x: string | number;
  y: number;
}

export interface StatusChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor: string;
    borderColor: string;
  }[];
}

export interface CustomerChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor: string;
    borderColor: string;
  }[];
}

export interface HourlyChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    borderColor: string;
    backgroundColor: string;
    fill: boolean;
  }[];
}
