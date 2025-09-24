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
from contextlib import suppress

# Optional SSH tunneling
with suppress(Exception):
    # These imports may not exist if SSH tunneling is disabled
    import paramiko  # type: ignore
    from sshtunnel import SSHTunnelForwarder  # type: ignore

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages MongoDB connections and database operations."""
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self.connected = False
        self._tunnel: Optional["SSHTunnelForwarder"] = None
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB."""
        try:
            mongo_url = settings.mongodb_url

            # Start SSH tunnel if enabled
            if getattr(settings, "ssh_tunnel_enable", False):
                logger.info("SSH tunnel enabled. Establishing tunnel to MongoDB...")
                ssh_pkey_arg = settings.ssh_pkey_path if getattr(settings, "ssh_pkey_path", None) else None
                self._tunnel = SSHTunnelForwarder(
                    (settings.ssh_host, settings.ssh_port),
                    ssh_username=settings.ssh_username,
                    ssh_pkey=ssh_pkey_arg,
                    ssh_private_key_password=settings.ssh_pkey_password,
                    remote_bind_address=(settings.ssh_bind_host, settings.ssh_bind_port),
                    local_bind_address=(settings.ssh_local_bind_host, settings.ssh_local_bind_port),
                )
                self._tunnel.start()
                logger.info(
                    f"SSH tunnel established: {settings.ssh_local_bind_host}:{self._tunnel.local_bind_port} -> "
                    f"{settings.ssh_bind_host}:{settings.ssh_bind_port} via {settings.ssh_host}"
                )
                mongo_url = f"mongodb://{settings.ssh_local_bind_host}:{self._tunnel.local_bind_port}/"

            self.client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
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
        if self._tunnel:
            with suppress(Exception):
                self._tunnel.stop()
                logger.info("SSH tunnel closed")


# Global database manager instance
db_manager = DatabaseManager()


class MachineQueries:
    """Database queries related to machines."""
    
    @staticmethod
    def get_all_machines(filters: Dict[str, Any] = None, start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, Any]]:
        """Retrieve all machines with optional filtering."""
        collection = db_manager.get_collection("machines")
        if collection is None:
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
        # Optional date range filter by ingestedDate (stored as YYYY-MM-DD string)
        if start_date or end_date:
            date_query: Dict[str, Any] = {}
            if start_date:
                date_query["$gte"] = start_date.strftime("%Y-%m-%d")
            if end_date:
                date_query["$lte"] = end_date.strftime("%Y-%m-%d")
            if date_query:
                query["ingestedDate"] = date_query
        # Remove empty filter values
        query = {k: v for k, v in query.items() if v is not None and v != ""}
        
        machines = list(collection.find(query))
        if len(machines) == 0:
            # Fallback: synthesize machine list from bearings if machines collection is empty
            bearings_collection = db_manager.get_collection("bearings")
            if bearings_collection is not None:
                try:
                    machine_ids = bearings_collection.distinct("machineId")
                    if machine_ids:
                        synthesized = [
                            {
                                "_id": mid,
                                "machineName": str(mid),
                                "customer": "Unknown",
                                "area": "Unknown",
                                "subarea": "Unknown",
                                "machineType": None,
                                "status": "Normal",
                                "ingestedDate": None,
                            }
                            for mid in machine_ids
                        ]
                        logger.info(
                            f"Machines empty; synthesized {len(synthesized)} from bearings distinct machineId"
                        )
                        return synthesized
                except Exception as ex:
                    logger.warning(f"Failed to synthesize machines from bearings: {ex}")

        logger.info(f"Retrieved {len(machines)} machines with filters: {query}")
        return machines
    
    @staticmethod
    def get_machine_by_id(machine_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single machine by its ID."""
        collection = db_manager.get_collection("machines")
        if collection is None:
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
                       machine_name: str = None, status: str = None,
                       start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, Any]]:
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
        
        return MachineQueries.get_all_machines(filters, start_date=start_date, end_date=end_date)


class BearingQueries:
    """Database queries related to bearings."""
    
    @staticmethod
    def get_bearings_by_machine_id(machine_id: str) -> List[Dict[str, Any]]:
        """Retrieve all bearings for a specific machine."""
        collection = db_manager.get_collection("bearings")
        if collection is None:
            logger.warning("Database not connected, returning empty bearings list (dev mode)")
            return []
        bearings = list(collection.find({"machineId": machine_id}))
        logger.info(f"Retrieved {len(bearings)} bearings for machine: {machine_id}")
        return bearings


class DataQueries:
    """Database queries related to sensor data."""
    
    @staticmethod
    def _to_epoch_seconds(dt: datetime) -> int:
        return int(dt.timestamp())

    @staticmethod
    def _normalize_timestamp(doc: Dict[str, Any]) -> Dict[str, Any]:
        ts = doc.get("timestamp")
        if isinstance(ts, (int, float)):
            try:
                doc["timestamp"] = datetime.fromtimestamp(ts)
            except Exception:
                pass
        return doc

    @staticmethod
    def query_data(bearing_id: str = None, machine_id: str = None, 
                   start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, Any]]:
        """Query sensor data with multiple filter criteria."""
        collection = db_manager.get_collection("data")
        if collection is None:
            logger.warning("Database not connected, returning empty data list (dev mode)")
            return []
        query = {}
        
        if bearing_id:
            query["bearingId"] = bearing_id
        if machine_id:
            query["machineId"] = machine_id
        if start_date or end_date:
            # Support both datetime and epoch-second numeric timestamps
            conds: List[Dict[str, Any]] = []
            dt_range: Dict[str, Any] = {}
            if start_date:
                dt_range["$gte"] = start_date
            if end_date:
                dt_range["$lte"] = end_date
            if dt_range:
                conds.append({"timestamp": dt_range})
            num_range: Dict[str, Any] = {}
            if start_date:
                num_range["$gte"] = DataQueries._to_epoch_seconds(start_date)
            if end_date:
                num_range["$lte"] = DataQueries._to_epoch_seconds(end_date)
            if num_range:
                conds.append({"timestamp": num_range})
            if conds:
                query["$or"] = conds
        
        data = list(collection.find(query).sort("timestamp", DESCENDING))
        data = [DataQueries._normalize_timestamp(d) for d in data]
        logger.info(f"Retrieved {len(data)} data records with query: {query}")
        return data
    
    @staticmethod
    def get_latest_readings_by_machine(machine_id: str) -> List[Dict[str, Any]]:
        """Get the latest reading for each bearing of a machine."""
        collection = db_manager.get_collection("data")
        if collection is None:
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
        if collection is None:
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
        if collection is None:
            # Return enhanced mock data for development
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
        if collection is None:
            logger.warning("Database not connected, returning mock hourly trends (dev mode)")
            # Return mock data for development
            mock_trends = []
            for hour in range(24):
                mock_trends.append({
                    "hour": hour,
                    "count": 50 + (hour * 2)  # Mock data showing increasing activity
                })
            return mock_trends
        
        # Build date filter supporting datetime and epoch (numeric) timestamps
        date_filter = {}
        if start_date or end_date:
            conds: List[Dict[str, Any]] = []
            dt_range: Dict[str, Any] = {}
            if start_date:
                dt_range["$gte"] = start_date
            if end_date:
                dt_range["$lte"] = end_date
            if dt_range:
                conds.append({"timestamp": dt_range})
            num_range: Dict[str, Any] = {}
            if start_date:
                num_range["$gte"] = DataQueries._to_epoch_seconds(start_date)
            if end_date:
                num_range["$lte"] = DataQueries._to_epoch_seconds(end_date)
            if num_range:
                conds.append({"timestamp": num_range})
            if conds:
                date_filter["$or"] = conds
        
        # Aggregation pipeline for hourly trends
        # Convert numeric timestamps to date for grouping
        pipeline = [
            {"$match": date_filter},
            {"$addFields": {
                "tsDate": {
                    "$cond": [
                        {"$isNumber": "$timestamp"},
                        {"$toDate": {"$multiply": ["$timestamp", 1000]}},
                        "$timestamp"
                    ]
                }
            }},
            {"$group": {
                "_id": {"$hour": "$tsDate"},
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
        if collection is None:
            logger.warning("Database not connected, returning mock status trends (dev mode)")
            # Return mock data for development
            from datetime import datetime, timedelta
            today = datetime.now()
            mock_trends = {}
            
            # Generate mock data for the last 7 days
            for i in range(7):
                date = today - timedelta(days=i)
                date_str = date.strftime("%Y-%m-%d")
                mock_trends[date_str] = {
                    "Normal": 15 + i,
                    "Satisfactory": 8 + i,
                    "Alert": 2 + i,
                    "Unacceptable": 1 + i
                }
            
            return mock_trends
        
        # Build match filter supporting datetime and epoch
        match_filter = {}
        if start_date or end_date:
            conds: List[Dict[str, Any]] = []
            dt_range: Dict[str, Any] = {}
            if start_date:
                dt_range["$gte"] = start_date
            if end_date:
                dt_range["$lte"] = end_date
            if dt_range:
                conds.append({"timestamp": dt_range})
            num_range: Dict[str, Any] = {}
            if start_date:
                num_range["$gte"] = DataQueries._to_epoch_seconds(start_date)
            if end_date:
                num_range["$lte"] = DataQueries._to_epoch_seconds(end_date)
            if num_range:
                conds.append({"timestamp": num_range})
            if conds:
                match_filter["$or"] = conds
        
        # If customer filter is provided, we need to join with machines
        if customer:
            # First get machine IDs for the customer
            machines_collection = db_manager.get_collection("machines")
            if machines_collection is None:
                logger.warning("Database not connected, cannot filter by customer; returning empty trends (dev mode)")
                return {}
            machine_ids = [m["_id"] for m in machines_collection.find({"customer": customer}, {"_id": 1})]
            match_filter["machineId"] = {"$in": machine_ids}
        
        # Aggregation pipeline for status trends
        pipeline = [
            {"$match": match_filter},
            {"$addFields": {
                "tsDate": {
                    "$cond": [
                        {"$isNumber": "$timestamp"},
                        {"$toDate": {"$multiply": ["$timestamp", 1000]}},
                        "$timestamp"
                    ]
                }
            }},
            {"$group": {
                "_id": {
                    "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$tsDate"}},
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
