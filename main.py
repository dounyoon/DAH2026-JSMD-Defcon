"""
DAH 2026 - 드론 스웜 AI 공방전 시뮬레이션 : 단일 진입점
=======================================================
이 파일 하나만 실행하면 전체 파이프라인이 자동으로 이어진다.

    python main.py

동작 흐름:
    config -> 환경 생성 -> 에피소드 반복 실행
    -> 스텝별 방어 에이전트 구동 -> 가용성/공격/방어 점수 집계 -> 결과 요약 출력

결과는 콘솔에 표시되며, 동시에 results.txt 파일에도 저장된다.
(CybORG 의존성인 pygame 이 콘솔 출력을 가로채는 경우가 있어, 파일 기록을 함께 남긴다.)
설정은 config.py 에서 바꾼다.
"""

import warnings
warnings.filterwarnings("ignore")   # 구형 gym/numpy 경고 숨김

import os
import sys
import config


def _ensure_cyborg_importable():
    """config.CYBORG_PATH 가 지정돼 있으면 CybORG 패키지를 sys.path 에 연결한다.
    (venv 에 CybORG 를 pip 설치하지 않은 경우를 위한 자동 경로 탐색)"""
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
from src.runner import run_episode
from src.scoring import format_report


def main():
    _init_report("results.txt")
    log("=" * 52)
    log(" DAH 2026 · 드론 스웜 AI 공방전 시뮬레이션")
    log("=" * 52)
    log(f" 드론 {config.NUM_DRONES}대 | 스텝 {config.MAX_STEPS} | "
        f"에피소드 {config.NUM_EPISODES}회")
    if config.USE_CUSTOM_AGENTS:
        log(" 적(Red) = 우리 공격 에이전트 / 아군(Blue) = 우리 방어 에이전트")
    else:
        log(" 적(Red) = CybORG 내장 웜 / 아군(Blue) = CybORG 내장 RandomAgent (raw)")
    log("-" * 52)

    totals = []
    for ep in range(config.NUM_EPISODES):
        log(f"\n[에피소드 {ep + 1}/{config.NUM_EPISODES}]")
        scores = run_episode(
            num_drones=config.NUM_DRONES,
            max_steps=config.MAX_STEPS,
            seed=config.SEED + ep,
            points_per_drone=config.POINTS_PER_DRONE,
            sla_threshold=config.SLA_THRESHOLD,
            verbose=config.VERBOSE,
            log_every=config.LOG_EVERY,
            use_custom_agents=config.USE_CUSTOM_AGENTS,
        )
        log(format_report(scores, config.SLA_THRESHOLD))
        totals.append(scores["total_score"])

    log("\n" + "=" * 52)
    log(f" 평균 총점: {sum(totals) / len(totals):.1f}  "
        f"(에피소드 {config.NUM_EPISODES}회)")
    log("=" * 52)
    log("\n(결과가 results.txt 파일에도 저장되었습니다.)")


if __name__ == "__main__":
    main()
