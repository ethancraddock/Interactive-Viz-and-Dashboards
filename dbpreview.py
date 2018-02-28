import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect

# Create the connection engine
engine = create_engine("sqlite:///belly_button_biodiversity.sqlite")

# Create inspector and connect it to the engine
inspector = inspect(engine)

# Collect the names of the tables within the db
tables = inspector.get_table_names()

# using the inspector to print the column names of tables
columns = inspector.get_columns(tables)

for column in columns:
    print(column['name'], column['type'])