from datetime import datetime, timezone


def utcnow() -> datetime:
    """Date/heure UTC naïve (compatible MySQL DATETIME)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
