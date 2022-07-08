from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Settings for the application
    """

    BASE_URL: str

    class Config:
        env_file = ".env"


settings = Settings()
