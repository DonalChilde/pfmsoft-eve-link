# Request Builder Prompt

I would like to use jinja to build EsiRequest python factory functions from an EsiSchema.

The intent of these factory functions is to have an up to date version in eve-link, but also allow a user to generate their own set of factory functions from the command line, just in case offical eve-link releases lag behind esi schema releases.

- The function names should be the operation_id, converted to lower csse snajke case.
- The functions should be grouped by tag, and sorted by name in the generated source code.
- The generated code should have a constant identifying the EsiSchema compatibility_date used to generate the functions.
- The function doc string is the operation description. This string may need to be sanitised, some contain newlines.
- Not all parameters sould be included as arguments, this should be configuarble in code, and mirror (but not use directly) UserSettableHeaders. So, make a dedicated exclude enum for path, query, and header params? the page parameter should be on the exclude list.
- required parameters should not have default values, optional parameters should have default values. Where possible, default values should be defined as constants.
- code should be fully type hinted.
- the layout of the source code and templates should be defined in the plan. I am thinking of src/pfmsoft/eve_link/request_builder as a top level..

```python
from pfmsoft.eve_link import EsiLink, EsiSchema, EsiRequest
from pfmsoft.eve_link.language import LangType
from uuid import uuid4

COMPATIBILITY_DATE: str = "1900-01-01"  # Use the esischema compatibility_date
LANG: LangType = "en"
X_TENANT: str = "tranquility"


####################################################
# Market
####################################################


def get_markets_groups(
    *,
    name: str | None = None,
    description: str | None = None,
    accept_language: LangType = LANG,
    x_compatibility_date=COMPATIBILITY_DATE,
    x_tenant=X_TENANT,
) -> EsiRequest:
    """Get a list of item groups This route expires daily at 11:05"""
    headers = {
        "Accept-Language": accept_language,
        "X-Compatibility-Date": x_compatibility_date,
        "X-Tenant": x_tenant,
    }
    request = EsiRequest(
        request_id=uuid4(),
        operation_id="GetMarketsGroups",
        header_parameters=headers,
    )
    return request
```
