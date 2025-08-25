# Redis-PostgreSQL Synchronization

This document explains the Redis-PostgreSQL synchronization system that keeps your local PostgreSQL database in sync with the Redis cloud database.

## Overview

The sync system automatically detects changes in Redis and updates PostgreSQL accordingly. It works in two modes:

1. **Real-time Sync**: Listens for Redis events and syncs changes as they happen
2. **Manual Sync**: Allows you to trigger a full sync at any time

## Architecture

```
Redis Cloud Database
       ↓ (pub/sub notifications)
   Sync Service
       ↓ (SQL operations)
Local PostgreSQL Database
```

### Components

- **RedisPgSyncService**: Main sync service that handles real-time synchronization
- **Background Tasks**: Manages the lifecycle of the sync service
- **API Endpoints**: Provides manual control over sync operations
- **Redis Client**: Enhanced with notification publishing

## Setup

### 1. Environment Variables

Make sure these variables are set in your `.env` file:

```env
# Redis Configuration
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_USERNAME=your-username
REDIS_PASSWORD=your-password
REDIS_SESSION_TTL_HOURS=24

# PostgreSQL Configuration  
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Verify Setup

```bash
python check_setup.py
```

## How It Works

### Automatic Sync

When the FastAPI application starts:

1. The sync service starts listening for Redis keyspace notifications
2. It subscribes to session update events
3. When a session is created or updated in Redis, it automatically syncs to PostgreSQL
4. An initial full sync runs on startup

### Data Mapping

The sync service maps Redis session data to PostgreSQL tables:

- **Sessions**: Redis sessions → `sessions` table
- **Messages**: Session messages → `messages` table  
- **Users**: Message senders → `users` table (auto-created if needed)
- **Groups**: Session groups → `groups` table (auto-created if needed)

### Conflict Resolution

- **Deduplication**: Messages are deduplicated based on content
- **User Creation**: Missing users are automatically created with basic info
- **Group Creation**: Default groups are created as needed
- **ID Mapping**: String session IDs are converted to integers for PostgreSQL

## API Endpoints

### Manual Sync

Trigger a full sync from Redis to PostgreSQL:

```bash
curl -X POST http://localhost:8000/api/v1/sync/manual
```

### Check Sync Status

Get the current status of the sync service:

```bash
curl http://localhost:8000/api/v1/sync/status
```

### Sync Specific Session

Sync a particular session:

```bash
curl -X POST http://localhost:8000/api/v1/sync/session/your_session_id
```

### Compare Data

Compare session counts between Redis and PostgreSQL:

```bash
curl http://localhost:8000/api/v1/sync/sessions/compare
```

## Testing

### Run the Test Script

```bash
cd backend
python test_sync.py
```

This test will:
1. Create a test session in Redis
2. Run manual sync
3. Verify data appears in PostgreSQL
4. Test real-time sync by adding a message

### Monitor Logs

The sync service logs all operations. Look for these log messages:

- `✅ Redis Cloud connection successful!`
- `Started Redis keyspace notification listener`
- `Successfully synced session X to PostgreSQL`
- `Manual sync completed`

## Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   - Check your Redis credentials and network connectivity
   - Verify `REDIS_HOST`, `REDIS_PORT`, `REDIS_USERNAME`, `REDIS_PASSWORD`

2. **PostgreSQL Connection Failed**
   - Ensure PostgreSQL is running
   - Check your `DATABASE_URL`
   - Verify database permissions

3. **Sync Not Working**
   - Check if keyspace notifications are enabled in Redis
   - Look for error messages in the application logs
   - Try running manual sync: `POST /api/v1/sync/manual`

4. **Missing Data**
   - Some data might be filtered out during sync (e.g., messages without sender_id)
   - Check the logs for "Skipped" or "Error" messages

### Debug Commands

```bash
# Check configuration
python check_setup.py

# Test sync manually
python test_sync.py

# Check sync status via API
curl http://localhost:8000/api/v1/sync/status

# View logs
tail -f logs/app.log  # if logging to file
```

### Performance Considerations

- The sync service processes events in real-time but includes small delays to prevent overwhelming the database
- Large Redis datasets may take time for initial sync
- Consider running manual sync during off-peak hours for large datasets

## Monitoring

### Health Checks

The sync service provides status information via the `/sync/status` endpoint:

```json
{
  "sync_enabled": true,
  "redis_connected": true, 
  "service_status": "running"
}
```

### Metrics to Monitor

- Sync success/failure rates
- Time between Redis update and PostgreSQL sync
- Number of sessions synced
- Error frequencies

## Customization

### Adding New Data Types

To sync additional data types:

1. Add detection logic in `_handle_redis_event()`
2. Create sync method similar to `_sync_session_to_postgres()`
3. Add appropriate PostgreSQL table mappings

### Changing Sync Behavior

Modify the `RedisPgSyncService` class to:
- Change deduplication logic
- Adjust error handling
- Add data transformations
- Implement custom conflict resolution

### Event Filtering

To sync only specific events, modify the pub/sub subscriptions in `start_sync_listener()`.

## Security

- Never log sensitive data like passwords
- Redis credentials are stored securely in environment variables
- PostgreSQL connections use proper authentication
- API endpoints can be secured with authentication middleware

## Contributing

When making changes to the sync system:

1. Test with the provided test script
2. Update this documentation
3. Add appropriate error handling
4. Include logging for debugging
5. Consider backward compatibility
