from pydantic import BaseModel


class UserRegister(BaseModel):
    id: int
