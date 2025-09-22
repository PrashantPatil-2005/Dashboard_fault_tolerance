from pymongo import MongoClient
import json

client = MongoClient("mongodb://localhost:27017/")
db = client["factory_db"]

# Open a file to write
with open("factory_data_data.txt", "w",encoding="utf-8") as f:

    # Machines
    """f.write("=== Machines ===\n")
    for m in db.machines.find():
        f.write(json.dumps(m, default=str) + "\n")  # default=str converts ObjectId/datetime to string
    f.write(f"Total Machines: {db.machines.count_documents({})}\n\n")

    # Bearings
    f.write("=== Bearings ===\n")
    for b in db.bearings.find():
        f.write(json.dumps(b, default=str) + "\n")
    f.write(f"Total Bearings: {db.bearings.count_documents({})}\n\n")

    # Data
    """
    f.write("=== Data ===\n")
    for d in db.data.find({}, {"rawData": 0}): 
        f.write(json.dumps(d, default=str) + "\n")
    f.write(f"Total Data Records: {db.data.count_documents({})}\n\n")

print("Data exported to factory_data.txt successfully!")
