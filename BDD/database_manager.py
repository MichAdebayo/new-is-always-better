# database.py
from sqlmodel import SQLModel, create_engine 
from models import Film, Person, Featuring

# URL de la base de données SQLite
DATABASE_URL = "sqlite:///./analytic_database.db"

def get_engine() :
    engine = create_engine(DATABASE_URL)
    return engine

# Fonction pour créer la base de données et les tables
def create_db():
    engine = get_engine()
    SQLModel.metadata.create_all(engine)

