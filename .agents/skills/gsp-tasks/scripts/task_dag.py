#!/usr/bin/env python3
"""Validate and suggest dispatch for the declared DAG in a Markdown document.

Python 3.9+, standard library only. No tasks are executed or files modified.
"""
import argparse
import heapq
import json
import math
import re
from pathlib import Path


class DAGError(ValueError):
    """Invalid document or DAG declaration."""


def _reject(message):
    raise DAGError(message)


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            _reject('duplicate JSON key: ' + key)
        result[key] = value
    return result


def parse_document(text):
    start, end = '<!-- GSP-DAG:START -->', '<!-- GSP-DAG:END -->'
    lines = text.splitlines()
    # Inline marker mentions in prose are not delimiters.
    if lines.count(start) != 1 or lines.count(end) != 1:
        _reject('expected exactly one START and one END DAG marker')
    if start not in lines or end not in lines:
        _reject('DAG markers must be standalone lines')
    a, b = lines.index(start), lines.index(end)
    if a >= b:
        _reject('DAG START must precede END')
    block = '\n'.join(lines[a + 1:b]).strip()
    match = re.fullmatch(r'```json\n([\s\S]*)\n```', block)
    if not match:
        _reject('DAG markers must contain only one json fenced block')
    try:
        return json.loads(match.group(1), object_pairs_hook=_object,
                          parse_constant=lambda value: _reject('nonfinite JSON value: ' + value))
    except (json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise DAGError('invalid DAG JSON: ' + str(exc)) from None


def _string(value):
    return isinstance(value, str) and bool(value.strip())


def _strings(value, label):
    if not isinstance(value, list) or any(not _string(x) for x in value):
        _reject(label + ' must be an array of nonempty strings')
    if len(value) != len(set(value)):
        _reject(label + ' contains duplicates')


def _path(value):
    if value == '.':
        return True
    return (not any(c in value for c in '\\*?[]') and
            all(part not in ('', '.', '..') for part in value.split('/')))


def overlaps(a, b):
    return a == '.' or b == '.' or a == b or a.startswith(b + '/') or b.startswith(a + '/')


def conflicts(a, b):
    reasons = []
    if a['owner'] is not None and a['owner'] == b['owner']:
        reasons.append('owner:' + a['owner'])
    for resource in sorted(set(a['resources']) & set(b['resources'])):
        reasons.append('resource:' + resource)
    for kind_a, kind_b in (('writes', 'writes'), ('writes', 'reads'), ('reads', 'writes')):
        for path_a in sorted(a[kind_a]):
            for path_b in sorted(b[kind_b]):
                if overlaps(path_a, path_b):
                    reasons.append('path:%s:%s/%s:%s' % (kind_a, path_a, kind_b, path_b))
    return reasons


def _revisions(value, label, contracts=None, nonempty=False):
    if not isinstance(value, dict) or (nonempty and not value):
        _reject(label + ' must be ' + ('a nonempty' if nonempty else 'an') + ' object')
    for key, revision in value.items():
        if not _string(key) or type(revision) is not int or revision <= 0:
            _reject(label + ': contract IDs must be nonempty and revisions positive integers')
        if contracts is not None and (key not in contracts or revision > contracts[key]):
            _reject(label + ': unknown contract or future revision: ' + key)


def _validity(data, order):
    """Current usability, independent of the recorded execution status.

    A revalidation edge waives stale causes from that historical input path.
    Every hold and stale causes on other paths remain effective.
    """
    tasks = {task['id']: task for task in data['tasks']}
    causes = {}
    for tid in order:
        task = tasks[tid]
        failures = []
        for contract, revision in sorted(task['basis'].items()):
            if revision != data['contracts'][contract]:
                failures.append((tid, 'stale', 'stale basis %s@%s (current %s)' %
                                 (contract, revision, data['contracts'][contract])))
        if 'hold' in task:
            failures.append((tid, 'hold', 'hold: ' + task['hold']))
        for dep in sorted(task['deps']):
            for source, kind, message in causes[dep]:
                if dep in task.get('revalidates', []) and kind == 'stale':
                    continue
                failure = (source, kind, message)
                if failure not in failures:
                    failures.append(failure)
        causes[tid] = failures
    return {tid: [('%s: ' % source if source != tid else '') + message
                  for source, kind, message in causes[tid]] for tid in sorted(tasks)}


def validate(data):
    if not isinstance(data, dict):
        _reject('root must be an object')
    version = data.get('version')
    if type(version) is not int or version not in (1, 2):
        _reject('version must be integer 1 or 2')
    fields = {'version', 'max_parallel', 'tasks'}
    if version == 2:
        fields |= {'plan_revision', 'contracts', 'acceptance'}
    if set(data) != fields:
        _reject('root has missing or unsupported fields')
    if version == 2:
        if type(data['plan_revision']) is not int or data['plan_revision'] <= 0:
            _reject('plan_revision must be a positive integer')
        _revisions(data['contracts'], 'contracts', nonempty=True)
    if type(data['max_parallel']) is not int or data['max_parallel'] <= 0:
        _reject('max_parallel must be a positive integer')
    if not isinstance(data['tasks'], list) or not data['tasks']:
        _reject('tasks must be a nonempty array')
    required = {'id', 'title', 'deps', 'status', 'owner', 'reads', 'writes', 'resources'}
    optional = {'estimate_minutes', 'estimate_basis', 'evidence', 'reason'}
    if version == 2:
        required |= {'basis'}
        optional |= {'hold', 'revalidates'}
    tasks = {}
    for task in data['tasks']:
        if not isinstance(task, dict) or not required <= set(task) or set(task) - required - optional:
            _reject('task has missing or unsupported fields')
        tid = task['id']
        if not isinstance(tid, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_.-]*', tid):
            _reject('invalid task id')
        if tid in tasks:
            _reject('duplicate task id: ' + tid)
        tasks[tid] = task
        if not _string(task['title']):
            _reject(tid + ': title must be nonempty')
        if not isinstance(task['status'], str) or task['status'] not in ('pending', 'running', 'done', 'blocked'):
            _reject(tid + ': invalid status')
        if task['owner'] is not None and not _string(task['owner']):
            _reject(tid + ': owner must be nonempty string or null')
        for key in ('deps', 'reads', 'writes', 'resources'):
            _strings(task[key], tid + '.' + key)
        for path in task['reads'] + task['writes']:
            if not _path(path):
                _reject(tid + ': invalid relative POSIX path: ' + path)
        if ('estimate_minutes' in task) != ('estimate_basis' in task):
            _reject(tid + ': estimate_minutes and estimate_basis must occur together')
        if 'estimate_minutes' in task:
            value = task['estimate_minutes']
            try:
                finite = type(value) in (int, float) and math.isfinite(value) and value > 0
            except OverflowError:
                finite = False
            if not finite:
                _reject(tid + ': estimate_minutes must be finite positive number')
        if version == 2:
            _revisions(task['basis'], tid + '.basis', data['contracts'])
            if 'revalidates' in task:
                _strings(task['revalidates'], tid + '.revalidates')
        for key in ('estimate_basis', 'evidence', 'reason', 'hold'):
            if key in task and not _string(task[key]):
                _reject(tid + ': ' + key + ' must be nonempty string')
        for status, key in (('done', 'evidence'), ('blocked', 'reason')):
            if task['status'] == status and key not in task:
                _reject(tid + ': ' + status + ' requires ' + key)
        if task['status'] == 'running' and task['owner'] is None:
            _reject(tid + ': running requires owner')
    children = {tid: [] for tid in tasks}
    degrees = {}
    for tid, task in tasks.items():
        degrees[tid] = len(task['deps'])
        for dep in task['deps']:
            if dep not in tasks or dep == tid:
                _reject(tid + ': unknown or self dependency: ' + dep)
            children[dep].append(tid)
    queue = [tid for tid in tasks if not degrees[tid]]
    heapq.heapify(queue)
    order = []
    while queue:
        tid = heapq.heappop(queue)
        order.append(tid)
        for child in children[tid]:
            degrees[child] -= 1
            if not degrees[child]:
                heapq.heappush(queue, child)
    if len(order) != len(tasks):
        _reject('dependency cycle detected')
    for tid, task in tasks.items():
        if task['status'] in ('running', 'done') and any(tasks[d]['status'] != 'done' for d in task['deps']):
            _reject(tid + ': running/done requires all dependencies done')
    if version == 2:
        for tid, task in tasks.items():
            for dep in task.get('revalidates', []):
                if dep not in task['deps'] or tasks[dep]['status'] != 'done':
                    _reject(tid + ': revalidates must reference direct done dependencies')
        acceptance = data['acceptance']
        if not isinstance(acceptance, list) or not acceptance:
            _reject('acceptance must be a nonempty array')
        ids = set()
        for item in acceptance:
            if not isinstance(item, dict) or set(item) != {'id', 'contracts', 'tasks'}:
                _reject('acceptance entry must contain exactly id, contracts, tasks')
            if not _string(item['id']) or item['id'] in ids:
                _reject('acceptance IDs must be nonempty and unique')
            ids.add(item['id'])
            _revisions(item['contracts'], 'acceptance.' + item['id'], data['contracts'], nonempty=True)
            _strings(item['tasks'], 'acceptance.' + item['id'] + '.tasks')
            if not item['tasks'] or any(tid not in tasks for tid in item['tasks']):
                _reject('acceptance tasks must be nonempty registered task IDs')
    running = sorted(tid for tid in tasks if tasks[tid]['status'] == 'running')
    if len(running) > data['max_parallel']:
        _reject('running tasks exceed max_parallel')
    for i, tid in enumerate(running):
        for other in running[i + 1:]:
            reasons = conflicts(tasks[tid], tasks[other])
            if reasons:
                _reject('running conflict %s / %s: %s' % (tid, other, ', '.join(reasons)))
    result = {'valid': True, 'topological_order': order,
              'edges': sorted([[dep, tid] for tid, task in tasks.items() for dep in task['deps']]),
              'warnings': []}
    if version == 2:
        result['task_validity'] = _validity(data, order)
    return result


def route(data):
    result = validate(data)
    tasks = {task['id']: task for task in data['tasks']}
    children = {tid: [] for tid in tasks}
    for tid, task in tasks.items():
        for dep in task['deps']:
            children[dep].append(tid)
    estimated = all('estimate_minutes' in task for task in tasks.values() if task['status'] != 'done')
    scores = {}
    for tid in reversed(result['topological_order']):
        task = tasks[tid]
        if task['status'] == 'done':
            scores[tid] = 0
        else:
            score = (task['estimate_minutes'] if estimated else 1) + max(
                (scores[c] for c in children[tid] if tasks[c]['status'] != 'done'), default=0)
            try:
                finite = math.isfinite(score)
            except OverflowError:
                finite = False
            if not finite:
                _reject('remaining critical-path score exceeds finite range: ' + tid)
            scores[tid] = score
    running = sorted(tid for tid in tasks if tasks[tid]['status'] == 'running')
    validity = result.get('task_validity', {})
    ready = sorted((tid for tid in tasks if tasks[tid]['status'] == 'pending' and not validity.get(tid) and
                    all(tasks[d]['status'] == 'done' for d in tasks[tid]['deps'])),
                   key=lambda tid: (-scores[tid], tid))
    reserved = list(running)
    dispatch, waiting = [], {}
    for tid in sorted(tasks):
        task = tasks[tid]
        if task['status'] == 'blocked':
            waiting[tid] = ['blocked: ' + task['reason']]
        elif task['status'] == 'pending' and tid not in ready:
            waiting[tid] = list(validity.get(tid, []))
            unfinished = sorted(d for d in task['deps'] if tasks[d]['status'] != 'done')
            if unfinished:
                waiting[tid].append('dependencies not done: ' + ', '.join(unfinished))
    for tid in ready:
        reasons = []
        if tasks[tid]['owner'] is None:
            reasons.append('owner not assigned')
        if len(reserved) >= data['max_parallel']:
            reasons.append('capacity: max_parallel reached')
        for other in reserved:
            reasons.extend('conflict with %s: %s' % (other, reason) for reason in conflicts(tasks[tid], tasks[other]))
        if reasons:
            waiting[tid] = reasons
        else:
            reserved.append(tid)
            dispatch.append({'task': tid, 'owner': tasks[tid]['owner'], 'score': scores[tid]})
    result.update(priority_basis='estimated_minutes' if estimated else 'dependency_steps',
                  priorities={tid: scores[tid] for tid in sorted(tasks)}, running=running,
                  ready=ready, dispatch=dispatch, waiting={tid: waiting[tid] for tid in sorted(waiting)})
    if data['version'] == 2:
        result['pause_required'] = {tid: validity[tid] for tid in running if validity[tid]}
    return result


def check(data):
    """Check current acceptance; this never alters execution history."""
    result = validate(data)
    tasks = {task['id']: task for task in data['tasks']}
    execution_complete = all(task['status'] == 'done' for task in tasks.values())
    result.update(version=data['version'], revision_validation=data['version'] == 2,
                  execution_complete=execution_complete)
    if data['version'] == 1:
        result.update(complete=execution_complete, acceptance=[])
        result['warnings'].append('v1 provides execution completion only; contract revisions are not validated')
        return result
    entries = []
    for item in data['acceptance']:
        reasons = []
        for contract, revision in sorted(item['contracts'].items()):
            if revision != data['contracts'][contract]:
                reasons.append('stale acceptance %s@%s (current %s)' %
                               (contract, revision, data['contracts'][contract]))
        for tid in item['tasks']:
            task = tasks[tid]
            if task['status'] != 'done':
                reasons.append(tid + ': evidence task is not done')
            reasons.extend(tid + ': ' + reason for reason in result['task_validity'][tid])
            for contract, revision in sorted(item['contracts'].items()):
                if task['basis'].get(contract) != revision:
                    reasons.append(tid + ': basis does not cover acceptance %s@%s' % (contract, revision))
        entries.append({'id': item['id'], 'satisfied': not reasons, 'reasons': reasons})
    result.update(plan_revision=data['plan_revision'], acceptance=entries,
                  complete=all(item['satisfied'] for item in entries))
    return result


def render(data):
    result = validate(data)
    tasks = {task['id']: task for task in data['tasks']}
    names = {tid: 'n%d' % i for i, tid in enumerate(sorted(tasks))}
    lines = ['```mermaid', 'flowchart TD']
    for tid in sorted(tasks):
        lines.append('  %s["%s (%s)"]' % (names[tid], tid, tasks[tid]['status']))
    for dep, tid in result['edges']:
        lines.append('  %s --> %s' % (names[dep], names[tid]))
    return '\n'.join(lines + ['```'])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('validate', 'route', 'render', 'check'))
    parser.add_argument('document', type=Path)
    args = parser.parse_args(argv)
    try:
        data = parse_document(args.document.read_text(encoding='utf-8'))
        output = {'validate': validate, 'route': route, 'render': render, 'check': check}[args.command](data)
        print(output if args.command == 'render' else json.dumps(output, ensure_ascii=False, indent=2, allow_nan=False))
        return 1 if args.command == 'check' and not output['complete'] else 0
    except (DAGError, OSError, UnicodeError, RecursionError) as exc:
        print(json.dumps({'valid': False, 'errors': [str(exc)]}, ensure_ascii=True))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
