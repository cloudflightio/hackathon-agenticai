"""
Central place to load and expose a validated ENVSettings singleton instance.
"""
import sys
from pydantic import ValidationError
from utils.settings import ENVSettings

try:
    settings = ENVSettings()
except ValidationError as exc:
    print("❌  Configuration error:\n")
    for err in exc.errors():
        field, msg = err["loc"][0], err["msg"]
        print(f"  • {field}: {msg}")
    sys.exit(1)