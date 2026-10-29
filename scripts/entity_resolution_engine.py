"""Deterministic, block-sharded entity resolution for vault ingestion.

The resolver is deliberately conservative: exact names are merged only when
entity type and stable context do not conflict; aliases require compatible
context. Taxonomy tags are evidence, never identity keys.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
import hashlib
import re
import unicodedata
from typing import Any, Iterable, Mapping, Sequence


_ALLOWED_CONTEXT_FIELDS = ("entity_type", "period", "place")


def normalize(text: str) -> str:
    """Return a stable comparison key without changing the source value."""
    folded = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", folded.lower())


def stable_key(*parts: str) -> str:
    payload = "\x1f".join(parts).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def murmurhash3_32(value: str, seed: int = 0) -> int:
    """MurmurHash3 x86_32, implemented to keep sharding reproducible."""
    data = value.encode("utf-8")
    length = len(data)
    h1 = seed & 0xFFFFFFFF
    c1 = 0xCC9E2D51
    c2 = 0x1B873593
    for offset in range(0, length - length % 4, 4):
        k1 = int.from_bytes(data[offset : offset + 4], "little")
        k1 = (k1 * c1) & 0xFFFFFFFF
        k1 = ((k1 << 15) | (k1 >> 17)) & 0xFFFFFFFF
        k1 = (k1 * c2) & 0xFFFFFFFF
        h1 ^= k1
        h1 = ((h1 << 13) | (h1 >> 19)) & 0xFFFFFFFF
        h1 = (h1 * 5 + 0xE6546B64) & 0xFFFFFFFF
    tail = data[length - length % 4 :]
    k1 = 0
    for index, byte in enumerate(tail):
        k1 |= byte << (index * 8)
    if tail:
        k1 = (k1 * c1) & 0xFFFFFFFF
        k1 = ((k1 << 15) | (k1 >> 17)) & 0xFFFFFFFF
        k1 = (k1 * c2) & 0xFFFFFFFF
        h1 ^= k1
    h1 ^= length
    h1 ^= h1 >> 16
    h1 = (h1 * 0x85EBCA6B) & 0xFFFFFFFF
    h1 ^= h1 >> 13
    h1 = (h1 * 0xC2B2AE35) & 0xFFFFFFFF
    h1 ^= h1 >> 16
    return h1


@dataclass(frozen=True, order=True)
class Mention:
    """A source-grounded entity mention emitted by an extraction worker."""

    mention_id: str
    name: str
    source_id: str
    entity_type: str = ""
    aliases: tuple[str, ...] = ()
    period: tuple[str, ...] = ()
    place: tuple[str, ...] = ()
    stable_ids: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any], source_id: str | None = None) -> "Mention":
        name = str(value.get("name", "")).strip()
        if not name:
            raise ValueError("mention.name is required")
        source = str(source_id or value.get("source_id", "")).strip()
        if not source:
            raise ValueError(f"mention {name!r} has no source_id")
        mention_id = str(value.get("mention_id") or stable_key(source, name, str(value.get("ordinal", "")))[:20])
        return cls(
            mention_id=mention_id,
            name=name,
            source_id=source,
            entity_type=_scalar(value.get("entity_type", value.get("type", ""))),
            aliases=_values(value.get("aliases", [])),
            period=_values(value.get("period", value.get("era", []))),
            place=_values(value.get("place", value.get("region", []))),
            stable_ids=_values(value.get("stable_ids", value.get("identifiers", []))),
            tags=_values(value.get("tags", [])),
            evidence=_values(value.get("evidence", value.get("citations", []))),
        )


@dataclass(frozen=True, order=True)
class ExistingEntity:
    """Canonical page metadata used for grounding clusters."""

    path: str
    title: str
    aliases: tuple[str, ...] = ()
    entity_type: str = ""
    period: tuple[str, ...] = ()
    place: tuple[str, ...] = ()
    stable_ids: tuple[str, ...] = ()


@dataclass
class DisjointSet:
    parent: dict[str, str] = field(default_factory=dict)
    rank: dict[str, int] = field(default_factory=dict)

    def add(self, item: str) -> None:
        if item not in self.parent:
            self.parent[item] = item
            self.rank[item] = 0

    def find(self, item: str) -> str:
        self.add(item)
        parent = self.parent[item]
        if parent != item:
            self.parent[item] = self.find(parent)
        return self.parent[item]

    def union(self, left: str, right: str) -> str:
        a, b = self.find(left), self.find(right)
        if a == b:
            return a
        if self.rank[a] < self.rank[b]:
            a, b = b, a
        self.parent[b] = a
        if self.rank[a] == self.rank[b]:
            self.rank[a] += 1
        return a


@dataclass(frozen=True)
class ResolutionResult:
    clusters: dict[str, tuple[Mention, ...]]
    canonical_paths: dict[str, str]
    bridges: tuple[tuple[str, str, str], ...]
    held: tuple[tuple[str, str], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "clusters": {
                key: [mention_to_dict(item) for item in mentions]
                for key, mentions in self.clusters.items()
            },
            "canonical_paths": dict(sorted(self.canonical_paths.items())),
            "bridges": [list(item) for item in self.bridges],
            "held": [list(item) for item in self.held],
        }


def _scalar(value: Any) -> str:
    if isinstance(value, (list, tuple, set)):
        return str(next(iter(value), "")).strip()
    return str(value or "").strip()


def _values(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value.strip(),) if value.strip() else ()
    return tuple(sorted({str(item).strip() for item in value if str(item).strip()}))


def mention_to_dict(mention: Mention) -> dict[str, Any]:
    return {
        "mention_id": mention.mention_id,
        "name": mention.name,
        "source_id": mention.source_id,
        "entity_type": mention.entity_type,
        "aliases": list(mention.aliases),
        "period": list(mention.period),
        "place": list(mention.place),
        "stable_ids": list(mention.stable_ids),
        "tags": list(mention.tags),
        "evidence": list(mention.evidence),
    }


class CanonicalEntityResolver:
    """Resolve source mentions in deterministic passes."""

    def __init__(self, existing_entities: Iterable[ExistingEntity] = ()) -> None:
        self.existing_entities = tuple(sorted(existing_entities, key=lambda item: item.path))
        self.ds = DisjointSet()

    @staticmethod
    def blocking_keys(mention: Mention) -> tuple[str, ...]:
        normalized = normalize(mention.name)
        keys = {f"stem:{normalized[:5]}" if normalized else "stem:"}
        if mention.entity_type:
            keys.add(f"type:{normalize(mention.entity_type)}")
        for period in mention.period:
            keys.add(f"period:{normalize(period)}")
        for place in mention.place:
            keys.add(f"place:{normalize(place)}")
        for tag in mention.tags:
            if tag.startswith(("theme/", "domain/", "type/", "period/", "place/", "subject/")):
                keys.add(f"facet:{tag.lower()}")
        for identifier in mention.stable_ids:
            keys.add(f"id:{normalize(identifier)}")
        return tuple(sorted(keys))

    @staticmethod
    def worker_for_block(block_key: str, workers: int) -> int:
        if workers < 1:
            raise ValueError("workers must be positive")
        return murmurhash3_32(block_key) % workers

    @staticmethod
    def _compatible(left: Mention | ExistingEntity, right: Mention | ExistingEntity) -> bool:
        if left.entity_type and right.entity_type and normalize(left.entity_type) != normalize(right.entity_type):
            return False
        left_ids = {normalize(item) for item in left.stable_ids}
        right_ids = {normalize(item) for item in right.stable_ids}
        if left_ids and right_ids and not left_ids.intersection(right_ids):
            return False
        for field_name in ("period", "place"):
            left_values = {normalize(item) for item in getattr(left, field_name)}
            right_values = {normalize(item) for item in getattr(right, field_name)}
            if left_values and right_values and not left_values.intersection(right_values):
                return False
        return True

    def is_match(self, left: Mention, right: Mention) -> tuple[bool, str]:
        if not self._compatible(left, right):
            return False, "context-conflict"
        if normalize(left.name) == normalize(right.name):
            return True, "exact-name"
        left_aliases = {normalize(item) for item in (left.aliases + (left.name,))}
        right_aliases = {normalize(item) for item in (right.aliases + (right.name,))}
        if left_aliases.intersection(right_aliases):
            return True, "alias-overlap"
        return False, "no-supported-equivalence"

    def resolve(self, raw_mentions: Iterable[Mention | Mapping[str, Any]]) -> ResolutionResult:
        mentions = tuple(sorted(
            item if isinstance(item, Mention) else Mention.from_mapping(item)
            for item in raw_mentions
        ))
        for mention in mentions:
            self.ds.add(mention.mention_id)

        buckets: dict[str, list[Mention]] = defaultdict(list)
        for mention in mentions:
            for key in self.blocking_keys(mention):
                buckets[key].append(mention)

        bridges: list[tuple[str, str, str]] = []
        held: list[tuple[str, str]] = []
        for block_key in sorted(buckets):
            items = sorted(buckets[block_key])
            for index, left in enumerate(items):
                for right in items[index + 1 :]:
                    matched, reason = self.is_match(left, right)
                    if matched:
                        self.ds.union(left.mention_id, right.mention_id)
                    elif reason == "context-conflict" and normalize(left.name) == normalize(right.name):
                        held.append((left.mention_id, right.mention_id))

        # Bridge pass is deliberately limited to stable identifiers and exact
        # normalized names. It closes components split by different block keys.
        by_identifier: dict[str, list[Mention]] = defaultdict(list)
        by_name: dict[str, list[Mention]] = defaultdict(list)
        for mention in mentions:
            for identifier in mention.stable_ids:
                by_identifier[normalize(identifier)].append(mention)
            by_name[normalize(mention.name)].append(mention)
        for key, items in sorted(by_identifier.items()):
            self._bridge_group(items, f"stable-id:{key}", bridges)
        for key, items in sorted(by_name.items()):
            self._bridge_group(items, f"exact-name:{key}", bridges)

        grouped: dict[str, list[Mention]] = defaultdict(list)
        for mention in mentions:
            grouped[self.ds.find(mention.mention_id)].append(mention)

        canonical_paths: dict[str, str] = {}
        output: dict[str, tuple[Mention, ...]] = {}
        for root, items in sorted(grouped.items()):
            ordered = tuple(sorted(items))
            canonical = self._canonical_target(ordered)
            target = canonical.path if canonical else f"candidate:{normalize(ordered[0].name)}"
            output[target] = ordered
            if canonical:
                canonical_paths[target] = canonical.path
        return ResolutionResult(
            clusters=dict(sorted(output.items())),
            canonical_paths=canonical_paths,
            bridges=tuple(sorted(set(bridges))),
            held=tuple(sorted(set(held))),
        )

    def _bridge_group(self, items: Sequence[Mention], reason: str, bridges: list[tuple[str, str, str]]) -> None:
        for left, right in zip(sorted(items), sorted(items)[1:]):
            matched, _ = self.is_match(left, right)
            if matched and self.ds.find(left.mention_id) != self.ds.find(right.mention_id):
                self.ds.union(left.mention_id, right.mention_id)
                bridges.append((left.mention_id, right.mention_id, reason))

    def _canonical_target(self, mentions: Sequence[Mention]) -> ExistingEntity | None:
        candidates: list[tuple[int, str, ExistingEntity]] = []
        for entity in self.existing_entities:
            score = 0
            for mention in mentions:
                if not self._compatible(mention, entity):
                    continue
                names = {normalize(mention.name), *(normalize(alias) for alias in mention.aliases)}
                entity_names = {normalize(entity.title), *(normalize(alias) for alias in entity.aliases)}
                if names.intersection(entity_names):
                    score = max(score, 2)
                if {normalize(item) for item in mention.stable_ids}.intersection(normalize(item) for item in entity.stable_ids):
                    score = max(score, 3)
            if score:
                candidates.append((-score, entity.path, entity))
        return sorted(candidates)[0][2] if candidates else None


def partition_mentions(mentions: Iterable[Mention], workers: int) -> dict[int, tuple[Mention, ...]]:
    """Assign mentions to deterministic workers by every blocking key."""
    if workers < 1:
        raise ValueError("workers must be positive")
    buckets: dict[int, list[Mention]] = defaultdict(list)
    for mention in sorted(mentions):
        worker_ids = {CanonicalEntityResolver.worker_for_block(key, workers) for key in CanonicalEntityResolver.blocking_keys(mention)}
        for worker_id in sorted(worker_ids):
            buckets[worker_id].append(mention)
    return {worker: tuple(sorted(items)) for worker, items in sorted(buckets.items())}
