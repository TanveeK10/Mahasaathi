#!/usr/bin/env python3
"""
Database setup script for MahaSaathi
Initializes PostgreSQL database with schema and sample data
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

PG_DSN = os.getenv("PG_DSN")

def setup_database():
    """
    Execute schema.sql to create tables and insert sample data
    """
    if not PG_DSN:
        print("❌ Error: PG_DSN not found in .env file")
        sys.exit(1)
    
    schema_file = os.path.join(os.path.dirname(__file__), 'schema.sql')
    
    if not os.path.exists(schema_file):
        print(f"❌ Error: schema.sql not found at {schema_file}")
        sys.exit(1)
    
    try:
        # Connect to database
        print(f"🔌 Connecting to database...")
        conn = psycopg2.connect(PG_DSN)
        conn.autocommit = True
        
        # Read schema file
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Execute schema
        print("📝 Executing schema.sql...")
        with conn.cursor() as cur:
            cur.execute(schema_sql)
        
        # Verify tables created
        print("\n✅ Database setup complete!")
        print("\n📊 Verification:")
        
        with conn.cursor() as cur:
            # Count locations by category
            cur.execute("SELECT category, COUNT(*) FROM locations GROUP BY category ORDER BY category")
            print("\nLocations by category:")
            for row in cur.fetchall():
                print(f"  - {row[0]}: {row[1]}")
            
            # Count RFID readers by zone
            cur.execute("SELECT zone, COUNT(*) FROM rfid_readers GROUP BY zone ORDER BY zone")
            print("\nRFID Readers by zone:")
            for row in cur.fetchall():
                print(f"  - Zone {row[0]}: {row[1]} readers")
            
            # Count users
            cur.execute("SELECT COUNT(*) FROM users")
            user_count = cur.fetchone()[0]
            print(f"\nUsers: {user_count}")
            
            # Count recent RFID activity
            cur.execute("SELECT COUNT(*) FROM rfid_activity WHERE created_at >= now() - INTERVAL '5 minutes'")
            recent_activity = cur.fetchone()[0]
            print(f"Recent RFID activity (last 5 min): {recent_activity}")
        
        conn.close()
        print("\n✅ All done! Database is ready for use.")
        
    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("MahaSaathi Database Setup")
    print("=" * 60)
    setup_database()
