import React from 'react';
import { PrimeReactProvider } from 'primereact/api';
import { DashboardProvider } from './context/DashboardContext';
import Dashboard from './components/Dashboard/Dashboard';
import TestMachineDetails from './components/Test/TestMachineDetails';
import 'primereact/resources/themes/lara-light-blue/theme.css';
import 'primereact/resources/primereact.min.css';
import 'primeicons/primeicons.css';
import 'primeflex/primeflex.css';
import './App.css';

function App() {
  return (
    <PrimeReactProvider>
      <DashboardProvider>
        <div className="App">
          <Dashboard />
        </div>
      </DashboardProvider>
    </PrimeReactProvider>
  );
}

export default App;
