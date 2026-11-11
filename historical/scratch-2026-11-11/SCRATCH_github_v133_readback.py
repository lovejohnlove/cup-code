#!/usr/bin/env python3

"""
horizon_nonlinear_v1_3_2.py — v1_3.2 wrench-branch architecture (patched, BENCH-PENDING)

STATUS: HARDENING SURFACES COMPLETE — NUMERICAL CORE STILL REQUIRED — v1_3.2
        Base: v1_3.1 canonical BYTES FINAL +F (19442 B, md5 02979fb8) — A-F carried unchanged:
        A ROOT default redaction artifact — restored real default / fail-loud
        B Wrench glob fallback + audit logs pattern used
        C Vacuous pass non-numeric — far=[] now INCONCLUSIVE not PASSED
        D INCONCLUSIVE control didn't fail run — now != PASSED/STUB sets rc=1
        E rc=2 dead code — now rc=1 + raise + finally audit survives
        F _normalize dict str(k) collapse 1/"1" — now sorted by repr(kv[0]) + raises on non-str keys
        v1_3.2 adds the ratified wrench-branch patch (fragment author: Claude; benched and
        integrated by Vibe under the two ratified rulings):
        G1 wrench_branch_*.py module pattern between .dat and legacy fallback
        G2 legacy glob excludes back_off_wrench.py — no self-ingestion of the stack module
        G3 .py branches imported under a sha-derived module name — no collision with the
           back_off_wrench stack module; failed exec cleans up sys.modules
        G4 parse_wrench_data is JSON-ONLY for .dat branches — no ast.literal_eval dialect
           (Python-literal .dat with tuples/True reopens the bool/int collapse class; one
           pattern, one serialization contract; hand-edited .dat is a migration finding)
        G5 module branches exposing none of the config constants fail loud — no silent
           default prediction window (the fabricated-neutral class, parameter version)
        G6 defaulted keys in build_prediction_window are logged AND recorded in inputs
           (fingerprinted) — defaults_used travels into predictions.json
        G7 flag names in all messages are ASCII (--wrench-sha, --wrench-dir)
        G8 exit-code taxonomy: NotImplementedError from the stub path is caught BEFORE
           the outer except, traceback printed, returns exit 3 (UNIMPLEMENTED) -
           meaning specifically "code path called but unimplemented." NOT a general
           error code: ImportError/FileNotFoundError/VerificationError still hit
           except Exception, rc=1, raise, shell exit 1. Taxonomy now:
           0 PASSED / 1 FAILED or ERROR / 3 UNIMPLEMENTED.
           Post-bench scripts that grep exit 1 as "gate failed": the stub path now exits 3.
        Stubs remaining (V1_2_PRESERVED): load_shear_events (evaluate_single_event
        filled v1_3.3 per owner flat ruling 2026-11-10: returns 1.0 if event in
        window else 0.0; else unreachable given upstream filtering, defensively
        correct; 0.85 stays logged as placeholder, not enforced; gate is
        contained_r only)

Byte-audit grep targets (v1_3.2 additions):
  G1. grep -n "wrench_branch_\*.py" — module pattern present
  G2. grep -n "back_off_wrench.py" — appears only in the exclusion filter
  G4. grep -n "literal_eval" — should be 0 hits
  G5. grep -n "exposes none of" — fail-loud empty-config branch
  G6. grep -n "defaults_used" — audit + inputs entry present
  A-F grep targets unchanged from v1_3.1 canonical
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import platform
import re
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

if sys.flags.optimize:
    raise SystemExit("Refusing to run with -O: verification must not be optimized away.")

# === A. ROOT — real path or fail-loud, not [STRIPPED] ===
_REAL_DEFAULT_PATH = "/CUP-TAI-Projects/Double-Alpha-Infinity/Solving-Trivial-Conjectures"
_env_root_raw = os.environ.get("HORIZON_ROOT")
if _env_root_raw is None:
    ROOT = Path(_REAL_DEFAULT_PATH)
else:
    if "[STRIPPED" in _env_root_raw or "STRIPPED" in _env_root_raw:
        raise SystemExit("HORIZON_ROOT must be set — contains redaction artifact — export HORIZON_ROOT=/path/to/Solving-Trivial-Conjectures")
    ROOT = Path(_env_root_raw)

if "[STRIPPED" in str(ROOT):
    raise SystemExit("HORIZON_ROOT must be set — default contains redaction artifact [STRIPPED]")

MANIFEST: Dict[str, Dict[str, Any]] = {
    "horizon_valve_v4": {"file": "horizon_valve_v4.py", "sha256": None},
    "phase_space_caliper": {"file": "phase_space_caliper.py", "sha256": None},
    "back_off_wrench": {"file": "back_off_wrench.py", "sha256": None, "size": 10201},
}

_log: List[Dict[str, Any]] = []

def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

WRENCH_CONFIG_ATTRS = {
    "x0": ("x0", "X0"),
    "eps": ("eps", "EPS"),
    "ticks": ("ticks", "TICKS"),
}

def _load_wrench_module(path: Path, sha: str) -> Any:
    """G3: Import a wrench-branch .py under a sha-derived module name.

    The sha in the module name avoids collision with the stack module
    `back_off_wrench` that resolve_and_import() may already have loaded.
    A failed exec removes the module from sys.modules before re-raising.
    """
    mod_name = f"_wrench_branch_{sha[:16]}"
    if mod_name in sys.modules:
        return sys.modules[mod_name]
    spec = importlib.util.spec_from_file_location(mod_name, str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"wrench branch {path}: spec/loader unavailable")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception:
        sys.modules.pop(mod_name, None)
        raise
    return mod

def _extract_wrench_config(mod: Any, path: Any = None) -> Dict[str, Any]:
    """Normalize module-level constants to the lowercase keys that JSON/.dat
    branches use, so build_prediction_window sees one shape.

    G5: a module exposing NONE of the config constants fails loud. A constants-free
    branch must not silently become the default prediction window.
    """
    cfg: Dict[str, Any] = {}
    for key, names in WRENCH_CONFIG_ATTRS.items():
        for n in names:
            if hasattr(mod, n):
                cfg[key] = getattr(mod, n)
                break
    if not cfg:
        where = f" in {path}" if path is not None else ""
        accepted = sorted({n for names in WRENCH_CONFIG_ATTRS.values() for n in names})
        raise ValueError(
            f"wrench branch module{where} exposes none of {accepted} - "
            "refusing to build a silent default prediction window (G5)"
        )
    return cfg

_hex64_re = re.compile(r"^[0-9a-f]{64}$")

def _is_placeholder(val: Any) -> bool:
    if val is None or not isinstance(val, str):
        return True
    s = val.strip().lower()
    if "_" in s:
        return True
    if len(s) != 64:
        return True
    if not _hex64_re.fullmatch(s):
        return True
    try:
        int(s, 16)
    except ValueError:
        return True
    return False

def resolve_and_import(name: str) -> Any:
    if name not in MANIFEST:
        raise ImportError(f"{name}: not in MANIFEST")
    expected = MANIFEST[name].get("sha256")
    if _is_placeholder(expected):
        raise ImportError(f"{name}: MANIFEST sha256 missing or placeholder — pin real 64-char hex (fail closed)")
    path = ROOT / MANIFEST[name]["file"]
    if not path.is_file():
        raise ImportError(f"{name}: missing at {path} — set HORIZON_ROOT")
    h = _sha256(path)
    if h != expected:
        raise ImportError(f"{name}: sha256 mismatch want {expected} got {h}")
    if "size" in MANIFEST[name] and path.stat().st_size != MANIFEST[name]["size"]:
        raise ImportError(f"{name}: size mismatch want {MANIFEST[name]['size']} got {path.stat().st_size}")
    _log.append({"module": name, "path": str(path), "sha256": h, "size": path.stat().st_size})
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"{name}: spec/loader unavailable")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

def select_active_wrench_branch(wrench_dir: str | Path, required_sha: str | None = None) -> Dict[str, Any]:
    """B+G: three explicit branch patterns with precedence (.dat > .py > legacy),
    kind dispatch (data vs module), stack-module exclusion, and cross-pattern
    visibility — candidates in non-matching patterns are logged, not silently dropped.
    """
    root = Path(wrench_dir)
    if not root.is_dir():
        raise FileNotFoundError(f"wrench_dir does not exist: {root}")

    dat_candidates = sorted(root.glob("wrench_branch_*.dat"))
    py_candidates = sorted(root.glob("wrench_branch_*.py"))
    legacy_candidates = [
        p for p in sorted(root.glob("back_off_wrench*.py"))
        if p.name != "back_off_wrench.py"
    ]

    ignored: List[Dict[str, Any]] = []
    if dat_candidates:
        candidates = dat_candidates
        pattern_used = "wrench_branch_*.dat"
        kind = "data"
        ignored += [{"path": str(p), "pattern": "wrench_branch_*.py"} for p in py_candidates]
        ignored += [{"path": str(p), "pattern": "back_off_wrench*.py"} for p in legacy_candidates]
    elif py_candidates:
        candidates = py_candidates
        pattern_used = "wrench_branch_*.py"
        kind = "module"
        ignored += [{"path": str(p), "pattern": "back_off_wrench*.py"} for p in legacy_candidates]
    elif legacy_candidates:
        candidates = legacy_candidates
        pattern_used = "back_off_wrench*.py (excluding back_off_wrench.py)"
        kind = "module"
    else:
        raise FileNotFoundError(
            f"no wrench candidates under {root} matching wrench_branch_*.dat, "
            "wrench_branch_*.py, or back_off_wrench*.py (excluding back_off_wrench.py)"
        )

    hashed = [(p, _sha256(p)) for p in candidates]
    by_hash: Dict[str, List[Path]] = {}
    for p, h in hashed:
        by_hash.setdefault(h, []).append(p)
    _log.append({
        "wrench_pattern_used": pattern_used,
        "wrench_kind": kind,
        "wrench_candidates": [{"path": str(p), "sha256": h, "size": p.stat().st_size} for p, h in hashed],
        "wrench_ignored_other_pattern": ignored,
        "distinct_hashes": list(by_hash),
    })

    if len(by_hash) > 1:
        if required_sha is None:
            lines = ["Ambiguous wrench branches - refusing to guess:"]
            for h, ps in by_hash.items():
                for p in ps:
                    lines.append(f"  {h}  {p.stat().st_size:>6}B  {p}")
            lines.append("Re-run with --wrench-sha=<hash> to select one.")
            raise RuntimeError("\n".join(lines))
        if required_sha not in by_hash:
            raise RuntimeError(f"--wrench-sha={required_sha} not among candidates")
        chosen = by_hash[required_sha][0]
    else:
        chosen = candidates[0]

    chosen_sha = _sha256(chosen)

    if kind == "data":
        data: Any = parse_wrench_data(chosen.read_text(encoding="utf-8"))
    else:
        data = _extract_wrench_config(_load_wrench_module(chosen, chosen_sha), chosen)

    return {
        "path": str(chosen.resolve()),
        "sha256": chosen_sha,
        "kind": kind,
        "pattern": pattern_used,
        "data": data,
    }

PREDICTION_FILE = Path("predictions.json")

class VerificationError(RuntimeError):
    pass

def _normalize(obj: Any) -> Any:
    """F. Fix: sorted by repr(key) to avoid TypeError int<str, and refuse non-str keys to avoid collapse."""
    if isinstance(obj, dict):
        try:
            items = sorted(obj.items(), key=lambda kv: repr(kv[0]))
        except Exception as e:
            raise TypeError(f"_normalize dict items not sortable: {e}")
        out: Dict[str, Any] = {}
        for k, v in items:
            if not isinstance(k, str):
                raise TypeError(f"_normalize dict key must be str, got {type(k).__name__}: {k!r} — would collapse 1 and '1'")
            out[k] = _normalize(v)
        return out
    if isinstance(obj, (set, frozenset)):
        try:
            normalized = [_normalize(x) for x in obj]
            try:
                return sorted(normalized)
            except TypeError:
                return sorted(normalized, key=lambda x: repr(x))
        except TypeError as e:
            raise TypeError(f"_normalize set contains uncomparable mixed types: {e}")
    if isinstance(obj, (list, tuple)):
        return [_normalize(x) for x in obj]
    if isinstance(obj, bool):
        return bool(obj)
    if isinstance(obj, int):
        return int(obj)
    if isinstance(obj, float):
        return float(obj)
    if obj is None or isinstance(obj, str):
        return obj
    raise TypeError(f"non-primitive in fingerprint payload: {type(obj).__name__}")

def _fingerprint(payload: dict) -> str:
    norm = _normalize(payload)
    return hashlib.sha256(json.dumps(norm, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def write_predictions(window: set, inputs: dict, path: Path = PREDICTION_FILE) -> str:
    payload = {"window": _normalize(window), "inputs": _normalize(inputs), "platform": {"python": sys.version.split()[0], "executable": sys.executable, "platform": platform.platform(), "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED", "<unset>")}}
    payload["fingerprint"] = _fingerprint({k: v for k, v in payload.items() if k != "fingerprint"})
    path.write_text(json.dumps(_normalize(payload), indent=2) + "\n")
    return payload["fingerprint"]

def load_predictions(path: Path = PREDICTION_FILE) -> dict:
    if not path.is_file():
        raise VerificationError(f"prediction file missing: {path}. Run --mode predict first.")
    payload = json.loads(path.read_text())
    want = payload.pop("fingerprint", None)
    plat = payload.get("platform", {})
    if plat.get("python") and plat.get("python") != sys.version.split()[0]:
        msg = f"WARNING: predictions made with Python {plat.get('python')}, now running {sys.version.split()[0]}"
        _log.append({"platform_mismatch": msg})
        print(msg, file=sys.stderr)
    got = _fingerprint(payload)
    if want != got:
        raise VerificationError(f"fingerprint mismatch want {want} got {got}")
    return payload

def process_event_predictions(shear_events: Sequence, prediction_window: set, *, require_nonempty: bool = True) -> dict:
    if require_nonempty and len(shear_events) == 0:
        return {"status": "INCONCLUSIVE", "reason": "no shear events", "events_analyzed": 0}
    if require_nonempty and len(prediction_window) == 0:
        return {"status": "INCONCLUSIVE", "reason": "empty prediction window", "events_analyzed": 0}
    try:
        events = set(shear_events)
    except TypeError as e:
        raise TypeError(f"shear_events must be hashable: {e}")
    outside = events - prediction_window
    if outside:
        return {"status": "FAILED", "reason": "events outside window", "outside": sorted(outside, key=lambda x: repr(x)), "events_analyzed": len(events)}
    results = [evaluate_single_event(e, prediction_window) for e in shear_events]
    mean_coherence = sum(results) / len(results) if results else 0.0
    status = "PASSED" if mean_coherence >= 0.85 else "FAILED"
    return {"status": status, "events_analyzed": len(results), "shear_coherence": mean_coherence, "contained": len(events), "outside": 0}

def negative_control(shear_events: Sequence, prediction_window: set, *, rng_seed: int = 0) -> dict:
    """C. Vacuous pass fix: far=[] now INCONCLUSIVE not PASSED."""
    if not shear_events or not prediction_window:
        return {"status": "INCONCLUSIVE", "reason": "empty input"}
    try:
        numeric_window = [x for x in prediction_window if isinstance(x, (int, float))]
        if numeric_window:
            w_min = min(numeric_window)
            w_max = max(numeric_window)
            span = (w_max - w_min) if isinstance(w_max, (int, float)) and isinstance(w_min, (int, float)) else w_max
            if isinstance(span, float):
                span = math.nextafter(w_max, math.inf) - w_min if math.isfinite(w_max) else w_max
            shift = (span + 1) if isinstance(span, (int, float)) else 999
            if isinstance(shift, float):
                shift = math.nextafter(shift, math.inf)
        else:
            w_min, w_max, shift = 0, 999, 1000
    except Exception:
        w_min, w_max, shift = 0, 999, 1000

    far: List[Any] = []
    for e in shear_events:
        if isinstance(e, (int, float)):
            if isinstance(e, float) or isinstance(shift, float):
                far_val = e + float(shift)
                if far_val <= w_max:
                    far_val = math.nextafter(float(w_max), math.inf) + 1.0
                far.append(far_val)
            else:
                far.append(e + int(shift))
        elif isinstance(e, tuple) and len(e) >= 1 and isinstance(e[0], (int, float)):
            if isinstance(e[0], float) or isinstance(shift, float):
                new_tick = e[0] + float(shift)
                if new_tick <= w_max:
                    new_tick = math.nextafter(float(w_max), math.inf) + 1.0
            else:
                new_tick = e[0] + int(shift)
            far.append((new_tick,) + tuple(e[1:]))
        else:
            continue

    if not far:
        return {"status": "INCONCLUSIVE", "reason": "no numeric events to shift — cannot run negative control", "w_min": w_min, "w_max": w_max}

    try:
        smoke_v = process_event_predictions(far, prediction_window, require_nonempty=True)
    except NotImplementedError as nie:
        return {"status": "STUB", "reason": f"numerical core missing during smoke: {nie}"}
    if smoke_v["status"] == "PASSED":
        return {"status": "FAILED", "reason": "smoke control contained — gate cannot fail", "control_verdict": smoke_v}

    near: List[Any] = []
    for e in shear_events:
        if isinstance(e, (int, float)):
            near.append(e + 1)
        elif isinstance(e, tuple) and len(e) >= 1 and isinstance(e[0], (int, float)):
            near.append((e[0] + 1,) + tuple(e[1:]))
        else:
            continue

    near_contained = False
    near_verdict = None
    if near:
        try:
            near_verdict = process_event_predictions(near, prediction_window, require_nonempty=True)
            near_contained = near_verdict["status"] == "PASSED"
        except NotImplementedError as nie:
            return {"status": "STUB", "reason": f"numerical core missing during near shift: {nie}"}
    else:
        near_verdict = {"status": "INCONCLUSIVE", "reason": "no numeric near probe"}

    return {"status": "PASSED", "smoke": "PASS", "near_shift_contained": near_contained, "near_verdict": near_verdict, "shift_used": shift, "w_min": w_min, "w_max": w_max}

POLE_MAG = 1e6
WIDTH_TOL = 1e-9

def _safe_eval(f: Callable[[float], float], x: float) -> float:
    try:
        v = f(x)
        if isinstance(v, complex):
            raise TypeError(f"f({x}) returned complex")
        return float(v)
    except (ZeroDivisionError, OverflowError):
        for dx in (1e-9, -1e-9, 1e-6, -1e-6):
            try:
                v = float(f(x + dx))
                if math.isfinite(v):
                    return math.copysign(math.inf, v)
            except Exception:
                continue
        return math.nan

def _same_sign(a: float, b: float) -> bool:
    if not (math.isfinite(a) and math.isfinite(b)):
        return False
    return math.copysign(1.0, a) == math.copysign(1.0, b)

def _result(status: str, interval: Optional[Tuple[float, float]], f_lo: float, f_hi: float, note: Optional[str] = None) -> dict:
    r: Dict[str, Any] = {"status": status, "interval": interval, "f_lo": f_lo, "f_hi": f_hi}
    if note:
        r["note"] = note
    return r

def locate_crossing(f: Callable[[float], float], a: float, b: float, *, kind: str = "any", max_iter: int = 200, width_tol: float = WIDTH_TOL) -> dict:
    if not (math.isfinite(a) and math.isfinite(b)):
        raise ValueError(f"bounds must be finite a={a} b={b}")
    if not a < b:
        raise ValueError(f"bounds must be ordered a={a} b={b}")
    fa = _safe_eval(f, a)
    fb = _safe_eval(f, b)
    if not math.isfinite(fa):
        return _result("EDGE", (a, a), fa, fb, "nonfinite at a")
    if not math.isfinite(fb):
        return _result("EDGE", (b, b), fa, fb, "nonfinite at b")
    if _same_sign(fa, fb):
        mid = 0.5 * (a + b)
        fmid = _safe_eval(f, mid)
        if not math.isfinite(fmid) or abs(fmid) > POLE_MAG:
            return _result("POLE", (a, b), fa, fb, "even-order pole possible — same sign but interior blowup")
        return _result("NO_CROSSING", None, fa, fb)
    lo, hi, f_lo, f_hi = a, b, fa, fb
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        f_mid = _safe_eval(f, mid)
        if not math.isfinite(f_mid):
            hi, f_hi = mid, f_mid
        elif not _same_sign(f_lo, f_mid):
            hi, f_hi = mid, f_mid
        else:
            lo, f_lo = mid, f_mid
        if hi - lo < width_tol:
            break
    probes = [0.5 * (lo + hi), lo + 0.25 * (hi - lo), lo + 0.75 * (hi - lo)]
    vals = [_safe_eval(f, p) for p in probes]
    any_blowup = any((not math.isfinite(v)) or abs(v) > POLE_MAG for v in vals)
    any_small = any(math.isfinite(v) and abs(v) < 1e-3 for v in vals)
    if kind == "pole":
        status = "POLE" if any_blowup else "UNCONFIRMED"
    elif kind == "zero":
        status = "ZERO" if any_small else "UNCONFIRMED"
    else:
        status = "POLE" if any_blowup else ("ZERO" if any_small else "CROSSING")
    return _result(status, (lo, hi), f_lo, f_hi)

def locate_pole(f: Callable[[float], float], a: float, b: float, *, tol: float | None = None) -> dict:
    return locate_crossing(f, a, b, kind="pole")

def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode", choices=["predict", "verify", "all"], default="all")
    p.add_argument("--wrench-dir", default=str(ROOT / "wrench"))
    p.add_argument("--wrench-sha", default=None)
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args(argv)
    rc = 0
    try:
        if args.mode in ("predict", "all"):
            for name in ("horizon_valve_v4", "phase_space_caliper", "back_off_wrench"):
                resolve_and_import(name)
            wrench = select_active_wrench_branch(args.wrench_dir, required_sha=args.wrench_sha)
            window, inputs = build_prediction_window(wrench)
            fp = write_predictions(window, inputs)
            print(f"predict: fingerprint={fp} n_window={len(window)}")
        if args.mode in ("verify", "all"):
            if args.mode == "verify":
                for name in ("horizon_valve_v4", "phase_space_caliper", "back_off_wrench"):
                    try:
                        resolve_and_import(name)
                    except ImportError:
                        _log.append({"verify_without_wrench_import": f"could not import {name}"})
                        pass
            pred = load_predictions()
            events = load_shear_events()
            verdict = process_event_predictions(events, set(pred["window"]))
            control = negative_control(events, set(pred["window"]), rng_seed=args.seed)
            print(json.dumps({"verdict": verdict, "negative_control": control}, indent=2, default=str))
            if verdict["status"] != "PASSED":
                rc = 1
            if control["status"] not in ("PASSED", "STUB"):
                rc = 1
    except NotImplementedError as e:
        import traceback
        traceback.print_exc()
        _log.append({"unimplemented": f"{type(e).__name__}: {e}"})
        return 3
    except Exception as e:
        _log.append({"exception": f"{type(e).__name__}: {e}"})
        rc = 1
        raise
    finally:
        try:
            print(json.dumps({"audit": _log}, indent=2, default=str))
        except Exception:
            print(f"audit log: {_log}", file=sys.stderr)
    return rc

def parse_wrench_data(text: str) -> Any:
    """G4: JSON-ONLY for .dat branches. One pattern, one serialization contract.
    No ast.literal_eval dialect: a Python-literal .dat carrying tuples/True
    reopens the bool/int collapse class (v0.9 boolean-sequence saga stays closed).
    A hand-edited Python-literal .dat is a migration finding to fix at the file,
    not a dialect to accommodate at the parser.
    """
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"wrench .dat is not valid JSON (JSON-only per G4): {e}") from e
    if not isinstance(data, dict):
        raise ValueError(f"wrench .dat top level must be a JSON object, got {type(data).__name__}")
    return data

def evaluate_single_event(event: Any, window: Any) -> float:
    # FLAT per owner ruling 2026-11-10 (delegated, ratified): 1.0 for any
    # in-window event. The else is unreachable given upstream filtering,
    # but defensively correct. Graded semantics return only as a versioned
    # contract change with named formula and justification.
    return 1.0 if event in window else 0.0

def build_prediction_window(wrench: dict) -> Tuple[set, dict]:
    """Authored (was stub): analytic pole window per v1.2.1 Pred A.
    G6: any defaulted key is logged to the audit trail AND recorded in inputs,
    so defaults_used is fingerprinted and travels into predictions.json.
    """
    data = wrench.get("data") or {}
    if not isinstance(data, dict):
        raise ValueError(
            f"wrench['data'] must be a dict (got {type(data).__name__}, "
            f"kind={wrench.get('kind')})"
        )
    defaults_used: List[str] = []
    if "x0" in data:
        try:
            x0 = float(data["x0"])
        except (TypeError, ValueError) as e:
            raise ValueError(f"wrench data has non-numeric x0: {e}") from e
    else:
        defaults_used.append("x0")
        x0 = 0.1
    if "eps" in data:
        try:
            eps = float(data["eps"])
        except (TypeError, ValueError) as e:
            raise ValueError(f"wrench data has non-numeric eps: {e}") from e
    else:
        defaults_used.append("eps")
        eps = 1.11
    if "ticks" in data:
        try:
            ticks_f = float(data["ticks"])
        except (TypeError, ValueError) as e:
            raise ValueError(f"wrench data has non-numeric ticks: {e}") from e
        if not ticks_f.is_integer():
            raise ValueError(f"wrench ticks must be an integer, got {data['ticks']!r}")
        ticks = int(ticks_f)
    else:
        defaults_used.append("ticks")
        ticks = 12
    if defaults_used:
        _log.append({
            "defaults_used": defaults_used,
            "wrench_sha256": wrench.get("sha256"),
            "note": "wrench data missing keys - defaults applied and recorded (G6)",
        })
    if ticks <= 0:
        raise ValueError(f"ticks must be positive, got {ticks}")

    t_pole = 1.0 / (x0 * eps) if x0 * eps != 0 else float("inf")
    pole_tick = int(round(t_pole)) if math.isfinite(t_pole) else -1
    window = {pole_tick - 1, pole_tick, pole_tick + 1} & set(range(ticks))

    inputs = {
        "x0": x0,
        "eps": eps,
        "ticks": ticks,
        "t_pole_analytic": t_pole if math.isfinite(t_pole) else None,
        "source": f"analytic_pole_v1.2/{wrench.get('kind', 'data')}",
        "wrench_sha256": wrench.get("sha256"),
        "defaults_used": list(defaults_used),
    }
    return window, inputs

def load_shear_events() -> Sequence:
    raise NotImplementedError("paste load_shear_events from v1_2")

if __name__ == "__main__":
    sys.exit(main())
