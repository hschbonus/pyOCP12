import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from epicevents.models import Base

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)


def init_db():
    Base.metadata.create_all(engine)
