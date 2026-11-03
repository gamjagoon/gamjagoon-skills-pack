#!/usr/bin/env python3
"""Opt-in local session change coordinator. Python 3.9+, Linux, stdlib only."""
import argparse
import base64
import contextlib
import fcntl
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import socket
import stat
import struct
import sys
import tempfile
import time


class ControlError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ControlError(message)


def identifier(value):
    require(isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', value), 'invalid ID')
    return value


def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        require(key not in obj, 'duplicate JSON key: ' + key)
        obj[key] = value
    return obj


def owned_path(value, kind=None):
    path = Path(value)
    require(path.is_absolute(), 'path must be absolute')
    require('..' not in path.parts, 'parent traversal forbidden')
    for part in [path] + list(path.parents):
        require(not part.is_symlink(), 'symlink forbidden: ' + str(part))
    info = path.stat()
    require(info.st_uid == os.getuid(), 'path is not owned by current user: ' + str(path))
    if kind == 'dir':
        require(stat.S_ISDIR(info.st_mode), 'expected directory')
    if kind == 'file':
        require(stat.S_ISREG(info.st_mode), 'expected regular file')
    if kind == 'socket':
        require(stat.S_ISSOCK(info.st_mode), 'expected Unix socket')
    return path


def lexical_document(value):
    require(isinstance(value, str) and Path(value).is_absolute(), 'document path must be absolute')
    require('..' not in Path(value).parts, 'parent traversal forbidden')
    # normpath intentionally preserves POSIX leading //; this local Linux tool
    # has no remote double-slash namespace, so collapse it explicitly.
    return os.path.normpath('/' + value.lstrip('/'))


def canonical_document(value):
    return str(owned_path(value, 'file').resolve(strict=True))


def same_document(left, right):
    if left == right:
        return True
    # Distinct canonical paths can still name the same currently existing inode.
    # Such hardlinks must not hide an unresolved event from check/run/resolve.
    try:
        return os.path.samefile(left, right)
    except OSError:
        return False


def stored_document(value):
    require(isinstance(value, str) and value == lexical_document(value),
            'noncanonical persisted document identity; explicit migration required')


def dag_module():
    # Installed managed trees are inputs, never bytecode output locations.
    sys.dont_write_bytecode = True
    path = Path(__file__).resolve().parents[2] / 'gsp-tasks/scripts/task_dag.py'
    spec = importlib.util.spec_from_file_location('gsp_session_task_dag', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_plan(value):
    path = Path(canonical_document(value))
    raw = path.read_bytes()
    module = dag_module()
    data = module.parse_document(raw.decode('utf-8'))
    module.validate(data)
    require(data.get('version') == 2, 'session control requires DAG v2')
    return data, hashlib.sha256(raw).hexdigest(), module


class Store:
    def __init__(self, root):
        self.root = owned_path(root, 'dir')
        require(self.root.name == '.gsp-work', 'work-root must end with .gsp-work')
        self.directory = self.root / 'control'
        if not self.directory.exists():
            self.directory.mkdir(mode=0o700, exist_ok=True)
        owned_path(self.directory, 'dir')
        self.path = self.directory / 'state.json'

    def open_lock(self, name):
        path = self.directory / name
        fd = os.open(str(path), os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        info = os.fstat(fd)
        if info.st_uid != os.getuid() or not stat.S_ISREG(info.st_mode):
            os.close(fd)
            raise ControlError('invalid lock ownership/type')
        return fd

    @contextlib.contextmanager
    def transaction(self):
        fd = self.open_lock('state.lock')
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            if self.path.exists() or self.path.is_symlink():
                owned_path(self.path, 'file')
                try:
                    require(self.path.stat().st_size <= 16 * 1024 * 1024, 'state size limit exceeded')
                    state = json.loads(self.path.read_text(), object_pairs_hook=unique_object, parse_constant=lambda v: require(False, 'nonfinite JSON value'))
                except (ValueError, UnicodeError, RecursionError) as exc:
                    raise ControlError('corrupt state: ' + str(exc)) from None
                validate_state(state)
            else:
                state = {'version': 1, 'sessions': {}, 'events': {}}
            yield state
            validate_state(state)
            encoded = json.dumps(state, ensure_ascii=False, sort_keys=True, indent=2)
            require(len(encoded.encode('utf-8')) <= 16 * 1024 * 1024, 'state size limit exceeded')
            tmpfd, tmpname = tempfile.mkstemp(prefix='state-', dir=str(self.directory))
            try:
                with os.fdopen(tmpfd, 'w') as output:
                    output.write(encoded)
                    output.flush()
                    os.fsync(output.fileno())
                os.replace(tmpname, self.path)
                dirfd = os.open(str(self.directory), os.O_RDONLY | os.O_DIRECTORY)
                try:
                    os.fsync(dirfd)
                finally:
                    os.close(dirfd)
            finally:
                if os.path.exists(tmpname):
                    os.unlink(tmpname)
        finally:
            os.close(fd)


def validate_state(state):
    require(isinstance(state, dict) and set(state) == {'version', 'sessions', 'events'} and type(state['version']) is int and state['version'] == 1, 'corrupt state header')
    require(isinstance(state['sessions'], dict) and isinstance(state['events'], dict), 'corrupt state mappings')
    threads = set()
    for sid, session in state['sessions'].items():
        identifier(sid)
        require(isinstance(session, dict) and set(session) == {'thread', 'tasks', 'document', 'cwd'}, 'corrupt session')
        identifier(session['thread'])
        require(session['thread'] not in threads, 'duplicate registered thread')
        threads.add(session['thread'])
        require(isinstance(session['tasks'], list) and session['tasks'] and len(set(session['tasks'])) == len(session['tasks']), 'corrupt session tasks')
        for task in session['tasks']:
            identifier(task)
        require(all(isinstance(session[k], str) and Path(session[k]).is_absolute() for k in ('document', 'cwd')), 'corrupt session paths')
        stored_document(session['document'])
    for eid, event in state['events'].items():
        identifier(eid)
        fields = {'revision', 'tasks', 'reason', 'document', 'digest', 'contracts', 'basis_keys', 'targets', 'unregistered', 'resolved', 'superseded_by', 'history'}
        require(isinstance(event, dict) and set(event) == fields, 'corrupt event')
        require(type(event['revision']) is int and event['revision'] > 0, 'corrupt event revision')
        require(isinstance(event['reason'], str) and event['reason'].strip() and isinstance(event['document'], str) and Path(event['document']).is_absolute() and isinstance(event['digest'], str) and re.fullmatch('[0-9a-f]{64}', event['digest']), 'corrupt event metadata')
        stored_document(event['document'])
        require(isinstance(event['tasks'], list) and event['tasks'] and len(event['tasks']) == len(set(event['tasks'])), 'corrupt event tasks')
        for tid in event['tasks']:
            identifier(tid)
        require(isinstance(event['basis_keys'], dict) and set(event['basis_keys']) == set(event['tasks']) and all(isinstance(keys, list) and all(isinstance(k, str) and k in event['contracts'] for k in keys) and len(keys) == len(set(keys)) for keys in event['basis_keys'].values()), 'corrupt captured basis keys')
        require(isinstance(event['contracts'], dict) and all(type(v) is int and v > 0 for v in event['contracts'].values()), 'corrupt captured contracts')
        require(isinstance(event['targets'], dict) and isinstance(event['unregistered'], list) and isinstance(event['history'], list), 'corrupt event targets/history')
        require(all(isinstance(t, str) and t in event['tasks'] for t in event['unregistered']) and len(set(event['unregistered'])) == len(event['unregistered']), 'corrupt unregistered tasks')
        require(type(event['resolved']) is bool and (event['superseded_by'] is None or event['superseded_by'] in state['events']), 'corrupt event closure')
        for sid, target in event['targets'].items():
            require(sid in state['sessions'] and isinstance(target, dict) and set(target) == {'delivery', 'attempts', 'ack', 'reason', 'evidence', 'registration'}, 'corrupt target')
            require(registration_covers(state['sessions'][sid], target['registration']), 'target registration identity changed')
            stored_document(target['registration']['document'])
            require(isinstance(target['reason'], str), 'corrupt target reason')
            require(target['delivery'] in ('pending', 'deferred', 'sending', 'uncertain', 'delivered'), 'corrupt delivery')
            require(isinstance(target['evidence'], list), 'corrupt ACK evidence list')
            previous_ack = None
            ranks = {None: 0, 'read': 1, 'held': 2, 'applied': 3}
            for entry in target['evidence']:
                require(isinstance(entry, dict) and set(entry) == {'state', 'evidence', 'revision'} and entry['state'] in ('read', 'held', 'applied') and isinstance(entry['evidence'], str) and entry['evidence'].strip() and entry['revision'] == event['revision'], 'corrupt ACK evidence')
                require(ranks[entry['state']] >= ranks[previous_ack] and (entry['state'] != 'applied' or previous_ack in ('held', 'applied')), 'corrupt ACK transition history')
                previous_ack = entry['state']
            require(target['ack'] == previous_ack, 'ACK lacks matching evidence')
            require(type(target['attempts']) is int and target['attempts'] >= 0 and target['ack'] in (None, 'read', 'held', 'applied') and isinstance(target['evidence'], list), 'corrupt target state')


def selected_tasks(plan, ids):
    require(ids and len(set(ids)) == len(ids), 'tasks must be nonempty and unique')
    tasks = {task['id']: task for task in plan['tasks']}
    require(all(tid in tasks for tid in ids), 'unknown task')
    return [tasks[tid] for tid in ids]


def registration_covers(current, captured):
    return (isinstance(captured, dict) and set(captured) == {'thread', 'tasks', 'document', 'cwd'} and all(current[k] == captured[k] for k in ('thread', 'cwd')) and same_document(current['document'], captured['document']) and isinstance(captured['tasks'], list) and all(isinstance(t, str) for t in captured['tasks']) and set(captured['tasks']) <= set(current['tasks']))


def register(store, args):
    args.document = canonical_document(args.document)
    plan, _, _ = load_plan(args.document)
    sid, thread = identifier(args.session), identifier(args.thread)
    owned_path(store.root / 'sessions' / sid / 'work.md', 'file')
    tasks = selected_tasks(plan, args.tasks)
    require(all(task['owner'] == sid for task in tasks), 'task owner must equal session ID')
    cwd = owned_path(args.cwd or store.root.parent, 'dir')
    document = Path(args.document)
    require(any(base == document or base in document.parents for base in (cwd, store.root.parent)), 'document outside registered project/main cwd')
    registration = {'thread': thread, 'tasks': sorted(args.tasks), 'document': str(Path(args.document)), 'cwd': str(cwd)}
    with store.transaction() as state:
        require(sid not in state['sessions'] or registration_covers(registration, state['sessions'][sid]), 'session already bound; removal or silent rebinding forbidden')
        require(all(key == sid or s['thread'] != thread for key, s in state['sessions'].items()), 'thread already registered')
        state['sessions'][sid] = registration
    return registration


def publish(store, args):
    args.document = canonical_document(args.document)
    plan, digest, module = load_plan(args.document)
    require(plan['plan_revision'] == args.expected_revision, 'plan revision mismatch')
    tasks = selected_tasks(plan, args.tasks)
    validity = module.validate(plan).get('task_validity', {})
    require(all(task.get('hold') or validity.get(task['id']) for task in tasks), 'each affected task must be stale or held')
    captured = {key: plan['contracts'][key] for task in tasks for key in task['basis']}
    identifier(args.change)
    require(bool(args.reason.strip()), 'reason required')
    with store.transaction() as state:
        signature = {'revision': args.expected_revision, 'tasks': sorted(args.tasks), 'reason': args.reason, 'document': args.document, 'digest': digest, 'contracts': captured, 'basis_keys': {task['id']: sorted(task['basis']) for task in tasks}}
        if args.change in state['events']:
            previous = state['events'][args.change]
            require(all(previous[k] == v for k, v in signature.items()), 'change ID reused with different content')
            return previous
        targets = {sid: {'delivery': 'pending', 'attempts': 0, 'ack': None, 'reason': '', 'evidence': [], 'registration': dict(s)} for sid, s in state['sessions'].items() if set(s['tasks']) & set(args.tasks) and same_document(s['document'], args.document)}
        covered = {t for sid in targets for t in state['sessions'][sid]['tasks']}
        event = dict(signature, targets=targets, unregistered=sorted(set(args.tasks) - covered), resolved=False, superseded_by=None, history=[])
        state['events'][args.change] = event
        return event


def event_by_id(state, eid):
    require(eid in state['events'], 'unknown change')
    return state['events'][eid]


def acknowledge(store, args):
    require(bool(args.evidence.strip()), 'evidence required')
    with store.transaction() as state:
        event = event_by_id(state, args.change)
        require(not event['resolved'] and not event['superseded_by'], 'event no longer unresolved')
        require(args.revision == event['revision'], 'ACK revision mismatch')
        require(args.session in event['targets'], 'session is not an event target')
        target = event['targets'][args.session]
        rank = {None: 0, 'read': 1, 'held': 2, 'applied': 3}
        require(rank[args.state] >= rank[target['ack']], 'ACK cannot regress')
        require(args.state != 'applied' or target['ack'] in ('held', 'applied'), 'applied requires held ACK')
        target['ack'] = args.state
        target['evidence'].append({'state': args.state, 'evidence': args.evidence, 'revision': args.revision})
        return target


def closure_reasons(event, plan, result, document):
    reasons = []
    if not same_document(document, event['document']):
        reasons.append('document mismatch')
    if plan['plan_revision'] < event['revision']:
        reasons.append('plan older than event')
    if any(plan['contracts'].get(k) != value for k, value in event['contracts'].items()):
        reasons.append('affected contract changed; publish and supersede required')
    current_tasks = {task['id']: task for task in plan['tasks']}
    if any(tid not in current_tasks or set(current_tasks[tid]['basis']) != set(keys) for tid, keys in event['basis_keys'].items()):
        reasons.append('affected task basis keys changed; publish and supersede required')
    if not result['complete']:
        reasons.append('current acceptance incomplete')
    if event['unregistered']:
        reasons.append('unregistered tasks')
    if any(t['ack'] != 'applied' for t in event['targets'].values()):
        reasons.append('applied ACK missing')
    return reasons


def acceptance_check(store, document):
    document = canonical_document(document)
    plan, _, module = load_plan(document)
    result = module.check(plan)
    with store.transaction() as state:
        unresolved = {eid: closure_reasons(e, plan, result, document) or ['explicit resolve required'] for eid, e in state['events'].items() if same_document(e['document'], document) and not e['resolved'] and not e['superseded_by']}
    return {'complete': bool(result['complete']) and not unresolved, 'dag': result, 'unresolved': unresolved}


def resolve(store, args):
    args.document = canonical_document(args.document)
    plan, _, module = load_plan(args.document)
    require(plan['plan_revision'] == args.expected_revision, 'current plan revision mismatch')
    require(args.evidence.strip(), 'evidence required')
    result = module.check(plan)
    with store.transaction() as state:
        event = event_by_id(state, args.change)
        require(not event['superseded_by'], 'superseded event cannot resolve')
        reasons = closure_reasons(event, plan, result, args.document)
        require(not reasons, '; '.join(reasons))
        event['resolved'] = True
        event['history'].append({'action': 'resolve', 'revision': args.expected_revision, 'evidence': args.evidence})
        return event


def supersede(store, args):
    require(args.change != args.by and args.evidence.strip(), 'distinct events and evidence required')
    with store.transaction() as state:
        old, new = event_by_id(state, args.change), event_by_id(state, args.by)
        require(same_document(old['document'], new['document']), 'supersede requires same document')
        require(not old['resolved'] and not old['superseded_by'] and not new['resolved'] and not new['superseded_by'], 'events must be unresolved')
        plan, digest, _ = load_plan(new['document'])
        require(new['revision'] == plan['plan_revision'] and new['digest'] == digest, 'new event is not current plan')
        current_tasks = {t['id']: t for t in plan['tasks']}
        require(all(tid in current_tasks and set(current_tasks[tid]['basis']) == set(keys) for tid, keys in new['basis_keys'].items()), 'new event basis key scope changed')
        require(new['revision'] >= old['revision'] and set(old['tasks']) <= set(new['tasks']) and set(old['targets']) <= set(new['targets']), 'new event must cover old tasks and sessions')
        old['superseded_by'] = args.by
        old['history'].append({'action': 'supersede', 'by': args.by, 'evidence': args.evidence})
        return old


class WebSocket:
    """Bounded Unix WebSocket JSON-RPC client; no subprocess or session creation."""
    MAX = 8 * 1024 * 1024

    def __init__(self, path, timeout=5):
        owned_path(path, 'socket')
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(timeout)
        self.timeout = timeout
        self.buffer = b''
        self.counter = 0
        self.deadline = time.monotonic() + timeout
        try:
            self.sock.connect(str(path))
            key = base64.b64encode(os.urandom(16)).decode()
            self.sock.sendall(('GET / HTTP/1.1\r\nHost: localhost\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: ' + key + '\r\nSec-WebSocket-Version: 13\r\n\r\n').encode())
            while b'\r\n\r\n' not in self.buffer:
                remaining = self.deadline - time.monotonic()
                require(remaining > 0, 'handshake timeout')
                self.sock.settimeout(remaining)
                require(len(self.buffer) < 16384, 'oversized WebSocket handshake')
                chunk = self.sock.recv(4096)
                require(chunk, 'closed during handshake')
                self.buffer += chunk
            header, self.buffer = self.buffer.split(b'\r\n\r\n', 1)
            require(len(header) <= 16384, 'oversized WebSocket handshake')
            lines = header.decode('ascii').split('\r\n')
            require(lines[0].split(' ', 2)[:2] == ['HTTP/1.1', '101'], 'WebSocket upgrade rejected')
            headers = {}
            for line in lines[1:]:
                k, v = line.split(':', 1)
                require(k.lower() not in headers, 'duplicate handshake header')
                headers[k.lower()] = v.strip()
            expected = base64.b64encode(hashlib.sha1((key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest()).decode()
            require(headers.get('sec-websocket-accept') == expected and headers.get('upgrade', '').lower() == 'websocket' and 'upgrade' in [x.strip().lower() for x in headers.get('connection', '').split(',')], 'invalid WebSocket handshake')
        except BaseException:
            self.close()
            raise

    def close(self):
        self.sock.close()

    def read_exact(self, count):
        while len(self.buffer) < count:
            remaining = self.deadline - time.monotonic()
            require(remaining > 0, 'WebSocket operation timeout')
            self.sock.settimeout(remaining)
            chunk = self.sock.recv(min(65536, count - len(self.buffer)))
            require(chunk, 'WebSocket closed')
            self.buffer += chunk
        value, self.buffer = self.buffer[:count], self.buffer[count:]
        return value

    def frame(self, opcode, payload):
        require(len(payload) <= self.MAX, 'message too large')
        mask = os.urandom(4)
        length = len(payload)
        head = bytes([0x80 | opcode])
        if length < 126:
            head += bytes([0x80 | length])
        elif length < 65536:
            head += bytes([0xFE]) + struct.pack('!H', length)
        else:
            head += bytes([0xFF]) + struct.pack('!Q', length)
        self.sock.sendall(head + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(payload)))

    def receive(self):
        fragments = bytearray()
        started = False
        while True:
            a, b = self.read_exact(2)
            require(not a & 0x70 and not b & 0x80, 'invalid server frame flags')
            opcode, length = a & 15, b & 127
            if length == 126:
                length = struct.unpack('!H', self.read_exact(2))[0]
            elif length == 127:
                length = struct.unpack('!Q', self.read_exact(8))[0]
            require(length <= self.MAX and len(fragments) + length <= self.MAX, 'oversized frame/message')
            require(opcode in (0, 1, 8, 9, 10), 'unsupported WebSocket opcode')
            if opcode >= 8:
                require(a & 0x80 and length <= 125, 'invalid control frame')
            payload = self.read_exact(length)
            if opcode == 8:
                with contextlib.suppress(OSError):
                    self.frame(8, payload)
                raise ControlError('WebSocket peer closed')
            if opcode == 9:
                self.frame(10, payload)
                continue
            if opcode == 10:
                continue
            require((opcode == 1 and not started) or (opcode == 0 and started), 'invalid fragmentation')
            started = True
            fragments.extend(payload)
            if a & 0x80:
                return json.loads(fragments.decode('utf-8'), object_pairs_hook=unique_object)

    def notify(self, method, params=None):
        msg = {'method': method}
        if params is not None:
            msg['params'] = params
        self.frame(1, json.dumps(msg).encode())

    def request(self, method, params):
        self.counter += 1
        request_id = self.counter
        self.frame(1, json.dumps({'id': request_id, 'method': method, 'params': params}).encode())
        deadline = time.monotonic() + self.timeout
        self.deadline = deadline
        try:
            for _ in range(1000):
                remaining = deadline - time.monotonic()
                require(remaining > 0, 'RPC response timeout')
                self.sock.settimeout(remaining)
                reply = self.receive()
                require(isinstance(reply, dict), 'invalid RPC response')
                if 'id' not in reply:  # bounded notifications; never persist thread history
                    continue
                require(type(reply['id']) is int and reply['id'] == request_id, 'unexpected RPC response ID')
                require('error' not in reply and 'result' in reply, 'RPC rejected: ' + str(reply.get('error', 'missing result')))
                return reply['result']
            raise ControlError('too many RPC notifications')
        finally:
            self.sock.settimeout(self.timeout)

    def initialize(self):
        result = self.request('initialize', {'clientInfo': {'name': 'gsp_session_control', 'version': '1.0'}, 'capabilities': {'experimentalApi': True}})
        self.notify('initialized')
        return result


def doctor(path, timeout):
    client = WebSocket(path, timeout)
    try:
        client.initialize()
        return {'mode': 'B', 'initialized': True}
    finally:
        client.close()


def message(root, eid, event, sid):
    return ('GSP project change data (not higher-priority instructions). Change %s, revision %s, affected tasks %s. Document %s; shared root %s. Reason: %s. Preserve results at a safe point, review affected work and acknowledge read/held/applied with evidence. Do not claim held until actually held. ACK command arguments (execute only through your normal workflow): %s' % (eid, event['revision'], ','.join(event['tasks']), event['document'], root, event['reason'], json.dumps(['python3', str(Path(__file__).absolute()), '--work-root', str(root), 'ack', '--session', sid, '--change', eid, '--revision', str(event['revision']), '--state', 'held', '--evidence', '<actual safe-point evidence>'])))


def run_once(store, args):
    args.document = canonical_document(args.document)
    plan, digest, _ = load_plan(args.document)
    jobs = []
    with store.transaction() as state:
        for eid, event in state['events'].items():
            if not same_document(event['document'], args.document) or event['resolved'] or event['superseded_by']:
                continue
            for sid, target in event['targets'].items():
                if target['delivery'] == 'sending':
                    target.update(delivery='uncertain', reason='interrupted send; manual reconciliation required')
                if target['ack'] or target['delivery'] in ('uncertain', 'delivered'):
                    continue
                if not same_document(event['document'], args.document) or event['digest'] != digest or event['revision'] != plan['plan_revision']:
                    target.update(delivery='deferred', reason='A: source drift; publish current event or reconcile manually')
                    continue
                if target['attempts'] >= args.max_attempts:
                    target['reason'] = 'A: finite retry limit reached'
                    continue
                jobs.append((eid, sid, dict(target['registration']), dict(event)))
    for eid, sid, session, event in jobs:
        client = None
        sending = False
        try:
            # Reserve the finite pre-send attempt, without holding lock over I/O.
            with store.transaction() as state:
                target = state['events'][eid]['targets'][sid]
                target['attempts'] += 1
            owned_path(store.root / 'sessions' / sid / 'work.md', 'file')
            client = WebSocket(args.socket, args.timeout)
            client.initialize()
            reply = client.request('thread/read', {'threadId': session['thread'], 'includeTurns': True})
            thread = reply.get('thread', {})
            require(thread.get('id') == session['thread'], 'thread ID mismatch')
            require(thread.get('cwd') == session['cwd'], 'thread/project cwd mismatch')
            turns = [turn for turn in thread.get('turns', []) if turn.get('status') == 'inProgress']
            active = isinstance(thread.get('status'), dict) and thread['status'].get('type') == 'active' and thread['status'].get('activeFlags') == []
            require(active and len(turns) == 1 and isinstance(turns[0].get('id'), str) and thread.get('canAcceptDirectInput') is True, 'thread not confirmed active/steerable; idle is not awakened')
            # Re-read source immediately before recording irreversible sending boundary.
            _, current_digest, _ = load_plan(args.document)
            require(current_digest == digest, 'source drift before send')
            with store.transaction() as state:
                current = state['events'][eid]
                target = current['targets'][sid]
                require(not current['resolved'] and not current['superseded_by'] and not target['ack'], 'event changed before send')
                target.update(delivery='sending', reason='send reserved; no automatic resend after this point')
            sending = True
            result = client.request('turn/steer', {'threadId': session['thread'], 'expectedTurnId': turns[0]['id'], 'input': [{'type': 'text', 'text': message(store.root, eid, event, sid), 'text_elements': []}]})
            require(isinstance(result, dict) and result.get('turnId') == turns[0]['id'], 'steer response turn mismatch')
            with store.transaction() as state:
                state['events'][eid]['targets'][sid].update(delivery='delivered', reason='transport accepted; business ACK still required')
        except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
            with store.transaction() as state:
                state['events'][eid]['targets'][sid].update(delivery='uncertain' if sending else 'deferred', reason=('A: ' + str(exc))[:600])
        finally:
            if client:
                client.close()


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--work-root', required=True, help='absolute shared main .gsp-work')
    sub = p.add_subparsers(dest='command', required=True)
    doctor_p = sub.add_parser('doctor')
    doctor_p.add_argument('--socket', required=True)
    doctor_p.add_argument('--timeout', type=float, default=5)
    reg = sub.add_parser('register')
    reg.add_argument('--session', required=True)
    reg.add_argument('--thread', required=True)
    reg.add_argument('--tasks', nargs='+', required=True)
    reg.add_argument('--document', required=True)
    reg.add_argument('--cwd', help='explicit registered main/worktree cwd; defaults to work-root parent')
    pub = sub.add_parser('publish')
    pub.add_argument('--change', required=True)
    pub.add_argument('--expected-revision', type=int, required=True)
    pub.add_argument('--tasks', nargs='+', required=True)
    pub.add_argument('--reason', required=True)
    pub.add_argument('--document', required=True)
    ack = sub.add_parser('ack')
    ack.add_argument('--session', required=True)
    ack.add_argument('--change', required=True)
    ack.add_argument('--revision', type=int, required=True)
    ack.add_argument('--state', choices=['read', 'held', 'applied'], required=True)
    ack.add_argument('--evidence', required=True)
    run = sub.add_parser('run')
    run.add_argument('--socket', required=True)
    run.add_argument('--document', required=True)
    run.add_argument('--once', action='store_true')
    run.add_argument('--timeout', type=float, default=5)
    run.add_argument('--max-attempts', type=int, default=3)
    run.add_argument('--interval', type=float, default=5)
    sub.add_parser('status')
    sub.add_parser('check').add_argument('--document', required=True)
    res = sub.add_parser('resolve')
    res.add_argument('--change', required=True)
    res.add_argument('--expected-revision', type=int, required=True)
    res.add_argument('--document', required=True)
    res.add_argument('--evidence', required=True)
    sup = sub.add_parser('supersede')
    sup.add_argument('--change', required=True)
    sup.add_argument('--by', required=True)
    sup.add_argument('--evidence', required=True)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        store = Store(args.work_root)
        if args.command == 'doctor':
            require(math.isfinite(args.timeout) and args.timeout > 0, 'timeout must be positive and finite')
            result = doctor(args.socket, args.timeout)
        elif args.command == 'register':
            result = register(store, args)
        elif args.command == 'publish':
            result = publish(store, args)
        elif args.command == 'ack':
            result = acknowledge(store, args)
        elif args.command == 'resolve':
            result = resolve(store, args)
        elif args.command == 'supersede':
            result = supersede(store, args)
        elif args.command == 'check':
            result = acceptance_check(store, args.document)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result['complete'] else 1
        elif args.command == 'run':
            require(args.max_attempts > 0 and math.isfinite(args.timeout) and math.isfinite(args.interval) and args.timeout > 0 and args.interval > 0, 'positive finite retry/time bounds required')
            lock = store.open_lock('watcher.lock')
            try:
                try:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    raise ControlError('another project watcher is running') from None
                while True:
                    run_once(store, args)
                    if args.once:
                        break
                    time.sleep(args.interval)
            finally:
                os.close(lock)
            result = {'mode': 'B opt-in / A for deferred targets', 'processed': True}
        else:
            with store.transaction() as state:
                result = state
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, ImportError, RecursionError) as exc:
        print(json.dumps({'mode': 'A', 'error': str(exc)}, ensure_ascii=False))
        return 2
    except KeyboardInterrupt:
        return 130


if __name__ == '__main__':
    raise SystemExit(main())
