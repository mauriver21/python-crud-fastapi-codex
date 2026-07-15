from pwdlib import PasswordHash
from sqlmodel import Session, delete, select

from db.engine import engine
from db.schema.users import User

from tests.constants import test_user_email
from tests.constants import test_user_password


def initialize_test_user():
    with Session(engine) as session:
        test_user = session.exec(
            select(User).where(User.email == test_user_email)
        ).first()

        if test_user is None:
            test_user = User(
                name="Controller Test User",
                email=test_user_email,
                password=PasswordHash.recommended().hash(test_user_password),
            )
            session.add(test_user)
        else:
            test_user.name = "Controller Test User"
            test_user.password = PasswordHash.recommended().hash(test_user_password)
            test_user.deleted_at = None

        session.commit()


def delete_all_users_except_test_user():
    with Session(engine) as session:
        session.exec(delete(User).where(User.email != test_user_email))
        session.commit()
