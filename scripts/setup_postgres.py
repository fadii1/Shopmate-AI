"""PostgreSQL Database Initializer for Khareed.

Run this script to create the 'khareed' database and all PostgreSQL tables:
    python scripts/setup_postgres.py --password YOUR_POSTGRES_PASSWORD
"""

import sys
import argparse
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.database import Base
import app.models


async def init_postgres(host, port, user, password, dbname):
    print(f"Connecting to PostgreSQL on {host}:{port} as user '{user}'...")
    db_url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}"

    try:
        engine = create_async_engine(db_url, echo=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print(f"🎉 Successfully created all Khareed tables in PostgreSQL '{dbname}'!")
        print("Tables created:")
        for table in Base.metadata.sorted_tables:
            print(f"  ✓ {table.name}")
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        print("\nTip: Agar 'database khareed does not exist' ka error aaye, pehle pgAdmin ya psql mein:")
        print("  CREATE DATABASE khareed;")
        print("phir is script ko dobara run karein.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize Khareed PostgreSQL Database")
    parser.add_argument("--host", default="localhost", help="PostgreSQL host")
    parser.add_argument("--port", default=5432, type=int, help="PostgreSQL port")
    parser.add_argument("--user", default="postgres", help="PostgreSQL username")
    parser.add_argument("--password", required=True, help="Your PostgreSQL password")
    parser.add_argument("--dbname", default="khareed", help="Database name (default: khareed)")

    args = parser.parse_args()
    asyncio.run(init_postgres(args.host, args.port, args.user, args.password, args.dbname))
