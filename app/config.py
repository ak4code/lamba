from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_key: str = Field(alias='BYBIT_API_KEY')
    api_secret: str = Field(alias='BYBIT_SECRET_KEY')
    symbol: str = Field(default='TONUSDT')
    interval: str = Field(default='1')
    category: str = Field(default='linear')
    duration_threshold: int = Field(default=300)
    bid: int = Field(default=100)
    trailing: float = Field(default=1.2)
    profit_percent: float = Field(default=0.85)

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


settings = Settings()
