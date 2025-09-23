"""
FastAPI application for the Factory Monitoring Backend.
Provides REST API endpoints for accessing industrial machine monitoring data.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query, Path, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.config import settings
from app.database import (
    MachineQueries, BearingQueries, DataQueries, DashboardQueries,
    db_manager
)
from app.models import (
    MachineResponse, BearingResponse, ReadingResponse, LatestReadingResponse,
    KPIStats, HourlyTrend, TimeSeriesPoint, ErrorResponse
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Factory Monitoring Backend",
    description="Industrial data monitoring system API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc)
        ).dict()
    )


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("Factory Monitoring Backend starting up...")
    logger.info(f"Database: {settings.database_name}")
    logger.info(f"API Host: {settings.api_host}:{settings.api_port}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Factory Monitoring Backend shutting down...")
    db_manager.close_connection()


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now()}


# ============================================================================
# MACHINE ENDPOINTS
# ============================================================================

@app.get("/api/machines", response_model=List[MachineResponse])
async def get_machines():
    """Retrieve a list of all machines."""
    try:
        machines = MachineQueries.get_all_machines()
        return [MachineResponse(**machine) for machine in machines]
    except Exception as e:
        logger.error(f"Error retrieving machines: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve machines")


@app.get("/api/machines/{machine_id}", response_model=MachineResponse)
async def get_machine_by_id(
    machine_id: str = Path(..., description="Machine ID")
):
    """Retrieve a single machine's details by its ID."""
    try:
        machine = MachineQueries.get_machine_by_id(machine_id)
        if not machine:
            raise HTTPException(status_code=404, detail="Machine not found")
        return MachineResponse(**machine)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving machine {machine_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve machine")


@app.get("/api/machines/search", response_model=List[MachineResponse])
async def search_machines(
    customer: Optional[str] = Query(None, description="Filter by customer"),
    area: Optional[str] = Query(None, description="Filter by area"),
    subarea: Optional[str] = Query(None, description="Filter by subarea"),
    machine_name: Optional[str] = Query(None, description="Filter by machine name"),
    status: Optional[str] = Query(None, description="Filter by status")
):
    """Search machines with multiple filter criteria."""
    try:
        machines = MachineQueries.search_machines(
            customer=customer,
            area=area,
            subarea=subarea,
            machine_name=machine_name,
            status=status
        )
        return [MachineResponse(**machine) for machine in machines]
    except Exception as e:
        logger.error(f"Error searching machines: {e}")
        raise HTTPException(status_code=500, detail="Failed to search machines")


@app.get("/api/machines/{machine_id}/latest-readings", response_model=List[LatestReadingResponse])
async def get_machine_latest_readings(
    machine_id: str = Path(..., description="Machine ID")
):
    """Get the latest reading for each bearing of a machine."""
    try:
        # Get latest readings
        latest_readings = DataQueries.get_latest_readings_by_machine(machine_id)
        
        # Get bearing information to include bearing location
        bearings = BearingQueries.get_bearings_by_machine_id(machine_id)
        bearing_info = {str(b["_id"]): b for b in bearings}
        
        # Combine reading data with bearing info
        result = []
        for reading in latest_readings:
            bearing_id = str(reading["bearingId"])
            bearing = bearing_info.get(bearing_id, {})
            
            result.append(LatestReadingResponse(
                bearingId=bearing_id,
                bearingLocation=bearing.get("bearingLocation", "Unknown"),
                timestamp=reading["timestamp"],
                status=reading["status"],
                acceleration=reading.get("acceleration"),
                velocity=reading.get("velocity"),
                temperature=reading.get("temperature")
            ))
        
        return result
    except Exception as e:
        logger.error(f"Error retrieving latest readings for machine {machine_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve latest readings")


@app.get("/api/machines/{machine_id}/timeseries", response_model=List[TimeSeriesPoint])
async def get_machine_timeseries(
    machine_id: str = Path(..., description="Machine ID"),
    bearing_id: str = Query(..., description="Bearing ID"),
    metric: str = Query(..., description="Metric to retrieve (acceleration, velocity, temperature)"),
    start_date: Optional[datetime] = Query(None, description="Start date for data range"),
    end_date: Optional[datetime] = Query(None, description="End date for data range"),
    limit: int = Query(1000, le=10000, description="Maximum number of data points")
):
    """Get time series data for a specific bearing and metric."""
    try:
        # Query data for the specific bearing
        data = DataQueries.query_data(
            bearing_id=bearing_id,
            machine_id=machine_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Extract the requested metric
        result = []
        for reading in data[:limit]:
            value = None
            if metric == "temperature":
                value = reading.get("temperature")
            elif metric == "acceleration" and reading.get("acceleration"):
                value = reading["acceleration"].get("rms")
            elif metric == "velocity" and reading.get("velocity"):
                value = reading["velocity"].get("rms")
            
            if value is not None:
                result.append(TimeSeriesPoint(
                    timestamp=reading["timestamp"],
                    value=value
                ))
        
        return result
    except Exception as e:
        logger.error(f"Error retrieving timeseries for machine {machine_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve timeseries data")


# ============================================================================
# BEARING ENDPOINTS
# ============================================================================

@app.get("/api/bearings", response_model=List[BearingResponse])
async def get_bearings(
    machine_id: str = Query(..., description="Machine ID to filter bearings")
):
    """Retrieve all bearings associated with a specific machine."""
    try:
        bearings = BearingQueries.get_bearings_by_machine_id(machine_id)
        return [BearingResponse(**bearing) for bearing in bearings]
    except Exception as e:
        logger.error(f"Error retrieving bearings for machine {machine_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve bearings")


# ============================================================================
# DATA ENDPOINTS
# ============================================================================

@app.get("/api/data/query", response_model=List[ReadingResponse])
async def query_data(
    bearing_id: Optional[str] = Query(None, description="Filter by bearing ID"),
    machine_id: Optional[str] = Query(None, description="Filter by machine ID"),
    start_date: Optional[datetime] = Query(None, description="Start date for data range"),
    end_date: Optional[datetime] = Query(None, description="End date for data range"),
    limit: int = Query(1000, le=10000, description="Maximum number of records")
):
    """Query sensor data with multiple filter criteria."""
    try:
        data = DataQueries.query_data(
            bearing_id=bearing_id,
            machine_id=machine_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Limit results
        limited_data = data[:limit]
        
        return [ReadingResponse(**reading) for reading in limited_data]
    except Exception as e:
        logger.error(f"Error querying data: {e}")
        raise HTTPException(status_code=500, detail="Failed to query data")


@app.get("/api/readings/{reading_id}/fft")
async def get_reading_fft(
    reading_id: str = Path(..., description="Reading ID")
):
    """Get FFT data for a specific reading."""
    try:
        reading = DataQueries.get_reading_by_id(reading_id)
        if not reading:
            raise HTTPException(status_code=404, detail="Reading not found")
        
        fft_data = reading.get("fftData") or reading.get("fft_data")
        if not fft_data:
            raise HTTPException(status_code=404, detail="FFT data not available for this reading")
        
        return {"fft_data": fft_data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving FFT data for reading {reading_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve FFT data")


# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@app.get("/api/dashboard/kpis", response_model=KPIStats)
async def get_dashboard_kpis(
    start_date: Optional[datetime] = Query(None, description="Start date for KPI calculation"),
    end_date: Optional[datetime] = Query(None, description="End date for KPI calculation")
):
    """Get KPI statistics for the dashboard."""
    try:
        stats = DashboardQueries.get_kpi_stats(start_date=start_date, end_date=end_date)
        return KPIStats(**stats)
    except Exception as e:
        logger.error(f"Error retrieving dashboard KPIs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard KPIs")


@app.get("/api/dashboard/trends/hourly", response_model=List[HourlyTrend])
async def get_hourly_trends(
    start_date: Optional[datetime] = Query(None, description="Start date for trend analysis"),
    end_date: Optional[datetime] = Query(None, description="End date for trend analysis")
):
    """Get hourly reading trends for the dashboard."""
    try:
        trends = DashboardQueries.get_hourly_trends(start_date=start_date, end_date=end_date)
        return [HourlyTrend(**trend) for trend in trends]
    except Exception as e:
        logger.error(f"Error retrieving hourly trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve hourly trends")


@app.get("/api/dashboard/trends/status")
async def get_status_trends(
    start_date: Optional[datetime] = Query(None, description="Start date for trend analysis"),
    end_date: Optional[datetime] = Query(None, description="End date for trend analysis"),
    customer: Optional[str] = Query(None, description="Filter by customer")
):
    """Get status trends by date for the dashboard."""
    try:
        trends = DashboardQueries.get_status_trends(
            start_date=start_date,
            end_date=end_date,
            customer=customer
        )
        # Convert dictionary format to array format for frontend
        trends_array = [{"date": date, "status_counts": counts} for date, counts in trends.items()]
        return trends_array
    except Exception as e:
        logger.error(f"Error retrieving status trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve status trends")


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.get("/api/stats")
async def get_system_stats():
    """Get system statistics."""
    try:
        machines_count = len(MachineQueries.get_all_machines())
        
        # Get total bearings count
        bearings_collection = db_manager.get_collection("bearings")
        bearings_count = bearings_collection.count_documents({})
        
        # Get total data records count
        data_collection = db_manager.get_collection("data")
        data_count = data_collection.count_documents({})
        
        return {
            "machines_count": machines_count,
            "bearings_count": bearings_count,
            "data_records_count": data_count,
            "database_name": settings.database_name,
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Error retrieving system stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system stats")


# ============================================================================
# MAIN APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower()
    )
