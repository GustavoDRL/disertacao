"""Sondas da revisão: sem ROS, hardware, treino ou alteração dos runs.

Execute com f1tenth_code/research/.venv/bin/python revisao-2026-09-10/reproduzir.py.
As asserções confirmam os defeitos observados, não o comportamento desejado.
"""
import ast
import json
import math
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
from types import SimpleNamespace as NS

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
CODE = ROOT / 'f1tenth_code'
sys.path[:0] = [str(CODE / 'research'), str(CODE / 'src/data_collector'),
               str(CODE / 'car/src/sim2real_bridge')]

from f1tenth_research.gate import evaluate_gate
from f1tenth_research.rollout import rollout_episode
from sim2real_bridge.guarda import Guarda, Limites
from sim2real_bridge.adaptador import adaptar, PerfilLidar

report = dict(laps_completed=100, laps_attempted=100, collisions=0,
              lap_times_by_seed=[[50.0]] * 10)
for stage in ['e2_il', 'e3_rl']:
    g = evaluate_gate(stage, report, t_pp=59.0)
    assert g.verdict == 'PASS' and len(g.criteria) == 2
    print('GATE_SEM_MEDICOES', stage, g.verdict, [c.id for c in g.criteria])

class FinishCollision:
    track = NS(length=10.0)
    max_episode_steps = 1
    _step_count = 1
    def reset(self, **kw):
        return None, {}
    def step(self, action):
        return None, 0, True, False, dict(progress_m=10.1, sim_time=1.0,
                                         collision=True, mu=1.0)

laps = rollout_episode(FinishCollision(), lambda *_: None, 0, 1)
assert len(laps) == 1 and laps[0].completed and not laps[0].collision
print('COLISAO_NA_CHEGADA', laps)

g = Guarda(Limites(max_speed_mps=-1.0, exigir_deadman=False), 0.0)
g.comando(0.0, 2.0, 0.0)
d = g.decidir(0.1)
assert d.speed == -1.0 and d.motivo == 'ok'
print('LIMITE_NEGATIVO', d)

scan = adaptar([1.0], 0.0, 0.01, PerfilLidar())
assert scan is not None and np.all(scan == 12.0)
print('SCAN_UM_FEIXE', 'aceito', len(scan), 'feixes; todos a', float(scan[0]), 'm')

import data_collector.failure_detector as fd
fd.time = NS(time=lambda: 1000.0)
detector = fd.FailureDetector()
events = []
for i in range(101):
    fd.time = NS(time=lambda i=i: 1000.0 + i / 10)
    events.extend(detector.update(
        dict(speed_magnitude=0.4, position=dict(x=i * 0.04, y=0.0)),
        dict(closest_point=dict(distance_m=10.0)),
        dict(speed=0.4, steering_angle=0.0, age_s=0.0)))
assert any(e['type'] == 'stuck' for e in events)
print('STUCK_EM_MOVIMENTO', [e for e in events if e['type'] == 'stuck'])

# Reusa somente os dublês dos testes existentes para executar o nó real.
runpy.run_path(str(CODE / 'tests/conftest.py'))
helpers = runpy.run_path(str(CODE / 'tests/test_policy_node_params.py'))
with tempfile.TemporaryDirectory() as tmp:
    onnx = Path(tmp) / 'fake.onnx'
    onnx.touch()
    node = helpers['_no'](str(onnx))
    node.session.run = lambda *_: [np.array([[0.1, 6.0]], dtype=np.float32)]
    node._scan_cb(NS(ranges=[5.0] * 1080))
    node._control_step()
    assert node.publicados[-1].drive.speed == 6.0
    print('POLITICA_SEM_ODOM', vars(node.publicados[-1].drive))
    print('ESTADO_ANTES_GUARDA', node._estado.speed_ambiente,
          '(permanece 6 mesmo se guarda limitar /drive a 1 ou zero)')

    node.session.run = lambda *_: [np.array([[np.nan, np.nan]], dtype=np.float32)]
    node._control_step()
    assert math.isnan(node.publicados[-1].drive.speed)
    print('POLITICA_SAIDA_NAN', vars(node.publicados[-1].drive))
    try:
        node._scan_cb(NS(ranges=[]))
    except IndexError as exc:
        print('POLITICA_SCAN_VAZIO', type(exc).__name__, str(exc))
    else:
        raise AssertionError('Esperado IndexError do scan vazio')

    # Executa o julgador Python original do script, com snapshots de apenas
    # 20 s válidos, embora a espera externa possa ter durado 60 s.
    source = (CODE / 'car/scripts/test/medir_gate_s2r.sh').read_text()
    judge = source.split("<<'PY'\n", 1)[1].rsplit('\nPY', 1)[0]
    health = Path(tmp) / 'policy_health.json'
    health.write_text(json.dumps(dict(control_hz_measured=20.0,
                                      latency_ms=dict(p99=0.3), timestamp=1020)))
    proc = subprocess.run([sys.executable, '-', str(health), '10', '19', '20', '80',
                           '200', '10', '600', '30'], input=judge,
                          text=True, capture_output=True)
    assert proc.returncode == 0
    print('GATE_60S_COM_APENAS_20S', proc.stdout.strip())

# E3: os checkpoints reais são lidos somente para inventário, sem inferência.
best = CODE / 'research/runs/best/checkpoints'
assert (best / 'sac.zip').is_file() and not (best / 'best.pt').exists()
print('REAVALIACAO_E3', sorted(p.name for p in best.iterdir()),
      'reevaluate() exige best.pt, inexistente')

# Execute apenas métodos do gap follower, sem importar/inicializar ROS.
source = CODE / 'src/gap_follow/gap_follow/gap_follow.py'
tree = ast.parse(source.read_text())
cls = next(n for n in tree.body if isinstance(n, ast.ClassDef)
           and n.name == 'ThreadedGapFollower')
methods = [n for n in cls.body if isinstance(n, ast.FunctionDef)
           and n.name in ('_on_control_timer',)]
namespace = {}
exec(compile(ast.Module(body=methods, type_ignores=[]), str(source), 'exec'), namespace)
commands = []
fake = NS(latest_scan_data=NS(is_valid=True, target_angle=0.0, timestamp=-10000),
          _compute_steering_command=lambda _: 0.0,
          _compute_speed_command=lambda _: 0.5,
          _publish_control_command=lambda steer, speed: commands.append((steer, speed)),
          get_logger=lambda: NS(error=print))
namespace['_on_control_timer'](fake)
assert commands == [(0.0, 0.5)]
print('GAP_SCAN_ANTIGO', commands)
print('SONDAS_CONCLUIDAS')
