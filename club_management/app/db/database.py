from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings


engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    from app.models import user, club, activity

    Base.metadata.create_all(engine)


def execute_schema_sql(sql):
    connection = engine.connect()
    try:
        connection.execute(text(sql))
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def update_soft_delete_schema():
    inspector = inspect(engine)
    has_deleted_at = False
    for column in inspector.get_columns('clubs'):
        if column['name'] == 'deleted_at':
            has_deleted_at = True

    if not has_deleted_at:
        execute_schema_sql('ALTER TABLE clubs ADD COLUMN deleted_at DATETIME NULL')

    has_index = False
    for index in inspector.get_indexes('clubs'):
        if index['name'] == 'ix_clubs_deleted_at':
            has_index = True

    if not has_index:
        execute_schema_sql('CREATE INDEX ix_clubs_deleted_at ON clubs (deleted_at)')


def check_tables():
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    for table_name in Base.metadata.tables:
        if table_name not in existing_tables:
            raise RuntimeError(f'Chưa tạo được bảng {table_name}')

        existing_columns = []
        for column in inspector.get_columns(table_name):
            existing_columns.append(column['name'])

        table = Base.metadata.tables[table_name]
        for column in table.columns:
            if column.name not in existing_columns:
                raise RuntimeError(f'Bảng {table_name} còn thiếu cột {column.name}')


def initialize_database():
    create_tables()
    update_soft_delete_schema()
    check_tables()
    print('Database đã sẵn sàng.')


if __name__ == '__main__':
    from app.db import database
    database.initialize_database()
