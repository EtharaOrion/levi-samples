"""Issue normalization with content-anchored multiset identity.

Phase 1 item 7 requires that findings be normalized so that identity is anchored
in content rather than in a scanner's own numbering, that the verifier owns issue
identifiers, and that an unknown severity fails closed to at least MEDIUM. This
module is the single place those rules are implemented, so every instrument and
every scanner adapter produces identifiers under one algorithm and a downstream
reviewer can re-derive any identifier from the evidence row alone.

Identity is a multiset rather than a set because the same rule firing twice at
two distinct anchors is two issues, while the same rule firing twice at one
anchor after a formatter pass is one issue counted once. The anchor deliberately
excludes absolute line numbers so that a finding survives reformatting and source
line drift, which Phase 2 item 4 requires proving as a selfcheck row.
"""

from __future__ import annotations

import collections
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

from core import Severity, canonical_digest, normalize_text, sha256_bytes

ANCHOR_CONTEXT_LINES = 3

_LINE_NUMBER_PREFIX = re.compile(r"^\s*\d+[:|]\s?")
_TRAILING_WHITESPACE = re.compile(r"[ \t]+$", re.MULTILINE)


def strip_line_numbers(raw: str) -> str:
    """Remove a leading line-number gutter from each line of a code excerpt.

    Scanners emit excerpts in several gutter dialects. Keeping the gutter would
    make the anchor depend on absolute position, which is exactly the drift the
    normalized fingerprint must survive.
    """
    return "\n".join(_LINE_NUMBER_PREFIX.sub("", line) for line in raw.splitlines())


def normalize_excerpt(raw: str) -> str:
    """Reduce a code excerpt to the bytes that decide whether two hits are one issue."""
    stripped = strip_line_numbers(raw)
    stripped = _TRAILING_WHITESPACE.sub("", stripped)
    lines = [line for line in stripped.splitlines() if line.strip()]
    return normalize_text("\n".join(lines))


@dataclass(frozen=True)
class Anchor:
    """The position-independent location of an issue.

    path is retained verbatim because a path rename is a real change of subject.
    symbol carries the enclosing function, class, rule target or test identifier
    when the tool reports one. excerpt carries the normalized surrounding bytes.
    """

    path: str
    symbol: str = ""
    excerpt: str = ""

    def digest(self) -> str:
        return canonical_digest(
            {
                "path": self.path,
                "symbol": self.symbol,
                "excerpt": normalize_excerpt(self.excerpt),
            }
        )


@dataclass(frozen=True)
class NormalizedIssue:
    """One issue under verifier-owned identity.

    issue_id is derived here and never taken from the tool. tool_ref retains the
    tool's own identifier so a reviewer can trace back, but nothing downstream
    keys on it.
    """

    rule: str
    anchor: Anchor
    severity: Severity
    message: str
    tool: str
    tool_ref: str = ""
    extra: dict = field(default_factory=dict)

    @property
    def issue_id(self) -> str:
        return canonical_digest(
            {
                "rule": self.rule,
                "anchor": self.anchor.digest(),
                "tool": self.tool,
            }
        )

    @property
    def fingerprint(self) -> str:
        """The drift-surviving content fingerprint, excluding the producing tool.

        Two tools reporting the same rule at the same anchor share a fingerprint
        and differ in issue_id. That distinction is what lets the evidence file
        record corroboration without double counting.
        """
        return canonical_digest({"rule": self.rule, "anchor": self.anchor.digest()})

    def to_row(self) -> dict:
        return {
            "issue_id": self.issue_id,
            "fingerprint": self.fingerprint,
            "rule": self.rule,
            "severity": self.severity.value,
            "tool": self.tool,
            "tool_ref": self.tool_ref,
            "path": self.anchor.path,
            "symbol": self.anchor.symbol,
            "excerpt_sha256": sha256_bytes(normalize_excerpt(self.anchor.excerpt).encode()),
            "message": self.message,
            "extra": dict(self.extra),
        }


def identity_multiset(issues: Iterable[NormalizedIssue]) -> dict[str, int]:
    """Count issues by verifier-owned identifier.

    A multiset rather than a set, so a rule firing at two anchors stays two.
    """
    counter: collections.Counter[str] = collections.Counter()
    for issue in issues:
        counter[issue.issue_id] += 1
    return dict(sorted(counter.items()))


def fingerprint_multiset(issues: Iterable[NormalizedIssue]) -> dict[str, int]:
    counter: collections.Counter[str] = collections.Counter()
    for issue in issues:
        counter[issue.fingerprint] += 1
    return dict(sorted(counter.items()))


def multiset_digest(issues: Iterable[NormalizedIssue]) -> str:
    return canonical_digest(identity_multiset(issues))


def multiset_equal(left: Iterable[NormalizedIssue], right: Iterable[NormalizedIssue]) -> bool:
    return identity_multiset(left) == identity_multiset(right)


def survives_drift(
    original: Sequence[NormalizedIssue], drifted: Sequence[NormalizedIssue]
) -> tuple[bool, dict]:
    """Report whether a fingerprint multiset is preserved across a drift transform.

    Phase 2 item 4 requires proving that normalized fingerprints survive
    formatting and source line drift where intended. The detail payload names
    which fingerprints appeared or vanished so an inert proof is distinguishable
    from a real one.
    """
    before = fingerprint_multiset(original)
    after = fingerprint_multiset(drifted)
    lost = {key: count for key, count in before.items() if after.get(key, 0) < count}
    gained = {key: count for key, count in after.items() if before.get(key, 0) < count}
    return (not lost and not gained), {"lost": lost, "gained": gained}
