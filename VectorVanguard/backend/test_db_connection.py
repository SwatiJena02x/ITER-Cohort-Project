import sys

from sqlalchemy import create_engine, text

from app.core.config import settings


def test_connection():
    print(f"[*] Application: {settings.APP_NAME}")
    print(
        f"[*] Target: {settings.DB_HOST}:{settings.DB_PORT}/"
        f"{settings.DB_NAME}"
    )

    try:
        engine = create_engine(
            settings.SQLALCHEMY_DATABASE_URI,
            echo=False,
        )

        with engine.connect() as connection:
            version = connection.execute(
                text("SELECT version();")
            ).scalar_one()

            database = connection.execute(
                text("SELECT current_database();")
            ).scalar_one()

            print("\n[SUCCESS] Connected to PostgreSQL!")
            print(f" -> Database: {database}")
            print(f" -> Server: {version}")

            return True

    except Exception as error:
        print(f"\n[ERROR] Connection failed: {error}", file=sys.stderr)
        return False

    finally:
        if "engine" in locals():
            engine.dispose()


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)