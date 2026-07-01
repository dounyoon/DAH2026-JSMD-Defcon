# 아키텍처 · 설계 설명

## 1. 전체 실행 흐름 (단일 진입점)

```
main.py
  │  config.py 읽기
  ▼
src/runner.run_episode()
  │
  ├─ src/environment.build_environment()
  │     └─ DroneSwarmScenarioGenerator (CybORG CC3, 드론 N대)
  │        └─ PettingZooParallelWrapper 로 래핑
  │
  ├─ 매 스텝:
  │     ├─ 각 블루(방어) 에이전트가 관측 → 행동(정수 액션) 결정
  │     ├─ env.step(actions)  ← 모든 블루 동시 적용, 적 웜/정상사용자는 내부 정책
  │     └─ 가용성 손실(정상통신 실패) 누적
  │
  └─ src/scoring.compute_scores()
        └─ 총점 = (공격 + 방어) × (가용성/100)
```

## 2. 세 진영 (CybORG CC3 구조)

| 진영 | 역할 | 이 프로젝트에서 |
|------|------|-----------------|
| **Blue** | 방어 (드론당 1개 분산 배치) | 우리가 제어 (기본=RandomAgent) |
| **Red** | 공격 (드론 장악 시도) | CybORG 내장 웜 (기본) |
| **Green** | 정상 사용자 (드론 통신) | CybORG 내장 (가용성 측정 기준) |

## 3. 대회 점수와 코드의 연결

- **가용성(availability)**: 정상 사용자(Green)의 통신 성공률.
  CybORG 의 `CommunicationAvailability` 보상(통신 실패 1건당 -1)을 누적해 0~100%로 환산.
  → 적이 드론을 장악하거나 통신을 막을수록 Green 통신이 실패해 가용성이 떨어진다.
- **방어 점수(defense)**: 에피소드 종료 시 지켜낸(생존) 드론 수 × 드론당 점수.
- **공격 점수(attack)**: 장악당한 드론 수 × 드론당 점수.
- **총점**: `(공격 + 방어) × 가용성` — 가용성이 곱셈 항이라, 이기더라도
  서비스가 무너지면 총점이 급락한다. (방산 특수성의 핵심)

## 4. 공격/방어 액션 (CybORG 원본 프리미티브)

| 진영 | 주요 액션 | 의미 |
|------|-----------|------|
| Red | `ExploitDroneVulnerability` | 취약점 침투 |
| Red | `SeizeControl` | 제어권 탈취(드론 장악) |
| Red | `FloodBandwidth` | 대역폭 소모(재밍/DoS 모사) |
| Blue | `RemoveOtherSessions` | 침입 세션만 격리 |
| Blue | `RetakeControl` | 뺏긴 드론 복구 |
| Blue | `BlockTraffic`/`AllowTraffic` | 트래픽 차단/허용(동적 페일오버) |

## 5. 환경 버전 정책

CybORG 드론 시나리오는 `gym==0.23.1` 전용이라, 재현성을 위해
**Python 3.11 + numpy 1.23.5 + gym 0.23.1** 로 고정한다.
최신 `gymnasium`/CybORG v4 로의 이식은 본선 진출 후 과제로 남긴다.
