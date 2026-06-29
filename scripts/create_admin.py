"""Promote an existing user to admin or owner role.

Usage:
    python scripts/create_admin.py <username>              # promote to admin
    python scripts/create_admin.py <username> --role owner  # promote to owner
"""
import sys

from src.db.session import SessionLocal
from src.users.models import User
from src.users.role import UserRole


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/create_admin.py <username> [--role owner]")
        sys.exit(1)

    username = sys.argv[1]
    role = UserRole.ADMIN

    if "--role" in sys.argv:
        idx = sys.argv.index("--role")
        if idx + 1 < len(sys.argv):
            role_name = sys.argv[idx + 1].lower()
            if role_name == "owner":
                role = UserRole.OWNER
            elif role_name == "admin":
                role = UserRole.ADMIN
            else:
                print(f"Error: Unknown role '{role_name}'. Use 'admin' or 'owner'.")
                sys.exit(1)

    db = SessionLocal()

    try:
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            print(f"Error: User '{username}' not found.")
            sys.exit(1)

        if user.role == role:
            print(f"User '{username}' already has role '{role.value}'.")
            sys.exit(0)

        user.role = role
        db.commit()
        print(f"User '{username}' has been promoted to {role.value}.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
