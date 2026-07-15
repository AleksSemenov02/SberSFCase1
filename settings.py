from pydantic_settings import BaseSettings, SettingsConfigDict


class S3Settings(BaseSettings):
    endpoint_url: str = "http://minio:9000/"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    bucket_name: str = "docs"

    model_config = SettingsConfigDict(
        env_prefix="S3_",
        env_file=".env",
        extra="ignore"
    )

class AppSettings(BaseSettings):
    database_url: str
    debug: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


S3 = S3Settings()
App = AppSettings()