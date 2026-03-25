import argparse

from db.base import (
    clear_all_tables,
    clear_bridge_tables,
    clear_table,
    get_bridge_tables,
    list_tables,
)


def main():
    parser = argparse.ArgumentParser(
        description="Helper para esvaziar tabelas da base de dados."
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--table",
        type=str,
        help="Nome de uma tabela específica para esvaziar.",
    )
    group.add_argument(
        "--bridge",
        type=str,
        help="Nome da bridge; esvazia todas as tabelas cujo nome contenha a bridge.",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Esvazia todas as tabelas.",
    )

    parser.add_argument(
        "--no-restart-identity",
        action="store_true",
        help="Não reinicia as sequences/identities.",
    )
    parser.add_argument(
        "--no-cascade",
        action="store_true",
        help="Não usa CASCADE no TRUNCATE.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirma automaticamente sem pedir input.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostra o que seria apagado, sem executar.",
    )

    args = parser.parse_args()

    restart_identity = not args.no_restart_identity
    cascade = not args.no_cascade

    if args.table:
        targets = [args.table]
        action_desc = f"table '{args.table}'"

    elif args.bridge:
        targets = get_bridge_tables(args.bridge)
        if not targets:
            raise ValueError(f"No tables found for bridge '{args.bridge}'.")
        action_desc = f"all tables for bridge '{args.bridge}'"

    else:
        targets = list_tables()
        action_desc = "ALL tables"

    print(f"Target: {action_desc}")
    print("Tables:")
    for table in targets:
        print(f" - {table}")

    if args.dry_run:
        print("\nDry run enabled. Nothing was deleted.")
        return

    if not args.yes:
        confirmation = input("\nType 'yes' to continue: ").strip().lower()
        if confirmation != "yes":
            print("Operation cancelled.")
            return

    if args.table:
        clear_table(
            args.table,
            restart_identity=restart_identity,
            cascade=cascade,
        )
    elif args.bridge:
        clear_bridge_tables(
            args.bridge,
            restart_identity=restart_identity,
            cascade=cascade,
        )
    else:
        clear_all_tables(
            restart_identity=restart_identity,
            cascade=cascade,
        )

    print("Done.")


if __name__ == "__main__":
    main()