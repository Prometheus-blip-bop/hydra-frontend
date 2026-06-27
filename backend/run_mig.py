import os
from dotenv import load_dotenv
load_dotenv()
os.environ["COMMON_AWS_REGION"] = "us-east-1"
os.environ["COMMON_AWS_ENDPOINT_URL"] = "http://localhost:4566"
os.environ["COMMON_KEY_ENCRYPTION_KEY_ARN"] = "dummy"
os.environ["COMMON_API_KEY_HASHING_SECRET"] = "dummy"
os.environ["SERVER_OPENAI_API_KEY"] = "dummy"
os.environ["SERVER_ENVIRONMENT"] = "local"
os.environ["COMMON_DB_URL"] = "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"

os.environ["ALEMBIC_DB_SCHEME"] = "postgresql+psycopg"
os.environ["ALEMBIC_DB_USER"] = "postgres"
os.environ["ALEMBIC_DB_PASSWORD"] = "postgres"
os.environ["ALEMBIC_DB_HOST"] = "localhost"
os.environ["ALEMBIC_DB_PORT"] = "5432"
os.environ["ALEMBIC_DB_NAME"] = "postgres"

os.system('alembic revision --autogenerate -m "Add BYOK fields"')
os.system('alembic upgrade head')
