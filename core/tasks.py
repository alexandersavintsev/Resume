from core.base import BaseEntity
from core.users import User
from core.queries import JobQuery


class MatchingTask(BaseEntity):
    def __init__(self, user: User, query: JobQuery):
        super().__init__()
        self._user = user
        self._query = query
        self._is_completed = False

    def mark_completed(self) -> None:
        self._is_completed = True
