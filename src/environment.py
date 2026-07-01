"""
시뮬레이션 환경 구성
====================
CybORG 드론 스웜 시나리오(CC3)를 생성하고 공식 PettingZoo 병렬 래퍼로 감싼다.

기본값은 순수 raw CybORG 이다 (적 = 내장 RedDroneWormAgent).
use_custom_attacker=True 일 때만 우리가 만든 공격 에이전트를 주입한다.
"""

from CybORG import CybORG
from CybORG.Simulator.Scenarios import DroneSwarmScenarioGenerator
from CybORG.Agents.Wrappers import PettingZooParallelWrapper


def build_environment(num_drones, max_steps, seed, use_custom_attacker=False):
    """드론 스웜 공방전 환경을 만들어 (raw_cyborg, wrapped_env) 로 반환한다.

    - raw_cyborg : 세밀한 관측/보상 조회용 (get_observation, get_rewards)
    - wrapped_env: 블루 에이전트들을 동시에 구동하는 공식 실행 인터페이스
    """
    kwargs = dict(num_drones=num_drones, maximum_steps=max_steps)

    if use_custom_attacker:
        # 우리 공격 에이전트를 적으로 주입 (옵션)
        from src.attack_agent import AdaptiveAttackAgent
        kwargs["default_red_agent"] = AdaptiveAttackAgent
    # else: CybORG 내장 RedDroneWormAgent 가 기본 적으로 동작

    scenario = DroneSwarmScenarioGenerator(**kwargs)
    cyborg = CybORG(scenario_generator=scenario, environment="sim", seed=seed)
    wrapped = PettingZooParallelWrapper(env=cyborg)
    return cyborg, wrapped
