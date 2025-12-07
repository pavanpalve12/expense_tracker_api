from debugpy.adapter.components import missing
from fastapi import FastAPI
from sqlalchemy import inspect
from server.db.connect_db import engine, Base
from server.utils.tabulate_data import display_data_table

def lifespan(app: FastAPI):
    # ----------- START UP --------------
    inspector = inspect(engine)

    defined_tables = set(Base.metadata.tables.keys()) # <--- tables defined in Base
    existing_tables = set(inspector.get_table_names()) # <--- tables already present

    missing_tables = defined_tables.difference(existing_tables)
    print(f"Defined Tables -> {defined_tables}\nExisting Tables -> {existing_tables}\nMissing tables ->{missing_tables}")

    if missing_tables:
        Base.metadata.create_all(
            bind=engine,
            tables= [Base.metadata.tables[table] for table in missing_tables],
            checkfirst=True
        )
        print(f"Missing Tables -> {missing_tables} are created.")
    else:
        print(f"Defined Tables -> {defined_tables} are already created.")

    for table in inspect(engine).get_table_names():
        print(f"{'=' * 35} \033[1;3m{table}\033[0m {'=' * 35}")
        display_data_table(inspector.get_columns(table))

    yield
    # ----------- SHUT DOWN -------------
    print("API is shutting down")