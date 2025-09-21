"""
Pydantic models for data validation and serialization in the Factory Monitoring Backend.
These models represent the structure of MongoDB documents and API request/response schemas.
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field
from pydantic.json_schema import JsonSchemaValue
from pydantic import GetJsonSchemaHandler
from pydantic_core import core_schema
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type compatible with Pydantic v2."""

    @classmethod
    def validate(cls, value):
        if isinstance(value, ObjectId):
            return value
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")
        return ObjectId(value)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        # Validate from string and return an ObjectId
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema()
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema_, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        json_schema = handler(core_schema_)
        json_schema.update(type="string")
        return json_schema


class Machine(BaseModel):
    """Model representing a machine document."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    machine_name: str = Field(..., alias="machineName")
    customer: str
    area: str
    subarea: str
    machine_type: Optional[str] = Field(None, alias="machineType")
    status: Optional[str] = "Normal"  # Normal, Satisfactory, Alert, Unacceptable
    ingested_date: Optional[str] = Field(None, alias="ingestedDate")
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class MachineResponse(BaseModel):
    """Response model for machine data."""
    
    id: str = Field(..., alias="_id")
    machine_name: str = Field(..., alias="machineName")
    customer: str
    area: str
    subarea: str
    machine_type: Optional[str] = Field(None, alias="machineType")
    status: Optional[str] = "Normal"
    ingested_date: Optional[str] = Field(None, alias="ingestedDate")
    
    class Config:
        allow_population_by_field_name = True


class Bearing(BaseModel):
    """Model representing a bearing document."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    machine_id: str = Field(..., alias="machineId")
    bearing_location: str = Field(..., alias="bearingLocation")
    bearing_type: Optional[str] = Field(None, alias="bearingType")
    position: Optional[str] = None
    status: Optional[str] = "Normal"
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class BearingResponse(BaseModel):
    """Response model for bearing data."""
    
    id: str = Field(..., alias="_id")
    machine_id: str = Field(..., alias="machineId")
    bearing_location: str = Field(..., alias="bearingLocation")
    bearing_type: Optional[str] = Field(None, alias="bearingType")
    position: Optional[str] = None
    status: Optional[str] = "Normal"
    
    class Config:
        allow_population_by_field_name = True


class AccelerationData(BaseModel):
    """Model for acceleration sensor data."""
    
    rms: Optional[float] = None
    peak: Optional[float] = None
    crest_factor: Optional[float] = Field(None, alias="crestFactor")
    kurtosis: Optional[float] = None
    
    class Config:
        allow_population_by_field_name = True


class VelocityData(BaseModel):
    """Model for velocity sensor data."""
    
    rms: Optional[float] = None
    peak: Optional[float] = None
    crest_factor: Optional[float] = Field(None, alias="crestFactor")
    
    class Config:
        allow_population_by_field_name = True


class FFTData(BaseModel):
    """Model for FFT analysis data."""
    
    frequencies: List[float] = []
    amplitudes: List[float] = []
    dominant_frequency: Optional[float] = Field(None, alias="dominantFrequency")
    
    class Config:
        allow_population_by_field_name = True


class Reading(BaseModel):
    """Model representing a sensor reading document."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    machine_id: str = Field(..., alias="machineId")
    bearing_id: str = Field(..., alias="bearingId")
    timestamp: datetime
    status: str  # Normal, Satisfactory, Alert, Unacceptable
    axis_id: str = Field(..., alias="Axis_Id")
    
    # Sensor data
    acceleration: Optional[AccelerationData] = None
    velocity: Optional[VelocityData] = None
    temperature: Optional[float] = None
    
    # Analysis data
    fft_data: Optional[FFTData] = Field(None, alias="fftData")
    analytics_types: Optional[str] = Field(None, alias="Analytics_Types")
    
    # Additional metadata
    measurement_type: Optional[str] = Field(None, alias="type")
    raw_data: Optional[Dict[str, Any]] = Field(None, alias="rawData")
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ReadingResponse(BaseModel):
    """Response model for reading data."""
    
    id: str = Field(..., alias="_id")
    machine_id: str = Field(..., alias="machineId")
    bearing_id: str = Field(..., alias="bearingId")
    timestamp: datetime
    status: str
    axis_id: str = Field(..., alias="Axis_Id")
    acceleration: Optional[AccelerationData] = None
    velocity: Optional[VelocityData] = None
    temperature: Optional[float] = None
    fft_data: Optional[FFTData] = Field(None, alias="fftData")
    
    class Config:
        allow_population_by_field_name = True


class LatestReadingResponse(BaseModel):
    """Response model for latest readings with bearing info."""
    
    bearing_id: str = Field(..., alias="bearingId")
    bearing_location: str = Field(..., alias="bearingLocation")
    timestamp: datetime
    status: str
    acceleration: Optional[AccelerationData] = None
    velocity: Optional[VelocityData] = None
    temperature: Optional[float] = None
    
    class Config:
        allow_population_by_field_name = True


class KPIStats(BaseModel):
    """Model for dashboard KPI statistics."""
    
    total_readings: int
    status_counts: Dict[str, int]


class HourlyTrend(BaseModel):
    """Model for hourly trend data."""
    
    hour: int
    count: int


class StatusTrend(BaseModel):
    """Model for status trend data."""
    
    date: str
    status_counts: Dict[str, int]


class TimeSeriesPoint(BaseModel):
    """Model for time series data points."""
    
    timestamp: datetime
    value: float


class DataQueryRequest(BaseModel):
    """Request model for data query endpoint."""
    
    bearing_id: Optional[str] = None
    machine_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: Optional[int] = Field(default=1000, le=10000)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ErrorResponse(BaseModel):
    """Standard error response model."""
    
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
