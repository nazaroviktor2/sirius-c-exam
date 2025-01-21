from typing import Optional

from pydantic import BaseModel, ConfigDict


class StatisticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    likes: int
    matches: int


class UpdateStatistics(BaseModel):
    likes: Optional[int] = None
    matches: Optional[int] = None
