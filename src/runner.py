"""
에피소드 실행 오케스트레이터
============================
환경을 초기화하고, 매 스텝마다 모든 블루 방어 에이전트의 행동을 모아
동시에 적용한다. 정상 통신 실패(가용성 손실)를 누적하고, 종료 시 점수를 낸다.

기본 경로(USE_CUSTOM_AGENTS=False):
    공식 CybORG evaluation 패턴 그대로.
    공격 = 내장 RedDroneWormAgent, 방어 = 내장 RandomAgent (정수 액션).
커스텀 경로(True):
    우리가 만든 규칙 기반 공격/방어 에이전트 사용.
"""

from CybORG.Agents.SimpleAgents.RandomAgent import RandomAgent

from src.environment import build_environment
from src.scoring import compute_scores
from src.reporter import log


def _blue_agents(env):
    """래퍼 기준 현재 살아있는 블루 에이전트 (스텝 액션 대상용)."""
    return [a for a in env.agents if "blue" in a]


def _alive_blue(cyborg):
    """raw 환경 기준 생존 블루 에이전트 (집계용, 종료 후에도 정확)."""
    return [a for a in cyborg.active_agents if "blue" in a]


def run_episode(num_drones, max_steps, seed, points_per_drone, sla_threshold,
                verbose=True, log_every=25, use_custom_agents=False):
    """한 에피소드를 끝까지 실행하고 점수 딕셔너리를 반환한다."""
    cyborg, env = build_environment(
        num_drones, max_steps, seed, use_custom_attacker=use_custom_agents
    )
    observations = env.reset()
    action_spaces = env.action_spaces

    # 드론마다 방어 에이전트 1개씩 분산 배치
    if use_custom_agents:
        from src.defense_agent import ReactiveDefenseAgent
        defenders = {name: ReactiveDefenseAgent(name) for name in _blue_agents(env)}
    else:
        defenders = {name: RandomAgent() for name in _blue_agents(env)}

    comm_failures = 0.0        # 누적 정상통신 실패 (가용성 손실 지표)
    steps_run = 0
    drones_defended = len(_alive_blue(cyborg))

    for step in range(max_steps):
        # 스텝 진입 시점(종료 정리 이전)에 생존 수를 읽어 집계 신뢰성 확보
        drones_defended = len(_alive_blue(cyborg))
        current_blue = _blue_agents(env)
        if not current_blue:
            break  # 블루 전멸 = 방어 실패, 게임 오버

        # 각 블루 에이전트가 관측을 보고 행동 결정
        actions = {}
        for name in current_blue:
            agent = defenders.get(name)
            if agent is None:
                agent = ReactiveDefenseAgent(name) if use_custom_agents else RandomAgent()
                defenders[name] = agent
            if use_custom_agents:
                # 커스텀 방어: raw 관측 + 정수->Action 매핑을 넘김
                actions[name] = agent.get_action(
                    cyborg.get_observation(name), env.agent_actions[name]
                )
            else:
                # 내장 방어: 래퍼 관측 + Discrete 액션공간(정수 sample)
                actions[name] = agent.get_action(
                    observations[name], action_spaces[name]
                )

        observations, rewards, dones, infos = env.step(actions)
        steps_run += 1

        # 가용성 손실 누적 (Blue 보상의 CommunicationAvailability 항목)
        breakdown = cyborg.get_rewards()
        blue_bd = breakdown.get("Blue", {})
        if isinstance(blue_bd, dict):
            comm_failures += -float(blue_bd.get("CommunicationAvailability", 0.0))

        if verbose and (step % log_every == 0):
            log(f"    step {step:3d} | 생존 블루 {drones_defended:2d}/{num_drones} "
                f"| 누적 통신실패 {comm_failures:.0f}")

    # 정상 통신 최대 실패치 = 정상사용자(green=드론수) x 진행 스텝
    comm_failure_max = num_drones * max(steps_run, 1)

    return compute_scores(
        num_drones=num_drones,
        drones_defended=drones_defended,
        comm_failures=comm_failures,
        comm_failure_max=comm_failure_max,
        points_per_drone=points_per_drone,
        sla_threshold=sla_threshold,
    )
