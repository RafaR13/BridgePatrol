from sqlalchemy import text
from db.connection import get_session


def test_database_connection():
    session = get_session()

    try:
        session.execute(text("SELECT 1"))
    finally:
        session.close()


if __name__ == "__main__":
    test_database_connection()