# Chat Backend

A backend for chat and collaboration, using SQLAlchemy ORM and PostgreSQL.

## Setup

1. Create a `.env` file with your database URL:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run migrations using the provided `schema.sql`.

## Structure
- Models: SQLAlchemy ORM models for each table
- Managers: CRUD logic for each entity
- Services: Business logic
- `db.py`: Database connection
