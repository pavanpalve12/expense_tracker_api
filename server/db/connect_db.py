from sqlalchemy import create_engine, Column, Integer, String, Numeric, Date, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from pathlib import Path as path
from datetime import date, datetime

db_name = "expense_tracker_db.sqlite"
this_file = path(__file__)
this_dir = this_file.parent
db_path = this_dir / db_name

db_url = f"sqlite:///{db_path.as_posix()}"
print(f"File -> {this_file}\nCurrent Dir -> {this_dir}\ndb path -> {db_path}\n db url -> {db_url}")

engine = create_engine(url=db_url)
sessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit = False)
Base = declarative_base()

Base.metadata.create_all(bind = engine)