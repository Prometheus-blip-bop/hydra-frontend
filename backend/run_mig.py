import os
from dotenv import load_dotenv
load_dotenv()
os.system('alembic revision --autogenerate -m "Add BYOK fields"')
os.system('alembic upgrade head')
