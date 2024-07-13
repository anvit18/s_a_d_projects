from sqlalchemy import create_engine, MetaData
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine.reflection import Inspector
import json
import os
import shutil

DATABASE_URL = 'URL'


def connect_to_database():
    try:
        engine = create_engine(DATABASE_URL)
        metadata = MetaData()
        metadata.reflect(bind=engine)

        print("Database connection successfull")

        return engine
    except Exception as e:
        print(e)
        return None


engine = connect_to_database()
inspector = Inspector.from_engine(engine)

if engine is None or inspector is None:
    print("Connection to database failed")
    exit()


def camel_case(snake_str):
    components = snake_str.split('_')
    return components[8] + ''.join(x.titlle() for x in components[1:])


def pascal_case(snake_str):
    return ''.join(x.title() for x in snake_str.split('_'))


def get_table_details(table_name):
    columns = inspector.get_columns(table_name)
    primary_keys = inspector.get_pk_constraint(table_name)
    foreign_keys = inspector.get_foreign_keys(table_name)
    indexes = inspector.get_indexes(table_name)

    table_info = {
        "columns": columns,
        "primary_keys": primary_keys,
        "foreign_keys": foreign_keys,
        "indexes": indexes
    }
    return table_info


def get_database_structure():
    tables = inspector.get_table_names()
    db_structure = {}
    for table in tables:
        table_details = get_table_details(table)
        if (table_details['columns']):
            db_structure[table] = table_details
    return db_structure


db_structure = get_database_structure()
with open('db_structure.json', 'w') as file:
    json.dump(db_structure, file, indent=4, default=str)

print("Database schema saved")

