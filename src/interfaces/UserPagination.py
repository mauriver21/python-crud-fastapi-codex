from sqlmodel import SQLModel


class UserPagination(SQLModel):
    total_pages: int
    size: int
    page: int
    total_elements: int
