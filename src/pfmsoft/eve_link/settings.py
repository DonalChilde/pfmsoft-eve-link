"""Settings module for the Eve ESI Link application."""

import logging
from dataclasses import dataclass
from pathlib import Path
from uuid import NAMESPACE_DNS, uuid5

from pfmsoft.api_request.settings import ApiRequestSettings
from pfmsoft.api_request.settings import get_settings as get_api_request_settings
from pfmsoft.eve_auth_manager.settings import EveAuthManagerSettings
from pfmsoft.eve_auth_manager.settings import get_settings as get_auth_manager_settings
from pydantic_settings import BaseSettings, SettingsConfigDict
from typer import get_app_dir

from pfmsoft.eve_link import __app_name__, __url__, __version__

logger = logging.getLogger(__name__)
# Typical application settings
USER_AGENT = f"{__app_name__}/{__version__} ({__url__})"
APP_DOMAIN = f"{__app_name__}"
APP_NAMESPACE = uuid5(NAMESPACE_DNS, __app_name__)
ENV_PREFIX = __app_name__.replace(".", "_").replace("-", "_").upper() + "_"
SETTINGS_KEY = ENV_PREFIX + "SETTINGS"

# ESI API URLs
COMPATIBILITY_DATES_URL = "https://esi.evetech.net/meta/compatibility-dates"
"""URL to fetch the list of compatibility dates from the ESI API."""
ESI_SCHEMA_URL = "https://esi.evetech.net/meta/openapi.json"
"""URL to fetch ESI OpenAPI schema."""
ESI_SCHEMA_CHANGELOG_URL = "https://esi.evetech.net/meta/changelog"
"""URL to fetch ESI schema changelog."""


@dataclass(slots=True, kw_only=True)
class EsiLinkSettings:
    """Configuration settings for the Eve ESI Link application."""

    application_directory: Path
    logging_directory: Path
    schema_cache_directory: Path
    # Eve Auth Manager settings
    eve_auth_manager_settings: EveAuthManagerSettings
    # API Request settings
    api_request_settings: ApiRequestSettings
    max_rate: float = 50.0
    time_period: float = 1.0


class EsiLinkSettingsPydantic(BaseSettings):
    """Pydantic-based configuration settings for the Eve ESI Link application."""

    model_config = SettingsConfigDict(
        env_prefix=ENV_PREFIX,
        env_file=(".env", ".env.dev"),
        env_file_encoding="utf-8",
    )

    application_directory: Path = Path(get_app_dir(__app_name__)).resolve()


def get_settings(
    application_directory: Path | None = None,
) -> EsiLinkSettings:
    """Build runtime settings from a Pydantic settings model or application directory.

    Args:
        application_directory (Path | None): Optional application directory path.
            If not provided, the default application directory is used.

    Returns:
        Runtime settings dataclass used by the application.

    Raises:
        ValueError: If the provided application directory exists but is not a directory.
    """
    if application_directory is None:
        # If the application directory is not provided, use the value from the Pydantic
        # settings model. This allows for environment variable overrides and .env file loading.
        application_directory = EsiLinkSettingsPydantic().application_directory
    application_directory = application_directory.expanduser().resolve()
    if application_directory.exists() and not application_directory.is_dir():
        raise ValueError(
            f"Application directory '{application_directory}' exists but is not a directory."
        )
    settings = _initialize_settings(application_directory)
    return settings


def _initialize_settings(application_directory: Path) -> EsiLinkSettings:
    """Build default runtime settings.

    Also ensures that the application directories exist.
    """
    settings = EsiLinkSettings(
        application_directory=application_directory,
        logging_directory=application_directory / "logs",
        schema_cache_directory=application_directory / "schema_cache",
        eve_auth_manager_settings=get_auth_manager_settings(
            application_directory=application_directory / "eve_auth_manager"
        ),
        api_request_settings=get_api_request_settings(
            application_directory=application_directory / "api_request"
        ),
    )
    # Ensure that the application directories exist.
    settings.application_directory.mkdir(parents=True, exist_ok=True)
    settings.logging_directory.mkdir(parents=True, exist_ok=True)
    settings.schema_cache_directory.mkdir(parents=True, exist_ok=True)
    return settings
