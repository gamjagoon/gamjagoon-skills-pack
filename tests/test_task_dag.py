#!/usr/bin/env python3
"""DAG contract checks; scheduling comparisons below use synthetic durations only."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / '.agents/skills/gsp-tasks/scripts/task_dag.py'
spec = importlib.util.spec_from_file_location('task_dag', SCRIPT)
dag = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dag)


def task(tid, deps=(), **kwargs):
    result = dict(id=tid, title=tid, deps=list(deps), status='pending', owner=tid,
                  reads=[], writes=[], resources=[])
    result.update(kwargs)
    return result


def graph(*tasks, capacity=2):
    return dict(version=1, max_parallel=capacity, tasks=list(tasks))


def document(data):
    return '# Tasks\n\n<!-- GSP-DAG:START -->\n```json\n' + json.dumps(data) + '\n```\n<!-- GSP-DAG:END -->\n'


class ParserTests(unittest.TestCase):
    def test_markers_fences_and_json(self):
        valid = document(graph(task('A')))
        self.assertEqual(dag.parse_document(valid)['version'], 1)
        prose = 'Use `<!-- GSP-DAG:START -->` and `<!-- GSP-DAG:END -->` markers.\n'
        self.assertEqual(dag.parse_document(prose + valid)['version'], 1)
        bad = ['', valid + valid, valid.replace('START', 'END'),
               valid.replace('<!-- GSP-DAG:START -->', 'prefix <!-- GSP-DAG:START -->'),
               valid.replace('```json', '```yaml'), valid.replace('```json', 'extra\n```json'),
               valid.replace('```\n<!--', '```\nextra\n<!--'),
               valid.replace('"version": 1', '"version": 1, "version": 1'),
               valid.replace('"version": 1', '"version": NaN'),
               valid.replace('"version": 1', '"version": Infinity'),
               valid.replace('"version": 1', '"version": -Infinity'),
               valid.replace('"version": 1', '"version": ')]
        for value in bad:
            with self.subTest(value=value[:100]), self.assertRaises(dag.DAGError):
                dag.parse_document(value)

    def test_nested_duplicate_keys(self):
        text = document(graph(task('A'))).replace('"title": "A"', '"title": "A", "title": "B"')
        with self.assertRaises(dag.DAGError):
            dag.parse_document(text)


class ValidationTests(unittest.TestCase):
    def rejects(self, data):
        with self.assertRaises(dag.DAGError):
            dag.validate(data)

    def test_root_fields_and_types(self):
        for data in [None, [], {}, graph(), graph(task('A'), capacity=True), graph(task('A'), capacity=0)]:
            self.rejects(data)
        for key, value in [('version', True), ('version', 2), ('tasks', {}), ('extra', 1)]:
            data = graph(task('A'))
            data[key] = value
            self.rejects(data)
        for key in ('version', 'max_parallel', 'tasks'):
            data = graph(task('A'))
            del data[key]
            self.rejects(data)

    def test_task_fields_types(self):
        bad = [('id', []), ('id', 'A"x'), ('id', '1A'), ('title', ' '), ('status', []),
               ('status', 'unknown'), ('owner', {}), ('owner', ''), ('deps', 'A'),
               ('reads', [1]), ('writes', [{}]), ('resources', ['x', 'x']), ('deps', ['B', 'B'])]
        for key, value in bad:
            with self.subTest(key=key, value=value):
                self.rejects(graph(task('A', **{key: value})))
        self.rejects(graph(None))
        self.rejects(graph(task('A'), task('A')))
        for key in task('A'):
            t = task('A')
            del t[key]
            self.rejects(graph(t))
        self.rejects(graph(task('A', extra=True)))
        for key in ('evidence', 'reason', 'estimate_basis'):
            self.rejects(graph(task('A', **{key: ' '})))

    def test_estimates(self):
        for value in [True, 0, -1, float('nan'), float('inf'), '3', None, [], 10**400]:
            self.rejects(graph(task('A', estimate_minutes=value, estimate_basis='measured')))
        self.rejects(graph(task('A', estimate_minutes=1)))
        self.rejects(graph(task('A', estimate_basis='measured')))
        dag.validate(graph(task('A', estimate_minutes=0.5, estimate_basis='sample')))

    def test_paths(self):
        for path in ['/root', '..', 'a/../b', 'a//b', 'a/', './a', 'a/./b', 'a\\b', '*.py', 'a?', 'a[x]']:
            with self.subTest(path=path):
                self.rejects(graph(task('A', reads=[path])))
        self.rejects(graph(task('A', reads=['a', 'a'])))
        dag.validate(graph(task('A', reads=['.', '.agents/a', 'src/a-b.py'], writes=['.'])))

    def test_dependencies_and_cycle(self):
        self.rejects(graph(task('A', ['B'])))
        self.rejects(graph(task('A', ['A'])))
        self.rejects(graph(task('A', ['B']), task('B', ['A'])))
        data = graph(task('Z'), task('B', ['Z']), task('A'))
        self.assertEqual(dag.validate(data)['topological_order'], ['A', 'Z', 'B'])
        self.assertEqual(dag.validate(data)['edges'], [['Z', 'B']])

    def test_states_capacity(self):
        for status in ('running', 'done'):
            self.rejects(graph(task('A'), task('B', ['A'], status=status, evidence='check')))
        self.rejects(graph(task('A', status='done')))
        self.rejects(graph(task('A', status='blocked')))
        self.rejects(graph(task('A', status='running', owner=None)))
        self.rejects(graph(task('A', status='running'), task('B', status='running'), capacity=1))
        dag.validate(graph(task('A', status='done', evidence='run'), task('B', ['A'], status='running')))

    def test_running_conflicts_and_read_read(self):
        cases = [dict(owner='same'), dict(resources=['gpu:0']), dict(writes=['src']), dict(reads=['src/a.py'])]
        for changes in cases:
            first = task('A', status='running', owner='same', resources=['gpu:0'], writes=['src'])
            self.rejects(graph(first, task('B', status='running', **changes)))
        dag.validate(graph(task('A', status='running', reads=['src']),
                           task('B', status='running', reads=['src/a.py'])))
        dag.validate(graph(task('A', status='running', writes=['src/a']),
                           task('B', status='running', writes=['src/ab'])))
        self.rejects(graph(task('A', status='running', writes=['.']), task('B', status='running', reads=['x'])))

    def test_long_iterative_chain(self):
        data = graph(*(task('T%d' % i, ['T%d' % (i-1)] if i else []) for i in range(2500)))
        result = dag.route(data)
        self.assertEqual(len(result['topological_order']), 2500)
        self.assertEqual(result['priorities']['T0'], 2500)
        self.assertEqual(result['dispatch'][0]['task'], 'T0')


class RoutingTests(unittest.TestCase):
    def test_weighted_priority_partial_estimates_and_ties(self):
        data = graph(task('A', estimate_minutes=1, estimate_basis='synthetic'),
                     task('B', estimate_minutes=5, estimate_basis='synthetic'),
                     task('C', ['B'], estimate_minutes=5, estimate_basis='synthetic'), capacity=1)
        result = dag.route(data)
        self.assertEqual(result['priority_basis'], 'estimated_minutes')
        self.assertEqual(result['dispatch'][0], dict(task='B', owner='B', score=10))
        del data['tasks'][2]['estimate_minutes']
        del data['tasks'][2]['estimate_basis']
        result = dag.route(data)
        self.assertEqual(result['priority_basis'], 'dependency_steps')
        self.assertEqual(result['priorities'], {'A': 1, 'B': 2, 'C': 1})
        self.assertEqual(dag.route(graph(task('Z'), task('A'), capacity=1))['ready'], ['A', 'Z'])
        shuffled = copy.deepcopy(data)
        shuffled['tasks'].reverse()
        self.assertEqual(dag.route(data), dag.route(shuffled))
        overflow = graph(task('A', estimate_minutes=1e308, estimate_basis='synthetic'),
                         task('B', ['A'], estimate_minutes=1e308, estimate_basis='synthetic'))
        with self.assertRaises(dag.DAGError):
            dag.route(overflow)

    def test_reservations_waiting_and_no_mutation(self):
        data = graph(task('R', status='running', writes=['src'], resources=['gpu']),
                     task('A', reads=['src/a']), task('B', resources=['gpu']),
                     task('C', owner='R'), task('D', owner=None), task('E'), task('F'),
                     task('G', ['E']), task('H', status='blocked', reason='decision'), capacity=2)
        original = copy.deepcopy(data)
        result = dag.route(data)
        self.assertEqual(data, original)
        self.assertEqual(result['running'], ['R'])
        self.assertEqual([x['task'] for x in result['dispatch']], ['E'])
        for tid, token in [('A', 'path:'), ('B', 'resource:'), ('C', 'owner:'),
                           ('D', 'owner not assigned'), ('F', 'capacity'), ('G', 'dependencies'), ('H', 'decision')]:
            self.assertIn(token, ' '.join(result['waiting'][tid]))

    def test_selected_conflicts_read_read_and_completion_dispatch(self):
        result = dag.route(graph(task('A', writes=['src']), task('B', reads=['src/a']), task('C')))
        self.assertEqual([x['task'] for x in result['dispatch']], ['A', 'C'])
        result = dag.route(graph(task('A', reads=['src']), task('B', reads=['src/a'])))
        self.assertEqual(len(result['dispatch']), 2)
        data = graph(task('A', status='done', evidence='actual observation'),
                     task('B', status='running'), task('C', ['A']))
        self.assertEqual([x['task'] for x in dag.route(data)['dispatch']], ['C'])
        result = dag.route(graph(task('A', status='done', evidence='check')))
        self.assertEqual(result['dispatch'], [])
        self.assertEqual(result['waiting'], {})

    def test_synthetic_duration_simulation(self):
        # Synthetic finite durations only: no measured project runtime or speed claim.
        data = graph(task('A'), task('B'), task('Z'), task('Y', ['Z']), capacity=2)
        durations = {'A': 2, 'B': 2, 'Z': 3, 'Y': 3}
        for t in data['tasks']:
            t.update(estimate_minutes=durations[t['id']], estimate_basis='synthetic fixture')

        def simulate(critical):
            current = copy.deepcopy(data)
            by_id = {t['id']: t for t in current['tasks']}
            active, now, events = {}, 0, []
            while any(t['status'] != 'done' for t in by_id.values()):
                result = dag.route(current)
                selected = [x['task'] for x in result['dispatch']]
                if not critical:
                    selected = sorted(result['ready'])[:2-len(active)]
                for tid in selected:
                    by_id[tid]['status'] = 'running'
                    active[tid] = now + durations[tid]
                    events.append((now, tid))
                self.assertTrue(active)
                now = min(active.values())
                for tid in list(active):
                    if active[tid] == now:
                        by_id[tid].update(status='done', evidence='synthetic completed')
                        del active[tid]
            return now, events
        critical, events = simulate(True)
        baseline, _ = simulate(False)
        self.assertEqual(critical, 6)
        self.assertEqual(baseline, 8)
        self.assertIn((3, 'Y'), events)  # follows Z immediately while B remains running

    def test_safe_render(self):
        text = dag.render(graph(task('A.-_1', title='"</script>'), task('B', ['A.-_1'])))
        self.assertIn('n0["A.-_1 (pending)"]', text)
        self.assertIn('n0 --> n1', text)
        self.assertNotIn('</script>', text)
        self.assertTrue(text.startswith('```mermaid\n'))


class CLITests(unittest.TestCase):
    def test_actual_cli_and_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'tasks.md'
            path.write_text(document(graph(task('A'))), encoding='utf-8')
            before = path.read_bytes(), path.stat().st_mtime_ns
            for command in ('validate', 'route', 'render'):
                run = subprocess.run([sys.executable, '-B', str(SCRIPT), command, str(path)],
                                     capture_output=True, text=True)
                self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
                self.assertEqual(run.stderr, '')
                if command != 'render':
                    self.assertTrue(json.loads(run.stdout)['valid'])
            self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), before)
            self.assertEqual([p.name for p in Path(directory).iterdir()], ['tasks.md'])
            for contents in [document(graph(task('A', status=[]))), 'invalid',
                             document(graph(task('A', estimate_minutes=1e309, estimate_basis='x')))]:
                path.write_text(contents, encoding='utf-8')
                run = subprocess.run([sys.executable, '-B', str(SCRIPT), 'route', str(path)], capture_output=True, text=True)
                self.assertEqual(run.returncode, 2)
                output = json.loads(run.stdout)
                self.assertEqual(output['valid'], False)
                self.assertNotIn('dispatch', output)
                self.assertEqual(run.stderr, '')
            path.write_bytes(b'\xff')
            for args in [('validate', str(path)), ('validate', str(path) + '.absent')]:
                run = subprocess.run([sys.executable, '-B', str(SCRIPT), *args], capture_output=True, text=True)
                self.assertEqual(run.returncode, 2)
                self.assertFalse(json.loads(run.stdout)['valid'])
            usage = subprocess.run([sys.executable, '-B', str(SCRIPT), 'unknown'], capture_output=True, text=True)
            self.assertEqual(usage.returncode, 2)
            self.assertIn('usage:', usage.stderr)


def graph_v2(*tasks, contracts=None, acceptance=None, capacity=2):
    result = graph(*tasks, capacity=capacity)
    result.update(version=2, plan_revision=1, contracts={'R1': 2} if contracts is None else contracts,
                  acceptance=[{'id': 'AC1', 'contracts': {'R1': 2}, 'tasks': [tasks[-1]['id']]}]
                  if acceptance is None else acceptance)
    for item in result['tasks']:
        item.setdefault('basis', {'R1': 2})
    return result


class RevisionTests(unittest.TestCase):
    def rejects(self, data):
        with self.assertRaises(dag.DAGError):
            dag.validate(data)

    def test_v1_exact_output_and_completion_scope(self):
        data = graph(task('A', status='done', evidence='observed'), task('B', ['A']))
        expected = {'valid': True, 'topological_order': ['A', 'B'],
                    'edges': [['A', 'B']], 'warnings': []}
        self.assertEqual(dag.validate(data), expected)
        expected.update(priority_basis='dependency_steps', priorities={'A': 0, 'B': 1},
                        running=[], ready=['B'], dispatch=[{'task': 'B', 'owner': 'B', 'score': 1}], waiting={})
        self.assertEqual(dag.route(data), expected)
        result = dag.check(data)
        self.assertFalse(result['revision_validation'])
        self.assertFalse(result['complete'])
        data['tasks'][1].update(status='done', evidence='observed')
        self.assertTrue(dag.check(data)['execution_complete'])
        self.assertTrue(dag.check(data)['complete'])
        self.assertIn('not validated', dag.check(data)['warnings'][0])

    def test_stale_history_consumers_unrelated_route_and_no_mutation(self):
        data = graph_v2(task('OLD', status='done', basis={'R1': 1}, evidence='old real execution'),
                        task('CONSUMER', ['OLD']), task('CHILD', ['CONSUMER']),
                        task('INDEPENDENT', basis={}))  # Administrative task, no contract-dependent output.
        before = copy.deepcopy(data)
        result = dag.route(data)
        self.assertEqual([x['task'] for x in result['dispatch']], ['INDEPENDENT'])
        self.assertIn('stale basis', ' '.join(result['waiting']['CONSUMER']))
        self.assertIn('OLD:', ' '.join(result['waiting']['CHILD']))
        self.assertFalse(dag.check(data)['complete'])
        self.assertEqual(data, before)
        self.assertEqual(data['tasks'][0]['status'], 'done')
        self.assertEqual(data['tasks'][0]['evidence'], 'old real execution')

    def test_revalidation_boundary_and_current_acceptance(self):
        data = graph_v2(task('OLD', status='done', basis={'R1': 1}, evidence='old execution'),
                        task('NEW', ['OLD'], revalidates=['OLD']))
        self.assertEqual(dag.route(data)['ready'], ['NEW'])
        self.assertFalse(dag.check(data)['complete'])
        data['tasks'][1].update(status='done', evidence='actual current recheck')
        self.assertTrue(dag.check(data)['complete'])
        self.assertTrue(dag.validate(data)['task_validity']['OLD'])
        self.assertEqual(dag.validate(data)['task_validity']['NEW'], [])
        # Revalidating a direct predecessor does not waive the worker's own stale basis.
        data['tasks'][1]['basis']['R1'] = 1
        self.assertFalse(dag.check(data)['complete'])

    def test_revalidation_never_bypasses_hold_or_other_dependency(self):
        data = graph_v2(task('OLD', status='done', basis={'R1': 1}, evidence='old execution', hold='ACK pending'),
                        task('NEW', ['OLD'], revalidates=['OLD']))
        self.assertEqual(dag.route(data)['dispatch'], [])
        self.assertIn('hold:', ' '.join(dag.route(data)['waiting']['NEW']))
        del data['tasks'][0]['hold']
        data['tasks'].insert(1, task('OTHER', status='done', evidence='old other', basis={'R1': 1}))
        data['tasks'][-1]['deps'].append('OTHER')
        self.assertEqual(dag.route(data)['dispatch'], [])
        data['tasks'][-1]['revalidates'].append('OTHER')
        self.assertEqual(dag.route(data)['ready'], ['NEW'])
        data['tasks'][-1]['hold'] = 'own transition'
        self.assertEqual(dag.route(data)['dispatch'], [])

    def test_revalidation_accepts_historical_chain_but_not_hold_or_own_stale(self):
        data = graph_v2(task('UPSTREAM', status='done', evidence='old', basis={'R1': 1}),
                        task('OLD', ['UPSTREAM'], status='done', evidence='old', basis={'R1': 1}),
                        task('NEW', ['OLD'], revalidates=['OLD']))
        before = copy.deepcopy(data)
        self.assertEqual(dag.route(data)['ready'], ['NEW'])
        self.assertEqual([item['task'] for item in dag.route(data)['dispatch']], ['NEW'])
        self.assertFalse(dag.check(data)['complete'])
        self.assertEqual(data, before)
        data['tasks'][-1].update(status='done', evidence='current integrated artifact revalidation')
        self.assertTrue(dag.check(data)['complete'])
        self.assertTrue(dag.validate(data)['task_validity']['UPSTREAM'])
        self.assertTrue(dag.validate(data)['task_validity']['OLD'])
        data['tasks'][0]['hold'] = 'ancestor semantic review pending'
        self.assertFalse(dag.check(data)['complete'])
        self.assertIn('UPSTREAM: hold:', ' '.join(dag.validate(data)['task_validity']['NEW']))
        del data['tasks'][0]['hold']
        data['tasks'][-1].update(status='pending', basis={'R1': 1})
        self.assertEqual(dag.route(data)['dispatch'], [])
        self.assertIn('stale basis', ' '.join(dag.route(data)['waiting']['NEW']))

    def test_revalidation_filters_each_edge_before_merging_diamond(self):
        data = graph_v2(task('ANCESTOR', status='done', evidence='old', basis={'R1': 1}),
                        task('RECHECKED', ['ANCESTOR'], status='done', evidence='old', basis={'R1': 1}),
                        task('OTHER', ['ANCESTOR'], status='done', evidence='old', basis={'R1': 2}),
                        task('NEW', ['RECHECKED', 'OTHER'], revalidates=['RECHECKED']))
        # The shared ancestor is waived through RECHECKED, but must survive through OTHER.
        self.assertEqual(dag.route(data)['dispatch'], [])
        self.assertIn('ANCESTOR: stale basis', ' '.join(dag.route(data)['waiting']['NEW']))
        data['tasks'][-1]['deps'].reverse()
        self.assertEqual(dag.route(data)['dispatch'], [])
        data['tasks'][-1]['revalidates'].append('OTHER')
        self.assertEqual(dag.route(data)['ready'], ['NEW'])
        data['tasks'][0]['hold'] = 'ancestor hold cannot be waived'
        self.assertEqual(dag.route(data)['dispatch'], [])
        self.assertIn('hold:', ' '.join(dag.route(data)['waiting']['NEW']))

    def test_running_pause_keeps_capacity_scope_and_owner_reservations(self):
        data = graph_v2(task('R', status='running', basis={'R1': 1}, writes=['src'], resources=['gpu']),
                        task('SCOPE', reads=['src/a']), task('RESOURCE', resources=['gpu']),
                        task('OWNER', owner='R'), task('FREE'), capacity=2)
        result = dag.route(data)
        self.assertEqual(result['running'], ['R'])
        self.assertIn('R', result['pause_required'])
        self.assertEqual([x['task'] for x in result['dispatch']], ['FREE'])
        for tid, reason in [('SCOPE', 'path:'), ('RESOURCE', 'resource:'), ('OWNER', 'owner:')]:
            self.assertIn(reason, ' '.join(result['waiting'][tid]))
        data['max_parallel'] = 1
        self.assertEqual(dag.route(data)['dispatch'], [])
        # Explicitly recorded safe hold: release the slot only once execution is blocked.
        data['tasks'][0].update(status='blocked', reason='worker confirmed safe pause')
        self.assertEqual(dag.route(data)['pause_required'], {})
        self.assertTrue(dag.route(data)['dispatch'])

    def test_running_consumer_pause_and_done_hold(self):
        data = graph_v2(task('OLD', status='done', evidence='observed', hold='meaning being revised'),
                        task('RUN', ['OLD'], status='running'))
        self.assertIn('RUN', dag.route(data)['pause_required'])
        data['tasks'][1].update(status='done', evidence='historical observation')
        self.assertFalse(dag.check(data)['complete'])
        del data['tasks'][0]['hold']
        self.assertTrue(dag.check(data)['complete'])

    def test_acceptance_current_coverage_and_unrelated_work(self):
        data = graph_v2(task('DONE', status='done', evidence='observed'), task('UNRELATED'),
                        acceptance=[{'id': 'AC1', 'contracts': {'R1': 2}, 'tasks': ['DONE']}])
        self.assertTrue(dag.check(data)['complete'])
        self.assertFalse(dag.check(data)['execution_complete'])
        data['tasks'][0]['basis'] = {}
        result = dag.check(data)
        self.assertFalse(result['complete'])
        self.assertIn('does not cover', ' '.join(result['acceptance'][0]['reasons']))
        data['tasks'][0]['basis'] = {'R1': 1}
        data['acceptance'][0]['contracts']['R1'] = 1
        self.assertTrue(dag.validate(data)['valid'])
        self.assertFalse(dag.check(data)['complete'])
        self.assertIn('stale acceptance', ' '.join(dag.check(data)['acceptance'][0]['reasons']))
        # Historical acceptance must not invalidate or gate unrelated dispatch.
        self.assertEqual(dag.route(data)['ready'], ['UNRELATED'])

    def test_v2_schema_errors(self):
        base = graph_v2(task('A'))
        bad_roots = [('plan_revision', True), ('plan_revision', 0), ('contracts', {}),
                     ('contracts', []), ('contracts', {'R1': True}), ('contracts', {'': 1}),
                     ('contracts', {'R1': 0}), ('acceptance', []), ('acceptance', {}), ('extra', 3)]
        for key, value in bad_roots:
            data = copy.deepcopy(base)
            data[key] = value
            with self.subTest(key=key, value=value):
                self.rejects(data)
        for key in ('plan_revision', 'contracts', 'acceptance'):
            data = copy.deepcopy(base)
            del data[key]
            self.rejects(data)
        for value in [[], None, {'R1': True}, {'R1': 0}, {'R1': 3}, {'UNKNOWN': 1}]:
            data = copy.deepcopy(base)
            data['tasks'][0]['basis'] = value
            self.rejects(data)
        data = copy.deepcopy(base)
        del data['tasks'][0]['basis']
        self.rejects(data)
        for key, value in [('hold', ''), ('hold', 1), ('revalidates', ['A']),
                           ('revalidates', ['MISSING']), ('revalidates', 'A'), ('extra', True)]:
            data = copy.deepcopy(base)
            data['tasks'][0][key] = value
            self.rejects(data)
        for key, value in [('id', ''), ('id', []), ('contracts', {}), ('contracts', {'R1': 3}),
                           ('contracts', {'UNKNOWN': 1}), ('contracts', {'R1': True}),
                           ('tasks', []), ('tasks', ['A', 'A']), ('tasks', ['NO']), ('extra', 1)]:
            data = copy.deepcopy(base)
            data['acceptance'][0][key] = value
            self.rejects(data)
        data = copy.deepcopy(base)
        data['acceptance'].append(copy.deepcopy(data['acceptance'][0]))
        self.rejects(data)
        self.rejects(graph_v2(task('A'), task('B', ['A'], revalidates=['A'])))
        self.rejects(graph_v2(task('A', status='done', evidence='x'),
                              task('B', ['A'], revalidates=['A', 'A'])))

    def test_v2_actual_cli_check_exit_codes_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'tasks.md'
            cases = [(graph_v2(task('A')), 1),
                     (graph_v2(task('A', status='done', evidence='actual')), 0)]
            historical = graph_v2(task('A', status='done', evidence='old', basis={'R1': 1}))
            historical['acceptance'][0]['contracts']['R1'] = 1
            cases.append((historical, 1))
            future = copy.deepcopy(historical)
            future['acceptance'][0]['contracts']['R1'] = 3
            cases.append((future, 2))
            for data, expected in cases:
                path.write_text(document(data), encoding='utf-8')
                before = path.read_bytes(), path.stat().st_mtime_ns
                run = subprocess.run([sys.executable, '-B', str(SCRIPT), 'check', str(path)],
                                     capture_output=True, text=True)
                self.assertEqual(run.returncode, expected, run.stdout + run.stderr)
                self.assertEqual(json.loads(run.stdout)['valid'], expected != 2)
                self.assertEqual(run.stderr, '')
                self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), before)
            self.assertEqual([p.name for p in Path(directory).iterdir()], ['tasks.md'])



if __name__ == '__main__':
    unittest.main()
