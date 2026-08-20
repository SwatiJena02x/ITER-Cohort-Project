from database import PostgreSQLConnection


def main():

    db = PostgreSQLConnection()

    connection = db.get_connection()

    result = connection.execute(
        "SELECT current_database();"
    ).fetchone()

    print(
        f"Connected database: {result[0]}"
    )

    db.close()


if __name__ == "__main__":
    main()