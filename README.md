## Set up environment and dependencies

```
mkdir backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install fastapi uvicorn python-dotenv
python -m pip install asyncpg
python -m pip install psycopg2-binary
```

## Run app

```
uvicorn app.main:app --reload
```

## Run Postgresql

```
docker compose up -d
set -a; source .env; set +a
docker exec -it postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB

```

## Integrate postgresql with Fastapi

```
python -m pip install "SQLAlchemy>=2.0" alembic psycopg python-dotenv
python -c "from app.core.config import settings; print(settings.DATABASE_URL)"

```

## Alembic migration

```
python -m alembic --version
alembic init alembic
```

## Create BASE

```
python -c "from app.db.base import Base; print(Base)"
```

## Run migration

```
alembic revision --autogenerate -m "init schema"
alembic upgrade head
```

## Test engine + driver

```
python - << 'EOF'
from sqlalchemy import text
import asyncio
from app.db.session import async_engine

async def t():
    async with async_engine.connect() as c:
        await c.execute(text("SELECT 1"))
        print("OK")

asyncio.run(t())
EOF
```

## Test schema

```
python - << 'EOF'
from app.schemas.tag import TagCreate
print(TagCreate.model_json_schema())
EOF
```
