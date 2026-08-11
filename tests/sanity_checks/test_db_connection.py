from sqlalchemy import text
from db.database import get_session


def test_database_connection():
    session = get_session()

    try:
        result = session.execute(text("SELECT 1")).scalar()
        assert result == 1
    finally:
        session.close()


if __name__ == "__main__":
    test_database_connection()
