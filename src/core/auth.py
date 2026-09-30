import os
from typing import Optional
from src.core.config import Config

class AuthService:
    """
    Staff Roles & PIN Access Control Service
    Enforces role separation: OPERATOR (guest/waiter) vs ADMIN (manager/supervisor).
    """
    ADMIN_PIN = os.environ.get("ADMIN_PIN", "1234")

    @classmethod
    def verify_pin(cls, pin: str) -> bool:
        """Validates manager/admin PIN."""
        if not pin:
            return False
        return pin.strip() == cls.ADMIN_PIN.strip()

auth_service = AuthService()
