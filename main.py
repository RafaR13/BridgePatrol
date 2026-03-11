from db.repository import *


def main():

    print("\n--- TABLES IN DATABASE ---")
    tables = list_tables()

    for t in tables:
        print(t)

    if not tables:
        print("No tables found")
        return

    print("\n--- PREVIEW FIRST TABLE ---")

    table = tables[45]

    rows = preview_table(table, limit=5)

    for r in rows:
        print(r)

    print("\n--- GENERIC FETCH TEST ---")

    rows = fetch_rows(table, limit=5)

    for r in rows:
        print(r)


if __name__ == "__main__":
    main()