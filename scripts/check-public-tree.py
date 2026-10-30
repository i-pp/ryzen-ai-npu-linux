#!/usr/bin/env python3
"""Narrow private-reference check for public candidates and optional Git history."""
import argparse
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {'private_chat_locator': re.compile(r'https?://chatgpt[.]com/(?:c/|share/)[^\s)]+'),
            'private_library_locator': re.compile(r'libfile_[a-f0-9]{20,}')}


def matches(text):
    return [{'kind': kind, 'line': text.count('\n', 0, match.start()) + 1}
            for kind, pattern in PATTERNS.items() for match in pattern.finditer(text)]


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--history', action='store_true')
    a = p.parse_args(argv)
    r = subprocess.run(['git', 'ls-files', '-c', '-o', '--exclude-standard', '-z'], cwd=ROOT,
                       capture_output=True, check=True, timeout=20)
    issues = []
    for name in sorted(set(r.stdout.decode().split('\0')) - {''}):
        path = ROOT / name
        if path.is_file():
            for match in matches(path.read_text(errors='replace')):
                issues.append({'path': name, **match})
    history = []
    if a.history:
        for pattern in [r'https?://chatgpt[.]com/(c/|share/)', r'libfile_[a-f0-9]{20,}']:
            r = subprocess.run(['git', 'log', '--all', '--format=%H', '-G', pattern, '--'], cwd=ROOT,
                               capture_output=True, text=True, check=True, timeout=30)
            history.extend(line for line in r.stdout.splitlines() if re.fullmatch(r'[0-9a-f]{40}', line))
    result = {'status': 'FAIL' if issues or history else 'PASS', 'current_tree_matches': issues,
              'history_checked': a.history, 'history_match_commits': sorted(set(history)),
              'scope': 'selected private locator patterns only; not rights clearance or a comprehensive secret scan'}
    print(json.dumps(result, indent=2))
    return 1 if result['status'] == 'FAIL' else 0


if __name__ == '__main__':
    raise SystemExit(main())
