"""
채점 모듈 (재정의판)
====================
조사한 사이버 공방전 평가 표준(CAGE Challenge, 레드/블루팀 KPI)을 반영해,
공격력과 방어력을 '독립적으로' 그리고 '시간 누적'으로 계산한다.

이전 버전 문제: 공격점수 = 장악 드론, 방어점수 = 지켜낸 드론 이라 둘의 합이
항상 전체 드론 수로 고정되어(여집합), 총점이 사실상 가용성 하나만 반영했다.

재정의:
  공격력(Red, 높을수록 강함) = 가용성 피해 + 장악 누적 + 속도
  방어력(Blue, 높을수록 강함) = 가용성 유지 + 자산 보호 누적 + 복원력
각 항목은 0~100 으로 정규화하고, 가중치로 합쳐 0~100 점으로 만든다.

주의: 한 판(우리 공격 vs 우리 방어) 안에서 가용성/장악은 공유되므로 공격·방어가
완전히 독립일 수는 없다. 그래서 '고정 상대'로 비교해야 한다(연구 표준).
예) baseline 과 current 는 같은 방어를 쓰므로, 공격력 비교가 공정하다.
"""


def _clamp(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, x))


def compute_scores(num_drones, steps_run, comm_failures,
                   compromise_integral, protection_integral,
                   recovery_events, seize_events, first_seize_step,
                   attack_weights, defense_weights, sla_threshold):
    """누적 통계로부터 공격력/방어력 점수를 계산한다."""
    T = max(steps_run, 1)
    max_integral = num_drones * T          # 드론수 × 스텝 (누적 최대치)
    comm_failure_max = num_drones * T      # 정상통신 실패 최대치

    # --- 가용성 (0~100): 정상 통신 성공률 ---
    availability = _clamp(100.0 * (1.0 - comm_failures / comm_failure_max))

    # --- 공격력 구성요소 (각 0~100) ---
    avail_damage = _clamp(100.0 * comm_failures / comm_failure_max)   # 상대 통신 마비 정도
    compromise = _clamp(100.0 * compromise_integral / max_integral)  # 장악 시간 누적
    speed = _clamp(100.0 * (T - first_seize_step) / T)               # 빨리 뚫을수록↑
    attack_score = (
        attack_weights["availability_damage"] * avail_damage
        + attack_weights["compromise"] * compromise
        + attack_weights["speed"] * speed
    )

    # --- 방어력 구성요소 (각 0~100) ---
    protection = _clamp(100.0 * protection_integral / max_integral)  # 보호 시간 누적
    resilience = _clamp(100.0 * recovery_events / max(seize_events, 1))  # 되찾은 비율
    defense_score = (
        defense_weights["availability"] * availability
        + defense_weights["protection"] * protection
        + defense_weights["resilience"] * resilience
    )

    return {
        "availability": availability,
        "attack_score": attack_score,
        "defense_score": defense_score,
        # 세부 구성요소 (리포트/디버깅용)
        "attack_avail_damage": avail_damage,
        "attack_compromise": compromise,
        "attack_speed": speed,
        "defense_availability": availability,
        "defense_protection": protection,
        "defense_resilience": resilience,
        "sla_met": availability >= sla_threshold,
    }


def format_report(s, sla_threshold):
    sla = "충족" if s["sla_met"] else f"미달 (SLA {sla_threshold:.0f}%)"
    return (
        f"  [공격력] {s['attack_score']:.1f} / 100\n"
        f"     - 가용성 피해 {s['attack_avail_damage']:.1f} | "
        f"장악 누적 {s['attack_compromise']:.1f} | 속도 {s['attack_speed']:.1f}\n"
        f"  [방어력] {s['defense_score']:.1f} / 100\n"
        f"     - 가용성 유지 {s['defense_availability']:.1f} | "
        f"자산 보호 {s['defense_protection']:.1f} | 복원력 {s['defense_resilience']:.1f}\n"
        f"  [가용성] {s['availability']:.1f}%  [{sla}]"
    )
