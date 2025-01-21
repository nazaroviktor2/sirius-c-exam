from typing import List, Optional

from pydantic import BaseModel, ConfigDict, model_validator

from webapp.models.meet.form import GenderEnum
from webapp.schema.form.form import FormResponse


class SearchFormsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    forms: List[FormResponse]


class SearchParamsUpdate(BaseModel):
    gender: Optional[GenderEnum] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    min_height: Optional[float] = None
    max_height: Optional[float] = None
    city_name: Optional[str] = None
    city_point: Optional[str] = None

    @model_validator(mode='after')
    def check_age_and_height(self):
        if self.min_age and self.max_age:
            if self.min_age > self.max_age:
                raise ValueError('max_age must be greater than min_age')

        if self.min_height and self.max_height:
            if self.min_height > self.max_height:
                raise ValueError('max_height must be greater than min_height')

        return self


class SearchParamsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    gender: Optional[GenderEnum]
    min_age: Optional[int]
    max_age: Optional[int]
    min_height: Optional[float]
    max_height: Optional[float]
    city_name: Optional[str]


class SearchLike(BaseModel):
    user_id: int
