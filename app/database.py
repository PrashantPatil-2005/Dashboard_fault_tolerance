"""
MongoDB database connection and query logic for the Factory Monitoring Backend.

SECURITY NOTE: When deploying to production, ensure MongoDB access is restricted
using firewall rules (e.g., AWS Security Groups) to allow connections only from
the application server. This is especially important when MongoDB's bindIp is
configured for external access (e.g., bindIp: 127.0.0.1,203.0.113.25).
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pymongo import MongoClient, DESCENDING
from pymongo.collection import Collection
from pymongo.database import Database
from app.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages MongoDB connections and database operations."""
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self.connected = False
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB."""
        try:
            self.client = MongoClient(settings.mongodb_url, serverSelectionTimeoutMS=5000)
            self.db = self.client[settings.database_name]
            # Test the connection
            self.client.admin.command('ping')
            self.connected = True
            logger.info(f"Successfully connected to MongoDB: {settings.database_name}")
        except Exception as e:
            logger.warning(f"Failed to connect to MongoDB: {e}")
            logger.info("Running in development mode without database connection")
            self.connected = False
    
    def get_collection(self, collection_name: str) -> Optional[Collection]:
        """Get a MongoDB collection."""
        if not self.connected or self.db is None:
            logger.warning(f"Database not connected, cannot access collection: {collection_name}")
            return None
        return self.db[collection_name]
    
    def close_connection(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


# Global database manager instance
db_manager = DatabaseManager()


class MachineQueries:
    """Database queries related to machines."""
    
    @staticmethod
    def get_all_machines(filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Retrieve all machines with optional filtering."""
        collection = db_manager.get_collection("machines")
        if not collection:
            # Return mock data for development
            return [
                {
                    "_id": "machine_001",
                    "machineName": "Pump A1",
                    "customer": "Factory Corp",
                    "area": "Production",
                    "subarea": "Line 1",
                    "machineType": "PUMP",
                    "status": "Normal",
                    "ingestedDate": "2025-09-17"
                },
                {
                    "_id": "machine_002", 
                    "machineName": "Motor B2",
                    "customer": "Industrial Ltd",
                    "area": "Assembly",
                    "subarea": "Line 2",
                    "machineType": "MOTOR",
                    "status": "Alert",
                    "ingestedDate": "2025-09-17"
                }
            ]
        
        query = filters or {}
        # Remove empty filter values
        query = {k: v for k, v in query.items() if v is not None and v != ""}
        
        machines = list(collection.find(query))
        logger.info(f"Retrieved {len(machines)} machines with filters: {query}")
        return machines
    
    @staticmethod
    def get_machine_by_id(machine_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single machine by its ID."""
        collection = db_manager.get_collection("machines")
        if not collection:
            # Return mock data for development
            mock_machines = {
                "machine_001": {
                    "_id": "machine_001",
                    "machineName": "Pump A1",
                    "customer": "Factory Corp",
                    "area": "Production",
                    "subarea": "Line 1",
                    "machineType": "PUMP",
                    "status": "Normal",
                    "ingestedDate": "2025-09-17"
                },
                "machine_002": {
                    "_id": "machine_002", 
                    "machineName": "Motor B2",
                    "customer": "Industrial Ltd",
                    "area": "Assembly",
                    "subarea": "Line 2",
                    "machineType": "MOTOR",
                    "status": "Alert",
                    "ingestedDate": "2025-09-17"
                }
            }
            return mock_machines.get(machine_id)
        
        machine = collection.find_one({"_id": machine_id})
        if machine:
            logger.info(f"Retrieved machine: {machine_id}")
        else:
            logger.warning(f"Machine not found: {machine_id}")
        return machine
    
    @staticmethod
    def search_machines(customer: str = None, area: str = None, subarea: str = None, 
                       machine_name: str = None, status: str = None) -> List[Dict[str, Any]]:
        """Search machines with multiple filter criteria."""
        filters = {}
        if customer:
            filters["customer"] = {"$regex": customer, "$options": "i"}
        if area:
            filters["area"] = {"$regex": area, "$options": "i"}
        if subarea:
            filters["subarea"] = {"$regex": subarea, "$options": "i"}
        if machine_name:
            filters["machineName"] = {"$regex": machine_name, "$options": "i"}
        if status:
            filters["status"] = status
        
        return MachineQueries.get_all_machines(filters)


class BearingQueries:
    """Database queries related to bearings."""
    
    @staticmethod
    def get_bearings_by_machine_id(machine_id: str) -> List[Dict[str, Any]]:
        """Retrieve all bearings for a specific machine."""
        collection = db_manager.get_collection("bearings")
        if not collection:
            logger.warning("Database not connected, returning empty bearings list (dev mode)")
            return []
        bearings = list(collection.find({"machineId": machine_id}))
        logger.info(f"Retrieved {len(bearings)} bearings for machine: {machine_id}")
        return bearings


class DataQueries:
    """Database queries related to sensor data."""
    
    @staticmethod
    def query_data(bearing_id: str = None, machine_id: str = None, 
                   start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, Any]]:
        """Query sensor data with multiple filter criteria."""
        collection = db_manager.get_collection("data")
        if not collection:
            logger.warning("Database not connected, returning empty data list (dev mode)")
            return []
        query = {}
        
        if bearing_id:
            query["bearingId"] = bearing_id
        if machine_id:
            query["machineId"] = machine_id
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            query["timestamp"] = date_query
        
        data = list(collection.find(query).sort("timestamp", DESCENDING))
        logger.info(f"Retrieved {len(data)} data records with query: {query}")
        return data
    
    @staticmethod
    def get_latest_readings_by_machine(machine_id: str) -> List[Dict[str, Any]]:
        """Get the latest reading for each bearing of a machine."""
        collection = db_manager.get_collection("data")
        if not collection:
            logger.warning("Database not connected, returning empty latest readings (dev mode)")
            return []
        
        # MongoDB aggregation pipeline to get latest reading per bearing
        pipeline = [
            {"$match": {"machineId": machine_id}},
            {"$sort": {"timestamp": -1}},
            {"$group": {
                "_id": "$bearingId",
                "latest_reading": {"$first": "$$ROOT"}
            }},
            {"$replaceRoot": {"newRoot": "$latest_reading"}}
        ]
        
        latest_readings = list(collection.aggregate(pipeline))
        logger.info(f"Retrieved {len(latest_readings)} latest readings for machine: {machine_id}")
        return latest_readings
    
    @staticmethod
    def get_reading_by_id(reading_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific reading by its ID."""
        collection = db_manager.get_collection("data")
        if not collection:
            logger.warning("Database not connected, cannot retrieve reading (dev mode)")
            return None
        reading = collection.find_one({"_id": reading_id})
        if reading:
            logger.info(f"Retrieved reading: {reading_id}")
        else:
            logger.warning(f"Reading not found: {reading_id}")
        return reading


class DashboardQueries:
    """Database queries for dashboard analytics."""
    
    @staticmethod
    def get_kpi_stats(start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """Get KPI statistics for the dashboard."""
        collection = db_manager.get_collection("data")
        if not collection:
            # Return mock data for development
            return {
                "total_readings": 1250,
                "status_counts": {
                    "Normal": 800,
                    "Satisfactory": 300,
                    "Alert": 120,
                    "Unacceptable": 30
                }
            }
        
        # Build date filter
        date_filter = {}
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            date_filter["timestamp"] = date_query
        
        # Simple count for now (can be enhanced with aggregation)
        total_readings = collection.count_documents(date_filter)
        
        # Get status counts
        status_counts = {"Normal": 0, "Satisfactory": 0, "Alert": 0, "Unacceptable": 0}
        for status in status_counts.keys():
            filter_with_status = dict(date_filter)
            filter_with_status["status"] = status
            status_counts[status] = collection.count_documents(filter_with_status)
        
        stats = {"total_readings": total_readings, "status_counts": status_counts}
        logger.info(f"Retrieved KPI stats: {stats}")
        return stats
    
    @staticmethod
    def get_hourly_trends(start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, Any]]:
        """Get hourly reading trends."""
        collection = db_manager.get_collection("data")
        if not collection:
            logger.warning("Database not connected, returning empty hourly trends (dev mode)")
            return []
        
        # Build date filter
        date_filter = {}
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            date_filter["timestamp"] = date_query
        
        # Aggregation pipeline for hourly trends
        pipeline = [
            {"$match": date_filter},
            {"$group": {
                "_id": {"$hour": "$timestamp"},
                "count": {"$sum": 1}
            }},
            {"$project": {
                "_id": 0,
                "hour": "$_id",
                "count": 1
            }},
            {"$sort": {"hour": 1}}
        ]
        
        trends = list(collection.aggregate(pipeline))
        logger.info(f"Retrieved hourly trends: {len(trends)} data points")
        return trends
    
    @staticmethod
    def get_status_trends(start_date: datetime = None, end_date: datetime = None, 
                         customer: str = None) -> Dict[str, Dict[str, int]]:
        """Get status trends by date."""
        collection = db_manager.get_collection("data")
        if not collection:
            logger.warning("Database not connected, returning empty status trends (dev mode)")
            return {}
        
        # Build match filter
        match_filter = {}
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            match_filter["timestamp"] = date_query
        
        # If customer filter is provided, we need to join with machines
        if customer:
            # First get machine IDs for the customer
            machines_collection = db_manager.get_collection("machines")
            if not machines_collection:
                logger.warning("Database not connected, cannot filter by customer; returning empty trends (dev mode)")
                return {}
            machine_ids = [m["_id"] for m in machines_collection.find({"customer": customer}, {"_id": 1})]
            match_filter["machineId"] = {"$in": machine_ids}
        
        # Aggregation pipeline for status trends
        pipeline = [
            {"$match": match_filter},
            {"$group": {
                "_id": {
                    "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                    "status": "$status"
                },
                "count": {"$sum": 1}
            }},
            {"$group": {
                "_id": "$_id.date",
                "status_counts": {
                    "$push": {
                        "status": "$_id.status",
                        "count": "$count"
                    }
                }
            }},
            {"$sort": {"_id": 1}}
        ]
        
        results = list(collection.aggregate(pipeline))
        
        # Transform results into the desired format
        trends = {}
        for result in results:
            date = result["_id"]
            status_dict = {"Normal": 0, "Satisfactory": 0, "Alert": 0, "Unacceptable": 0}
            for status_count in result["status_counts"]:
                status_dict[status_count["status"]] = status_count["count"]
            trends[date] = status_dict
        
        logger.info(f"Retrieved status trends for {len(trends)} dates")
        return trends
