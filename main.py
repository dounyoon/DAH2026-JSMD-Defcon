"""
DAH 2026 - 드론 스웜 AI 공방전 시뮬레이션 : 단일 진입점
=======================================================
    python main.py

config.py 의 MODE 로 결정한다.
  "evaluate" : [대회 기준·기본] 내 점수 계산.
  "sample"/"baseline"/"current" : 개선 과정을 보여주는 비교용(self-play).
결과는 화면과 results.txt 에 저장된다.
"""

import warnings
warnings.filterwarnings("ignore")

import os
import sys
import config


def _ensure_cyborg_importable():
    base = getattr(config, "CYBORG_PATH", "") or ""
    if not base or not os.path.isdir(base):
        return
    for root, dirs, files in os.walk(base):
        if os.path.basename(root) == "CybORG" and "__init__.py" in files:
            parent = os.path.dirname(root)
            if parent not in sys.path:
                sys.path.insert(0, parent)
            return
    if base not in sys.path:
        sys.path.insert(0, base)


_ensure_cyborg_importable()

from src.reporter import init as _init_report, log
from src.runner import run_episode, run_my_score
from src.scoring import format_report

_MODE_LABEL = {
    "sample": "적=CybORG 내장 웜 / 아군=CybORG 내장 RandomAgent (개선 전 참조)",
    "baseline": "적=우리 공격(개선 전) / 아군=우리 방어 (공격 비교용)",
    "current": "적=우리 공격(가용성 공격 집중, IEEE 논문) / 아군=우리 방어 (공격 비교용)",
}


def _run_evaluate():
    """[대회 기준] 세 버전(sample/baseline/current)을 모두 '내 점수'로 재서 비교."""
    log("=" * 60)
    log(" DAH 2026 · 대회 기준 점수 비교 (sample / baseline / current)")
    log("=" * 60)
    log(f" 드론 {config.NUM_DRONES}대 | 스텝 {config.MAX_STEPS} | 각 측정 {config.NUM_EPISODES}회 평균")
    log(" 각 버전마다: 공격=기준방어(RandomAgent) 상대, 방어=기준공격(웜) 상대로 따로 잰다.")
    log("-" * 60)

    rows = []
    for version in ("sample", "baseline", "current"):
        log(f"\n===== [{version}] 측정 시작 =====")
        r = run_my_score(
            version=version,
            num_drones=config.NUM_DRONES, max_steps=config.MAX_STEPS,
            seed=config.SEED, num_episodes=config.NUM_EPISODES,
            attack_weights=config.ATTACK_WEIGHTS, defense_weights=config.DEFENSE_WEIGHTS,
            sla_threshold=config.SLA_THRESHOLD,
            verbose=config.VERBOSE, log_every=config.LOG_EVERY,
        )
        rows.append(r)
        log(f"[{version}] 결과")
        log(f"   내 공격력 {r['my_attack']:.1f} (상대 가용성 {r['their_availability']:.1f}%로 저하)"
            f" | 내 방어력 {r['my_defense']:.1f} | 내 가용성 {r['my_availability']:.1f}%")
        log(f"   ★ 내 대회점수 = (공격+방어)×가용성 = {r['my_total']:.1f}")
        log("")

    log("-" * 60)
    log(" 요약 (내 대회점수):")
    for r in rows:
        log(f"   {r['version']:<9} {r['my_total']:.1f}")
    log("=" * 60)


def _run_selfplay(mode):
    """비교용 self-play 모드 (sample / baseline / current)."""
    log("=" * 56)
    log(" DAH 2026 · 드론 스웜 AI 공방전 시뮬레이션 (비교용)")
    log("=" * 56)
    log(f" 드론 {config.NUM_DRONES}대 | 스텝 {config.MAX_STEPS} | "
        f"에피소드 {config.NUM_EPISODES}회 | MODE = {mode}")
    log(f" {_MODE_LABEL.get(mode, mode)}")
    log("-" * 56)

    atk, dfn, avail = [], [], []
    for ep in range(config.NUM_EPISODES):
        log(f"\n[에피소드 {ep + 1}/{config.NUM_EPISODES}]")
        s = run_episode(
            num_drones=config.NUM_DRONES, max_steps=config.MAX_STEPS,
            seed=config.SEED + ep, mode=mode,
            attack_weights=config.ATTACK_WEIGHTS, defense_weights=config.DEFENSE_WEIGHTS,
            sla_threshold=config.SLA_THRESHOLD,
            verbose=config.VERBOSE, log_every=config.LOG_EVERY,
        )
        log(format_report(s, config.SLA_THRESHOLD))
        atk.append(s["attack_score"]); dfn.append(s["defense_score"]); avail.append(s["availability"])

    n = len(atk)
    log("\n" + "=" * 56)
    log(f" [{mode}] 평균  공격력 {sum(atk)/n:.1f} | 방어력 {sum(dfn)/n:.1f} | "
        f"가용성 {sum(avail)/n:.1f}%  (에피소드 {n}회)")
    log("=" * 56)


def main():
    _init_report("results.txt")
    mode = getattr(config, "MODE", "evaluate")
    if mode == "evaluate":
        _run_evaluate()
    else:
        _run_selfplay(mode)
    log("\n(결과가 results.txt 파일에도 저장되었습니다.)")


if __name__ == "__main__":
    main()
