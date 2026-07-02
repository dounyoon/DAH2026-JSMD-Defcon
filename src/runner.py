"""
에피소드 실행 오케스트레이터
============================
공통 실행기(_run_one_episode)로 한 에피소드를 돌리고, 두 가지 방식으로 쓴다.

  1) run_episode(mode)  : self-play 비교용 (sample / baseline / current)
  2) run_my_score()     : [대회 기준] 내 점수.
       - 내 공격 vs 기준 방어(RandomAgent)  → 내 공격력
       - 내 방어 vs 기준 공격(CybORG 웜)    → 내 방어력 · 내 가용성
       - 내 대회점수 = (내 공격력 + 내 방어력) × 내 가용성
"""

import statistics as st

from CybORG import CybORG
from CybORG.Simulator.Scenarios import DroneSwarmScenarioGenerator
from CybORG.Agents.Wrappers import PettingZooParallelWrapper
from CybORG.Agents.SimpleAgents.RandomAgent import RandomAgent

from src.scoring import compute_scores
from src.reporter import log


def _alive_blue(cyborg):
    return [a for a in cyborg.active_agents if "blue" in a]


def _run_one_episode(num_drones, max_steps, seed, red_cls, blue_kind,
                     attack_weights, defense_weights, sla_threshold,
                     verbose=False, log_every=25):
    """red_cls=None 이면 CybORG 내장 웜. blue_kind: 'mine'(우리 방어) / 'random'(기준 방어)."""
    kwargs = dict(num_drones=num_drones, maximum_steps=max_steps)
    if red_cls is not None:
        kwargs["default_red_agent"] = red_cls
    sg = DroneSwarmScenarioGenerator(**kwargs)
    cyborg = CybORG(scenario_generator=sg, environment="sim", seed=seed)
    env = PettingZooParallelWrapper(env=cyborg)
    observations = env.reset()
    action_spaces = env.action_spaces

    blue = [a for a in env.agents if "blue" in a]
    if blue_kind == "mine":
        from src.defense_agent import ReactiveDefenseAgent
        defenders = {n: ReactiveDefenseAgent(n) for n in blue}
    else:
        defenders = {n: RandomAgent() for n in blue}

    comm_failures = 0.0
    compromise_integral = 0
    protection_integral = 0
    seize_events = 0
    recovery_events = 0
    first_seize_step = None
    steps_run = 0
    prev = len(_alive_blue(cyborg))

    for step in range(max_steps):
        alive = len(_alive_blue(cyborg))
        comp = num_drones - alive
        compromise_integral += comp
        protection_integral += alive
        if alive < prev:
            seize_events += (prev - alive)
        elif alive > prev:
            recovery_events += (alive - prev)
        if comp > 0 and first_seize_step is None:
            first_seize_step = step
        prev = alive

        current_blue = [a for a in env.agents if "blue" in a]
        if not current_blue:
            break

        actions = {}
        for name in current_blue:
            agent = defenders.get(name)
            if agent is None:
                if blue_kind == "mine":
                    from src.defense_agent import ReactiveDefenseAgent
                    agent = ReactiveDefenseAgent(name)
                else:
                    agent = RandomAgent()
                defenders[name] = agent
            if blue_kind == "mine":
                actions[name] = agent.get_action(cyborg.get_observation(name), env.agent_actions[name])
            else:
                actions[name] = agent.get_action(observations[name], action_spaces[name])

        observations, rewards, dones, infos = env.step(actions)
        steps_run += 1

        breakdown = cyborg.get_rewards()
        blue_bd = breakdown.get("Blue", {})
        if isinstance(blue_bd, dict):
            comm_failures += -float(blue_bd.get("CommunicationAvailability", 0.0))

        if verbose and (step % log_every == 0):
            log(f"    step {step:3d} | 생존 블루 {len(_alive_blue(cyborg)):2d}/{num_drones} "
                f"| 누적 통신실패 {comm_failures:.0f}")

    if first_seize_step is None:
        first_seize_step = steps_run

    return compute_scores(
        num_drones=num_drones, steps_run=steps_run, comm_failures=comm_failures,
        compromise_integral=compromise_integral, protection_integral=protection_integral,
        recovery_events=recovery_events, seize_events=seize_events,
        first_seize_step=first_seize_step, attack_weights=attack_weights,
        defense_weights=defense_weights, sla_threshold=sla_threshold,
    )


def run_episode(num_drones, max_steps, seed, mode,
                attack_weights, defense_weights, sla_threshold,
                verbose=True, log_every=25):
    """self-play 비교용 (sample / baseline / current)."""
    red_cls = None
    if mode == "baseline":
        from src.attack_agent_baseline import BaselineAttackAgent
        red_cls = BaselineAttackAgent
    elif mode == "current":
        from src.attack_agent import AdaptiveAttackAgent
        red_cls = AdaptiveAttackAgent
    blue_kind = "random" if mode == "sample" else "mine"
    return _run_one_episode(num_drones, max_steps, seed, red_cls, blue_kind,
                            attack_weights, defense_weights, sla_threshold,
                            verbose, log_every)


def _attack_class(version):
    """버전별 공격 에이전트 (sample=CybORG 웜=None)."""
    if version == "sample":
        return None
    if version == "baseline":
        from src.attack_agent_baseline import BaselineAttackAgent
        return BaselineAttackAgent
    from src.attack_agent import AdaptiveAttackAgent
    return AdaptiveAttackAgent


def _defense_setup(version):
    """버전별 방어. (blue_kind, RetakeControl 복구확률)
       sample=무작위, baseline=우리 방어(복구 없음), current=우리 방어(복구 있음)."""
    if version == "sample":
        return "random", None
    if version == "baseline":
        return "mine", 0.0     # 복구 로직 고치기 전(옛 방어) 재현
    return "mine", 0.5         # 복구 로직 개선 후


def run_my_score(version, num_drones, max_steps, seed, num_episodes,
                 attack_weights, defense_weights, sla_threshold,
                 verbose=True, log_every=25):
    """[대회 기준] 특정 버전의 내 점수.
       공격측: 그 버전 공격 vs 기준 방어(RandomAgent)
       방어측: 그 버전 방어 vs 기준 공격(CybORG 웜)
       내 대회점수 = (내 공격력 + 내 방어력) × 내 가용성."""
    # 공격측
    red = _attack_class(version)
    atk, their_av = [], []
    for ep in range(num_episodes):
        if verbose:
            log(f"  [{version} · 공격측 ep {ep + 1}/{num_episodes}] 내 공격 vs 기준 방어(RandomAgent)")
        s = _run_one_episode(num_drones, max_steps, seed + ep,
                             red, "random",
                             attack_weights, defense_weights, sla_threshold,
                             verbose, log_every)
        atk.append(s["attack_score"])
        their_av.append(s["availability"])

    # 방어측 (기준 공격=웜에 대해)
    blue_kind, retake_p = _defense_setup(version)
    if blue_kind == "mine":
        from src.defense_agent import ReactiveDefenseAgent
        ReactiveDefenseAgent.RETAKE_PROBABILITY = retake_p
    dfn, my_av = [], []
    for ep in range(num_episodes):
        if verbose:
            log(f"  [{version} · 방어측 ep {ep + 1}/{num_episodes}] 내 방어 vs 기준 공격(웜)")
        s = _run_one_episode(num_drones, max_steps, seed + 1000 + ep,
                             None, blue_kind,
                             attack_weights, defense_weights, sla_threshold,
                             verbose, log_every)
        dfn.append(s["defense_score"])
        my_av.append(s["availability"])

    ma, md = st.mean(atk), st.mean(dfn)
    mv, tv = st.mean(my_av), st.mean(their_av)
    return {
        "version": version,
        "my_attack": ma,
        "my_defense": md,
        "my_availability": mv,
        "their_availability": tv,
        "my_total": (ma + md) * mv / 100.0,
    }
