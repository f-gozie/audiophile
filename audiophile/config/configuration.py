from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Settings for the application
    """

    BASE_URL: str = "http://localhost:8000"
    FILE_PATH: str = "audiophile/utils/media"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = ""
    AWS_S3_BUCKET: str = ""
    S3_BUCKET_URL: str = ""
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_HOST: str = ""
    DB_PORT: str = ""
    DB_NAME: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
