# getsocialapi (deprecated)

This package has been **renamed to `getsocialapi-instagram`**.

`getsocialapi` 0.1.x was only ever installable from git
(`pip install git+https://github.com/GetSocialAPI/Instagram-Scraper-API.git`).
It is now published on PyPI under the new name with the import
`getsocialapi_instagram`.

This shim keeps old imports working:

```python
from getsocialapi import Client  # DeprecationWarning; use getsocialapi_instagram
```

## Migrate

```bash
pip uninstall getsocialapi
pip install getsocialapi-instagram
```

```python
# before
from getsocialapi import Client
from getsocialapi.exceptions import RateLimitError

# after
from getsocialapi_instagram import Client
from getsocialapi_instagram.exceptions import RateLimitError
```

The API is identical — only the import path changed.
