from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _bool(name: str, default: bool = False) -> bool:
    value = _env(name, "true" if default else "false").lower()
    return value in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    bind: str
    port: int
    log_level: str
    database_path: str
    api_key: str
    webhook_secret: str

    librenms_base_url: str
    librenms_api_token: str
    librenms_verify_tls: bool

    glpi_base_url: str
    glpi_api_mode: str
    glpi_app_token: str
    glpi_user_token: str
    glpi_verify_tls: bool
    glpi_asset_itemtype: str
    glpi_default_group_id: int | None

    @classmethod
    def from_env(cls) -> "Settings":
        group_raw = _env("GLPI_DEFAULT_GROUP_ID")
        return cls(
            bind=_env("INTEGRATION_BIND", "0.0.0.0"),
            port=int(_env("INTEGRATION_PORT", "8088")),
            log_level=_env("INTEGRATION_LOG_LEVEL", "INFO").upper(),
            database_path=_env("INTEGRATION_DB_PATH", "/data/correlations.db"),
            api_key=_env("INTEGRATION_API_KEY"),
            webhook_secret=_env("WEBHOOK_SECRET"),
            librenms_base_url=_env("LIBRENMS_BASE_URL", "http://librenms:8000").rstrip("/"),
            librenms_api_token=_env("LIBRENMS_API_TOKEN"),
            librenms_verify_tls=_bool("LIBRENMS_VERIFY_TLS", True),
            glpi_base_url=_env("GLPI_BASE_URL", "http://glpi").rstrip("/"),
            glpi_api_mode=_env("GLPI_API_MODE", "legacy_v1"),
            glpi_app_token=_env("GLPI_APP_TOKEN"),
            glpi_user_token=_env("GLPI_USER_TOKEN"),
            glpi_verify_tls=_bool("GLPI_VERIFY_TLS", True),
            glpi_asset_itemtype=_env("GLPI_ASSET_ITEMTYPE", "Computer"),
            glpi_default_group_id=int(group_raw) if group_raw else None,
        )

    def validate_runtime(self) -> list[str]:
        errors: list[str] = []
        required = {
            "INTEGRATION_API_KEY": self.api_key,
            "WEBHOOK_SECRET": self.webhook_secret,
            "LIBRENMS_API_TOKEN": self.librenms_api_token,
            "GLPI_APP_TOKEN": self.glpi_app_token,
            "GLPI_USER_TOKEN": self.glpi_user_token,
        }
        for name, value in required.items():
            if not value:
                errors.append(f"{name} is required")

        if self.glpi_api_mode != "legacy_v1":
            errors.append(
                "GLPI_API_MODE currently supports only legacy_v1 for write operations"
            )
        return errors


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_env()
