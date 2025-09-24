import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { DashboardState, Machine, KPIStats, StatusTrend, HourlyTrend } from '../types';
import { machineAPI, dashboardAPI } from '../services/api';
import { format, startOfMonth, endOfMonth } from 'date-fns';

// Action types
type DashboardAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_SELECTED_DATE'; payload: Date }
  | { type: 'SET_MACHINES'; payload: Machine[] }
  | { type: 'SET_FILTERED_MACHINES'; payload: Machine[] }
  | { type: 'SET_KPI_STATS'; payload: KPIStats | null }
  | { type: 'SET_STATUS_TRENDS'; payload: StatusTrend[] }
  | { type: 'SET_HOURLY_TRENDS'; payload: HourlyTrend[] }
  | { type: 'SET_SEARCH_FILTERS'; payload: Partial<DashboardState['searchFilters']> }
  | { type: 'CLEAR_FILTERS' }
  | { type: 'RESET_DASHBOARD' };

// Initial state
const initialState: DashboardState = {
  selectedDate: new Date(),
  machines: [],
  filteredMachines: [],
  kpiStats: null,
  statusTrends: [],
  hourlyTrends: [],
  loading: false,
  error: null,
  searchFilters: {
    customer: '',
    area: '',
    subarea: '',
    machineName: '',
    status: '',
  },
};

// Reducer function
function dashboardReducer(state: DashboardState, action: DashboardAction): DashboardState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false };
    
    case 'SET_SELECTED_DATE':
      return { ...state, selectedDate: action.payload };
    
    case 'SET_MACHINES':
      return { ...state, machines: action.payload, filteredMachines: action.payload };
    
    case 'SET_FILTERED_MACHINES':
      return { ...state, filteredMachines: action.payload };
    
    case 'SET_KPI_STATS':
      return { ...state, kpiStats: action.payload };
    
    case 'SET_STATUS_TRENDS':
      return { ...state, statusTrends: action.payload };
    
    case 'SET_HOURLY_TRENDS':
      return { ...state, hourlyTrends: action.payload };
    
    case 'SET_SEARCH_FILTERS':
      return { 
        ...state, 
        searchFilters: { ...state.searchFilters, ...action.payload }
      };
    
    case 'CLEAR_FILTERS':
      return { 
        ...state, 
        searchFilters: initialState.searchFilters,
        filteredMachines: state.machines
      };
    
    case 'RESET_DASHBOARD':
      return initialState;
    
    default:
      return state;
  }
}

// Context
const DashboardContext = createContext<{
  state: DashboardState;
  dispatch: React.Dispatch<DashboardAction>;
  actions: {
    loadDashboardData: (date: Date) => Promise<void>;
    searchMachines: (filters: Partial<DashboardState['searchFilters']>) => Promise<void>;
    clearFilters: () => void;
    setSelectedDate: (date: Date) => void;
  };
} | null>(null);

// Provider component
export function DashboardProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(dashboardReducer, initialState);

  // Action creators
  const loadDashboardData = async (date: Date) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'SET_ERROR', payload: null });

      const startDate = format(startOfMonth(date), 'yyyy-MM-dd');
      const endDate = format(endOfMonth(date), 'yyyy-MM-dd');

      // Load all data in parallel
      const [machines, kpiStats, statusTrends, hourlyTrends] = await Promise.all([
        machineAPI.getAllMachines(startDate, endDate),
        dashboardAPI.getKPIs(startDate, endDate),
        dashboardAPI.getStatusTrends(startDate, endDate),
        dashboardAPI.getHourlyTrends(startDate, endDate),
      ]);

      dispatch({ type: 'SET_MACHINES', payload: machines });
      dispatch({ type: 'SET_KPI_STATS', payload: kpiStats });
      dispatch({ type: 'SET_STATUS_TRENDS', payload: statusTrends });
      dispatch({ type: 'SET_HOURLY_TRENDS', payload: hourlyTrends });
      dispatch({ type: 'SET_LOADING', payload: false });
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      dispatch({ 
        type: 'SET_ERROR', 
        payload: error instanceof Error ? error.message : 'Failed to load dashboard data'
      });
    }
  };

  const searchMachines = async (filters: Partial<DashboardState['searchFilters']>) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'SET_SEARCH_FILTERS', payload: filters });

      // Try backend search first
      try {
        const searchParams = Object.entries(filters).reduce((acc, [key, value]) => {
          if (value) {
            acc[key === 'machineName' ? 'machine_name' : key] = value;
          }
          return acc;
        }, {} as Record<string, string>);

        const filteredMachines = await machineAPI.searchMachines({
          ...searchParams,
          start_date: format(startOfMonth(state.selectedDate), 'yyyy-MM-dd'),
          end_date: format(endOfMonth(state.selectedDate), 'yyyy-MM-dd'),
        });
        dispatch({ type: 'SET_FILTERED_MACHINES', payload: filteredMachines });
      } catch (backendError) {
        console.warn('Backend search failed, using client-side filtering:', backendError);
        
        // Fallback to client-side filtering
        const clientFilteredMachines = state.machines.filter(machine => {
          const matchesSearch = !filters.machineName || 
            machine.machineName.toLowerCase().includes(filters.machineName.toLowerCase()) ||
            machine._id.toLowerCase().includes(filters.machineName.toLowerCase());
          
          const matchesCustomer = !filters.customer || machine.customer === filters.customer;
          const matchesArea = !filters.area || machine.area === filters.area;
          const matchesSubarea = !filters.subarea || machine.subarea === filters.subarea;
          const matchesStatus = !filters.status || machine.status === filters.status;
          
          return matchesSearch && matchesCustomer && matchesArea && matchesSubarea && matchesStatus;
        });
        
        dispatch({ type: 'SET_FILTERED_MACHINES', payload: clientFilteredMachines });
      }
      
      dispatch({ type: 'SET_LOADING', payload: false });
    } catch (error) {
      console.error('Error searching machines:', error);
      dispatch({ 
        type: 'SET_ERROR', 
        payload: error instanceof Error ? error.message : 'Failed to search machines'
      });
    }
  };

  const clearFilters = () => {
    dispatch({ type: 'CLEAR_FILTERS' });
  };

  const setSelectedDate = (date: Date) => {
    dispatch({ type: 'SET_SELECTED_DATE', payload: date });
    loadDashboardData(date);
  };

  const actions = {
    loadDashboardData,
    searchMachines,
    clearFilters,
    setSelectedDate,
  };

  return (
    <DashboardContext.Provider value={{ state, dispatch, actions }}>
      {children}
    </DashboardContext.Provider>
  );
}

// Custom hook to use the context
export function useDashboard() {
  const context = useContext(DashboardContext);
  if (!context) {
    throw new Error('useDashboard must be used within a DashboardProvider');
  }
  return context;
}
