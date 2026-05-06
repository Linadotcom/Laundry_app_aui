import pymongo
from datetime import datetime

def log_order_to_mongo(order_data: dict) -> None:
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        db = client["laundry_nosql"]
        collection = db["order_logs"]
        
        document = {
            "order_id": order_data.get("order_id"),
            "student_id": order_data.get("student_id"),
            "machine_id": order_data.get("machine_id"),
            "service_type": order_data.get("service_type"),
            "total_price": float(order_data.get("total_price", 0.0)),
            "timestamp": datetime.utcnow(),
            "source": "flask_app"
        }
        
        result = collection.insert_one(document)
        print(f"✅ Successfully logged NoSQL order info to MongoDB with _id: {result.inserted_id}")
    except Exception as e:
        print(f"❌ Failed to log order to MongoDB: {e}")
