from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from utils.cfg import cfg_db


engine = create_engine(f'sqlite:///{cfg_db.DATABASE_NAME}.sqlite')
Session = sessionmaker(bind=engine)

Base = declarative_base()


def create_db():
    Base.metadata.create_all(engine)

