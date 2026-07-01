"""
채점 모듈
=========
대회 공식을 그대로 구현한다:

    total_score = (attack_score + defense_score) * (availability / 100)

- availability : 정상 사용자(green) 통신 성공률로 산출 (0~100).
                 CybORG 의 CommunicationAvailability 보상(실패 1건당 -1)을 누적해 계산.
- defense_score: 에피소드 종료 시 지켜낸(생존) 드론 수 * 드론당 점수.
- attack_score : 장악당한(뺏긴) 드론 수 * 드론당 점수.
"""


def compute_scores(num_drones, drones_defended, comm_failures, comm_failure_max,
                   points_per_drone, sla_threshold):
    """집계된 통계로부터 대회 점수를 계산해 딕셔너리로 반환한다."""
    drones_compromised = num_drones - drones_defended

    # 가용성(%) = 정상 통신 성공 비율
    if comm_failure_max > 0:
        availability = 100.0 * (1.0 - comm_failures / comm_failure_max)
    else:
        availability = 100.0
    availability = max(0.0, min(100.0, availability))

    defense_score = points_per_drone * drones_defended
    attack_score = points_per_drone * drones_compromised
    total_score = (attack_score + defense_score) * (availability / 100.0)

    return {
        "attack_score": attack_score,
        "defense_score": defense_score,
        "availability": availability,
        "total_score": total_score,
        "drones_defended": drones_defended,
        "drones_compromised": drones_compromised,
        "sla_met": availability >= sla_threshold,
    }


def format_report(scores, sla_threshold):
    """점수 딕셔너리를 사람이 읽기 좋은 문자열로 변환한다."""
    sla = "충족" if scores["sla_met"] else f"미달 (SLA {sla_threshold:.0f}%)"
    return (
        f"  공격 점수 (attack)      : {scores['attack_score']:.1f}  "
        f"(장악 드론 {scores['drones_compromised']}대)\n"
        f"  방어 점수 (defense)     : {scores['defense_score']:.1f}  "
        f"(방어 드론 {scores['drones_defended']}대)\n"
        f"  가용성 (availability)   : {scores['availability']:.1f}%  [{sla}]\n"
        f"  --------------------------------------------\n"
        f"  총점 = (공격+방어) x 가용성 = {scores['total_score']:.1f}"
    )
