"""eve-esi-link package.

CLI and library interface for working with EVE Online ESI.

For library usage, EsiLink is the primary entrypoint.
"""

from importlib.metadata import version

__project_namespace__ = "pfmsoft"
__author__ = "Chad Lowe"
__email__ = "pfmsoft.dev@gmail.com"
__app_name__ = "pfmsoft-eve-link"
__description__ = "A command line first interface to the Eve Online ESI API"
__version__ = version(__app_name__)
__release__ = __version__
__url__ = "https://github.com/DonalChilde/pfmsoft-eve-link"
__license__ = "MIT"


from pfmsoft.eve_link import request_factory
from pfmsoft.eve_link.esi_link import EsiLink, SimpleRequests
from pfmsoft.eve_link.esi_request.models import (
    EsiRequest,
    EsiRequestGroup,
    EsiResponse,
    EsiResponseGroup,
    FailedEsiResponse,
)
from pfmsoft.eve_link.schema.cache import SchemaCacheManager
from pfmsoft.eve_link.schema.models import EsiSchema
from pfmsoft.eve_link.settings import EsiLinkSettings, get_settings

__all__ = [
    "EsiLink",
    "EsiRequest",
    "EsiRequestGroup",
    "EsiResponse",
    "EsiResponseGroup",
    "EsiSchema",
    "SimpleRequests",
    "FailedEsiResponse",
    "EsiLinkSettings",
    "get_settings",
    "SchemaCacheManager",
    "request_factory",
]
