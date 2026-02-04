from core.base import BaseEntity


class JobQuery(BaseEntity):
    def __init__(self, keywords: list[str]):
        super().__init__()
        self._keywords = keywords
