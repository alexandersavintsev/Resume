from abc import ABC, abstractmethod
from core.resumes import Resume
from core.queries import JobQuery


class MLModel(ABC):

    @abstractmethod
    def predict(
        self,
        query: JobQuery,
        resumes: list[Resume]
    ) -> dict[Resume, float]:
        """
        Returns relevance score for each resume
        """
        pass
