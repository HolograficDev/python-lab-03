from dataclasses import dataclass
from datetime import datetime

from .connection import get_connection


@dataclass
class ActivityLogEntry:
    log_id: int
    book_id: int
    action: str
    details: str
    created_at: datetime


class ActivityLogRepository:
    def get_all(self, limit: int = 200) -> list[ActivityLogEntry]:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, book_id, action, details, created_at
                    FROM activity_logs
                    ORDER BY id DESC
                    LIMIT %s;
                    """,
                    (limit,),
                )
                return [ActivityLogEntry(*row) for row in cursor.fetchall()]
