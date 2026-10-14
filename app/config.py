from pydantic import Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DB_USER: str = "postgres"
    DB_PASSWORD: SecretStr = SecretStr("postgres")
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "kleva_db"
    DB_ECHO: bool = False

    SECRET_KEY: SecretStr = Field(min_length=32)  # obligatoria: sin ella la app no arranca
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    ENVIRONMENT: str = "development"  # development | test | production

    # Emulación de llamadas (ver building-kleva-collections/references/call-emulation.md)
    DISPATCHER_ENABLED: bool = True
    DISPATCH_INTERVAL_SECONDS: float = 5
    SIMULATION_SEED: int | None = None  # None = distinto en cada arranque; fijalo para una demo reproducible
    ANSWER_RATE: float = Field(0.65, ge=0, le=1)
    RETRY_NO_ANSWER_MINUTES: int = 30
    REFUSED_COOLDOWN_DAYS: int = 7
    PROMISE_GRACE_DAYS: int = 1

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        # URL.create escapa caracteres especiales de la contraseña
        return URL.create(
            "postgresql+asyncpg",
            username=self.DB_USER,
            password=self.DB_PASSWORD.get_secret_value(),
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
        ).render_as_string(hide_password=False)


settings = Settings()
