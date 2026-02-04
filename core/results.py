from core.base import BaseEntity
from core.resumes import Resume


class MatchingResult(BaseEntity):
    def __init__(self, scores: dict[Resume, float]):
        super().__init__()
        self._scores = scores

    def top_k(self, k: int) -> list[Resume]:
        return sorted(
            self._scores,
            key=self._scores.get,
            reverse=True
        )[:k]
