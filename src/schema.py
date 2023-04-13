from pydantic.main import BaseModel


class Base(BaseModel):
    pass


class HashableBase(Base):
    def __hash__(self) -> int:
        return id(self)
