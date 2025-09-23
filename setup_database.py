#!/usr/bin/env python3
"""
Database Setup and Sample Data Population Script

This script sets up MongoDB collections and populates them with realistic
sample data for the Factory Monitoring Dashboard.

Usage:
    python setup_database.py

Requirements:
    - MongoDB running on localhost:27017
    - pymongo installed
"""

import json
import random
from datetime import datetime, timedelta
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseSeeder:
    """Handles database setup and sample data population."""

    def __init__(self, mongodb_url="mongodb://localhost:27017/", database_name="factory_db"):
        """Initialize database connection."""
        self.mongodb_url = mongodb_url
        self.database_name = database_name
        self.client = None
        self.db = None

    def connect(self):
        """Establish connection to MongoDB."""
        try:
            self.client = MongoClient(self.mongodb_url, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.database_name]
            # Test the connection
            self.client.admin.command('ping')
            logger.info(f"✅ Connected to MongoDB: {self.database_name}")
            return True
        except ServerSelectionTimeoutError:
            logger.error("❌ Failed to connect to MongoDB. Please ensure MongoDB is running.")
            logger.info("💡 The application will work with mock data without MongoDB.")
            return False
        except Exception as e:
            logger.error(f"❌ Database connection error: {e}")
            return False

    def setup_collections(self):
        """Create necessary collections and indexes."""
        if not self.db:
            return False

        try:
            # Create collections
            collections = ['machines', 'bearings', 'data']
            for collection_name in collections:
                if collection_name not in self.db.list_collection_names():
                    self.db.create_collection(collection_name)
                    logger.info(f"✅ Created collection: {collection_name}")

            # Create indexes for better query performance
            self.db.machines.create_index([('customer', 1), ('area', 1), ('status', 1)])
            self.db.bearings.create_index([('machineId', 1), ('bearingLocation', 1)])
            self.db.data.create_index([('machineId', 1), ('bearingId', 1), ('timestamp', -1)])

            logger.info("✅ Created database indexes")
            return True
        except Exception as e:
            logger.error(f"❌ Error setting up collections: {e}")
            return False

    def generate_sample_machines(self):
        """Generate realistic machine sample data."""
        machines = [
            {
                "_id": "MACHINE_001",
                "machineName": "Pump Station Alpha",
                "customer": "Industrial Corp",
                "area": "Production Floor A",
                "subarea": "Pump Section 1",
                "machineType": "CENTRIFUGAL_PUMP",
                "status": "Normal",
                "ingestedDate": "2025-01-15",
                "createdAt": datetime.now() - timedelta(days=30),
                "updatedAt": datetime.now() - timedelta(hours=2)
            },
            {
                "_id": "MACHINE_002",
                "machineName": "Motor Assembly B2",
                "customer": "Manufacturing Ltd",
                "area": "Assembly Line 2",
                "subarea": "Motor Section",
                "machineType": "ELECTRIC_MOTOR",
                "status": "Satisfactory",
                "ingestedDate": "2025-01-10",
                "createdAt": datetime.now() - timedelta(days=25),
                "updatedAt": datetime.now() - timedelta(hours=1)
            },
            {
                "_id": "MACHINE_003",
                "machineName": "Compressor Unit C",
                "customer": "Tech Industries",
                "area": "Maintenance Bay",
                "subarea": "Compressor Zone",
                "machineType": "AIR_COMPRESSOR",
                "status": "Alert",
                "ingestedDate": "2025-01-20",
                "createdAt": datetime.now() - timedelta(days=20),
                "updatedAt": datetime.now() - timedelta(minutes=30)
            },
            {
                "_id": "MACHINE_004",
                "machineName": "Generator Set D",
                "customer": "Power Solutions Inc",
                "area": "Power Generation",
                "subarea": "Generator Room",
                "machineType": "DIESEL_GENERATOR",
                "status": "Normal",
                "ingestedDate": "2025-01-05",
                "createdAt": datetime.now() - timedelta(days=35),
                "updatedAt": datetime.now() - timedelta(hours=4)
            },
            {
                "_id": "MACHINE_005",
                "machineName": "Conveyor Belt E1",
                "customer": "Logistics Pro",
                "area": "Warehouse",
                "subarea": "Conveyor Area",
                "machineType": "CONVEYOR_SYSTEM",
                "status": "Unacceptable",
                "ingestedDate": "2025-01-25",
                "createdAt": datetime.now() - timedelta(days=15),
                "updatedAt": datetime.now() - timedelta(minutes=15)
            }
        ]
        return machines

    def generate_sample_bearings(self):
        """Generate realistic bearing sample data."""
        bearings = [
            {
                "_id": "BEARING_001",
                "machineId": "MACHINE_001",
                "bearingLocation": "Pump Input Shaft",
                "bearingType": "Deep Groove Ball Bearing",
                "position": "Front",
                "status": "Normal",
                "createdAt": datetime.now() - timedelta(days=30)
            },
            {
                "_id": "BEARING_002",
                "machineId": "MACHINE_001",
                "bearingLocation": "Pump Output Shaft",
                "bearingType": "Angular Contact Bearing",
                "position": "Rear",
                "status": "Normal",
                "createdAt": datetime.now() - timedelta(days=30)
            },
            {
                "_id": "BEARING_003",
                "machineId": "MACHINE_002",
                "bearingLocation": "Motor Drive End",
                "bearingType": "Cylindrical Roller Bearing",
                "position": "Front",
                "status": "Satisfactory",
                "createdAt": datetime.now() - timedelta(days=25)
            },
            {
                "_id": "BEARING_004",
                "machineId": "MACHINE_002",
                "bearingLocation": "Motor Non-Drive End",
                "bearingType": "Deep Groove Ball Bearing",
                "position": "Rear",
                "status": "Satisfactory",
                "createdAt": datetime.now() - timedelta(days=25)
            },
            {
                "_id": "BEARING_005",
                "machineId": "MACHINE_003",
                "bearingLocation": "Compressor Main Shaft",
                "bearingType": "Spherical Roller Bearing",
                "position": "Center",
                "status": "Alert",
                "createdAt": datetime.now() - timedelta(days=20)
            }
        ]
        return bearings

    def generate_sample_data(self):
        """Generate realistic sensor data."""
        data = []
        base_time = datetime.now() - timedelta(days=7)

        # Generate data for each bearing over the last 7 days
        for bearing_id in ["BEARING_001", "BEARING_002", "BEARING_003", "BEARING_004", "BEARING_005"]:
            for day in range(7):
                for hour in range(24):
                    timestamp = base_time + timedelta(days=day, hours=hour)

                    # Determine status based on bearing and some randomness
                    if bearing_id == "BEARING_005":  # Alert bearing
                        status = random.choices(["Normal", "Satisfactory", "Alert", "Unacceptable"],
                                              weights=[0.4, 0.3, 0.2, 0.1])[0]
                    elif bearing_id in ["BEARING_003", "BEARING_004"]:  # Satisfactory bearings
                        status = random.choices(["Normal", "Satisfactory", "Alert"],
                                              weights=[0.5, 0.4, 0.1])[0]
                    else:  # Normal bearings
                        status = random.choices(["Normal", "Satisfactory"],
                                              weights=[0.8, 0.2])[0]

                    # Generate sensor readings
                    temperature = 65 + random.uniform(-5, 10)
                    if status in ["Alert", "Unacceptable"]:
                        temperature += random.uniform(5, 15)  # Higher temperature for problematic bearings

                    acceleration_rms = 0.5 + random.uniform(-0.2, 0.3)
                    if status in ["Alert", "Unacceptable"]:
                        acceleration_rms += random.uniform(0.3, 0.8)

                    velocity_rms = 0.3 + random.uniform(-0.1, 0.2)
                    if status in ["Alert", "Unacceptable"]:
                        velocity_rms += random.uniform(0.2, 0.5)

                    reading = {
                        "_id": f"READING_{bearing_id}_{day}_{hour}",
                        "machineId": bearing_id.replace("BEARING", "MACHINE"),
                        "bearingId": bearing_id,
                        "timestamp": timestamp,
                        "status": status,
                        "Axis_Id": f"AXIS_{bearing_id[-1]}",
                        "acceleration": {
                            "rms": round(acceleration_rms, 3),
                            "peak": round(acceleration_rms * 1.5, 3),
                            "crestFactor": round(random.uniform(2.0, 4.0), 2),
                            "kurtosis": round(random.uniform(2.5, 4.5), 2)
                        },
                        "velocity": {
                            "rms": round(velocity_rms, 3),
                            "peak": round(velocity_rms * 1.3, 3),
                            "crestFactor": round(random.uniform(1.8, 3.5), 2)
                        },
                        "temperature": round(temperature, 1),
                        "measurementType": "vibration_analysis",
                        "createdAt": timestamp
                    }

                    data.append(reading)

        return data

    def populate_sample_data(self):
        """Populate database with sample data."""
        if not self.db:
            return False

        try:
            # Clear existing data
            self.db.machines.delete_many({})
            self.db.bearings.delete_many({})
            self.db.data.delete_many({})

            # Insert sample data
            machines = self.generate_sample_machines()
            bearings = self.generate_sample_bearings()
            data = self.generate_sample_data()

            if machines:
                self.db.machines.insert_many(machines)
                logger.info(f"✅ Inserted {len(machines)} machines")

            if bearings:
                self.db.bearings.insert_many(bearings)
                logger.info(f"✅ Inserted {len(bearings)} bearings")

            if data:
                self.db.data.insert_many(data)
                logger.info(f"✅ Inserted {len(data)} sensor readings")

            return True
        except Exception as e:
            logger.error(f"❌ Error populating sample data: {e}")
            return False

    def get_database_stats(self):
        """Get database statistics."""
        if not self.db:
            return None

        try:
            stats = {
                "machines_count": self.db.machines.count_documents({}),
                "bearings_count": self.db.bearings.count_documents({}),
                "data_records_count": self.db.data.count_documents({}),
                "database_name": self.database_name,
                "collections": self.db.list_collection_names()
            }

            logger.info("📊 Database Statistics:")
            logger.info(f"   - Machines: {stats['machines_count']}")
            logger.info(f"   - Bearings: {stats['bearings_count']}")
            logger.info(f"   - Data Records: {stats['data_records_count']}")
            logger.info(f"   - Collections: {', '.join(stats['collections'])}")

            return stats
        except Exception as e:
            logger.error(f"❌ Error getting database stats: {e}")
            return None

def main():
    """Main function to set up the database."""
    print("🏭 Factory Monitoring Database Setup")
    print("=" * 50)

    # Initialize database seeder
    seeder = DatabaseSeeder()

    # Connect to database
    if not seeder.connect():
        print("❌ Cannot connect to MongoDB.")
        print("💡 To use MongoDB:")
        print("   1. Install MongoDB Community Server")
        print("   2. Start MongoDB service: net start MongoDB")
        print("   3. Or run mongod.exe manually")
        print("   4. Then run this script again")
        print("\n🚀 The application will work with mock data without MongoDB!")
        return False

    # Setup collections
    if not seeder.setup_collections():
        return False

    # Populate sample data
    if not seeder.populate_sample_data():
        return False

    # Get and display statistics
    stats = seeder.get_database_stats()
    if stats:
        print("\n" + "=" * 50)
        print("✅ Database setup completed successfully!")
        print(f"📊 Database: {stats['database_name']}")
        print(f"🏭 Machines: {stats['machines_count']}")
        print(f"⚙️  Bearings: {stats['bearings_count']}")
        print(f"📈 Data Records: {stats['data_records_count']}")
        print("=" * 50)
        print("🎉 Your Factory Monitoring Dashboard is ready!")
        print("🔌 Backend API: http://localhost:8000")
        print("📚 API Documentation: http://localhost:8000/docs")
        return True

    return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n⚠️  Database setup encountered issues, but the application will work with mock data.")
        print("🚀 You can still run the dashboard - it will use realistic sample data!")
