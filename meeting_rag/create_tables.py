from database.db import engine, Base
import database.models

Base.metadata.create_all(bind=engine)

print("Tables created successfully")