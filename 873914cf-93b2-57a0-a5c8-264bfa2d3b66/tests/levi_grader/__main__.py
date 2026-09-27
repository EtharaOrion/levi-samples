import argparse
import sys
from pathlib import Path

from . import grade


def main(argv=None):
    p = argparse.ArgumentParser(prog="levi_grader")
    p.add_argument("--tests-dir", type=Path, default=Path("/tests"))
    p.add_argument("--patch", type=Path, default=Path("/logs/artifacts/agent.patch"))
    p.add_argument("--out-dir", type=Path, default=Path("/logs/verifier"))
    a = p.parse_args(argv)
    doc = grade.run(a.tests_dir, a.patch, a.out_dir)
    if "reason" in doc:
        print(f"[levi_grader] invalid: {doc['reason']} (stage {doc['stage']})")
    else:
        print(f"[levi_grader] reward={doc['reward']} outcome={doc['outcome']['score']} "
              f"det={doc['deterministic']['score']} rubric={doc['rubric']['score']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
