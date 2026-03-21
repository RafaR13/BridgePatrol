from db.database import get_session
from .detection_alert_model import DetectionAlert


class DetectionAlertRepository:
    def insert_many(self, alerts: list[DetectionAlert]):
        if not alerts:
            return

        session = get_session()
        try:
            session.add_all(alerts)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()