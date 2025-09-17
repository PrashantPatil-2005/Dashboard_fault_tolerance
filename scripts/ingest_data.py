#!/usr/bin/env python3
"""
Data Ingestion Script for Factory Monitoring Backend.

This script fetches data from external APIs and stores it in MongoDB.
Refactored from the original db_store.py script to be more robust and schedulable.

Usage:
    python ingest_data.py [--date YYYY-MM-DD] [--backfill-days N]

Cron Job Setup:
    To run this script daily at 2 AM, add the following line to your crontab:
    0 2 * * * /usr/bin/python3 /path/to/factory_monitoring_backend/scripts/ingest_data.py >> /var/log/ingestion_cron.log 2>&1

    To edit crontab:
    crontab -e

    To view current crontab:
    crontab -l
"""

import os
import sys
import argparse
import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Add the parent directory to the Python path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.database import db_manager


class DataIngestionError(Exception):
    """Custom exception for data ingestion errors."""
    pass


class ExternalAPIClient:
    """Client for interacting with external APIs."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def fetch_machines(self, date_str: str) -> List[Dict[str, Any]]:
        """Fetch machines data from external API."""
        url = f"{self.base_url}/Machine"
        payload = {"date": date_str}
        
        try:
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Fetched {len(data)} machines for {date_str}")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch machines for {date_str}: {e}")
            raise DataIngestionError(f"Failed to fetch machines: {e}")
    
    def fetch_bearings(self, machine_id: str) -> List[Dict[str, Any]]:
        """Fetch bearings data for a specific machine."""
        url = f"{self.base_url}/Bearing"
        params = {"machineId": machine_id}
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            logger.debug(f"Fetched {len(data)} bearings for machine {machine_id}")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch bearings for machine {machine_id}: {e}")
            raise DataIngestionError(f"Failed to fetch bearings: {e}")
    
    def fetch_data(self, machine_id: str, bearing_id: str, machine_type: str, 
                   axis: str = "A-Axis", analytics: str = "MF") -> Optional[Dict[str, Any]]:
        """Fetch sensor data for a specific bearing."""
        url = f"{self.base_url}/Data"
        payload = {
            "machineId": machine_id,
            "bearingLocationId": bearing_id,
            "Axis_Id": axis,
            "type": machine_type,
            "Analytics_Types": analytics
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            logger.debug(f"Fetched data for bearing {bearing_id}")
            return data
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to fetch data for bearing {bearing_id}: {e}")
            return None


class DataIngestionService:
    """Service for ingesting data into MongoDB."""
    
    def __init__(self, api_client: ExternalAPIClient):
        self.api_client = api_client
        self.machines_collection = db_manager.get_collection("machines")
        self.bearings_collection = db_manager.get_collection("bearings")
        self.data_collection = db_manager.get_collection("data")
    
    def ingest_machines(self, date_str: str) -> int:
        """Ingest machines data for a specific date."""
        try:
            machines = self.api_client.fetch_machines(date_str)
            inserted_count = 0
            
            for machine in machines:
                # Add ingestion metadata
                machine["ingestedDate"] = date_str
                machine["createdAt"] = datetime.now()
                
                # Insert machine (replace if exists)
                result = self.machines_collection.replace_one(
                    {"_id": machine["_id"]},
                    machine,
                    upsert=True
                )
                
                if result.upserted_id or result.modified_count > 0:
                    inserted_count += 1
            
            logger.info(f"Processed {inserted_count} machines for {date_str}")
            return inserted_count
            
        except Exception as e:
            logger.error(f"Failed to ingest machines for {date_str}: {e}")
            raise DataIngestionError(f"Machine ingestion failed: {e}")
    
    def ingest_bearings(self, machine_id: str) -> int:
        """Ingest bearings data for a specific machine."""
        try:
            # Check if bearings already exist for this machine
            existing_count = self.bearings_collection.count_documents({"machineId": machine_id})
            if existing_count > 0:
                logger.debug(f"Bearings already exist for machine {machine_id}, skipping")
                return 0
            
            bearings = self.api_client.fetch_bearings(machine_id)
            inserted_count = 0
            
            for bearing in bearings:
                bearing["machineId"] = machine_id
                bearing["createdAt"] = datetime.now()
                
                # Insert bearing
                result = self.bearings_collection.insert_one(bearing)
                if result.inserted_id:
                    inserted_count += 1
            
            logger.info(f"Inserted {inserted_count} bearings for machine {machine_id}")
            return inserted_count
            
        except Exception as e:
            logger.error(f"Failed to ingest bearings for machine {machine_id}: {e}")
            return 0
    
    def ingest_sensor_data(self, machine_id: str, bearing_id: str, machine_type: str) -> bool:
        """Ingest sensor data for a specific bearing."""
        try:
            data_entry = self.api_client.fetch_data(machine_id, bearing_id, machine_type)
            
            if not data_entry:
                return False
            
            # Add metadata
            data_entry["machineId"] = machine_id
            data_entry["bearingId"] = bearing_id
            data_entry["Axis_Id"] = "A-Axis"
            data_entry["timestamp"] = datetime.now()
            
            # Insert data
            result = self.data_collection.insert_one(data_entry)
            return bool(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Failed to ingest sensor data for bearing {bearing_id}: {e}")
            return False
    
    def run_daily_ingestion(self, date_str: str) -> Dict[str, int]:
        """Run complete daily ingestion process."""
        logger.info(f"🚀 Starting daily ingestion for {date_str}")
        stats = {"machines": 0, "bearings": 0, "data_records": 0, "errors": 0}
        
        try:
            # Step 1: Ingest machines
            stats["machines"] = self.ingest_machines(date_str)
            
            # Step 2: Get all machines and ingest bearings
            machines = list(self.machines_collection.find({"ingestedDate": date_str}))
            
            for machine in machines:
                machine_id = machine["_id"]
                
                # Ingest bearings for this machine
                bearing_count = self.ingest_bearings(machine_id)
                stats["bearings"] += bearing_count
            
            # Step 3: Ingest sensor data for all bearings
            all_bearings = list(self.bearings_collection.find({}))
            
            for bearing in all_bearings:
                machine_id = bearing["machineId"]
                bearing_id = bearing["_id"]
                
                # Get machine type
                machine_doc = self.machines_collection.find_one(
                    {"_id": machine_id},
                    sort=[("ingestedDate", -1)]
                )
                machine_type = machine_doc.get("machineType", "OFFLINE") if machine_doc else "OFFLINE"
                
                # Ingest sensor data
                if self.ingest_sensor_data(machine_id, bearing_id, machine_type):
                    stats["data_records"] += 1
                else:
                    stats["errors"] += 1
            
            logger.info(f"✅ Completed ingestion for {date_str}: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Daily ingestion failed for {date_str}: {e}")
            stats["errors"] += 1
            raise DataIngestionError(f"Daily ingestion failed: {e}")


def setup_logging(log_file: str = "ingestion.log", log_level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Factory data ingestion script")
    parser.add_argument(
        "--date",
        type=str,
        help="Date to ingest data for (YYYY-MM-DD). Defaults to today."
    )
    parser.add_argument(
        "--backfill-days",
        type=int,
        help="Number of days to backfill from the specified date (or today)"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default="ingestion.log",
        help="Log file path"
    )
    return parser.parse_args()


def main():
    """Main function for the ingestion script."""
    args = parse_arguments()
    
    # Setup logging
    global logger
    logger = setup_logging(args.log_file, args.log_level)
    
    try:
        # Initialize API client and ingestion service
        api_client = ExternalAPIClient(settings.external_api_base_url)
        ingestion_service = DataIngestionService(api_client)
        
        # Determine dates to process
        if args.date:
            end_date = datetime.strptime(args.date, "%Y-%m-%d")
        else:
            end_date = datetime.now()
        
        if args.backfill_days:
            start_date = end_date - timedelta(days=args.backfill_days - 1)
            dates_to_process = []
            current = start_date
            while current.date() <= end_date.date():
                dates_to_process.append(current.strftime("%Y-%m-%d"))
                current += timedelta(days=1)
        else:
            dates_to_process = [end_date.strftime("%Y-%m-%d")]
        
        # Process each date
        total_stats = {"machines": 0, "bearings": 0, "data_records": 0, "errors": 0}
        
        for date_str in dates_to_process:
            try:
                stats = ingestion_service.run_daily_ingestion(date_str)
                for key in total_stats:
                    total_stats[key] += stats[key]
            except DataIngestionError as e:
                logger.error(f"Ingestion failed for {date_str}: {e}")
                total_stats["errors"] += 1
                continue
        
        # Log final summary
        logger.info(f"🎉 Ingestion completed. Total stats: {total_stats}")
        
        # Exit with error code if there were errors
        if total_stats["errors"] > 0:
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"💥 Fatal error in ingestion script: {e}")
        sys.exit(1)
    
    finally:
        # Close database connection
        db_manager.close_connection()


if __name__ == "__main__":
    main()
