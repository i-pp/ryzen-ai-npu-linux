#!/usr/bin/env python3
"""Static DT_NEEDED closure preflight. Never loads a library or opens a device."""
import argparse
import collections
import json
from pathlib import Path
import re
import subprocess

TOOL_ENV = {'PATH': '/usr/sbin:/usr/bin:/sbin:/bin', 'LC_ALL': 'C'}
SYSTEM_DIRS = [Path(p) for p in ['/lib/x86_64-linux-gnu', '/usr/lib/x86_64-linux-gnu', '/lib64', '/usr/lib64', '/lib', '/usr/lib']]


def metadata(path):
    r = subprocess.run(['readelf', '--wide', '-d', str(path)], env=TOOL_ENV,
                       capture_output=True, text=True, check=True, timeout=10)
    result = {'needed': [], 'rpath': [], 'runpath': [], 'soname': []}
    for key, value in re.findall(r'\((NEEDED|RPATH|RUNPATH|SONAME)\).*?\[(.*?)\]', r.stdout):
        result[key.lower()].append(value)
    return result


def ld_cache():
    r = subprocess.run(['ldconfig', '-p'], env=TOOL_ENV, capture_output=True,
                       text=True, check=True, timeout=10)
    result = {}
    for line in r.stdout.splitlines():
        match = re.match(r'\s*(\S+)\s+\([^)]*x86-64[^)]*\)\s+=>\s+(\S+)', line)
        if match:
            result.setdefault(match[1], []).append(Path(match[2]))
    return result


def closure(roots, environment_dirs, system_dirs, cache, reader=metadata, limit=256):
    allowed = [p.resolve() for p in [*environment_dirs, *system_dirs]]
    queue = collections.deque((Path(p), []) for p in roots)
    visited, edges, issues, selected = {}, [], [], {}
    while queue:
        path, inherited = queue.popleft()
        path = path.resolve()
        if path in visited:
            continue
        if len(visited) >= limit:
            issues.append({'kind': 'closure_limit', 'limit': limit})
            break
        if not path.is_file() or not any(path.is_relative_to(parent) for parent in allowed):
            issues.append({'kind': 'missing_or_outside_candidate', 'path': str(path)})
            continue
        try:
            info = reader(path)
        except (OSError, ValueError, subprocess.SubprocessError):
            issues.append({'kind': 'unreadable_elf', 'path': str(path)})
            continue
        visited[path] = info
        for soname in info['soname']:
            selected.setdefault(soname, path)
        origin = str(path.parent)
        def expand(values):
            dirs = []
            for value in values:
                for item in value.split(':'):
                    item = item.replace('${ORIGIN}', origin).replace('$ORIGIN', origin)
                    if not item or '$' in item or not Path(item).is_absolute():
                        issues.append({'kind': 'unsupported_search_path', 'path': str(path)})
                    else:
                        dirs.append(Path(item))
            return dirs
        own_rpath = expand(info['rpath']) if not info['runpath'] else []
        runpath = expand(info['runpath'])
        inherited_next = [*own_rpath, *inherited]
        for needed in info['needed']:
            target = selected.get(needed)
            if target is None:
                if '/' in needed:
                    candidates = [Path(needed)] if Path(needed).is_absolute() else []
                else:
                    search = [*own_rpath, *inherited, *environment_dirs, *runpath]
                    candidates = [d / needed for d in search] + cache.get(needed, []) + [d / needed for d in system_dirs]
                target = next((candidate.resolve() for candidate in candidates if candidate.is_file()), None)
            edges.append({'from': str(path), 'soname': needed, 'candidate': str(target) if target else None})
            if target is None:
                issues.append({'kind': 'unresolved_soname', 'from': str(path), 'soname': needed})
            elif not any(target.is_relative_to(parent) for parent in allowed):
                issues.append({'kind': 'dependency_escapes_candidate', 'from': str(path), 'soname': needed})
            else:
                selected.setdefault(needed, target)
                queue.append((target, inherited_next))
    return {'static_status': 'FAIL' if issues else 'PASS', 'objects': [str(p) for p in visited],
            'edges': edges, 'issues': issues,
            'scope': 'DT_NEEDED plus explicit ORT/EP/XRT-plugin/Peano roots; candidate resolution, not a runtime loader/ABI verdict'}


def package_owner(path):
    r = subprocess.run(['dpkg-query', '-S', str(path)], env=TOOL_ENV,
                       capture_output=True, text=True, timeout=10)
    if r.returncode:
        return None
    package = r.stdout.splitlines()[0].split(': /', 1)[0]
    q = subprocess.run(['dpkg-query', '-W', '-f=${Version}', package], env=TOOL_ENV,
                       capture_output=True, text=True, timeout=10)
    return {'package': package, 'version': q.stdout.strip()} if q.returncode == 0 else None


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sdk-root', required=True, type=Path)
    p.add_argument('--xrt-root', required=True, type=Path)
    a = p.parse_args(argv)
    lib = a.sdk_root.resolve() / 'cpp-test/sdk/onnxruntime/lib'
    peano = a.sdk_root.resolve() / 'cpp-test/peano'
    xrt = a.xrt_root.resolve() / 'lib'
    roots = [lib / 'libonnxruntime.so.1', lib / 'libonnxruntime_vitisai_ep.so',
             peano / 'libpeano-lib.so.21.0git',
             *[xrt / ('libxrt_' + name + '.so.2') for name in ['coreutil', 'core', 'driver_xdna']]]
    result = closure(roots, [xrt, lib, peano], SYSTEM_DIRS, ld_cache())
    host_packages = {}
    for item in result['objects']:
        path = Path(item)
        if any(path.is_relative_to(d.resolve()) for d in SYSTEM_DIRS):
            owner = package_owner(path)
            if owner is None:
                result['issues'].append({'kind': 'unowned_host_library', 'path': str(path)})
            else:
                host_packages[path.name] = owner
    if result['issues']:
        result['static_status'] = 'FAIL'
    result.update(host_packages=host_packages, status='FAIL' if result['static_status'] == 'FAIL' else 'SKIP',
                  dynamic_loader_and_abi='SKIP: requires a separately authorized clean-host link/load/run',
                  device_execution=False)
    aliases = [(str(a.sdk_root.resolve()), '<SDK>'), (str(a.xrt_root.resolve()), '<XRT>')]
    encoded = json.dumps(result, indent=2)
    for original, alias in sorted(aliases, key=lambda x: len(x[0]), reverse=True):
        encoded = encoded.replace(original, alias)
    print(encoded)
    return 1 if result['status'] == 'FAIL' else 2


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        print(json.dumps({'status': 'FAIL', 'detail': str(e), 'device_execution': False}))
        raise SystemExit(1)
