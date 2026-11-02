#!/usr/bin/env bash
# Benchmark the (embedding, generator) pair in bench/models.json against local
# Ollama + Antfly. Workload is frozen in bench/fixture.json.
set -euo pipefail
cd "$(dirname "$0")"
exec python3 bench/model_bench.py
