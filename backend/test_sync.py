"""
Test script for Redis-PostgreSQL synchronization
"""
import asyncio
import sys
import os

# Add the parent directory to sys.path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.redis_client import redis_client
from app.services.redis_postgres_sync import sync_service
from app.db.postgres_manager.db import SessionLocal
from app.db.postgres_manager.managers.messages import MessageManager
from app.db.postgres_manager.managers.sessions import SessionManager
from app.db.postgres_manager.managers.users import UserManager
from app.db.postgres_manager.managers.groups import GroupManager

async def test_sync():
    """Test the Redis-PostgreSQL sync functionality"""
    print("🧪 Testing Redis-PostgreSQL Sync")
    print("=" * 50)
    
    # Test 1: Check Redis connection
    print("1. Testing Redis connection...")
    if redis_client.is_connected():
        print("✅ Redis connected")
    else:
        print("❌ Redis not connected")
        return
    
    # Test 2: Create a test session in Redis
    print("\n2. Creating test session in Redis...")
    test_session_id = "test_session_123"
    test_session_data = {
        "session_id": test_session_id,
        "group_id": 1,
        "created_by": 1,
        "topic": "Test Sync Session",
        "created_at": "2024-01-01T10:00:00",
        "updated_at": "2024-01-01T10:00:00",
        "messages": [
            {
                "content": "Hello, this is a test message",
                "sender_id": 1,
                "timestamp": "2024-01-01T10:00:00"
            },
            {
                "content": "This is another test message",
                "sender_id": 2,
                "timestamp": "2024-01-01T10:01:00"
            }
        ]
    }
    
    success = redis_client.store_session(test_session_id, test_session_data)
    if success:
        print(f"✅ Test session {test_session_id} created in Redis")
    else:
        print(f"❌ Failed to create test session in Redis")
        return
    
    # Test 3: Manual sync
    print("\n3. Running manual sync...")
    try:
        await sync_service.manual_full_sync()
        print("✅ Manual sync completed")
    except Exception as e:
        print(f"❌ Manual sync failed: {e}")
        return
    
    # Test 4: Verify data in PostgreSQL
    print("\n4. Verifying data in PostgreSQL...")
    db = SessionLocal()
    try:
        # Check if users were created
        user1 = UserManager.get_user_by_id(db, 1)
        user2 = UserManager.get_user_by_id(db, 2)
        print(f"✅ User 1 exists: {user1 is not None}")
        print(f"✅ User 2 exists: {user2 is not None}")
        
        # Check if group was created
        group = GroupManager.get_group_by_id(db, 1)
        print(f"✅ Group exists: {group is not None}")
        
        # Check if session was created
        session_id_int = int(test_session_id.split('_')[-1]) if test_session_id.split('_')[-1].isdigit() else hash(test_session_id) % (2**31)
        session = SessionManager.get_session_by_id(db, session_id_int)
        print(f"✅ Session exists: {session is not None}")
        
        # Check if messages were created
        if session:
            messages = MessageManager.get_messages_by_session(db, session_id_int)
            print(f"✅ Messages synced: {len(messages)} messages found")
            for i, msg in enumerate(messages):
                print(f"   Message {i+1}: {msg.content[:50]}...")
        
    finally:
        db.close()
    
    # Test 5: Test real-time sync by adding a message
    print("\n5. Testing real-time sync...")
    new_message = {
        "content": "This message should sync automatically",
        "sender_id": 1,
        "timestamp": "2024-01-01T10:02:00"
    }
    
    redis_client.add_message_to_session(test_session_id, new_message)
    print("✅ Added new message to Redis session")
    
    # Wait a moment for sync to happen
    await asyncio.sleep(2)
    
    # Check if the new message appears in PostgreSQL
    db = SessionLocal()
    try:
        messages = MessageManager.get_messages_by_session(db, session_id_int)
        print(f"✅ Total messages after real-time sync: {len(messages)}")
    finally:
        db.close()
    
    print("\n🎉 Sync test completed!")

if __name__ == "__main__":
    asyncio.run(test_sync())
