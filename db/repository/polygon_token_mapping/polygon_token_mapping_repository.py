from dataclasses import dataclass
from datetime import datetime

from db.database import Base, engine, get_session
from db.repository.bridge_tables.polygon import (
    PolygonChildTokenBurn,
    PolygonExitedToken,
    PolygonLockedToken,
    PolygonTokenDeposited,
    PolygonTokenMapping,
)


@dataclass(frozen=True)
class PolygonTokenMappingRecord:
    root_token: str
    child_token: str | None
    checked_at: datetime | None


class PolygonTokenMappingRepository:
    @staticmethod
    def get_all_by_root_token() -> dict[str, PolygonTokenMappingRecord]:
        session = get_session()
        try:
            return {
                str(row.root_token).lower(): PolygonTokenMappingRecord(
                    root_token=row.root_token,
                    child_token=row.child_token,
                    checked_at=row.checked_at,
                )
                for row in session.query(PolygonTokenMapping).all()
                if row.root_token
            }
        finally:
            session.close()

    @staticmethod
    def get_all_ordered() -> list[PolygonTokenMappingRecord]:
        session = get_session()
        try:
            return [
                PolygonTokenMappingRecord(
                    root_token=row.root_token,
                    child_token=row.child_token,
                    checked_at=row.checked_at,
                )
                for row in session.query(PolygonTokenMapping)
                .order_by(PolygonTokenMapping.root_token)
                .all()
            ]
        finally:
            session.close()

    @staticmethod
    def ensure_tables() -> None:
        Base.metadata.create_all(bind=engine)

    @staticmethod
    def get_observed_root_tokens() -> set[str]:
        raw_models = (
            PolygonLockedToken,
            PolygonExitedToken,
            PolygonTokenDeposited,
            PolygonChildTokenBurn,
        )
        root_tokens: set[str] = set()
        session = get_session()
        try:
            for model in raw_models:
                rows = session.query(model.root_token).distinct().all()
                root_tokens.update(
                    str(row.root_token).lower()
                    for row in rows
                    if row.root_token
                )
            return root_tokens
        finally:
            session.close()

    @staticmethod
    def insert_missing_root_tokens(root_tokens: set[str]) -> int:
        inserted = 0
        session = get_session()
        try:
            for root_token in sorted(root_tokens):
                normalized_root_token = str(root_token).lower()
                if session.get(PolygonTokenMapping, normalized_root_token):
                    continue

                session.add(PolygonTokenMapping(root_token=normalized_root_token))
                inserted += 1

            session.commit()
            return inserted
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def upsert(
        root_token: str,
        child_token: str | None,
        checked_at: datetime | None,
    ) -> PolygonTokenMappingRecord:
        normalized_root_token = str(root_token).lower()
        normalized_child_token = str(child_token).lower() if child_token else None
        session = get_session()
        try:
            row = session.get(PolygonTokenMapping, normalized_root_token)
            if row is None:
                row = PolygonTokenMapping(root_token=normalized_root_token)
                session.add(row)

            row.child_token = normalized_child_token
            row.checked_at = checked_at
            session.commit()

            return PolygonTokenMappingRecord(
                root_token=row.root_token,
                child_token=row.child_token,
                checked_at=row.checked_at,
            )
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
