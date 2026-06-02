from db.repository.detection_alert.detection_alert_model import DetectionAlert


class CheckEventCallersMixin:
    def check_event_callers(self) -> list[DetectionAlert]:
        print("starting analysis for check_event_callers")
        # 1) identificar evento de destino (mint, release, transfer, etc)
        # 2) verificar se o caller interno do evento é autorizado
        alerts = []
        print(f"cought {len(alerts)} alerts")
        return alerts
