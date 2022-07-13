from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Settings for the application
    """

    FILE_PATH: str = "audiophile/utils/media"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = ""
    AWS_S3_BUCKET: str = ""
    S3_BUCKET_URL: str = ""
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_HOST: str = ""
    POSTGRES_PORT: str = ""
    POSTGRES_DB: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
