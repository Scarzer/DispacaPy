# This will be a trader account
# Only traders can be allowed to trade

import requests
import json
import dataclasses


@dataclass
class DBClient:
    url: str
    headers: dict 


