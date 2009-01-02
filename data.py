from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    def __init__(self, name, description):
        self.name = name
        self.description = description
    
    def __repr__(self):
        return '<Project: %s>' %self.name

db = 'sqlite:///blog.db'
engine = create_engine(db)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
