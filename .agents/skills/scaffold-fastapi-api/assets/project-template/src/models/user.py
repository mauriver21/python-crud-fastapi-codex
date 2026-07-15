from math import ceil
from sqlmodel import Session, func, select
from db.engine import engine
from db.schema.users import User
from interfaces.UserAuth import UserAuth
from interfaces.UserCreate import UserCreate
from interfaces.UserModelList import UserModelList
from interfaces.UserPagination import UserPagination
from interfaces.UserUpdate import UserUpdate
from utils.utc_now import utc_now


def create(user: UserCreate) -> User:
    db_user = User(**user.model_dump())

    with Session(engine) as session:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user


def read(id: str) -> User | None:
    with Session(engine) as session:
        return session.get(User, id)


def find_by_email(email: str) -> User | None:
    with Session(engine) as session:
        statement = select(User).where(
            User.email == email,
            User.deleted_at.is_(None),
        )
        return session.exec(statement).first()


def update(id: str, user: UserUpdate) -> User | None:
    with Session(engine) as session:
        db_user = session.get(User, id)
        if db_user is None:
            return None

        for key, value in user.model_dump(
            exclude_unset=True, exclude_none=True
        ).items():
            setattr(db_user, key, value)

        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user


def logical_delete(id: str) -> User | None:
    with Session(engine) as session:
        db_user = session.get(User, id)
        if db_user is None:
            return None

        db_user.deleted_at = utc_now()
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user


def list(page: int = 0, page_size: int = 10) -> UserModelList:
    offset = page * page_size

    with Session(engine) as session:
        statement = (
            select(User)
            .where(User.deleted_at.is_(None))
            .offset(offset)
            .limit(page_size)
        )
        data = session.exec(statement).all()

        count_statement = (
            select(func.count()).select_from(User).where(User.deleted_at.is_(None))
        )
        total_elements = session.exec(count_statement).one()

    total_pages = ceil(total_elements / page_size) if page_size > 0 else 0

    return UserModelList(
        data=data,
        pagination=UserPagination(
            total_pages=total_pages,
            size=page_size,
            page=page,
            total_elements=total_elements,
        ),
    )
