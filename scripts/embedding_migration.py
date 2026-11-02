"""Manage the Ollama embedding index migration for the Rome Antfly corpus.

Provides idempotent commands for checking backfill coverage, cutting over
to the new index, and rolling back.  Designed so cutover is blocked until
100% coverage is verified and the old index is always preserved.

Usage:
    python scripts/embedding_migration.py status          # backfill progress
    python scripts/embedding_migration.py cutover         # switch .env to new index
    python scripts/embedding_migration.py rollback        # revert .env to old index
    python scripts/embedding_migration.py verify-cpu      # confirm Ollama CPU-only
    python scripts/embedding_migration.py create-index    # idempotent index creation
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ANTFLY_URL = os.environ.get("ANTFLY_URL", "http://127.0.0.1:18080")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
# Inside the Antfly container, host services are at the Docker bridge gateway
OLLAMA_URL_FROM_CONTAINER = os.environ.get("OLLAMA_URL_CONTAINER", "http://172.17.0.1:11434")

TABLE = "rome"
OLD_INDEX = "body_dense"
NEW_INDEX = "body_dense_nomic"
EMBEDDER_MODEL = "nomic-embed-text-cpu"
EMBEDDING_DIM = 768
ENV_KEY = "ANTFLY_INDEX"

VAULT_ROOT = Path(__file__).resolve().parent.parent


def _antfly(*args: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "ANTFLY_URL": ANTFLY_URL}
    return subprocess.run(["antfly", *args], capture_output=True, text=True, env=env)


def _antfly_json(*args: str) -> dict:
    result = _antfly(*args)
    if result.returncode != 0:
        raise RuntimeError(f"antfly {' '.join(args)}: {result.stderr.strip() or result.stdout.strip()}")
    return json.loads(result.stdout)


def index_exists(name: str) -> bool:
    result = _antfly("index", "get", "--table", TABLE, "--index", name)
    return result.returncode == 0


def get_index_status(name: str) -> dict:
    return _antfly_json("index", "get", "--table", TABLE, "--index", name)


def get_coverage(name: str) -> dict:
    status = get_index_status(name)
    cov = status.get("status", {}).get("source_coverage") or status.get("status", {}).get("coverage", {})
    return {
        "total": cov.get("total", 0),
        "covered": cov.get("covered", 0),
        "pending": cov.get("pending", 0),
        "failed": cov.get("failed", 0),
        "skipped": cov.get("skipped", 0),
        "complete": cov.get("complete", False),
        "healthy": cov.get("healthy", False),
    }


def read_env() -> dict[str, str]:
    env_path = VAULT_ROOT / ".env"
    entries: dict[str, str] = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and "=" in stripped:
                k, _, v = stripped.partition("=")
                entries[k.strip()] = v.strip()
    return entries


def current_index() -> str:
    env = read_env()
    return env.get(ENV_KEY, OLD_INDEX)


def cmd_status(_args) -> int:
    print(f"Table:         {TABLE}")
    print(f"Current index: {current_index()}")
    print()

    for name in (OLD_INDEX, NEW_INDEX):
        if not index_exists(name):
            print(f"  [{name}] does not exist")
            continue
        cov = get_coverage(name)
        pct = (cov["covered"] / cov["total"] * 100) if cov["total"] else 0
        print(f"  [{name}]")
        print(f"    coverage: {cov['covered']:,}/{cov['total']:,} ({pct:.1f}%)")
        print(f"    pending:  {cov['pending']:,}")
        print(f"    failed:   {cov['failed']}")
        print(f"    complete: {cov['complete']}")
        print(f"    healthy:  {cov['healthy']}")

        status = get_index_status(name)
        activity = status.get("status", {}).get("activity", {})
        if activity:
            print(f"    phase:    {activity.get('phase', 'unknown')}")
            print(f"    batches:  {activity.get('embedding_batches_completed', 0)}")
            print(f"    embedded: {activity.get('embeddings_computed', 0)}")

        config = status.get("config", {})
        embedder = config.get("embedder", {})
        if embedder:
            print(f"    embedder: {embedder.get('provider')}:{embedder.get('model')}")
        print()
    return 0


def cmd_cutover(args) -> int:
    if not index_exists(NEW_INDEX):
        print(f"ERROR: new index '{NEW_INDEX}' does not exist. Run create-index first.", file=sys.stderr)
        return 1

    cov = get_coverage(NEW_INDEX)
    if not cov["complete"]:
        pct = (cov["covered"] / cov["total"] * 100) if cov["total"] else 0
        print(f"ERROR: backfill not complete ({cov['covered']:,}/{cov['total']:,} = {pct:.1f}%)", file=sys.stderr)
        print(f"       {cov['pending']:,} pending, {cov['failed']} failed", file=sys.stderr)
        if cov["failed"] > 0 and not args.force:
            print("       Use --force to cut over despite failures.", file=sys.stderr)
            return 1
        if not args.force:
            return 1

    if not cov["healthy"] and not args.force:
        print(f"ERROR: index reports unhealthy. Use --force to override.", file=sys.stderr)
        return 1

    if not index_exists(OLD_INDEX):
        print(f"WARNING: old index '{OLD_INDEX}' not found; cutover will proceed but rollback is not available.", file=sys.stderr)

    _set_env_index(NEW_INDEX)
    print(f"Cutover complete: {ENV_KEY}={NEW_INDEX}")
    print(f"Old index '{OLD_INDEX}' is preserved for rollback.")
    return 0


def cmd_rollback(_args) -> int:
    if not index_exists(OLD_INDEX):
        print(f"ERROR: old index '{OLD_INDEX}' does not exist; cannot roll back.", file=sys.stderr)
        return 1

    _set_env_index(OLD_INDEX)
    print(f"Rollback complete: {ENV_KEY}={OLD_INDEX}")
    return 0


def _set_env_index(index_name: str) -> None:
    env_path = VAULT_ROOT / ".env"
    lines = env_path.read_text().splitlines() if env_path.exists() else []
    found = False
    new_lines = []
    for line in lines:
        if line.strip().startswith(f"{ENV_KEY}=") or line.strip().startswith(f"# {ENV_KEY}="):
            if not found:
                new_lines.append(f"{ENV_KEY}={index_name}")
                found = True
            # skip duplicate lines
        else:
            new_lines.append(line)
    if not found:
        # Insert after the QMD section comment or at end
        new_lines.append(f"\n# --- Antfly Embedding Index ---")
        new_lines.append(f"{ENV_KEY}={index_name}")
    env_path.write_text("\n".join(new_lines) + "\n")


def cmd_verify_cpu(_args) -> int:
    """Check that the embedding model loaded in Ollama has zero VRAM usage."""
    import urllib.request
    try:
        resp = urllib.request.urlopen(f"{OLLAMA_URL}/api/ps", timeout=5)
        data = json.loads(resp.read())
    except Exception as e:
        print(f"ERROR: cannot reach Ollama at {OLLAMA_URL}: {e}", file=sys.stderr)
        return 1

    models = data.get("models", [])
    found = False
    for m in models:
        if EMBEDDER_MODEL in m.get("name", ""):
            found = True
            vram = m.get("size_vram", -1)
            if vram == 0:
                print(f"CPU-ONLY VERIFIED: {m['name']} size_vram=0")
            else:
                print(f"WARNING: {m['name']} size_vram={vram} (expected 0)", file=sys.stderr)
                return 1

    if not found:
        # Model not currently loaded; embed a test input to load it
        try:
            req = urllib.request.Request(
                f"{OLLAMA_URL}/api/embed",
                data=json.dumps({"model": EMBEDDER_MODEL, "input": "test"}).encode(),
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=30)
        except Exception as e:
            print(f"ERROR: cannot embed with {EMBEDDER_MODEL}: {e}", file=sys.stderr)
            return 1
        # Re-check
        resp = urllib.request.urlopen(f"{OLLAMA_URL}/api/ps", timeout=5)
        data = json.loads(resp.read())
        for m in data.get("models", []):
            if EMBEDDER_MODEL in m.get("name", ""):
                found = True
                vram = m.get("size_vram", -1)
                if vram == 0:
                    print(f"CPU-ONLY VERIFIED: {m['name']} size_vram=0")
                else:
                    print(f"WARNING: {m['name']} size_vram={vram} (expected 0)", file=sys.stderr)
                    return 1

    if not found:
        print(f"ERROR: model {EMBEDDER_MODEL} not found in Ollama", file=sys.stderr)
        return 1
    return 0


def cmd_create_index(_args) -> int:
    """Idempotently create the new embedding index."""
    if index_exists(NEW_INDEX):
        print(f"Index '{NEW_INDEX}' already exists (idempotent).")
        return 0

    embedder = json.dumps({
        "provider": "ollama",
        "model": EMBEDDER_MODEL,
        "url": OLLAMA_URL_FROM_CONTAINER,
    })
    result = _antfly(
        "index", "create",
        "--table", TABLE,
        "--index", NEW_INDEX,
        "--type", "embeddings",
        "--field", "embedding_text",
        "--dimension", str(EMBEDDING_DIM),
        "--embedder", embedder,
        "--publication-policy", "progressive",
        "--coverage-policy", "strict",
    )
    if result.returncode != 0:
        print(f"ERROR: {result.stderr.strip() or result.stdout.strip()}", file=sys.stderr)
        return 1
    print(f"Created index '{NEW_INDEX}' with Ollama embedder ({EMBEDDER_MODEL}).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Show backfill coverage and index health")
    cut = sub.add_parser("cutover", help="Switch .env to the new index")
    cut.add_argument("--force", action="store_true", help="Override safety checks")
    sub.add_parser("rollback", help="Revert .env to the old index")
    sub.add_parser("verify-cpu", help="Confirm embedding model uses zero VRAM")
    sub.add_parser("create-index", help="Idempotently create the new embedding index")

    args = parser.parse_args()
    dispatch = {
        "status": cmd_status,
        "cutover": cmd_cutover,
        "rollback": cmd_rollback,
        "verify-cpu": cmd_verify_cpu,
        "create-index": cmd_create_index,
    }
    return dispatch[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
