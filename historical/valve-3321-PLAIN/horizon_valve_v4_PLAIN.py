import hashlib
import json
import copy
import math
from typing import Any, Dict, Optional

class HorizonValve:
    """PLAIN valve — verify_integrity only. No bare verify."""

    def __init__(self, manifest: Optional[Dict[str, Any]] = None):
        self.manifest = manifest or {}

    def verify_integrity(self, payload: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Integrity check only. Returns (ok, message)."""
        if not isinstance(payload, dict):
            return False, "NOT_DICT"
        # Minimal PLAIN behavior — no bare verify path
        required = ["head", "body"]
        for k in required:
            if k not in payload:
                return False, f"MISSING_{k.upper()}"
        # Simple hash check if present
        if "hash" in payload and "body" in payload:
            computed = hashlib.sha256(json.dumps(payload["body"], sort_keys=True).encode()).hexdigest()
            if computed != payload["hash"]:
                return False, "HEAD_MISMATCH"
        return True, None
