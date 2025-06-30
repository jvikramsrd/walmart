from pymongo import MongoClient
import os
import subprocess

def check_and_populate():
    """
    Checks if the database is empty and runs the populate_sample_data.py script if it is.
    """
    try:
        # --- Database Connection ---
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        mongodb_db = os.getenv("MONGODB_DB", "walmart")
        client = MongoClient(mongodb_uri)
        db = client[mongodb_db]

        # --- Check if any collection has data ---
        # Using 'orders' as a representative collection
        if db.orders.count_documents({}) == 0:
            print("Database appears to be empty. Populating with sample data...")
            
            # --- Run the population script ---
            # Construct the path to the script relative to this file's location
            current_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(current_dir, "populate_sample_data.py")

            # Execute the script
            process = subprocess.run(
                ["python", script_path],
                capture_output=True,
                text=True,
                check=True 
            )
            print(process.stdout)
            if process.stderr:
                print("Error during data population:")
                print(process.stderr)
        else:
            print("Database already contains data. Skipping population.")

    except Exception as e:
        print(f"An error occurred during the database check: {e}")

if __name__ == "__main__":
    check_and_populate() 