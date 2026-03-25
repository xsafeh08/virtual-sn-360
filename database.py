from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///E:/virtual_sn_360.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Propriete(Base):
    __tablename__ = "proprietes"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    nom = Column(String)
    ville = Column(String)
    prix = Column(Float)
    surface = Column(Integer)
    disponible = Column(Boolean, default=True)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()