from logging import getLogger
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from ..settings import DATABASE_URL


logger = getLogger('mediafeed.databases')
Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def initdb():
    logger.info('Criando base de dados')
    Base.metadata.create_all(engine, checkfirst=True)
