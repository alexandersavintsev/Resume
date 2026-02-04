from enum import Enum
from core.base import BaseEntity


class UserRole(Enum):
    EMPLOYER = "employer"
    ADMIN = "admin"


class User(BaseEntity):
    def __init__(self, email: str, role: UserRole, balance: float = 0.0):
        super().__init__()
        self._email = email
        self._role = role
        self._balance = balance

    def can_spend(self, amount: float) -> bool:
        return self._balance >= amount

    def spend(self, amount: float) -> None:
        if not self.can_spend(amount):
            raise ValueError("Insufficient balance")
        self._balance -= amount


class Admin(User):
    def __init__(self, email: str):
        super().__init__(email=email, role=UserRole.ADMIN)

    def top_up_user(self, user: User, amount: float) -> None:
        user._balance += amount
