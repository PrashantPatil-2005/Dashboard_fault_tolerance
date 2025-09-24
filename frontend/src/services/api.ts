import axios from 'axios';
import { Machine, Bearing, KPIStats, HourlyTrend, StatusTrend, Reading } from '../types';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Machine API calls
export const machineAPI = {
  // Get all machines
  getAllMachines: async (startDate?: string, endDate?: string): Promise<Machine[]> => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const qs = params.toString();
    const url = qs ? `/machines?${qs}` : '/machines';
    const response = await api.get(url);
    return response.data;
  },

  // Get machine by ID
  getMachineById: async (machineId: string): Promise<Machine> => {
    const response = await api.get(`/machines/${machineId}`);
    return response.data;
  },

  // Search machines with filters
  searchMachines: async (filters: {
    customer?: string;
    area?: string;
    subarea?: string;
    machine_name?: string;
    status?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<Machine[]> => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.append(key, value);
    });
    const response = await api.get(`/machines/search?${params.toString()}`);
    return response.data;
  },

  // Get bearings for a machine
  getBearings: async (machineId: string): Promise<Bearing[]> => {
    const response = await api.get(`/bearings?machine_id=${machineId}`);
    return response.data;
  },

  // Get latest readings for a machine
  getLatestReadings: async (machineId: string): Promise<Reading[]> => {
    const response = await api.get(`/machines/${machineId}/latest-readings`);
    return response.data;
  },

  // Get time series data for a machine
  getTimeSeries: async (
    machineId: string,
    bearingId: string,
    metric: string,
    startDate?: string,
    endDate?: string,
    limit: number = 1000
  ): Promise<{ timestamp: string; value: number }[]> => {
    const params = new URLSearchParams({
      bearing_id: bearingId,
      metric,
      limit: limit.toString(),
    });
    
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const response = await api.get(`/machines/${machineId}/timeseries?${params.toString()}`);
    return response.data;
  },
};

// Dashboard API calls
export const dashboardAPI = {
  // Get KPI statistics
  getKPIs: async (startDate?: string, endDate?: string): Promise<KPIStats> => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const response = await api.get(`/dashboard/kpis?${params.toString()}`);
    return response.data;
  },

  // Get hourly trends
  getHourlyTrends: async (startDate?: string, endDate?: string): Promise<HourlyTrend[]> => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const response = await api.get(`/dashboard/trends/hourly?${params.toString()}`);
    return response.data;
  },

  // Get status trends
  getStatusTrends: async (
    startDate?: string,
    endDate?: string,
    customer?: string
  ): Promise<StatusTrend[]> => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (customer) params.append('customer', customer);
    
    const response = await api.get(`/dashboard/trends/status?${params.toString()}`);
    return response.data;
  },
};

// Data API calls
export const dataAPI = {
  // Query sensor data
  queryData: async (filters: {
    bearing_id?: string;
    machine_id?: string;
    start_date?: string;
    end_date?: string;
    limit?: number;
  }): Promise<Reading[]> => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.append(key, value.toString());
    });
    
    const response = await api.get(`/data/query?${params.toString()}`);
    return response.data;
  },

  // Get FFT data for a reading
  getFFTData: async (readingId: string): Promise<{ fft_data: any }> => {
    const response = await api.get(`/readings/${readingId}/fft`);
    return response.data;
  },
};

// System API calls
export const systemAPI = {
  // Health check
  healthCheck: async (): Promise<{ status: string; timestamp: string }> => {
    const response = await api.get('/health');
    return response.data;
  },

  // Get system statistics
  getSystemStats: async (): Promise<{
    machines_count: number;
    bearings_count: number;
    data_records_count: number;
    database_name: string;
    timestamp: string;
  }> => {
    const response = await api.get('/stats');
    return response.data;
  },
};

export default api;
