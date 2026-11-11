import hashlib
import json
import copy
import math
from typing import Any, Dict, Optional

class HorizonValveV4:
    def __init__(self):
        self.ledger = []
        self.prev_hash = "0" * 64
        self.chain = self.ledger
        self.genesis = "0" * 64

    def _is_finite_number(self, obj):
        if isinstance(obj, float):
            if not math.isfinite(obj):
                return False
        elif isinstance(obj, dict):
            return all(self._is_finite_number(v) for v in obj.values())
        elif isinstance(obj, (list, tuple)):
            return all(self._is_finite_number(v) for v in obj)
        return True

    def _compute_hash(self, state, context, prev_hash):
        payload = {"prev_hash": prev_hash, "state": state, "context": context}
        serialized = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def log_state(self, state, context=None, *, event="STEP", label="NONE", **kwargs):
        if context is not None and not isinstance(context, dict):
            if event != "STEP" or label != "NONE" or "context" in kwargs:
                raise TypeError(f"event/label kwargs set but second positional context is non-dict")
            raise TypeError(f"context must be dict, got {type(context)}")
        actual_context = context if context is not None else kwargs.get("context", {})
        if not isinstance(actual_context, dict):
            raise TypeError(f"context must be dict, got {type(actual_context)}")
        if event != "STEP" or label != "NONE":
            actual_context = dict(actual_context)
            actual_context.setdefault("event", event)
            actual_context.setdefault("label", label)
        if not self._is_finite_number(state) or not self._is_finite_number(actual_context):
            raise ValueError("non-finite float (NaN/Inf) rejected")
        state_copy = copy.deepcopy(state)
        context_copy = copy.deepcopy(actual_context)
        current_hash = self._compute_hash(state_copy, context_copy, self.prev_hash)
        entry = {"prev_hash": self.prev_hash, "state": state_copy, "context": context_copy, "hash": current_hash}
        self.ledger.append(entry)
        self.prev_hash = current_hash
        return current_hash

    def verify_integrity(self):
        expected_prev = self.genesis
        for i, entry in enumerate(self.ledger):
            if not isinstance(entry, dict):
                return False, f"MALFORMED at {i}"
            if "hash" not in entry or "prev_hash" not in entry:
                return False, f"MALFORMED at {i}: missing keys"
            try:
                expected_hash = self._compute_hash(entry["state"], entry["context"], expected_prev)
            except Exception as e:
                return False, f"MALFORMED at {i}: {e}"
            if expected_hash != entry["hash"]:
                return False, i
            if entry["prev_hash"] != expected_prev:
                return False, i
            expected_prev = entry["hash"]
        if not self.ledger:
            if self.prev_hash != self.genesis:
                return False, "HEAD_MISMATCH"
        else:
            if self.prev_hash != self.ledger[-1]["hash"]:
                return False, f"HEAD_MISMATCH"
        return True, None
