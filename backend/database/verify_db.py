#!/usr/bin/env python3
"""
Database verification script for MahaSaathi
Checks existing database and optionally adds test users
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

PG_DSN = os.getenv("PG_DSN")

def verify_database():
    """
    Verify existing database structure and data
    """
    if not PG_DSN:
        print("❌ Error: PG_DSN not found in .env file")
        sys.exit(1)
    
    try:
        # Connect to database
        print(f"🔌 Connecting to database...")
        conn = psycopg2.connect(PG_DSN)
        conn.autocommit = True
        
        print("✅ Database connection successful!\n")
        print("=" * 60)
        print("DATABASE VERIFICATION")
        print("=" * 60)
        
        with conn.cursor() as cur:
            # Check tables exist
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)
            tables = [row[0] for row in cur.fetchall()]
            print(f"\n📋 Tables found: {', '.join(tables)}")
            
            required_tables = ['locations', 'rfid_readers', 'rfid_activity', 'users']
            missing = [t for t in required_tables if t not in tables]
            if missing:
                print(f"⚠️  Missing tables: {', '.join(missing)}")
            else:
                print("✅ All required tables exist")
            
            # Count locations by category
            print("\n📍 Locations by category:")
            cur.execute("SELECT category, COUNT(*) FROM locations GROUP BY category ORDER BY category")
            total_locations = 0
            for row in cur.fetchall():
                print(f"   - {row[0]}: {row[1]}")
                total_locations += row[1]
            print(f"   TOTAL: {total_locations} locations")
            
            # Count RFID readers by zone
            print("\n📡 RFID Readers by zone:")
            cur.execute("SELECT zone, COUNT(*) FROM rfid_readers GROUP BY zone ORDER BY zone")
            for row in cur.fetchall():
                print(f"   - Zone {row[0]}: {row[1]} readers")
            
            # Count users
            cur.execute("SELECT COUNT(*) FROM users")
            user_count = cur.fetchone()[0]
            print(f"\n👥 Users: {user_count}")
            
            # Count recent RFID activity
            cur.execute("SELECT COUNT(*) FROM rfid_activity WHERE created_at >= now() - INTERVAL '5 minutes'")
            recent_activity = cur.fetchone()[0]
            print(f"📊 Recent RFID activity (last 5 min): {recent_activity}")
            
            # Count total RFID activity
            cur.execute("SELECT COUNT(*) FROM rfid_activity")
            total_activity = cur.fetchone()[0]
            print(f"📊 Total RFID activity: {total_activity}")
            
            # Suggest adding test users if none exist
            if user_count == 0:
                print("\n" + "=" * 60)
                print("⚠️  No users found in database")
                print("=" * 60)
                response = input("\nWould you like to add test users? (y/n): ").strip().lower()
                
                if response == 'y':
                    add_test_users(cur)
                    print("\n✅ Test users added successfully!")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ Database verification complete!")
        print("=" * 60)
        print("\n💡 Next steps:")
        print("   1. Run RAG ingestion: python chatbot/rag_ingest.py")
        print("   2. Test CLI: python chatbot/main_cli.py --ingest")
        
    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

def add_test_users(cur):
    """
    Add test users to the database
    """
    print("\n📝 Adding test users...")
    
    # Get some reader IDs
    cur.execute("SELECT id, zone FROM rfid_readers ORDER BY id LIMIT 3")
    readers = cur.fetchall()
    
    if not readers:
        print("⚠️  No RFID readers found. Cannot add test users.")
        return
    
    # Insert test users
    test_users = [
        ('test_user_001', readers[0][0], readers[0][1]),
        ('test_user_002', readers[1][0] if len(readers) > 1 else readers[0][0], readers[1][1] if len(readers) > 1 else readers[0][1]),
        ('test_user_003', readers[2][0] if len(readers) > 2 else readers[0][0], readers[2][1] if len(readers) > 2 else readers[0][1]),
    ]
    
    for user_uid, reader_id, zone in test_users:
        cur.execute("""
            INSERT INTO users (user_uid, last_seen_reader, last_seen_zone, last_seen_time)
            VALUES (%s, %s, %s, now() - INTERVAL '2 minutes')
            ON CONFLICT (user_uid) DO NOTHING
        """, (user_uid, reader_id, zone))
        
        # Add some RFID activity for the user
        cur.execute("""
            INSERT INTO rfid_activity (tag_uid, user_uid, reader_id, zone, created_at)
            VALUES (%s, %s, %s, %s, now() - INTERVAL '3 minutes')
        """, (f'TAG_{user_uid}', user_uid, reader_id, zone))
    
    print(f"   Added {len(test_users)} test users")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("MahaSaathi Database Verification")
    print("=" * 60)
    verify_database()
