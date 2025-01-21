from pydantic import BaseModel, ConfigDict


class UserData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    name: str
    rank: int
    likes: int


class LeaderboardResponse(BaseModel):
    users: list[UserData]
