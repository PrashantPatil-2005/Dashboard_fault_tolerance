"""
Data export script for factory monitoring data.
Exports data from MongoDB collections to text files.
"""

import json
import logging
import sys
import os
from datetime import datetime

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import db_manager
from app.ssh_tunnel import ssh_tunnel_manager
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def export_factory_data():
    """Export all factory data to a text file."""
    try:
        # Ensure SSH tunnel is started if needed
        if settings.use_ssh_tunnel:
            if not ssh_tunnel_manager.start_tunnel():
                logger.error("Failed to start SSH tunnel")
                return False
        
        # Check database connection
        if not db_manager.connected:
            logger.error("Database not connected")
            return False
        
        # Open file for writing
        output_file = "factory_data_export.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"Factory Data Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            
            # Export Machines
            logger.info("Exporting machines...")
            f.write("=== Machines ===\n")
            machines_collection = db_manager.get_collection("machines")
            if machines_collection:
                machine_count = 0
                for machine in machines_collection.find():
                    f.write(json.dumps(machine, default=str, indent=2) + "\n")
                    machine_count += 1
                f.write(f"Total Machines: {machine_count}\n\n")
            else:
                f.write("Machines collection not accessible\n\n")
            
            # Export Bearings
            logger.info("Exporting bearings...")
            f.write("=== Bearings ===\n")
            bearings_collection = db_manager.get_collection("bearings")
            if bearings_collection:
                bearing_count = 0
                for bearing in bearings_collection.find():
                    f.write(json.dumps(bearing, default=str, indent=2) + "\n")
                    bearing_count += 1
                f.write(f"Total Bearings: {bearing_count}\n\n")
            else:
                f.write("Bearings collection not accessible\n\n")
            
            # Export Data (excluding rawData for readability)
            logger.info("Exporting sensor data...")
            f.write("=== Sensor Data ===\n")
            data_collection = db_manager.get_collection("data")
            if data_collection:
                data_count = 0
                for data_record in data_collection.find({}, {"rawData": 0}):
                    f.write(json.dumps(data_record, default=str, indent=2) + "\n")
                    data_count += 1
                f.write(f"Total Data Records: {data_count}\n\n")
            else:
                f.write("Data collection not accessible\n\n")
        
        logger.info(f"Data exported successfully to {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        return False
    
    finally:
        # Clean up SSH tunnel if it was started
        if settings.use_ssh_tunnel:
            ssh_tunnel_manager.stop_tunnel()


def export_machines_only():
    """Export only machines data."""
    try:
        if settings.use_ssh_tunnel:
            if not ssh_tunnel_manager.start_tunnel():
                logger.error("Failed to start SSH tunnel")
                return False
        
        if not db_manager.connected:
            logger.error("Database not connected")
            return False
        
        output_file = "machines_export.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"Machines Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            
            machines_collection = db_manager.get_collection("machines")
            if machines_collection:
                machine_count = 0
                for machine in machines_collection.find():
                    f.write(json.dumps(machine, default=str, indent=2) + "\n")
                    machine_count += 1
                f.write(f"Total Machines: {machine_count}\n")
            else:
                f.write("Machines collection not accessible\n")
        
        logger.info(f"Machines exported successfully to {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error exporting machines: {e}")
        return False
    
    finally:
        if settings.use_ssh_tunnel:
            ssh_tunnel_manager.stop_tunnel()


def export_data_only():
    """Export only sensor data (excluding rawData)."""
    try:
        if settings.use_ssh_tunnel:
            if not ssh_tunnel_manager.start_tunnel():
                logger.error("Failed to start SSH tunnel")
                return False
        
        if not db_manager.connected:
            logger.error("Database not connected")
            return False
        
        output_file = "sensor_data_export.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"Sensor Data Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            
            data_collection = db_manager.get_collection("data")
            if data_collection:
                data_count = 0
                for data_record in data_collection.find({}, {"rawData": 0}):
                    f.write(json.dumps(data_record, default=str, indent=2) + "\n")
                    data_count += 1
                f.write(f"Total Data Records: {data_count}\n")
            else:
                f.write("Data collection not accessible\n")
        
        logger.info(f"Sensor data exported successfully to {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error exporting sensor data: {e}")
        return False
    
    finally:
        if settings.use_ssh_tunnel:
            ssh_tunnel_manager.stop_tunnel()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Export factory monitoring data")
    parser.add_argument("--type", choices=["all", "machines", "data"], default="all",
                       help="Type of data to export (default: all)")
    
    args = parser.parse_args()
    
    logger.info(f"Starting data export - Type: {args.type}")
    logger.info(f"SSH Tunnel: {'Enabled' if settings.use_ssh_tunnel else 'Disabled'}")
    
    success = False
    if args.type == "all":
        success = export_factory_data()
    elif args.type == "machines":
        success = export_machines_only()
    elif args.type == "data":
        success = export_data_only()
    
    if success:
        logger.info("Export completed successfully!")
    else:
        logger.error("Export failed!")
        sys.exit(1)
