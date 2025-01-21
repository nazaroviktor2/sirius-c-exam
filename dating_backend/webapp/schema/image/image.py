from pydantic import BaseModel, ConfigDict

from webapp.models.meet.image import ContentEnum


class ImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    url: str
    content_type: ContentEnum
