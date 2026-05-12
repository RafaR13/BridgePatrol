from sqlalchemy import BigInteger, Column, Enum as SAEnum, String

from db.database import Base
from signature_detection.constants import AlertSeverity, AlertStatus, SignatureType


class DetectionAlert(Base):
    __tablename__ = "detection_alerts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    signature_type = Column(
        SAEnum(SignatureType, name="signature_type"),
        nullable=False,
    )
    severity = Column(
        SAEnum(AlertSeverity, name="alert_severity"),
        nullable=False,
    )
    #status = Column(
    #    SAEnum(AlertStatus, name="alert_status"),
    #    nullable=False,
    #    default=AlertStatus.OPEN,
    #)

    bridge = Column(String(32), nullable=False)
    correlation_id = Column(String(128), nullable=True)
    correlation_type = Column(String(128), nullable=True)

    src_event_id = Column(BigInteger, nullable=True)
    dst_event_id = Column(BigInteger, nullable=True)

    title = Column(String(255), nullable=False)
    description = Column(String(4000), nullable=False)

    created_at_ts = Column(BigInteger, nullable=True)

    probability = Column(String(4000), nullable=False)

    def __repr__(self):
        signature_type = getattr(self.signature_type, "value", self.signature_type)
        severity = getattr(self.severity, "value", self.severity)
        return (
            f"<DetectionAlert(id={self.id}, "
            f"signature_type={signature_type}, "
            f"severity={severity}, "
            f"bridge={self.bridge}, "
            f"correlation_type={self.correlation_type}, "
            f"correlation_id={self.correlation_id}, "
            f"src_event_id={self.src_event_id}, "
            f"dst_event_id={self.dst_event_id}), "
            f"title={self.title}, "
            f"description={self.description}, "
            f"probability={self.probability}>"
        )
