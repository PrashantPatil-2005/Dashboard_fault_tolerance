import React, { useState, useEffect } from 'react';
import { Card } from 'primereact/card';
import { InputText } from 'primereact/inputtext';
import { Dropdown } from 'primereact/dropdown';
import { Button } from 'primereact/button';
import { useDashboard } from '../../context/DashboardContext';
import { STATUS_COLORS } from '../../constants/colors';

const SearchFilters: React.FC = () => {
  const { state, actions } = useDashboard();
  const [searchTerm, setSearchTerm] = useState('');
  const [localFilters, setLocalFilters] = useState(state.searchFilters);

  // Get unique values for dropdowns
  const uniqueCustomers = [...new Set(state.machines.map(m => m.customer))].sort();
  const uniqueAreas = [...new Set(state.machines.map(m => m.area))].sort();
  const uniqueSubareas = [...new Set(state.machines.map(m => m.subarea))].sort();
  
  const statusOptions = [
    { label: 'All Statuses', value: '' },
    { label: 'Normal', value: 'Normal' },
    { label: 'Satisfactory', value: 'Satisfactory' },
    { label: 'Alert', value: 'Alert' },
    { label: 'Unacceptable', value: 'Unacceptable' },
  ];

  // Update local filters when state changes
  useEffect(() => {
    setLocalFilters(state.searchFilters);
  }, [state.searchFilters]);

  const handleSearch = () => {
    actions.searchMachines({
      ...localFilters,
      machineName: searchTerm,
    });
  };

  // Real-time filtering as user types
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (searchTerm || Object.values(localFilters).some(value => value)) {
        actions.searchMachines({
          ...localFilters,
          machineName: searchTerm,
        });
      }
    }, 300); // Debounce for 300ms

    return () => clearTimeout(timeoutId);
  }, [searchTerm, localFilters, actions]);

  const handleClearFilters = () => {
    setSearchTerm('');
    setLocalFilters({
      customer: '',
      area: '',
      subarea: '',
      machineName: '',
      status: '',
    });
    actions.clearFilters();
  };

  const handleFilterChange = (field: string, value: string) => {
    setLocalFilters(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const getStatusColor = (status: string) => {
    return STATUS_COLORS[status as keyof typeof STATUS_COLORS] || '#6c757d';
  };

  return (
    <Card className="mb-3">
      <div className="flex justify-content-between align-items-center mb-3">
        <div>
          <h3 className="text-lg font-semibold text-900 m-0">Search & Filter</h3>
          <p className="text-600 text-sm m-0 mt-1">Filter machines by criteria</p>
        </div>
        <div className="flex gap-2">
          <Button
            label="Search"
            icon="pi pi-search"
            onClick={handleSearch}
            loading={state.loading}
            size="small"
          />
          <Button
            label="Clear"
            icon="pi pi-times"
            onClick={handleClearFilters}
            className="p-button-outlined"
            severity="secondary"
            size="small"
          />
        </div>
      </div>

      <div className="grid">
        {/* Search Input */}
        <div className="col-12 md:col-6 lg:col-3">
          <div className="field">
            <label htmlFor="search" className="block text-900 font-medium mb-1 text-sm">
              Search Machine
            </label>
            <InputText
              id="search"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by name or ID..."
              className="w-full"
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              size="small"
            />
          </div>
        </div>

        {/* Customer Filter */}
        <div className="col-12 md:col-6 lg:col-2">
          <div className="field">
            <label htmlFor="customer" className="block text-900 font-medium mb-1 text-sm">
              Customer
            </label>
            <Dropdown
              id="customer"
              value={localFilters.customer}
              options={[
                { label: 'All Customers', value: '' },
                ...uniqueCustomers.map(customer => ({ label: customer, value: customer }))
              ]}
              onChange={(e) => handleFilterChange('customer', e.value)}
              placeholder="Customer"
              className="w-full"
              showClear
              size="small"
            />
          </div>
        </div>

        {/* Area Filter */}
        <div className="col-12 md:col-6 lg:col-2">
          <div className="field">
            <label htmlFor="area" className="block text-900 font-medium mb-1 text-sm">
              Area
            </label>
            <Dropdown
              id="area"
              value={localFilters.area}
              options={[
                { label: 'All Areas', value: '' },
                ...uniqueAreas.map(area => ({ label: area, value: area }))
              ]}
              onChange={(e) => handleFilterChange('area', e.value)}
              placeholder="Area"
              className="w-full"
              showClear
              size="small"
            />
          </div>
        </div>

        {/* Subarea Filter */}
        <div className="col-12 md:col-6 lg:col-2">
          <div className="field">
            <label htmlFor="subarea" className="block text-900 font-medium mb-1 text-sm">
              Subarea
            </label>
            <Dropdown
              id="subarea"
              value={localFilters.subarea}
              options={[
                { label: 'All Subareas', value: '' },
                ...uniqueSubareas.map(subarea => ({ label: subarea, value: subarea }))
              ]}
              onChange={(e) => handleFilterChange('subarea', e.value)}
              placeholder="Subarea"
              className="w-full"
              showClear
              size="small"
            />
          </div>
        </div>

        {/* Status Filter */}
        <div className="col-12 md:col-6 lg:col-2">
          <div className="field">
            <label htmlFor="status" className="block text-900 font-medium mb-1 text-sm">
              Status
            </label>
            <Dropdown
              id="status"
              value={localFilters.status}
              options={statusOptions}
              onChange={(e) => handleFilterChange('status', e.value)}
              placeholder="Status"
              className="w-full"
              showClear
              optionLabel="label"
              optionValue="value"
              size="small"
            />
          </div>
        </div>
      </div>

      {/* Active Filters Display */}
      {(localFilters.customer || localFilters.area || localFilters.subarea || localFilters.status || searchTerm) && (
        <div className="mt-3 pt-3 border-top-1 surface-border">
          <div className="flex align-items-center gap-2 flex-wrap">
            <span className="text-600 text-sm font-medium">Active Filters:</span>
            {searchTerm && (
              <span className="p-tag p-tag-info">
                Search: {searchTerm}
                <i className="pi pi-times ml-1 cursor-pointer" onClick={() => setSearchTerm('')} />
              </span>
            )}
            {localFilters.customer && (
              <span className="p-tag p-tag-info">
                Customer: {localFilters.customer}
                <i className="pi pi-times ml-1 cursor-pointer" onClick={() => handleFilterChange('customer', '')} />
              </span>
            )}
            {localFilters.area && (
              <span className="p-tag p-tag-info">
                Area: {localFilters.area}
                <i className="pi pi-times ml-1 cursor-pointer" onClick={() => handleFilterChange('area', '')} />
              </span>
            )}
            {localFilters.subarea && (
              <span className="p-tag p-tag-info">
                Subarea: {localFilters.subarea}
                <i className="pi pi-times ml-1 cursor-pointer" onClick={() => handleFilterChange('subarea', '')} />
              </span>
            )}
            {localFilters.status && (
              <span 
                className="p-tag"
                style={{ 
                  backgroundColor: getStatusColor(localFilters.status),
                  color: 'white'
                }}
              >
                Status: {localFilters.status}
                <i className="pi pi-times ml-1 cursor-pointer" onClick={() => handleFilterChange('status', '')} />
              </span>
            )}
          </div>
        </div>
      )}
    </Card>
  );
};

export default SearchFilters;
