from pydantic import BaseSettings


class Settings(BaseSettings):
    MONGODB_URL: str
    FORM_DB_NAME: str
    FORM_DB_COLLECTION: str

    class Config:
        case_sensitive = True
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()


