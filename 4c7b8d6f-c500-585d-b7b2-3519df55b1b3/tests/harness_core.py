"""The execution and parsing path shared by measurement and grading.

This file is the one implementation of "given a finished test run, what passed".
Measurement imports it directly; the bundle carries a byte-identical copy at
/tests/harness_core.py and its runner imports that. Neither has a private copy.

That is not tidiness. The two sides held separate implementations of this logic
and drifted three times, and the last drift was silent: measurement parsed the
runner's stdout while the bundle parsed the report files, so for any language
whose runner writes reports the measured preserve set came back empty. An empty
preserve set makes the preserve check vacuously true, and the oracle still
reaches 1.0, the empty submission still reaches 0.0, and the evidence controls
still find nothing. Nothing in the gate stack could see it.

A shared path cannot drift. The conformance suite asserts the emitted copy is
byte-identical to this file, so a change to one is a change to both.
"""

from __future__ import annotations

import glob as _glob
import json as _json
import os
import re as _re

_GO_JSON_ACTION = {"pass": "PASS", "fail": "FAIL", "skip": "SKIP"}

def parse_go_json(output: str) -> dict[str, str]:
    """Map Go tests to outcomes from `go test -json` event output."""
    out: dict[str, str] = {}
    for line in output.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = _json.loads(line)
        except ValueError:
            continue
        verdict = _GO_JSON_ACTION.get(event.get("Action"))
        if verdict is None:
            continue
        package, test = event.get("Package"), event.get("Test")
        if test:
            out[test] = verdict
            if package:
                segments = package.split("/")
                for i in range(len(segments)):
                    out["/".join(segments[i:]) + "::" + test] = verdict
        elif package:
            out.setdefault("package:" + package, verdict)
    return out

def parse_go(output: str) -> dict[str, str]:
    """Map Go test names to outcomes from `go test -v` or `-json` output."""
    for line in output.splitlines():
        stripped = line.strip()
        if stripped.startswith('{"Time"') or stripped.startswith('{"Action"'):
            return parse_go_json(output)
    out: dict[str, str] = {}
    for line in output.splitlines():
        stripped = line.strip()
        for marker, verdict in (("--- PASS: ", "PASS"), ("--- FAIL: ", "FAIL"),
                                ("--- SKIP: ", "SKIP")):
            if stripped.startswith(marker):
                out[stripped[len(marker):].split(" ")[0]] = verdict
        if stripped.startswith("FAIL\t") or stripped.startswith("ok  \t"):
            parts = stripped.split("\t")
            if len(parts) > 1 and parts[1].strip():
                key = "package:" + parts[1].strip()
                out.setdefault(key, "PASS" if stripped.startswith("ok") else "FAIL")
    return out

_TRANSPORT_TIMESTAMP = _re.compile(
    r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?\s+")
_TRANSPORT_PIPE_PREFIX = _re.compile(r"^[\w.-]+\s+\|\s?")
_TRANSPORT_TAG_PREFIX = _re.compile(r"^\[[\w .:/-]+\]\s+")
_TRANSPORT_PROGRESS_SUFFIX = _re.compile(r"\s+\[\s*\d+%\]\s*$")

def _strip_transport_noise(line: str) -> str:
    """Remove log-transport decoration a runner or aggregator wraps around a line.

    Result lines travel through compose-style service prefixes (`svc-1  | `),
    timestamped log shippers, bracketed suite tags, and progress counters before
    they reach this parser. None of that decoration is part of the test identity
    or verdict, and anchored prefix matching over the decorated bytes silently
    drops every outcome, misgrading a green suite as a suite that never ran.
    Each pattern is shape-exact (a full ISO instant, a pipe-delimited token, a
    bracketed tag with trailing whitespace, a whitespace-separated percent
    group), so a verdict token or a parametrized node id, which attaches its
    bracket without whitespace, can never be eaten.
    """
    prev = None
    while prev != line:
        prev = line
        line = _TRANSPORT_TIMESTAMP.sub("", line)
        line = _TRANSPORT_PIPE_PREFIX.sub("", line)
        line = _TRANSPORT_TAG_PREFIX.sub("", line)
    return _TRANSPORT_PROGRESS_SUFFIX.sub("", line)

_PYTEST_VERBOSE = _re.compile(
    r"^(?P<id>\S.*?::.+?)\s+(?P<v>PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS)"
    r"(?:\s+\[\s*\d+%\])?\s*$")

_PYTEST_VERDICT = {"PASSED": "PASS", "FAILED": "FAIL", "ERROR": "FAIL", "SKIPPED": "SKIP",
                   "XFAIL": "SKIP", "XPASS": "PASS"}

def _pytest_summary_id(rest: str) -> str:
    """Node id from an `-rA` summary line, which is `nodeid - reason` or bare `nodeid`.

    Splitting on the first space truncates every parametrized id that contains one, and
    pytest emits plenty: `test_install_mode[Dnf-x86-dnf install -y package1 package2]`
    became `test_install_mode[Dnf-x86-dnf`, a key no declaration can ever match. The
    separator is " - " at bracket depth zero, so scan for that rather than for a space.
    """
    depth = 0
    for i, ch in enumerate(rest):
        if ch in "[(":
            depth += 1
        elif ch in "])":
            depth = max(0, depth - 1)
        elif depth == 0 and rest.startswith(" - ", i):
            return rest[:i].strip()
    return rest.strip()

_PYTEST_COLLECTION_ERROR = _re.compile(r"^_+ ERROR collecting (?P<path>\S+) _+$")

def parse_pytest(output: str) -> dict[str, str]:
    """Map pytest node ids to outcomes, from either `-rA` or `-v` output.

    A module that pytest reports under an `ERROR collecting <path>` header is
    recorded as a FAIL keyed by the bare module path: the submission broke the
    module at import time, which is a graded failure of every test inside it,
    not an absence of grading. resolve_declared maps declared ids under such a
    module by exact module identity only.
    """
    out: dict[str, str] = {}
    for line in output.splitlines():
        stripped = _strip_transport_noise(line.strip())
        for marker, verdict in (("PASSED ", "PASS"), ("FAILED ", "FAIL"),
                                ("ERROR ", "FAIL"), ("SKIPPED ", "SKIP")):
            if stripped.startswith(marker):
                out[_pytest_summary_id(stripped[len(marker):])] = verdict
                break
        else:
            m = _PYTEST_VERBOSE.match(stripped)
            if m:
                out.setdefault(m.group("id").strip(), _PYTEST_VERDICT[m.group("v")])
    for line in output.splitlines():
        header = _PYTEST_COLLECTION_ERROR.match(_strip_transport_noise(line.strip()))
        if header:
            out.setdefault(header.group("path"), "FAIL")
    return out

_NODE_DURATION = _re.compile(r"\s+[\d.]+\s*(?:ms|s)$|\s+\([\d.]+\s*(?:ms|s)\)$")

_ANSI = _re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

_NODE_FILE_SUFFIX = _re.compile(r"\s*\(\d+\s+tests?\)$")
_NODE_TEST_ID = _re.compile(r"\.(test|spec)\.[jt]sx?\b| > ")

def _parse_mocha_json(output: str) -> dict[str, str]:
    """Outcomes from a mocha `--reporter json` document, keyed as the bound evaluator keys them.

    material-ui runs its unit suite with the JSON reporter, which prints no per-test lines, so
    the line matcher parsed nothing from a 7604-test run and every declared target read as
    absent. The evaluator keys a test `file:fullTitle` when mocha records its file and the bare
    `fullTitle` otherwise, and a failure outranks a skip, which outranks a pass.
    """
    import json as _json
    out: dict[str, str] = {}
    if '"stats"' not in output:
        return out
    decoder = _json.JSONDecoder()
    pos = 0
    while True:
        idx = output.find('"stats"', pos)
        if idx == -1:
            break
        pos = idx + 7
        start = output.rfind("{", 0, idx)
        if start == -1:
            continue
        try:
            doc, end = decoder.raw_decode(output[start:])
        except ValueError:
            continue
        if not isinstance(doc, dict) or not all(k in doc for k in ("passes", "failures", "pending")):
            continue
        pos = start + end
        for key, verdict in (("passes", "PASS"), ("pending", "SKIP"), ("failures", "FAIL")):
            for t in doc.get(key) or []:
                if not isinstance(t, dict) or "fullTitle" not in t:
                    continue
                tid = f"{t['file']}:{t['fullTitle']}" if t.get("file") else t["fullTitle"]
                if out.get(tid) != "FAIL":
                    out[tid] = verdict
    return out

def parse_node(output: str) -> dict[str, str]:
    """Map test titles to outcomes from mocha or vitest reporter output."""
    out: dict[str, str] = _parse_mocha_json(output)
    for line in output.splitlines():
        stripped = _ANSI.sub("", line).replace("\x00", "").strip()
        verdict = None
        if stripped.startswith(("✓ ", "√ ")):
            verdict = "PASS"
        elif stripped.startswith(("✗ ", "× ", "✘ ")):
            verdict = "FAIL"
        elif stripped.startswith(("- ", "↓ ")):
            verdict = "SKIP"
        if verdict is None:
            continue
        title = _NODE_DURATION.sub("", stripped[2:].strip()).strip()
        title = _NODE_FILE_SUFFIX.sub("", title).strip()
        if not title:
            continue
        if verdict == "SKIP" and not _NODE_TEST_ID.search(title):
            continue
        out[title] = verdict
    return out

_UNITTEST_HEAD = _re.compile(r"^(\S+)\s+\(([^)]+)\)\s*\.\.\.\s*(.*)$")
_UNITTEST_VERDICT = {"ok": "PASS", "FAIL": "FAIL", "ERROR": "FAIL",
                     "skipped": "SKIP", "expected failure": "SKIP",
                     "unexpected success": "FAIL"}

def _unittest_verdict(text: str):
    text = text.strip()
    for token, verdict in _UNITTEST_VERDICT.items():
        if text == token or text.startswith(token + " "):
            if text == token or text[len(token):].lstrip().startswith("("):
                return verdict
    return None

def parse_unittest(output: str) -> dict[str, str]:
    """Map unittest / Django test ids to outcomes from verbose runner output."""
    out: dict[str, str] = {}
    pending = None
    for line in output.splitlines():
        stripped = line.strip()
        head = _UNITTEST_HEAD.match(stripped)
        if head:
            name, dotted, tail = head.group(1), head.group(2), head.group(3)
            ident = dotted if dotted.endswith(name) else dotted + "." + name
            verdict = _unittest_verdict(tail)
            if verdict:
                out[ident] = verdict
                pending = None
            else:
                pending = ident
            continue
        if pending:
            verdict = _unittest_verdict(stripped)
            if verdict:
                out[pending] = verdict
                pending = None
    return out

def choose_python_parser(output: str):
    """Pick between the pytest and unittest readers by what the output actually looks like.

    Language alone does not determine the runner. linkding is lang=python and so was handed
    the pytest reader, but it runs Django's unittest runner, which prints
    `name (dotted.Class.name) ... ok`. The pytest reader found 86 incidental keys, none of
    which any declaration could match, and the slot was reported as a vocabulary mismatch
    when the real cause was reading the wrong format. The unittest reader resolves 13 of
    its 17 declared targets from the same bytes.
    """
    py, ut = parse_pytest(output), parse_unittest(output)
    return (parse_unittest, ut) if len(ut) > len(py) else (parse_pytest, py)

def parse_rust(output: str) -> dict[str, str]:
    """Map Rust test paths to outcomes from `cargo test` output."""
    out: dict[str, str] = {}
    for line in output.splitlines():
        stripped = _strip_transport_noise(line.strip())
        if not stripped.startswith("test "):
            continue
        body = stripped[5:]
        for suffix, verdict in ((" ... ok", "PASS"), (" ... FAILED", "FAIL"),
                                (" ... ignored", "SKIP")):
            if body.endswith(suffix):
                out[body[: -len(suffix)].strip()] = verdict
                break
    return out

def parse_gtest(output: str) -> dict[str, str]:
    """Map test names to outcomes from GoogleTest or ctest output.

    The trailing summary block repeats every failure under the same marker, so
    a name is taken only when it looks like a test identifier rather than a
    count, which is what separates the per-test lines from the recap.
    """
    out: dict[str, str] = {}
    for line in output.splitlines():
        stripped = line.strip()
        for marker, verdict in (("[       OK ]", "PASS"), ("[  FAILED  ]", "FAIL")):
            if not stripped.startswith(marker):
                continue
            rest = stripped[len(marker):].strip()
            if not rest:
                continue
            name = rest.split(" ")[0].strip().rstrip(",")
            if not name or name[0].isdigit() or "." not in name:
                continue
            if verdict == "FAIL" or name not in out:
                out[name] = verdict
        if stripped.startswith("Test  #") and ":" in stripped:
            name = stripped.split(":", 1)[1].split()[0]
            out[name] = "PASS" if " Passed " in stripped else (
                "FAIL" if "***Failed" in stripped else out.get(name, "PASS"))
    return out

def parse_junit_xml(report_text: str) -> dict[str, str]:
    """Map JUnit XML testcases to outcomes.

    Reads the report every Java runner writes rather than the stdout it prints,
    because the report records what ran while the stdout records what the runner
    decided to mention. The input is the concatenation of every report file, so
    each document is located by its own root element rather than by assuming one.
    """
    import re as _re
    import xml.etree.ElementTree as ET

    report_text = _re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", report_text)

    out: dict[str, str] = {}
    for match in _re.finditer(r"<(testsuites|testsuite)\b.*?</\1>", report_text, _re.S):
        try:
            root = ET.fromstring(match.group(0))
        except ET.ParseError:
            continue
        for case in root.iter("testcase"):
            name = ("%s.%s" % (case.get("classname", ""), case.get("name", ""))).strip(".")
            verdict = "PASS"
            for child in case:
                tag = child.tag.lower()
                if tag in ("failure", "error"):
                    verdict = "FAIL"
                elif tag == "skipped":
                    verdict = "SKIP"
            if name:
                out[name] = verdict
    return out

PARSERS = {"go": parse_go, "go_json": parse_go_json, "pytest": parse_pytest, "node": parse_node,
           "unittest": parse_unittest,
           "rust": parse_rust, "gtest": parse_gtest, "junit_xml": parse_junit_xml}

def collect_reports(repo_dir: str, report_globs) -> str:
    """Concatenate every structured report the profile names.

    Languages whose runner prints little per test record what ran in a report
    file instead. Reading stdout for those reports nothing.
    """
    chunks = []
    for pattern in report_globs or []:
        for path in sorted(_glob.glob(os.path.join(repo_dir, pattern), recursive=True)):
            try:
                with open(path, encoding="utf-8", errors="replace") as handle:
                    chunks.append(handle.read())
            except OSError:
                continue
    return "\n".join(chunks)

ID_SEPARATORS = ("::", " > ", ">", "/", "\\", "#", ".", "::")

def id_components(identifier):
    """An identifier's components, in order, with empties dropped."""
    text = identifier.strip()
    for sep in ID_SEPARATORS:
        text = text.replace(sep, "\x00")
    return tuple(part for part in text.split("\x00") if part)

def _suffix_index(parsed):
    """Every trailing component sequence of every parsed id, to its ids."""
    index = {}
    for key in parsed:
        parts = id_components(key)
        for size in range(1, len(parts) + 1):
            index.setdefault(parts[-size:], set()).add(key)
    return index

def resolve_declared(declared, parsed):
    """Match declared target ids onto parsed ones. Returns (resolved, ambiguous, missing).

    Exact set membership only. A declared id resolves when the parsed output
    carries exactly that id. A declared id whose module was recorded FAIL by a
    collection error also resolves FAIL, established by exact module identity:
    the submission broke the module at import, which grades every test inside
    it as failed rather than absent. Anything else is missing. Suffix and component
    matching were removed because a fuzzy bridge lets a poisoned or truncated
    log line claim credit for a target it never ran, and every bundle in this
    corpus declares its targets in the parser's own canonical vocabulary, so
    the bridge carried risk without carrying any resolution.
    """
    resolved, ambiguous, missing = {}, [], []
    for target in declared:
        if target in parsed:
            resolved[target] = parsed[target]
        elif "::" in target and parsed.get(target.split("::", 1)[0]) == "FAIL":
            resolved[target] = "FAIL"
        else:
            missing.append(target)
    return resolved, ambiguous, missing

_ANSI = _re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

def strip_ansi(text: str) -> str:
    """Remove terminal colour codes so a marker is at the start of its line."""
    return _ANSI.sub("", text or "")

def outcomes(repo_dir: str, report_globs, stdout: str, parser_name: str) -> dict:
    """The outcomes of one finished run, read the same way on both sides.

    Reports win over stdout where a profile names them, and stdout is the
    fallback where it names none or where none were written. Every phase of
    measurement and every phase of grading goes through here, so no phase can
    read a different source than another phase of the same run.
    """
    stdout = strip_ansi(stdout)
    parser = PARSERS[parser_name]
    source = collect_reports(repo_dir, report_globs) or stdout
    return parser(source)
