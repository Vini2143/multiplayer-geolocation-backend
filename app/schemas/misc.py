from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, EmailStr, Field, ValidationInfo, computed_field, model_validator
from pydantic_core import PydanticCustomError

from ._base import PASSWORD_REGEX, OrmBaseSchema, clean_cpf_format


PaginatedT = TypeVar("PaginatedT")

class PaginatedList(OrmBaseSchema, Generic[PaginatedT]):
    page_limit: int = Field(ge=0)
    page_size: int = Field(ge=0)
    total_size: int = Field(ge=0)
    data: list[PaginatedT]

    current_page: int = Field(default=1, ge=1)


    @computed_field(return_type=Optional[int])
    def previous_page(self):
        return self.current_page - 1 if self.current_page > 1 else None

    @computed_field(return_type=Optional[int])
    def next_page(self):
        total_pages = self.total_size // self.page_limit + 1

        return self.current_page + 1 if self.current_page < total_pages  else None

    
    @model_validator(mode="after")
    def is_out_of_range(self, info: ValidationInfo):
        total_pages = self.total_size // self.page_limit or 1

        if self.total_size > 0:
            total_pages = total_pages + 1 if self.total_size % self.page_limit else total_pages

        if self.current_page > total_pages:
            raise PydanticCustomError("page_out_range_error", "page out of range 0-{total_pages}", {"total_pages": total_pages})
        
        return self


class Message(BaseModel):
    message: str


class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str | None = None


class LoginSchema(BaseModel):
    username: str
    password: str
