"""Behavioral tests: temporary projects and synthetic Unix WebSocket only."""
import argparse
import base64
import copy
import contextlib
import fcntl
import io
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / '.agents/skills/gsp-development/scripts/session_control.py'
spec = importlib.util.spec_from_file_location('session_control', SCRIPT)
control = importlib.util.module_from_spec(spec)
spec.loader.exec_module(control)


class Server:
    def __init__(self, path, cwd, mode='active', fragment=False):
        self.path, self.cwd, self.mode, self.fragment = str(path), str(cwd), mode, fragment
        self.methods = []
        self.requests = []
        self.error = None
        self.listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.listener.bind(self.path)
        self.listener.listen(1)
        self.listener.settimeout(3)
        self.worker = threading.Thread(target=self.serve, daemon=True)
        self.worker.start()

    def exact(self, sock, n):
        value = b''
        while len(value) < n:
            chunk = sock.recv(n - len(value))
            if not chunk:
                raise EOFError()
            value += chunk
        return value

    def frame(self, sock, obj):
        raw = json.dumps(obj).encode()
        def send(opcode, payload, fin=True):
            size = len(payload)
            head = bytes([(128 if fin else 0) | opcode])
            if size < 126:
                head += bytes([size])
            else:
                head += bytes([126]) + struct.pack('!H', size)
            sock.sendall(head + payload)
        if self.fragment:
            send(1, raw[:5], False)
            send(9, b'ping')
            send(0, raw[5:])
        else:
            send(1, raw)

    def serve(self):
        try:
            conn, _ = self.listener.accept()
            with conn:
                conn.settimeout(2)
                header = b''
                while not header.endswith(b'\r\n\r\n'):
                    header += self.exact(conn, 1)
                key = [line.split(b': ', 1)[1] for line in header.split(b'\r\n') if line.startswith(b'Sec-WebSocket-Key:')][0]
                digest = base64.b64encode(hashlib.sha1(key + b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').digest())
                if self.mode == 'bad-handshake':
                    digest = b'wrong'
                conn.sendall(b'HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: ' + digest + b'\r\n\r\n')
                while True:
                    a, b = self.exact(conn, 2)
                    assert a & 128 and b & 128, 'client must mask frames'
                    size = b & 127
                    if size == 126:
                        size = struct.unpack('!H', self.exact(conn, 2))[0]
                    if size == 127:
                        size = struct.unpack('!Q', self.exact(conn, 8))[0]
                    mask = self.exact(conn, 4)
                    raw = self.exact(conn, size)
                    raw = bytes(c ^ mask[i % 4] for i, c in enumerate(raw))
                    if a & 15 == 10:
                        continue
                    obj = json.loads(raw)
                    self.methods.append(obj['method'])
                    self.requests.append(obj)
                    if obj['method'] == 'initialized':
                        continue
                    if obj['method'] == 'initialize':
                        if self.mode == 'close':
                            conn.sendall(b'\x88\x00')
                            return
                        if self.mode == 'oversized':
                            conn.sendall(b'\x81\x7f' + struct.pack('!Q', 9 * 1024 * 1024))
                            return
                        result = {'userAgent': 'synthetic'}
                    elif obj['method'] == 'thread/read':
                        result = {'thread': {'id': 'thread-a', 'cwd': '/wrong' if self.mode == 'wrong-cwd' else self.cwd, 'status': {'type': 'idle' if self.mode == 'idle' else 'active', 'activeFlags': ['waitingOnApproval'] if self.mode == 'waiting' else []}, 'canAcceptDirectInput': False if self.mode == 'refused' else (None if self.mode == 'unknown' else True), 'turns': [] if self.mode == 'idle' else [{'id': 'turn-a', 'status': 'inProgress'}]}}
                    elif obj['method'] == 'turn/steer':
                        if self.mode == 'lost':
                            return
                        result = {'turnId': 'turn-a'}
                    else:
                        raise AssertionError('unauthorized method ' + obj['method'])
                    self.frame(conn, {'id': obj['id'] + (99 if self.mode == 'wrong-id' else 0), 'result': result})
        except (EOFError, BrokenPipeError, ConnectionResetError):
            pass
        except BaseException as exc:
            self.error = exc
        finally:
            self.listener.close()

    def finish(self):
        self.worker.join(4)
        if self.error:
            raise self.error


class ControlTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)
        self.root = self.project / '.gsp-work'
        (self.root / 'sessions' / 'worker').mkdir(parents=True)
        (self.root / 'sessions' / 'worker' / 'work.md').write_text('own session')
        self.document = self.project / 'tasks.md'
        self.plan = {'version': 2, 'plan_revision': 5, 'max_parallel': 1, 'contracts': {'R1': 2}, 'tasks': [{'id': 'T1', 'title': 'task', 'owner': 'worker', 'deps': [], 'status': 'done', 'reads': [], 'writes': ['a'], 'resources': [], 'evidence': 'previous execution', 'basis': {'R1': 2}, 'hold': 'changed work'}], 'acceptance': [{'id': 'A1', 'contracts': {'R1': 2}, 'tasks': ['T1']}]}
        self.write_plan()
        self.store = control.Store(str(self.root))

    def write_plan(self):
        self.document.write_text('<!-- GSP-DAG:START -->\n```json\n' + json.dumps(self.plan) + '\n```\n<!-- GSP-DAG:END -->\n')

    def args(self, **kw):
        return argparse.Namespace(document=str(self.document), **kw)

    def register(self):
        return control.register(self.store, self.args(session='worker', thread='thread-a', tasks=['T1'], cwd=None))

    def publish(self, change='C1'):
        return control.publish(self.store, self.args(change=change, expected_revision=self.plan['plan_revision'], tasks=['T1'], reason='interface changed'))

    def ack(self, state, revision=5, change='C1'):
        return control.acknowledge(self.store, self.args(session='worker', change=change, revision=revision, state=state, evidence='safe point ' + state))

    def event(self, eid='C1'):
        with self.store.transaction() as state:
            return copy.deepcopy(state['events'][eid])

    def run_server(self, mode='active', fragment=False):
        path = self.project / ('socket-' + mode)
        server = Server(path, self.project, mode, fragment)
        with contextlib.redirect_stdout(io.StringIO()):
            control.main(['--work-root', str(self.root), 'run', '--socket', str(path), '--document', str(self.document), '--once', '--timeout', '0.5', '--max-attempts', '8'])
        server.finish()
        return server

    def test_cm_a1_hold_clear_new_revision_and_independent_event(self):
        self.register()
        self.publish()
        self.publish('C2')
        self.ack('held')
        self.ack('applied')
        self.plan['plan_revision'] = 6
        del self.plan['tasks'][0]['hold']
        self.write_plan()
        control.resolve(self.store, self.args(change='C1', expected_revision=6, evidence='verified current acceptance'))
        self.assertTrue(self.event()['resolved'])
        self.assertFalse(control.acceptance_check(self.store, str(self.document))['complete'])
        with self.assertRaisesRegex(control.ControlError, 'revision mismatch'):
            self.ack('held', revision=6, change='C2')
        self.ack('held', change='C2')
        self.ack('applied', change='C2')
        control.resolve(self.store, self.args(change='C2', expected_revision=6, evidence='verified C2'))
        self.assertTrue(control.acceptance_check(self.store, str(self.document))['complete'])

    def test_capture_current_contract_not_stale_basis(self):
        self.plan['tasks'][0]['basis']['R1'] = 1
        self.write_plan()
        self.register()
        event = self.publish()
        self.assertEqual({'R1': 2}, event['contracts'])

    def test_idempotent_publish_owner_and_rebinding(self):
        self.register()
        self.assertEqual(self.publish(), self.publish())
        with self.assertRaises(control.ControlError):
            control.publish(self.store, self.args(change='C1', expected_revision=5, tasks=['T1'], reason='different'))
        with self.assertRaises(control.ControlError):
            control.register(self.store, self.args(session='worker', thread='different', tasks=['T1'], cwd=None))
        self.plan['tasks'][0]['owner'] = 'other'
        self.write_plan()
        with self.assertRaises(control.ControlError):
            self.register()

    def test_ack_monotonic_exact_and_unregistered(self):
        self.publish()
        self.assertEqual(['T1'], self.event()['unregistered'])
        with self.assertRaises(control.ControlError):
            self.ack('held')
        self.register()
        self.publish('C2')
        with self.assertRaises(control.ControlError):
            self.ack('applied', change='C2')
        self.ack('held', change='C2')
        with self.assertRaises(control.ControlError):
            self.ack('read', change='C2')
        self.assertFalse(control.acceptance_check(self.store, str(self.document))['complete'])

    def test_supersede_requires_coverage_and_new_acks(self):
        self.register()
        self.publish()
        self.ack('held')
        self.plan['contracts']['R1'] = 3
        self.plan['plan_revision'] = 6
        self.write_plan()
        self.publish('C2')
        control.supersede(self.store, self.args(change='C1', by='C2', evidence='new contract'))
        self.assertEqual('C2', self.event()['superseded_by'])
        self.assertIsNone(self.event('C2')['targets']['worker']['ack'])
        self.assertIn('C2', control.acceptance_check(self.store, str(self.document))['unresolved'])
        with self.assertRaises(control.ControlError):
            self.ack('applied')

    def test_contract_drift_blocks_resolution(self):
        self.register()
        self.publish()
        self.ack('held')
        self.ack('applied')
        self.plan['contracts']['R1'] = 3
        self.plan['plan_revision'] = 6
        self.write_plan()
        with self.assertRaisesRegex(control.ControlError, 'affected contract changed'):
            control.resolve(self.store, self.args(change='C1', expected_revision=6, evidence='wrong'))

    def test_active_fragment_ping_delivery_and_captured_identity(self):
        self.register()
        self.publish()
        server = self.run_server(fragment=True)
        self.assertEqual(['initialize', 'initialized', 'thread/read', 'turn/steer'], server.methods)
        target = self.event()['targets']['worker']
        self.assertEqual('delivered', target['delivery'])
        self.assertIsNone(target['ack'])
        self.assertEqual('thread-a', target['registration']['thread'])
        self.assertEqual('turn-a', server.requests[-1]['params']['expectedTurnId'])
        self.assertIn('revision 5', server.requests[-1]['params']['input'][0]['text'])

    def test_idle_and_wrong_cwd_never_steer(self):
        self.register()
        self.publish()
        for mode in ('idle', 'wrong-cwd', 'waiting', 'refused', 'unknown'):
            server = self.run_server(mode)
            self.assertNotIn('turn/steer', server.methods)
            self.assertEqual('deferred', self.event()['targets']['worker']['delivery'])
            self.assertIsNone(self.event()['targets']['worker']['ack'])

    def test_lost_steer_ack_uncertain_and_restart_no_resend(self):
        self.register()
        self.publish()
        server = self.run_server('lost')
        self.assertIn('turn/steer', server.methods)
        self.assertEqual('uncertain', self.event()['targets']['worker']['delivery'])
        args = self.args(socket=str(self.project / 'missing'), timeout=.1, max_attempts=3)
        control.run_once(self.store, args)
        self.assertEqual(1, self.event()['targets']['worker']['attempts'])
        with self.store.transaction() as state:
            state['events']['C1']['targets']['worker']['delivery'] = 'sending'
        control.run_once(self.store, args)
        self.assertEqual('uncertain', self.event()['targets']['worker']['delivery'])

    def test_pre_send_retry_bound_and_source_drift(self):
        self.register()
        self.publish()
        args = self.args(socket=str(self.project / 'missing'), timeout=.1, max_attempts=2)
        for _ in range(4):
            control.run_once(self.store, args)
        self.assertEqual(2, self.event()['targets']['worker']['attempts'])
        self.plan['plan_revision'] = 6
        self.write_plan()
        control.run_once(self.store, args)
        self.assertIn('source drift', self.event()['targets']['worker']['reason'])

    def test_corrupt_state_duplicate_json_symlink(self):
        self.store.path.write_text('{bad')
        with self.assertRaises(control.ControlError):
            with self.store.transaction():
                pass
        self.assertEqual('{bad', self.store.path.read_text())
        self.store.path.write_text('{"version":1,"version":1,"sessions":{},"events":{}}')
        with self.assertRaises(control.ControlError):
            with self.store.transaction():
                pass
        self.store.path.unlink()
        self.store.path.symlink_to(self.document)
        with self.assertRaises(control.ControlError):
            with self.store.transaction():
                pass

    def test_protocol_bad_handshake_and_wrong_response_id(self):
        for mode in ('bad-handshake', 'wrong-id', 'close', 'oversized'):
            server = Server(self.project / mode, self.project, mode)
            with self.assertRaises(control.ControlError):
                control.doctor(self.project / mode, .5)
            server.finish()

    def test_concurrent_cli_acks_keep_all_evidence(self):
        self.register()
        self.publish()
        commands = [[sys.executable, str(SCRIPT), '--work-root', str(self.root), 'ack', '--session', 'worker', '--change', 'C1', '--revision', '5', '--state', 'held', '--evidence', str(i)] for i in range(5)]
        procs = [subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for cmd in commands]
        for proc in procs:
            out, err = proc.communicate(timeout=5)
            self.assertEqual(0, proc.returncode, (out, err))
        self.assertEqual(5, len(self.event()['targets']['worker']['evidence']))

    def test_cli_lexical_document_aliases_cannot_bypass_unresolved_event(self):
        canonical = str(self.document)
        aliases = [canonical.replace('/tasks.md', '//tasks.md'), canonical.replace('/tasks.md', '/./tasks.md'), '/' + canonical]
        def cli(document, *args):
            return subprocess.run([sys.executable, str(SCRIPT), '--work-root', str(self.root)] + list(args) + ['--document', document], capture_output=True, text=True)
        for alias in aliases:
            self.assertEqual(0, cli(alias, 'register', '--session', 'worker', '--thread', 'thread-a', '--tasks', 'T1').returncode)
            self.assertEqual(0, cli(alias, 'publish', '--change', 'C1', '--expected-revision', '5', '--tasks', 'T1', '--reason', 'same change').returncode)
        self.assertEqual(canonical, self.event()['document'])
        self.assertEqual(canonical, self.event()['targets']['worker']['registration']['document'])
        self.plan['plan_revision'] = 6
        del self.plan['tasks'][0]['hold']
        self.write_plan()
        for alias in aliases:
            result = cli(alias, 'check')
            self.assertEqual(1, result.returncode, result.stdout)
            self.assertIn('C1', json.loads(result.stdout)['unresolved'])
            run = cli(alias, 'run', '--socket', str(self.project / 'missing'), '--once')
            self.assertEqual(0, run.returncode, run.stdout)
            self.assertIn('source drift', self.event()['targets']['worker']['reason'])
        self.ack('held')
        self.ack('applied')
        for alias in aliases:
            result = cli(alias, 'resolve', '--change', 'C1', '--expected-revision', '6', '--evidence', 'current acceptance and applied ACK')
            self.assertEqual(0, result.returncode, result.stdout)
            self.assertEqual(0, cli(alias, 'check').returncode)

    def test_stale_persisted_lexical_identity_fails_without_rewrite(self):
        self.register()
        self.publish()
        self.ack('held')
        self.ack('applied')
        self.plan['plan_revision'] = 6
        del self.plan['tasks'][0]['hold']
        self.write_plan()
        original = json.loads(self.store.path.read_text())
        for location in ('event', 'session', 'capture'):
            state = copy.deepcopy(original)
            alias = str(self.document).replace('/tasks.md', '//tasks.md')
            if location == 'event':
                state['events']['C1']['document'] = alias
            elif location == 'session':
                state['sessions']['worker']['document'] = alias
            else:
                state['events']['C1']['targets']['worker']['registration']['document'] = alias
            self.store.path.write_text(json.dumps(state))
            before = self.store.path.read_bytes()
            proc = subprocess.run([sys.executable, str(SCRIPT), '--work-root', str(self.root), 'check', '--document', str(self.document)], capture_output=True, text=True)
            self.assertEqual(2, proc.returncode, proc.stdout)
            self.assertIn('noncanonical persisted document', proc.stdout)
            self.assertEqual(before, self.store.path.read_bytes())

    def test_existing_hardlink_alias_shares_unresolved_gate(self):
        self.register()
        self.publish()
        self.ack('held')
        self.ack('applied')
        self.plan['plan_revision'] = 6
        del self.plan['tasks'][0]['hold']
        self.write_plan()
        alias = self.project / 'hardlink.md'
        os.link(self.document, alias)
        result = control.acceptance_check(self.store, str(alias))
        self.assertFalse(result['complete'])
        self.assertIn('C1', result['unresolved'])
        control.resolve(self.store, argparse.Namespace(document=str(alias), change='C1', expected_revision=6, evidence='same existing file'))
        self.assertTrue(control.acceptance_check(self.store, str(self.document))['complete'])

    def test_document_symlink_and_parent_traversal_remain_rejected(self):
        alias = self.project / 'symlink.md'
        alias.symlink_to(self.document)
        for path in (str(alias), str(self.project / 'x' / '..' / 'tasks.md')):
            with self.assertRaises(control.ControlError):
                control.acceptance_check(self.store, path)

    def test_two_documents_remain_independent_and_cross_supersede_rejected(self):
        self.register()
        self.publish()
        other_document = self.project / 'other.md'
        other_plan = copy.deepcopy(self.plan)
        other_plan['tasks'][0]['owner'] = 'worker-b'
        other_document.write_text('<!-- GSP-DAG:START -->\n```json\n' + json.dumps(other_plan) + '\n```\n<!-- GSP-DAG:END -->\n')
        (self.root / 'sessions' / 'worker-b').mkdir()
        (self.root / 'sessions' / 'worker-b' / 'work.md').write_text('other session')
        control.register(self.store, argparse.Namespace(document=str(other_document), session='worker-b', thread='thread-b', tasks=['T1'], cwd=None))
        control.publish(self.store, argparse.Namespace(document=str(other_document), change='CB', expected_revision=5, tasks=['T1'], reason='other change'))
        untouched = self.event('CB')
        with self.assertRaisesRegex(control.ControlError, 'same document'):
            control.supersede(self.store, self.args(change='C1', by='CB', evidence='must reject'))
        self.ack('held')
        self.ack('applied')
        self.plan['plan_revision'] = 6
        del self.plan['tasks'][0]['hold']
        self.write_plan()
        control.resolve(self.store, self.args(change='C1', expected_revision=6, evidence='current A complete'))
        self.assertTrue(control.acceptance_check(self.store, str(self.document))['complete'])
        self.assertFalse(control.acceptance_check(self.store, str(other_document))['complete'])
        control.run_once(self.store, self.args(socket=str(self.project / 'missing'), timeout=.1, max_attempts=2))
        self.assertEqual(untouched, self.event('CB'))

    def test_per_task_basis_key_scope_drift_requires_supersede(self):
        self.register()
        self.publish()
        self.ack('held')
        self.ack('applied')
        self.plan['contracts']['R2'] = 1
        self.plan['tasks'][0]['basis']['R2'] = 1
        del self.plan['tasks'][0]['hold']
        self.plan['plan_revision'] = 6
        self.write_plan()
        with self.assertRaisesRegex(control.ControlError, 'basis keys changed'):
            control.resolve(self.store, self.args(change='C1', expected_revision=6, evidence='new scope not reviewed'))
        self.plan['tasks'][0]['hold'] = 'new scope'
        self.write_plan()
        self.publish('C2')
        control.supersede(self.store, self.args(change='C1', by='C2', evidence='new basis scope reviewed'))
        self.assertEqual({'T1': ['R1', 'R2']}, self.event('C2')['basis_keys'])

    def test_additive_registration_keeps_captured_event_identity(self):
        self.register()
        self.publish()
        second = copy.deepcopy(self.plan['tasks'][0])
        second.update(id='T2', writes=['b'])
        self.plan['tasks'].append(second)
        self.write_plan()
        expanded = control.register(self.store, self.args(session='worker', thread='thread-a', tasks=['T1', 'T2'], cwd=None))
        self.assertEqual(['T1', 'T2'], expanded['tasks'])
        self.assertEqual(['T1'], self.event()['targets']['worker']['registration']['tasks'])
        with self.assertRaises(control.ControlError):
            self.register()
        control.publish(self.store, self.args(change='C2', expected_revision=5, tasks=['T1', 'T2'], reason='added work'))
        control.supersede(self.store, self.args(change='C1', by='C2', evidence='scope expanded'))
        self.assertEqual(['T1', 'T2'], self.event('C2')['targets']['worker']['registration']['tasks'])

    def test_finite_time_bounds_and_single_watcher(self):
        args = ['--work-root', str(self.root), 'run', '--socket', str(self.project / 'none'), '--document', str(self.document), '--once']
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(2, control.main(args + ['--timeout', 'inf']))
        fd = self.store.open_lock('watcher.lock')
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            proc = subprocess.run([sys.executable, str(SCRIPT)] + args, capture_output=True, text=True)
            self.assertEqual(2, proc.returncode)
            self.assertIn('another project watcher', proc.stdout)
        finally:
            os.close(fd)

    def test_publish_rejects_wrong_revision_duplicate_unknown_and_current_tasks(self):
        for ids, revision in [(['T1'], 6), (['T1', 'T1'], 5), (['UNKNOWN'], 5)]:
            with self.assertRaises(control.ControlError):
                control.publish(self.store, self.args(change='C1', expected_revision=revision, tasks=ids, reason='change'))
        del self.plan['tasks'][0]['hold']
        self.write_plan()
        with self.assertRaises(control.ControlError):
            self.publish()

    def test_explicit_worktree_and_missing_session_record(self):
        other = self.project / 'worktree'
        other.mkdir()
        reg = control.register(self.store, self.args(session='worker', thread='thread-a', tasks=['T1'], cwd=str(other)))
        self.assertEqual(str(other), reg['cwd'])
        (self.root / 'sessions' / 'worker' / 'work.md').unlink()
        with self.assertRaises(OSError):
            self.register()

    def test_state_malformed_and_ack_history_failure_preserve_original(self):
        self.register()
        self.publish()
        state = json.loads(self.store.path.read_text())
        state['events']['C1']['targets']['worker']['ack'] = 'applied'
        self.store.path.write_text(json.dumps(state))
        original = self.store.path.read_bytes()
        with self.assertRaises(control.ControlError):
            with self.store.transaction():
                pass
        self.assertEqual(original, self.store.path.read_bytes())

    def test_real_cli_register_publish_ack_and_check_exit(self):
        def cli(*args):
            return subprocess.run([sys.executable, str(SCRIPT), '--work-root', str(self.root)] + list(args), capture_output=True, text=True)
        self.assertEqual(0, cli('register', '--session', 'worker', '--thread', 'thread-a', '--tasks', 'T1', '--document', str(self.document)).returncode)
        self.assertEqual(0, cli('publish', '--change', 'C1', '--expected-revision', '5', '--tasks', 'T1', '--reason', 'change', '--document', str(self.document)).returncode)
        self.assertEqual(1, cli('check', '--document', str(self.document)).returncode)
        self.assertEqual(2, cli('ack', '--session', 'worker', '--change', 'C1', '--revision', '6', '--state', 'held', '--evidence', 'wrong').returncode)
        self.assertIn('unresolved', json.loads(cli('check', '--document', str(self.document)).stdout))


if __name__ == '__main__':
    unittest.main()
