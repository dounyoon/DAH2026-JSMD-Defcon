"""
시뮬레이션 환경 구성
====================
CybORG 드론 스웜 시나리오(CC3)를 생성하고 공식 PettingZoo 병렬 래퍼로 감싼다.
실행 모드에 따라 적(Red) 공격 에이전트를 다르게 주입한다.

  - "sample"   : 주입 안 함 → CybORG 내장 웜(RedDroneWormAgent)이 공격.
  - "baseline" : BaselineAttackAgent (개선 전 탐색·장악 위주).
  - "current"  : AdaptiveAttackAgent (가용성 공격 집중, IEEE 논문 적용).
"""

from CybORG import CybORG
from CybORG.Simulator.Scenarios import DroneSwarmScenarioGenerator
from CybORG.Agents.Wrappers import PettingZooParallelWrapper


def build_environment(num_drones, max_steps, seed, mode="current"):
    """(raw_cyborg, wrapped_env) 를 반환한다."""
    kwargs = dict(num_drones=num_drones, maximum_steps=max_steps)

    if mode == "baseline":
        from src.attack_agent_baseline import BaselineAttackAgent
        kwargs["default_red_agent"] = BaselineAttackAgent
    elif mode == "current":
        from src.attack_agent import AdaptiveAttackAgent
        kwargs["default_red_agent"] = AdaptiveAttackAgent
    # mode == "sample": default_red_agent 를 주입하지 않아 CybORG 내장 웜이 동작

    scenario = DroneSwarmScenarioGenerator(**kwargs)
    cyborg = CybORG(scenario_generator=scenario, environment="sim", seed=seed)
    wrapped = PettingZooParallelWrapper(env=cyborg)
    return cyborg, wrapped
