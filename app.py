import sqlite3
import json
import os
from datetime import date, datetime

# Configuration
DB_FILE = 'trade_guardian_v4 (15).db'  # Rename this if your file is named differently
OUTPUT_FILE = 'trade_data.json'

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return str(obj)

def extract_data():
    if not os.path.exists(DB_FILE):
        print(f"Error: Database file '{DB_FILE}' not found.")
        return

    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        print("--- Connecting to Database ---")

        # 1. Extract Trades
        print("Extracting Trades...")
        trades = []
        try:
            cursor.execute("SELECT * FROM trades")
            rows = cursor.fetchall()
            for row in rows:
                trades.append(dict(row))
            print(f"  Found {len(trades)} trades.")
        except sqlite3.Error as e:
            print(f"  Error reading trades: {e}")

        # 2. Extract Snapshots
        print("Extracting Snapshots...")
        snapshots = {}
        try:
            # Order by date to ensure charts are correct
            cursor.execute("SELECT * FROM snapshots ORDER BY snapshot_date ASC")
            rows = cursor.fetchall()
            for row in rows:
                row_dict = dict(row)
                t_id = row_dict.get('trade_id')
                if t_id:
                    if t_id not in snapshots:
                        snapshots[t_id] = []
                    snapshots[t_id].append(row_dict)
            print(f"  Found snapshots for {len(snapshots)} trades.")
        except sqlite3.Error as e:
            print(f"  Error reading snapshots: {e}")

        # 3. Extract Strategy Config
        print("Extracting Strategy Config...")
        strategies = []
        try:
            cursor.execute("SELECT * FROM strategy_config")
            rows = cursor.fetchall()
            for row in rows:
                strategies.append(dict(row))
            print(f"  Found {len(strategies)} strategies.")
        except sqlite3.Error as e:
            print(f"  Error reading strategy_config: {e}")
            
        conn.close()

        # Construct Final JSON Structure
        data = {
            "trades": trades,
            "snapshots": snapshots,
            "strategies": strategies,
            "meta": {
                "generated_at": datetime.now().isoformat(),
                "source": DB_FILE
            }
        }

        # Write to file
        print(f"--- Writing to {OUTPUT_FILE} ---")
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(data, f, default=json_serial, indent=2)
        
        print("Success! You can now load 'trade_data.json' into the Trade Analyzer App.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    extract_data()
