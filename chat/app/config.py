import os
from pydantic import BaseSettings, Field


class Settings(BaseSettings):


    # Базовые настройки
    PROJECT_NAME: str = Field("MyFastAPIProject", env="PROJECT_NAME")
    ENVIRONMENT: str = Field("development", env="ENVIRONMENT")
    DEBUG: bool = Field(True, env="DEBUG")

    # Настройки базы данных
    DB_HOST: str = Field("localhost", env="DB_HOST")
    DB_PORT: int = Field(5432, env="DB_PORT")
    DB_USER: str = Field("postgres", env="DB_USER")
    DB_PASSWORD: str = Field("postgres", env="DB_PASSWORD")
    DB_NAME: str = Field("mydatabase", env="DB_NAME")

    class Config:
        env_file = ".env"   # При необходимости можно указать файл с переменными окружения
        env_file_encoding = "utf-8"


# Создаём один экземпляр настроек, чтобы использовать его по всему приложению
settings = Settings()
