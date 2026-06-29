"""Promote an existing user to admin role.

Usage: python scripts/create_admin.py <username>
"""
import sys

from src.db.session import SessionLocal
from src.users.models import User
from src.users.role import UserRole


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/create_admin.py <username>")
        sys.exit(1)

    username = sys.argv[1]
    db = SessionLocal()

    try:
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            print(f"Error: User '{username}' not found.")
            sys.exit(1)

        if user.role == UserRole.ADMIN:
            print(f"User '{username}' is already an admin.")
            sys.exit(0)

        user.role = UserRole.ADMIN
        db.commit()
        print(f"User '{username}' has been promoted to admin.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
