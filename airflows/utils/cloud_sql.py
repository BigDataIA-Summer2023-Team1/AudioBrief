import os
from sqlalchemy.orm import sessionmaker
from google.cloud.sql.connector import Connector
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, select, exists, or_, JSON


def connect_to_sql():
    try:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "./utils/metadata-sql.json"

        return Connector().connect(
            instance_connection_string=os.environ['INSTANCE_CONNECTION_NAME'],
            driver=os.environ["DB_DRIVER"],
            user=os.environ["DB_USER"],
            password=os.environ['DB_PASS'],
            db=os.environ["DB_NAME"]
        )
    except Exception as e:
        print(str(e))


def get_sql_client(conn):
    try:
        return create_engine("postgresql+pg8000://", creator=conn)
    except Exception as e:
        print(str(e))


def check_if_books_exist(engine, data):
    try:
        # Create a session
        Session = sessionmaker(bind=engine)
        session = Session()

        # Define the metadata
        metadata = MetaData(bind=engine)

        books_table = Table(
            'books', metadata,
            Column('book_id', String(36), primary_key=True),
            Column('source_id', Integer),
            Column('title', String(255)),
            Column('author', String(80)),
            Column('category', String(20)),
            Column('publish', Integer),
            Column('pages', Integer),
            Column('url', String(225)),
            Column('chapters', JSON)
        )

        # Execute a SELECT EXISTS query with WHERE clause
        query = select([exists().where(books_table.c.title == data["title"])])
        result = engine.execute(query).scalar()

        # Close the session & close connection
        session.close()
        engine.dispose()

        return result
    except Exception as e:
        print(str(e))


def fetch_last_read_book_id(engine):
    try:
        # Create a session
        Session = sessionmaker(bind=engine)
        session = Session()

        # Define the metadata
        metadata = MetaData(bind=engine)

        last_read_table = Table(
            'last_read_data', metadata,
            Column('source_id', Integer),
        )

        # Execute a SELECT EXISTS query with WHERE clause
        query = select([last_read_table]).order_by(last_read_table.c.source_id.desc()).limit(1)

        # Execute the query
        result = engine.execute(query).fetchone()

        # Close the session & close connection
        session.close()
        engine.dispose()

        return result if result else 0
    except Exception as e:
        print(str(e))


def insert_to_books_table(engine, data):
    try:
        # Create a session
        Session = sessionmaker(bind=engine)
        session = Session()

        # Define the metadata
        metadata = MetaData(bind=engine)

        books_table = Table(
            'books', metadata,
            Column('book_id', String(36), primary_key=True),
            Column('source_id', Integer),
            Column('title', String(80)),
            Column('author', String(80)),
            Column('category', String(20)),
            Column('publish', Integer),
            Column('pages', Integer),
            Column('url', String(225)),
            Column('chapters', JSON)
        )

        # Create an insert statement
        stmt = books_table.insert().values(data)

        # Execute the insert statement
        session.execute(stmt)

        # Commit the transaction
        session.commit()

        # Close the session
        session.close()
        engine.dispose()
    except Exception as e:
        print(str(e))


def insert_to_last_read_table(engine, data):
    try:
        # Create a session
        Session = sessionmaker(bind=engine)
        session = Session()

        # Define the metadata
        metadata = MetaData(bind=engine)

        # table = Table(table_name, metadata, autoload=True, autoload_with=engine)
        last_read_table = Table(
            'last_read_data', metadata,
            Column('source_id', Integer),
        )

        # Create an insert statement
        stmt = last_read_table.insert().values(data)

        # Execute the insert statement
        session.execute(stmt)

        # Commit the transaction
        session.commit()

        # Close the session
        session.close()
        engine.dispose()
    except Exception as e:
        print(str(e))
