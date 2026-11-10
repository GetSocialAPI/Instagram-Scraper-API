import warnings

warnings.warn(
    "The 'getsocialapi' package has been renamed to 'getsocialapi-instagram' "
    "(import 'getsocialapi_instagram'). Migrate with: "
    "pip uninstall getsocialapi && pip install getsocialapi-instagram. "
    "This compatibility shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from getsocialapi_instagram import *  # noqa: E402, F401, F403

__version__ = "0.1.1"
