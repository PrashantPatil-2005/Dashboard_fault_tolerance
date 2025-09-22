import React, { useState } from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { Tag } from 'primereact/tag';
import { Card } from 'primereact/card';
import { useDashboard } from '../../context/DashboardContext';
import { Machine } from '../../types';
import { STATUS_COLORS } from '../../constants/colors';
import MachineDetailsModal from '../MachineDetails/MachineDetailsModal';

const MachineTable: React.FC = () => {
  const { state } = useDashboard();
  const [selectedMachines, setSelectedMachines] = useState<Machine[]>([]);
  const [selectedMachine, setSelectedMachine] = useState<Machine | null>(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);

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

  const statusBodyTemplate = (rowData: Machine) => {
    return (
      <Tag
        value={rowData.status}
        icon={getStatusIcon(rowData.status)}
        style={{ 
          backgroundColor: getStatusColor(rowData.status),
          color: 'white',
          border: 'none'
        }}
      />
    );
  };

  const viewDetailsBodyTemplate = (rowData: Machine) => {
    return (
      <Button
        label="View Details"
        icon="pi pi-eye"
        size="small"
        className="p-button-outlined"
        onClick={() => handleViewDetails(rowData)}
      />
    );
  };

  const [showModal,setShowModal]=useState(false);
  const handleViewDetails = (machine: Machine) => {
    setSelectedMachine(machine);
    setShowDetailsModal(true);
  };

  const handleCloseDetails = () => {
    setShowDetailsModal(false);
    setSelectedMachine(null);
  };

  const header = (
    <div className="flex justify-content-between align-items-center">
      <h3 className="text-lg font-semibold text-900 m-0">Machines</h3>
      <div className="flex align-items-center gap-2">
        <span className="text-600 text-sm">
          Showing {state.filteredMachines.length} of {state.machines.length} machines
        </span>
        {selectedMachines.length > 0 && (
          <Button
            label={`${selectedMachines.length} selected`}
            icon="pi pi-check"
            size="small"
            className="p-button-outlined"
            onClick={() => setSelectedMachines([])}
          />
        )}
      </div>
    </div>
  );

  const emptyMessage = (
    <div className="text-center py-4">
      <i className="pi pi-search text-4xl text-400 mb-3" />
      <h4 className="text-900 mb-2">No machines found</h4>
      <p className="text-600 mb-3">
        {state.machines.length === 0 
          ? 'No machines available for the selected date'
          : 'Try adjusting your search filters'
        }
      </p>
      {state.machines.length > 0 && (
        <Button
          label="Clear Filters"
          icon="pi pi-times"
          className="p-button-outlined"
          onClick={() => {
            // Clear filters logic will be handled by parent component
          }}
        />
      )}
    </div>
  );

  return (
    <Card>
      <DataTable
        value={state.filteredMachines}
        selection={selectedMachines}
        onSelectionChange={(e) => setSelectedMachines(e.value)}
        dataKey="_id"
        paginator
        rows={10}
        rowsPerPageOptions={[5, 10, 25, 50]}
        paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
        currentPageReportTemplate="Showing {first} to {last} of {totalRecords} machines"
        emptyMessage={emptyMessage}
        header={header}
        className="p-datatable-sm"
        loading={state.loading}
        sortField="machineName"
        sortOrder={1}
        removableSort
        resizableColumns
        columnResizeMode="expand"
        scrollable
        scrollHeight="400px"
      >
        <Column 
          selectionMode="multiple" 
          headerStyle={{ width: '3rem' }}
          frozen
        />
        
        <Column
          field="customer"
          header="Customer"
          sortable
          style={{ minWidth: '120px' }}
        />
        
        <Column
          field="area"
          header="Area"
          sortable
          style={{ minWidth: '100px' }}
        />
        
        <Column
          field="subarea"
          header="Subarea"
          sortable
          style={{ minWidth: '120px' }}
        />
        
        <Column
          field="machineName"
          header="Machine"
          sortable
          style={{ minWidth: '150px' }}
        />
        
        <Column
          field="status"
          header="Status"
          body={statusBodyTemplate}
          sortable
          style={{ minWidth: '120px' }}
        />
        
        <Column
          header="View Details"
          body={viewDetailsBodyTemplate}
          style={{ minWidth: '120px' }}
          frozen
          alignFrozen="right"
        />
      </DataTable>

      {/* Machine Details Modal */}
      <MachineDetailsModal
        machine={selectedMachine}
        visible={showDetailsModal}
        onHide={handleCloseDetails}
      />
    </Card>
  );
};

export default MachineTable;
