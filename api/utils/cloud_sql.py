import os
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from google.cloud.sql.connector import Connector
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, select, exists, or_, JSON, distinct

load_dotenv("../.env")


def connect_to_sql():
    try:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "./utils/metadata-sql.json"

        return Connector().connect(
            instance_connection_string="audiobrief:us-east1:audio-brief",
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

def check_if_user_exist(engine, data):
    try:
        # Create a session
        Session = sessionmaker(bind=engine)
        session = Session()

        # Define the metadata
        metadata = MetaData(bind=engine)

        users_table = Table(
            'users', metadata,
            Column('email', String(50), primary_key=True),
            Column('password', String(255)),
            Column('plan', String(80)),
            Column('role', String(20))
        )

        # Execute a SELECT EXISTS query with WHERE clause
        query = select([exists().where(users_table.c.email == data["email"])])
        result = engine.execute(query).scalar()

        # Close the session & close connection
        session.close()
        engine.dispose()

        return result
    except Exception as e:
        print(str(e))


def fetch_user_by_email(engine, data):
    try:
        # Create a session
        Session = sessionmaker(bind=engine)
        session = Session()

        # Define the metadata
        metadata = MetaData(bind=engine)

        users_table = Table(
            'users', metadata,
            Column('email', String(50), primary_key=True),
            Column('password', String(255)),
            Column('plan', String(80)),
            Column('role', String(20))
        )

        # Execute a SELECT EXISTS query with WHERE clause
        stmt = select(users_table.c.email, users_table.c.password, users_table.c.plan, users_table.c.role).where(users_table.c.email == data["email"])
        result = engine.execute(stmt).fetchone()

        result = {"email": result[0], "password": result[1], "plan": result[2], "role": result[3]}

        # Close the session & close connection
        session.close()
        engine.dispose()

        return result
    except Exception as e:
        print(str(e))


def insert_to_users_table(engine, data):
    try:
        # Create a session
        Session = sessionmaker(bind=engine)
        session = Session()

        # Define the metadata
        metadata = MetaData(bind=engine)

        # table = Table(table_name, metadata, autoload=True, autoload_with=engine)
        users_table = Table(
            'users', metadata,
            Column('email', String(50), primary_key=True),
            Column('password', String(255)),
            Column('plan', String(80)),
            Column('role', String(20))
        )

        # Create an insert statement
        stmt = users_table.insert().values(data)

        # Execute the insert statement
        session.execute(stmt)

        # Commit the transaction
        session.commit()

        # Close the session
        session.close()

        # engine dispose
        engine.dispose()
    except Exception as e:
        print(str(e))

def fetch_authors(engine):
    try:
        # Create a session
        Session = sessionmaker(bind=engine)
        session = Session()

        # Define the metadata
        metadata = MetaData(bind=engine)

        # table = Table(table_name, metadata, autoload=True, autoload_with=engine)
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
        stmt = select(distinct(books_table.c.author))
        authors = engine.execute(stmt).fetchall()

        session.close()
        engine.dispose()

        return authors
    except Exception as e:
        print(str(e))


def fetch_books_by_author(engine, data):
    try:
        # Create a session
        Session = sessionmaker(bind=engine)
        session = Session()

        # Define the metadata
        metadata = MetaData(bind=engine)

        # table = Table(table_name, metadata, autoload=True, autoload_with=engine)
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
        if "author" in data:
            stmt = select(distinct(books_table.c.title), books_table.c.book_id,
                          books_table.c.chapters).where(books_table.c.author == data["author"])
            books = engine.execute(stmt).fetchall()
        else:
            stmt = select(distinct(books_table.c.title), books_table.c.book_id,
                          books_table.c.chapters)
            books = engine.execute(stmt).fetchall()

        books = [{"id": book[0], "title": book[1], "chapters": book[2]} for book in books]

        session.close()
        engine.dispose()

        return books
    except Exception as e:
        print(str(e))
