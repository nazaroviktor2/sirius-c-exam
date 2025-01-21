from datetime import timedelta

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BIND_HOST: str
    BIND_PORT: int
    DB_URL: str

    API_V1_STR: str = "/api/v1"

    JWT_SECRET_SALT: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    REDIS_MEET_CACHE_PREFIX: str

    RABBIT_USER: str
    RABBIT_PASS: str

    RABBIT_MEET_USER_PREFIX: str = 'user_search'

    LOG_LEVEL: str = 'debug'

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_ENDPOINT_URL: str
    AWS_REGION: str = 'ru-central1'
    AWS_SERVICE_NAME: str = 's3'
    AWS_BUCKET_NAME: str = 'meet-bot'

    MAX_FORMS_PER_REQUEST: int = 1

    SHOWN_IDS_EXPIRE_TIME: timedelta = timedelta(hours=12)
    FILE_EXPIRE_TIME: timedelta = timedelta(minutes=15)


settings = Settings()
