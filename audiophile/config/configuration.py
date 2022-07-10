from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Settings for the application
    """

    BASE_URL: str
    FILE_PATH: str = "audiophile/utils/media"

    class Config:
        env_file = ".env"


settings = Settings()
