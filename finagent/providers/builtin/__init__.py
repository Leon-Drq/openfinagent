"""Built-in data providers shipped with openfinagent.

Each provider is opt-in: nothing is constructed until you reference it
from a ``config.yaml`` ``providers:`` block (or instantiate it directly
in Python).  This keeps the import-time surface small and avoids
forcing every dependency on every user.
"""

from finagent.providers.builtin.fred import FredProvider
from finagent.providers.builtin.qveris import QverisProvider
from finagent.providers.builtin.sample import SampleProvider
from finagent.providers.builtin.sec_edgar import SecEdgarProvider
from finagent.providers.builtin.yfinance_provider import YFinanceProvider

# Mapping used by ``config.yaml`` -> instance resolution.  Keys are the
# strings users write under ``type:``.
BUILTIN_PROVIDERS = {
    "builtin.yfinance": YFinanceProvider,
    "builtin.sec_edgar": SecEdgarProvider,
    "builtin.fred": FredProvider,
    "builtin.qveris": QverisProvider,
    "builtin.sample": SampleProvider,
}

__all__ = [
    "YFinanceProvider",
    "SecEdgarProvider",
    "FredProvider",
    "QverisProvider",
    "SampleProvider",
    "BUILTIN_PROVIDERS",
]
